import time
import cockroachdb as db
from study_term import StudyTerm
from flashcard import Flashcard
from flask import session

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
        if len(self.stack) < 1:
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
                    uid = '{session["uid"]}'
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
                    learning_log.uid = '{session["uid"]}'

                ORDER BY 6 DESC
                LIMIT {self.limit}
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
