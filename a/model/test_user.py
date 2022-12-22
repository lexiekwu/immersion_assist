from a.model import user
import uuid
from a.third_party import session_storage
import pytest


class TestUser:
    def setup_method(self):
        self.test_users = []

    def test_new(self):
        u = user.User.new("Testley", "testley@aol.com", "iLikeTests")
        self.test_users.append(u)
        assert (
            u.uid is not None and u.name == "Testley" and u.email == "testley@aol.com"
        )

        # don't allow same email
        with pytest.raises(Exception):
            user.User.new("Jen", "testley@aol.com", "iLikeTests2")

    def test_get_by_id(self):
        u = user.User.new("Testley", "testley@aol.com", "iLikeTests")
        self.test_users.append(u)
        assert user.User.get_by_id(u.uid) == u
        assert user.User.get_by_id(uuid.uuid4()) is None

    def test_get_by_email(self):
        u = user.User.new("Testley", "testley@aol.com", "iLikeTests")
        self.test_users.append(u)
        assert user.User.get_by_email("testley@aol.com") == u
        assert user.User.get_by_email("testley2@aol.com") is None

    def test_is_correct_password(self):
        u = user.User.new("Testley", "testley@aol.com", "iLikeTests")
        self.test_users.append(u)
        assert u.is_correct_password("iLikeTests")
        assert not u.is_correct_password("iLikeTest_s")
        assert not u.is_correct_password("")

    def test_login(self):
        session_storage.set("uid", None)
        u = user.User.new("Testley", "testley@aol.com", "iLikeTests")
        self.test_users.append(u)
        assert session_storage.logged_in_user() is None
        u.login("iLikeTest_s")
        assert session_storage.logged_in_user() is None
        u.login("iLikeTests")
        assert session_storage.logged_in_user() == u.uid

    def teardown_method(self):
        for u in self.test_users:
            u.delete_all_data_TESTS_ONLY()
