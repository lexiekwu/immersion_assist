import uuid
import time
import language
import cockroachdb as db

TW_CODE = "zh-TW"  # TODO make flexible


class StudyTerm:
    def __init__(
        self,
        id,
        term,
        translated_term,
        pronunciation,
        target_language=TW_CODE,
    ):
        self.id = id
        self.term = term
        self.target_language = target_language
        self.translated_term = translated_term
        self.pronunciation = pronunciation

    @classmethod
    def _build_from_term(cls, term, target_language):
        translated_term = language.get_translation(term, target_language)
        pronunciation = language.get_pronunciation(translated_term, target_language)
        id = uuid.uuid4()
        return cls(id, term, translated_term, pronunciation, target_language)

    def _save(self):
        now = int(time.time())
        insert_term_sql = f"""
            UPSERT INTO study_term (id, term, translated_term, pronunciation)
            VALUES
                (
                    '{self.id}',
                    '{self.term}',
                    '{self.translated_term}',
                    '{self.pronunciation}'
                )
        """
        insert_learning_log_sql = f"""
            UPSERT INTO learning_log (id, term_id, quiz_type, knowledge_factor, last_review)
            VALUES
                ('{uuid.uuid4()}', '{self.id}', 'pronunciation', 1.0, {now}),
                ('{uuid.uuid4()}', '{self.id}', 'reverse_translation', 1.0, {now}),
                ('{uuid.uuid4()}', '{self.id}', 'translation', 1.0, {now})
        """
        db.sql_update_multi([insert_term_sql, insert_learning_log_sql])

    @classmethod
    def create_and_save(cls, term, target_language=TW_CODE):
        term = cls._build_from_term(term, target_language)
        term._save()
        return term

    @classmethod
    def get_by_id(cls, id):
        card_dict = db.sql_query(
            f"""
            SELECT *
            FROM study_term
            WHERE id = '{id}'
            """
        )[0]
        return cls(
            id,
            card_dict["term"],
            card_dict["translated_term"],
            card_dict["pronunciation"],
        )

    def toString(self):
        return f"{self.term}: {self.translated_term} ({self.pronunciation})"
