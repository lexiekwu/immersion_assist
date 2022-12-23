from a.controller import login
import a


def test_try_login():
    user = a.model.user.User.new("Testley", "testley@aol.com", "iLikeTests")

    assert login.try_login("testley@gmail.com", "iLikeTests") == (False, False)
    assert login.try_login("testley@aol.com", "iLike_Tests") == (True, False)
    assert login.try_login("testley@aol.com", "iLikeTests") == (True, True)

    user.delete_all_data_TESTS_ONLY()
