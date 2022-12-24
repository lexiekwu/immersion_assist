import uuid
import time
from a.third_party import session_storage, cockroachdb as db
import a


class StudyTerm:
    def __init__(
        self,
        id,
        term,
        translated_term,
        pronunciation,
        target_language=a.third_party.language.TW_CODE,
    ):
        self.id = id
        self.term = term
        self.target_language = target_language
        self.translated_term = translated_term
        self.pronunciation = pronunciation

    @classmethod
    def build(cls, term=None, translated_term=None, pronunciation=None):
        assert (
            term or translated_term
        ), "Cannot build a study term without either a term or a translated term given"

        if not term:
            term = a.third_party.language.get_translation(
                translated_term, a.third_party.language.TW_CODE
            )
        if not translated_term:
            translated_term = a.third_party.language.get_translation(
                term, a.third_party.language.EN_CODE
            )
        pronunciation = pronunciation or a.third_party.language.get_pronunciation(
            term, a.third_party.language.TW_CODE
        )
        id = uuid.uuid4()
        return cls(id, term, translated_term, pronunciation)

    def save(self):
        logged_in_user = session_storage.logged_in_user()
        now = int(time.time())
        insert_term_sql = f"""
            INSERT INTO study_term (id, term, translated_term, pronunciation, uid, time_added)
            VALUES
                (
                    '{self.id}',
                    '{self.term}',
                    '{self.translated_term}',
                    '{self.pronunciation}',
                    '{logged_in_user}',
                    '{now}'
                )
            ON CONFLICT (uid, term)
            DO UPDATE SET
                translated_term = '{self.translated_term}',
                pronunciation = '{self.pronunciation}',
                time_added = '{now}';
        """
        insert_learning_log_sql = f"""
            UPSERT INTO learning_log (id, term_id, quiz_type, knowledge_factor, last_review, uid)
            VALUES
                ('{uuid.uuid4()}', '{self.id}', 'pronunciation', 1.0, {now}, '{logged_in_user}'),
                ('{uuid.uuid4()}', '{self.id}', 'reverse_translation', 1.0, {now}, '{logged_in_user}'),
                ('{uuid.uuid4()}', '{self.id}', 'translation', 1.0, {now}, '{logged_in_user}')
        """
        db.sql_update_multi([insert_term_sql, insert_learning_log_sql])

    @classmethod
    def get_by_id(cls, id):
        card_dict = db.sql_query_single(
            f"""
            SELECT *
            FROM study_term
            WHERE
                uid = '{session_storage.logged_in_user()}' AND
                id = '{id}'
            """
        )
        if not card_dict:
            return None

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
                    '{session_storage.logged_in_user()}'
                )
        """
        )

    def delete(self):
        logged_in_user = session_storage.logged_in_user()
        delete_term_sql = f"""
            DELETE FROM study_term
            WHERE 
                id = '{self.id}' AND
                uid = '{logged_in_user}'
        """
        delete_learning_log_sql = f"""
            DELETE FROM learning_log
            WHERE 
                term_id = '{self.id}' AND
                uid = '{logged_in_user}'
        """
        db.sql_update_multi([delete_term_sql, delete_learning_log_sql])

    @classmethod
    def from_string(cls, term_str):
        characters, pinyin, english = _split_term(term_str)
        assert (
            characters and english and pinyin
        ), f"could not successfully split '{term_str}'"
        study_term = cls(uuid.uuid4(), characters, english, pinyin)
        return study_term

    @classmethod
    def from_dict(cls, d):
        return cls(
            d["id"],
            d["term"],
            d["translated_term"],
            d["pronunciation"],
            d.get("target_language", a.third_party.language.TW_CODE),
        )

    def to_dict(self):
        return {
            "id": self.id,
            "term": self.term,
            "target_language": self.target_language,
            "translated_term": self.translated_term,
            "pronunciation": self.pronunciation,
        }

    def __eq__(self, other: object) -> bool:
        return type(self) == type(other) and (
            self.term,
            self.translated_term,
            self.pronunciation,
            self.target_language,
        ) == (
            other.term,
            other.translated_term,
            other.pronunciation,
            other.target_language,
        )

    def __repr__(self):
        return f"{self.term}: {self.translated_term} {self.pronunciation}"


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
            uid = '{session_storage.logged_in_user()}'
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
            uid = '{session_storage.logged_in_user()}'
        """
    )["cnt"]
