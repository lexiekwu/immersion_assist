from a.controller import signup
import a


def test_signup():
    assert signup.try_signup(
        "testley@aol.com",
        "iLikeTests",
        "Testley",
        "en",
        "zh-TW",
    ) == (True, None)
    assert a.third_party.session_storage.logged_in_user() is not None
    assert signup.try_signup("testley@aol.com", "", "", "", "") == (
        False,
        a.controller.signup.SignupFailureReason.USER_EXISTS,
    )

    a.model.user.User.get_by_email("testley@aol.com").delete_all_data_TESTS_ONLY()


def test_can_email_signup():
    assert signup.can_email_signup("tes.tley@.aol.com") == (
        False,
        a.controller.signup.SignupFailureReason.INVALID_EMAIL,
    )

    assert signup.can_email_signup("tes.tley@@.aol.com") == (
        False,
        a.controller.signup.SignupFailureReason.INVALID_EMAIL,
    )

    assert signup.can_email_signup("tim.com") == (
        False,
        a.controller.signup.SignupFailureReason.INVALID_EMAIL,
    )

    assert signup.can_email_signup("testley@aol.com") == (True, None)
