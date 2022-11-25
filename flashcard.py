import time
import cockroachdb as db
import re
from study_term import StudyTerm
from daily_stats import DailyStats
from flask import session


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

        # set up stats to update, default to today
        self.daily_stats = DailyStats.get_for_day()

    def is_correct_guess(self, guess):
        return (
            re.sub("-|\s", "", self.correct_answer, 0, re.IGNORECASE).lower()
            == re.sub("-|\s", "", guess, 0, re.IGNORECASE).lower()
        )

    def update_on_incorrect(self):
        now = int(time.time())
        db.sql_update(
            f"""
            UPDATE learning_log
            SET
                knowledge_factor = knowledge_factor / 8,
                last_review = {now}
            WHERE
                term_id = '{self.study_term.id}' AND
                quiz_type = '{self.quiz_type}' AND
                uid = '{session["uid"]}'
        """
        )
        self.daily_stats.update(False)

    def update_on_correct(self):
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
                uid = '{session["uid"]}'
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
