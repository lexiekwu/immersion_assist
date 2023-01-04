import a.third_party.cockroachdb as db
import uuid
import bcrypt
from a.third_party import session_storage, language


class User:
    def __init__(self, uid, name, email, home_language, learning_language):
        self.uid = uid
        self.name = name
        self.email = email
        self.home_language = home_language
        self.learning_language = learning_language

    @classmethod
    def get_by_id(cls, uid):
        user_dict = db.sql_query_single(
            f"""
            SELECT *
            FROM users
            WHERE uid = '{uid}'
            """
        )
        if not user_dict:
            return None
        return cls(
            uid,
            user_dict["name"],
            user_dict["email"],
            user_dict["home_language"],
            user_dict["learning_language"],
        )

    @classmethod
    def get_by_email(cls, email):
        user_dict = db.sql_query_single(
            f"""
            SELECT uid, name, email, home_language, learning_language
            FROM users
            WHERE
                email = '{email}'
            """
        )
        if not user_dict:
            return None
        return cls(
            user_dict["uid"],
            user_dict["name"],
            user_dict["email"],
            user_dict["home_language"],
            user_dict["learning_language"],
        )

    @classmethod
    def new(
        cls,
        name,
        email,
        password,
        home_language=language.EN_CODE,
        learning_language=language.TW_CODE,
    ):
        uid = uuid.uuid4()

        # Hash the ecoded password and generate a salt:
        password = password.encode("utf-8")
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt()).decode("UTF-8")

        db.sql_update(
            f"""
            INSERT INTO users (uid, name, email, 
                hashed_password, home_language, learning_language)
            VALUES ('{uid}', '{name}', '{email}', 
                '{hashed_password}', '{home_language}', '{learning_language}')
            """
        )
        return cls(uid, name, email, home_language, learning_language)

    def _get_hashed_password(self):
        return db.sql_query_single(
            f"""
            SELECT hashed_password
            FROM users
            WHERE uid = '{self.uid}'
        """
        )["hashed_password"]

    def is_correct_password(self, guessed_password):
        correct_hashed_password = self._get_hashed_password().encode("utf-8")

        # Encode the tried password:
        guessed_password = guessed_password.encode("utf-8")

        # Use conditions to compare the authenticating password with the stored one:
        return bcrypt.checkpw(guessed_password, correct_hashed_password)

    def login(self, guessed_password):
        if self.is_correct_password(guessed_password):
            session_storage.set("uid", self.uid)
            session_storage.set("home_language", self.home_language)
            session_storage.set("learning_language", self.learning_language)

    def __eq__(self, other):
        return type(self) == type(other) and (
            str(self.uid),
            self.name,
            self.email,
            self.home_language,
            self.learning_language,
        ) == (
            str(other.uid),
            other.name,
            other.email,
            other.home_language,
            other.learning_language,
        )

    def __repr__(self):
        return f"\n{self.uid}\n{self.name}\n{self.email}"

    def delete_all_data_TESTS_ONLY(self):
        db.sql_update_multi(
            f"DELETE FROM {table} WHERE uid = '{self.uid}'"
            for table in ["daily_stats", "learning_log", "study_term", "users"]
        )
