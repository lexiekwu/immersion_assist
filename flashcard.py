import time
import cockroachdb as db
from study_term import StudyTerm


class Flashcard:
    def __init__(self, study_term, quiz_type):
        self.study_term = study_term
        self.quiz_type = quiz_type
        if self.quiz_type == "translation":
            self.prompt = f'translation of "{study_term.term}"'
            self.correct_answer = study_term.translated_term.partition("(")[0]
            if self.correct_answer[-1] == " ":
                self.correct_answer = self.correct_answer[:-1]
        elif self.quiz_type == "pronunciation":
            self.prompt = f'pronunciation of "{study_term.term}"'
            self.correct_answer = study_term.pronunciation
        elif self.quiz_type == "reverse_translation":
            self.prompt = f'translation of "{study_term.translated_term}"'
            self.correct_answer = study_term.term

    def is_correct_guess(self, guess):
        return self.correct_answer == guess

    def update_after_guess(self, guess):
        if self.is_correct_guess(guess):
            self._update_on_correct()
        else:
            self._update_on_incorrect()

    def _update_on_incorrect(self):
        now = int(time.time())
        db.sql_update(
            f"""
            UPDATE learning_log
            SET
                knowledge_factor = knowledge_factor / 16,
                last_review = {now}
            WHERE
                term_id = '{self.study_term.id}' AND
                quiz_type = '{self.quiz_type}'
        """
        )

    def _update_on_correct(self):
        now = int(time.time())
        db.sql_update(
            f"""
            UPDATE learning_log
            SET
                knowledge_factor = knowledge_factor * 2,
                last_review = {now}
            WHERE
                term_id = '{self.study_term.id}' AND
                quiz_type = '{self.quiz_type}'
        """
        )

    @classmethod
    def get_by_study_term_id_and_quiz_type(cls, study_term_id, quiz_type):
        study_term = StudyTerm.get_by_id(study_term_id)
        return cls(study_term, quiz_type)
