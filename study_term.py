import uuid
import time
import language
import cockroachdb as db
from flask import session

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
    def build_from_term(cls, term):
        translated_term = language.get_translation(term, language.EN_CODE)
        pronunciation = language.get_pronunciation(term, language.TW_CODE)
        id = uuid.uuid4()
        return cls(id, term, translated_term, pronunciation)

    @classmethod
    def _build_from_translated_term(cls, translated_term, target_language):
        term = language.get_translation(translated_term, target_language)
        pronunciation = language.get_pronunciation(term, target_language)
        id = uuid.uuid4()
        return cls(id, term, translated_term, pronunciation, target_language)

    def save(self):
        now = int(time.time())
        insert_term_sql = f"""
            UPSERT INTO study_term (id, term, translated_term, pronunciation, uid, time_added)
            VALUES
                (
                    '{self.id}',
                    '{self.term}',
                    '{self.translated_term}',
                    '{self.pronunciation}',
                    '{session["uid"]}',
                    '{now}'
                )
        """
        insert_learning_log_sql = f"""
            UPSERT INTO learning_log (id, term_id, quiz_type, knowledge_factor, last_review, uid)
            VALUES
                ('{uuid.uuid4()}', '{self.id}', 'pronunciation', 1.0, {now}, '{session["uid"]}'),
                ('{uuid.uuid4()}', '{self.id}', 'reverse_translation', 1.0, {now}, '{session["uid"]}'),
                ('{uuid.uuid4()}', '{self.id}', 'translation', 1.0, {now}, '{session["uid"]}')
        """
        db.sql_update_multi([insert_term_sql, insert_learning_log_sql])

    @classmethod
    def build_and_save_from_translated_term(
        cls, translated_term, target_language=TW_CODE
    ):
        term = cls._build_from_translated_term(translated_term, target_language)
        term.save()
        return term

    @classmethod
    def get_by_id(cls, id):
        card_dict = db.sql_query_single(
            f"""
            SELECT *
            FROM study_term
            WHERE
                uid = '{session["uid"]}' AND
                id = '{id}'
            """
        )
        return cls(
            id,
            card_dict["term"],
            card_dict["translated_term"],
            card_dict["pronunciation"],
        )

    def update(self, term, translated_term, pronunciation):
        self.term = term
        self.translated_term = translated_term
        self.pronunciation = pronunciation
        db.sql_update(
            f"""
            UPSERT INTO study_term (id, term, translated_term, pronunciation, uid)
            VALUES
                (
                    '{self.id}',
                    '{term}',
                    '{translated_term}',
                    '{pronunciation}',
                    '{session["uid"]}'
                )
        """
        )

    def toString(self):
        return f"{self.term}: {self.translated_term} ({self.pronunciation})"

    @classmethod
    def save_from_string(cls, term_str):
        characters, pinyin, english = _split_term(term_str)
        assert (
            characters and english and pinyin
        ), f"could not successfully split '{term_str}'"
        study_term = cls(uuid.uuid4(), characters, english, pinyin)
        study_term.save()
        return study_term

    @classmethod
    def from_dict(cls, d):
        return cls(
            d["id"],
            d["term"],
            d["translated_term"],
            d["pronunciation"],
            d.get("target_language", TW_CODE),
        )

    def to_dict(self):
        return {
            "id": self.id,
            "term": self.term,
            "target_language": self.target_language,
            "translated_term": self.translated_term,
            "pronunciation": self.pronunciation,
        }


def _split_term(term):
    parts = term.split(" ")
    characters = parts[0]
    i = 1
    while (
        i < len(parts)
        and len(parts[i]) > 1
        and parts[i][0].isalpha()
        and parts[i][-1].isnumeric()
    ):
        i += 1
    pinyin = " ".join(parts[1:i])
    english = " ".join(parts[i:])
    return characters, pinyin, english


def get_term_page(page_number, limit):
    ds = db.sql_query(
        f"""
        SELECT *
        FROM study_term
        WHERE
            uid = '{session["uid"]}'
        ORDER BY 
            time_added DESC, 
            translated_term ASC
        LIMIT {limit}
        OFFSET {limit * (page_number-1)}
        """
    )
    return [StudyTerm.from_dict(d) for d in ds]


def get_count():
    return db.sql_query_single(
        f"""
        SELECT 
            COUNT(*) AS cnt
        FROM study_term
        WHERE
            uid = '{session["uid"]}'
        """
    )["cnt"]
