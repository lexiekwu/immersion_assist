from a.model.rate_limit import rate_limited_action
import pytest
from a.third_party import session_storage
import uuid
import time


def test_rate_limit_action(mocker):
    session_storage.set("uid", uuid.uuid4())

    now = time.time()
    mocker.patch("time.time", return_value=now)
    rate_limited_action("test_action", "minutely", 3)
    rate_limited_action("test_action", "minutely", 3)
    rate_limited_action("test_action", "minutely", 3)
    with pytest.raises(AssertionError):
        rate_limited_action("test_action", "minutely", 3)

    mocker.patch("time.time", return_value=now + 60)
    rate_limited_action("test_action", "minutely", 3)

    mocker.patch("time.time", return_value=now)
    rate_limited_action("test_action", "daily", 2)
    rate_limited_action("test_action", "daily", 2)
    with pytest.raises(AssertionError):
        rate_limited_action("test_action", "daily", 2)

    mocker.patch("time.time", return_value=now + 60 * 60 * 24)
    rate_limited_action("test_action", "daily", 2)
