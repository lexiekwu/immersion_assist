from a.controller import signup
import a


def test_signup():

    assert signup.try_signup(
        "tes.tley@.aol.com",
        "iLikeTests",
        "Testley",
        "en",
        "zh-TW",
    ) == (False, a.controller.signup.SignupFailureReason.INVALID_EMAIL)

    assert signup.try_signup(
        "tes.tley@@.aol.com",
        "iLikeTests",
        "Testley",
        "en",
        "zh-TW",
    ) == (False, a.controller.signup.SignupFailureReason.INVALID_EMAIL)

    assert signup.try_signup(
        "tim.com",
        "iLikeTests",
        "Testley",
        "en",
        "zh-TW",
    ) == (False, a.controller.signup.SignupFailureReason.INVALID_EMAIL)

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
