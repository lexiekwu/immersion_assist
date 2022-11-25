import time
import cockroachdb as db
from study_term import StudyTerm
from flashcard import Flashcard
from flask import session

MIN_TIME_BETWEEN_REVIEWS_SEC = 60 * 2  # two minutes


class FlashcardStack:
    def __init__(self):
        pass

    def pop_card(self):
        return self.get_ordered_cards(1)[0]

    def get_ordered_cards(self, limit):
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
                LIMIT {limit}
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

        return flashcards
