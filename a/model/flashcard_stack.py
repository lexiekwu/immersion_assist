import time
from a.third_party import cockroachdb as db, session_storage
from .study_term import StudyTerm
from .flashcard import Flashcard
from .rate_limit import rate_limited_action

MIN_TIME_BETWEEN_REVIEWS_SEC = 60 * 2  # two minutes
DEFAULT_LIMIT = 10


class FlashcardStack:
    def __init__(self, limit=DEFAULT_LIMIT, existing_stack=[]):
        self.limit = limit
        if existing_stack:
            self.stack = existing_stack
        else:
            self.stack = []
            self._refresh()  # fill cards up to limit

    def pop_card(self):
        rate_limited_action("pop_card", "minutely", 50)
        while len(self.stack) < 1:
            self._refresh()
        card = self.stack[0]
        self.stack = self.stack[1:]
        return card

    def _refresh(self):
        now = int(time.time())
        card_dicts = db.sql_query(
            f"""
            WITH 
            
            -- anything in the last MIN_TIME_BETWEEN_REVIEWS_SEC seconds, for any review type
            very_recently_reviewed_terms AS (
                SELECT
                    term_id
                FROM learning_log
                WHERE
                    last_review > {now - MIN_TIME_BETWEEN_REVIEWS_SEC} AND
                    uid = '{session_storage.logged_in_user()}'
            ), 
            
            learning_log_ordered AS (
                SELECT
                    id,
                    learning_log.term_id,
                    quiz_type,
                    knowledge_factor,
                    last_review,
                    (RANDOM()::DECIMAL)
                        * (1.0 * {now} - 1.0 * last_review)
                        / knowledge_factor
                    AS idx
                FROM learning_log
                
                -- exclude very recently reviewed terms
                LEFT JOIN very_recently_reviewed_terms
                ON
                    very_recently_reviewed_terms.term_id = learning_log.term_id
                WHERE
                    very_recently_reviewed_terms.term_id IS NULL AND
                    learning_log.uid = '{session_storage.logged_in_user()}'

                ORDER BY 6 DESC
                LIMIT {self.limit * 10}
            ),

            learning_log_ordered_min_idx AS (
                SELECT
                    term_id,
                    MIN(idx) AS idx
                FROM learning_log_ordered
                GROUP BY 1
            )

            SELECT
                f.id,
                l.quiz_type,
                f.term,
                f.translated_term,
                f.pronunciation
            FROM learning_log_ordered l
            INNER JOIN study_term f
            ON
                f.id = l.term_id
            INNER JOIN learning_log_ordered_min_idx llom
            ON
                l.term_id = llom.term_id AND
                l.idx = llom.idx
            LIMIT {self.limit}
            """
        )
        flashcards = []
        for card_dict in card_dicts:
            study_term = StudyTerm(
                card_dict["id"],
                card_dict["term"],
                card_dict["translated_term"],
                card_dict["pronunciation"],
            )
            flashcard = Flashcard(study_term, card_dict["quiz_type"])
            flashcards.append(flashcard)
        self.stack = flashcards

    def to_dicts(self):
        return [flashcard.to_dict() for flashcard in self.stack]

    @classmethod
    def from_dicts(cls, ds):
        return cls(existing_stack=[Flashcard.from_dict(d) for d in ds])
