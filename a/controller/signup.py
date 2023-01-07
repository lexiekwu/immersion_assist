import a
import re
from enum import Enum


class SignupFailureReason(Enum):
    USER_EXISTS = 1
    INVALID_EMAIL = 2


email_regex = re.compile(
    r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
)


def try_signup(email, password, name, home_language, learning_language):
    if not _is_valid_email(email):
        return False, SignupFailureReason.INVALID_EMAIL
    elif a.model.user.User.get_by_email(email):
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


def _is_valid_email(email):
    return re.fullmatch(email_regex, email)
