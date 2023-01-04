from a.model import study_term
import a
import uuid


def _mock_translate(text, to_learning_language):
    if not to_learning_language:
        return "hello"
    return "你好"


class TestStudyTerm:
    def setup_method(self):
        self.test_user = a.model.user.User.new(
            "Testley", "testley2@aol.com", "iLikeTests"
        )
        self.test_user.login("iLikeTests")

    def test_build(self, mocker):

        mocker.patch("a.third_party.language.get_translation", _mock_translate)
        mocker.patch(
            "a.third_party.language.get_pronunciation", return_value="ni3 hao3"
        )

        st = study_term.StudyTerm.build(term="你好")
        assert (
            st.term,
            st.translated_term,
            st.pronunciation,
        ) == ("你好", "hello", "ni3 hao3")

        st = study_term.StudyTerm.build(term="你好", pronunciation="ni2 hao3")
        assert (
            st.term,
            st.translated_term,
            st.pronunciation,
        ) == ("你好", "hello", "ni2 hao3")

        mocker.patch("a.third_party.language.get_translation", _mock_translate)
        mocker.patch(
            "a.third_party.language.get_pronunciation", return_value="ni3 hao3"
        )

        st = study_term.StudyTerm.build(term="hello")
        assert (
            st.term,
            st.translated_term,
            st.pronunciation,
        ) == ("你好", "hello", "ni3 hao3")

    def test_save_and_get(self):
        uuid1 = uuid.uuid4()
        st = study_term.StudyTerm(
            uuid1,
            "你好",
            "hello",
            "ni3 hao3",
        )
        assert study_term.StudyTerm.get_by_id(uuid1) is None
        assert study_term.get_count() == 0

        st.save()
        assert study_term.StudyTerm.get_by_id(uuid1) == st
        assert study_term.get_count() == 1

        # test on conflict update
        st = study_term.StudyTerm(
            uuid.uuid4(),
            "你好",
            "hi",
            "ni2 hao3",
        )
        st.save()
        assert study_term.StudyTerm.get_by_id(uuid1) == study_term.StudyTerm(
            uuid1,
            "你好",
            "hi",
            "ni2 hao3",
        )
        assert study_term.get_count() == 1

    def test_update(self):
        uuid1 = uuid.uuid4()
        st = study_term.StudyTerm(uuid1, "你好", "hello", "ni3 hao3")
        st.update("再見", "goodbye", "zai4 jian4")
        assert (
            st.term,
            st.translated_term,
            st.pronunciation,
        ) == ("再見", "goodbye", "zai4 jian4")

        st_loaded = study_term.StudyTerm.get_by_id(uuid1)
        assert (
            st_loaded.term,
            st_loaded.translated_term,
            st_loaded.pronunciation,
        ) == ("再見", "goodbye", "zai4 jian4")

    def test_delete(self):
        uuid1 = uuid.uuid4()
        st = study_term.StudyTerm(uuid1, "你好", "hello", "ni3 hao3")
        st.save()
        assert study_term.get_count() == 1
        st.delete()
        assert study_term.get_count() == 0

    def test_from_string(self):
        st = study_term.StudyTerm.from_string("你好,hello,ni3 hao3")
        assert (
            st.term,
            st.translated_term,
            st.pronunciation,
        ) == ("你好", "hello", "ni3 hao3")

        st = study_term.StudyTerm.from_string("你好,hello")
        assert (
            st.term,
            st.translated_term,
            st.pronunciation,
        ) == ("你好", "hello", "")

    def test_from_dict(self):
        uuid1 = uuid.uuid4()
        dct = {
            "id": uuid1,
            "term": "你好",
            "translated_term": "hello",
            "pronunciation": "ni3 hao3",
        }

        st = study_term.StudyTerm.from_dict(dct)
        assert (
            st.term,
            st.translated_term,
            st.pronunciation,
        ) == ("你好", "hello", "ni3 hao3")

    def test_to_dict(self):
        uuid1 = uuid.uuid4()
        st = study_term.StudyTerm(uuid1, "你好", "hello", "ni3 hao3")
        assert st.to_dict() == {
            "id": uuid1,
            "term": "你好",
            "translated_term": "hello",
            "pronunciation": "ni3 hao3",
        }

    def test_get_term_page(self):
        def _get_numbered_term(i):
            return study_term.StudyTerm(uuid.uuid4(), f"你好{i}", f"hello{i}", "ni3 hao3")

        terms = []
        for i in range(5):
            term = _get_numbered_term(i)
            terms.append(term)
            term.save()

        assert set([st.term for st in terms]) == set(
            [st.term for st in study_term.get_term_page(1, 5)]
        )
        assert set() == set(study_term.get_term_page(2, 5))

    def test_get_count(self):
        def _get_numbered_term(i):
            return study_term.StudyTerm(uuid.uuid4(), f"你好{i}", f"hello{i}", "ni3 hao3")

        for i in range(3):
            assert study_term.get_count() == i
            term = _get_numbered_term(i)
            term.save()
        assert study_term.get_count() == 3

    def teardown_method(self):
        self.test_user.delete_all_data_TESTS_ONLY()
