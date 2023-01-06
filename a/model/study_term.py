import uuid
import time
from a.third_party import session_storage, cockroachdb as db, language
import a


class StudyTerm:
    def __init__(
        self,
        id,
        term,
        translated_term,
        pronunciation,
    ):
        self.id = id
        self.term = term
        self.translated_term = translated_term
        self.pronunciation = pronunciation

    @classmethod
    def build(cls, term, pronunciation=None):
        if language.is_learning_language(term):
            translated_term = language.get_translation(term, to_learning_language=False)
        else:
            translated_term = term
            term = language.get_translation(translated_term, to_learning_language=True)

        pronunciation = pronunciation or language.get_pronunciation(term)

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
        pronunciation_row_sql = (
            f"('{uuid.uuid4()}', '{self.id}', 'pronunciation', 1.0, {now}, '{logged_in_user}'),"
            if self.pronunciation
            else ""
        )
        insert_learning_log_sql = f"""
            UPSERT INTO learning_log (id, term_id, quiz_type, knowledge_factor, last_review, uid)
            VALUES
                {pronunciation_row_sql}
                ('{uuid.uuid4()}', '{self.id}', 'reverse_translation', 1.0, {now}, '{logged_in_user}'),
                ('{uuid.uuid4()}', '{self.id}', 'translation', 1.0, {now}, '{logged_in_user}')
        """
        db.sql_update_multi(
            [insert_term_sql, insert_learning_log_sql],
            inputs_to_escape=[self.term, self.pronunciation, self.translated_term],
        )

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
        """,
            inputs_to_escape=[self.term, self.pronunciation, self.translated_term],
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
        split_term = term_str.split(",")
        if len(split_term) == 2:
            term, translated_term = split_term
            pronunciation = ""
        elif len(split_term) == 3:
            term, translated_term, pronunciation = split_term
        else:
            assert False, f"could not successfully split '{term_str}'"

        study_term = cls(uuid.uuid4(), term, translated_term, pronunciation)
        return study_term

    @classmethod
    def from_dict(cls, d):
        return cls(
            d["id"],
            d["term"],
            d["translated_term"],
            d["pronunciation"],
        )

    def to_dict(self):
        return {
            "id": self.id,
            "term": self.term,
            "translated_term": self.translated_term,
            "pronunciation": self.pronunciation,
        }

    def __eq__(self, other: object) -> bool:
        return type(self) == type(other) and (
            self.term,
            self.translated_term,
            self.pronunciation,
        ) == (
            other.term,
            other.translated_term,
            other.pronunciation,
        )

    def __repr__(self):
        return f"{self.term}: {self.translated_term} {self.pronunciation}"


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
