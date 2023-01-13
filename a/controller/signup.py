import a
import re
from enum import Enum


class SignupFailureReason(Enum):
    USER_EXISTS = 1
    INVALID_EMAIL = 2


email_regex = re.compile(
    r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
)


def can_email_signup(email):
    if not _is_valid_email(email):
        return False, SignupFailureReason.INVALID_EMAIL
    elif a.model.user.User.get_by_email(email):
        return False, SignupFailureReason.USER_EXISTS
    return True, None


def try_signup(email, password, name, home_language, learning_language):
    email_signup_ok, issue = can_email_signup(email)
    if not email_signup_ok:
        return False, issue

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
