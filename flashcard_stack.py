import time
import cockroachdb as db
from study_term import StudyTerm
from flashcard import Flashcard


class FlashcardStack:
    def __init__(self):
        # eventually will take in the user info
        pass

    def pop_card(self):
        return self.get_ordered_cards(1)[0]

    def get_ordered_cards(self, limit):
        now = int(time.time())
        card_dicts = db.sql_query(
            f"""
            WITH learning_log_ordered AS (
                SELECT
                    id,
                    term_id,
                    quiz_type,
                    knowledge_factor,
                    last_review,
                    (1.0 * {now} - 1.0 * last_review) / knowledge_factor AS idx
                FROM learning_log
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
