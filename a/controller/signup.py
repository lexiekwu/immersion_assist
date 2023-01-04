import a
from enum import Enum


class SignupFailureReason(Enum):
    USER_EXISTS = 0


def try_signup(email, password, name, home_language, learning_language):
    if a.model.user.User.get_by_email(email):
        return False, SignupFailureReason.USER_EXISTS

    user = a.model.user.User.new(
        name=name,
        email=email,
        password=password,
        home_language=home_language,
        learning_language=learning_language,
    )

    user.login(password)
    return True, None
