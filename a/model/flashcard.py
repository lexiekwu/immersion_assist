import time
from a.third_party import cockroachdb as db, session_storage
import re
from .study_term import StudyTerm
from .daily_stats import DailyStats
from .rate_limit import rate_limited_action
from flask import session


class Flashcard:
    def __init__(self, study_term, quiz_type):
        self.study_term = study_term
        self.quiz_type = quiz_type

        # set up stats to update, default to today
        self.daily_stats = DailyStats.get_for_day()

    def get_prompt(self):
        if self.quiz_type == "translation":
            return f'translation of "{self.study_term.term}"'
        elif self.quiz_type == "pronunciation":
            return f'pronunciation of "{self.study_term.term}"'
        elif self.quiz_type == "reverse_translation":
            return f'translation of "{self.study_term.translated_term}"'

    def is_correct_guess(self, guess):
        correct_answer = ""
        if self.quiz_type == "translation":
            correct_answer = self.study_term.translated_term.partition("(")[0]
            if correct_answer[-1] == " ":
                correct_answer = correct_answer[:-1]
        elif self.quiz_type == "pronunciation":
            correct_answer = self.study_term.pronunciation
        elif self.quiz_type == "reverse_translation":
            correct_answer = self.study_term.term

        return (
            re.sub("-| ", "", correct_answer, 0, re.IGNORECASE).lower()
            == re.sub("-| ", "", guess, 0, re.IGNORECASE).lower()
        )

    def update_on_incorrect(self):
        rate_limited_action("update_card", "minutely", 50)
        now = int(time.time())
        db.sql_update(
            f"""
            UPDATE learning_log
            SET
                knowledge_factor = knowledge_factor / 4,
                last_review = {now}
            WHERE
                term_id = '{self.study_term.id}' AND
                quiz_type = '{self.quiz_type}' AND
                uid = '{session_storage.logged_in_user()}'
        """
        )
        self.daily_stats.update(False)

    def update_on_correct(self):
        rate_limited_action("update_card", "minutely", 50)
        now = int(time.time())
        db.sql_update(
            f"""
            UPDATE learning_log
            SET
                knowledge_factor = knowledge_factor * 2,
                last_review = {now}
            WHERE
                term_id = '{self.study_term.id}' AND
                quiz_type = '{self.quiz_type}' AND
                uid = '{session_storage.logged_in_user()}'
        """
        )
        self.daily_stats.update(True)

    @classmethod
    def get_by_study_term_id_and_quiz_type(cls, study_term_id, quiz_type):
        study_term = StudyTerm.get_by_id(study_term_id)
        return cls(study_term, quiz_type)

    def to_dict(self):
        return {"study_term": self.study_term.to_dict(), "quiz_type": self.quiz_type}

    @classmethod
    def from_dict(cls, d):
        return cls(
            StudyTerm.from_dict(d["study_term"]),
            d["quiz_type"],
        )

    def __eq__(self, other):
        return type(self) == type(other) and (self.study_term, self.quiz_type) == (
            other.study_term,
            other.quiz_type,
        )
