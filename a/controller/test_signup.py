from a.controller import signup
import a


def test_signup():

    assert signup.try_signup("testley@aol.com", "iLikeTests", "Testley") == (True, None)
    assert a.third_party.session_storage.logged_in_user() is not None
    assert signup.try_signup("testley@aol.com", "", "") == (
        False,
        a.controller.signup.SignupFailureReason.USER_EXISTS,
    )

    a.model.user.User.get_by_email("testley@aol.com").delete_all_data_TESTS_ONLY()
