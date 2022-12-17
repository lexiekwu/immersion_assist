import third_party.cockroachdb as db
import uuid
import bcrypt


class User:
    def __init__(self, uid, name, email):
        self.uid = uid
        self.name = name
        self.email = email

    @classmethod
    def get_by_id(cls, uid):
        user_dict = db.sql_query_single(
            f"""
            SELECT *
            FROM users
            WHERE uid = '{uid}'
            """
        )
        return cls(uid, user_dict["name"], user_dict["email"])

    @classmethod
    def get_by_email(cls, email):
        user_dict = db.sql_query_single(
            f"""
            SELECT uid, name, email
            FROM users
            WHERE
                email = '{email}'
            """
        )
        if not user_dict:
            return None
        return cls(user_dict["uid"], user_dict["name"], user_dict["email"])

    @classmethod
    def new(cls, name, email, password):
        uid = uuid.uuid4()

        # Hash the ecoded password and generate a salt:
        password = password.encode("utf-8")
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt()).decode("UTF-8")

        db.sql_update(
            f"""
            INSERT INTO users (uid, name, email, hashed_password)
            VALUES ('{uid}', '{name}', '{email}', '{hashed_password}')
            """
        )
        return cls(uid, name, email)

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
