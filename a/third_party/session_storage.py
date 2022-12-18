from os import environ
from flask import session

_TEST_SESSION_DICT = {}


def update(dict):
    if "PYTEST_CURRENT_TEST" in environ:
        _TEST_SESSION_DICT.update(dict)
    else:
        session.update(dict)


def get(key):
    if "PYTEST_CURRENT_TEST" in environ:
        return _TEST_SESSION_DICT.get(key)
    else:
        return session.get(key)


def set(key, value):
    if "PYTEST_CURRENT_TEST" in environ:
        _TEST_SESSION_DICT[key] = value
    else:
        session[key] = value


def logged_in_user():
    if "PYTEST_CURRENT_TEST" in environ:
        return _TEST_SESSION_DICT.get("uid")
    else:
        return session.get("uid")
