from a.model import flashcard, study_term, daily_stats
from a.third_party import cockroachdb as db
from datetime import datetime
import a
import uuid


class TestFlashcard:
    def setup_method(self):
        self.test_user = a.model.user.User.new(
            "Testley", "testley2@aol.com", "iLikeTests"
        )
        self.test_user.login("iLikeTests")

        # reset stats
        today = str(datetime.today().date())
        daily_stats.DailyStats(today, 0, 0)._save()

    def test_get_prompt(self):
        st = study_term.StudyTerm(
            uuid.uuid4(),
            "你好",
            "hello",
            "ni3 hao3",
        )
        f = flashcard.Flashcard(st, "translation")
        assert f.get_prompt() == 'translation of "你好"'

        f = flashcard.Flashcard(st, "reverse_translation")
        assert f.get_prompt() == 'translation of "hello"'

        f = flashcard.Flashcard(st, "pronunciation")
        assert f.get_prompt() == 'pronunciation of "你好"'

    def test_is_correct_guess(self):
        st = study_term.StudyTerm(
            uuid.uuid4(),
            "你好",
            "hello",
            "ni3 hao3",
        )
        f = flashcard.Flashcard(st, "translation")
        assert f.is_correct_guess("hello") is True
        assert f.is_correct_guess("hEllo-") is True
        assert f.is_correct_guess("hi") is False
        assert f.is_correct_guess("he llo") is True

        f = flashcard.Flashcard(st, "reverse_translation")
        assert f.is_correct_guess("你好") is True
        assert f.is_correct_guess("妳好") is False
        assert f.is_correct_guess("ni3 hao3") is False

        f = flashcard.Flashcard(st, "pronunciation")
        assert f.is_correct_guess("ni3 hao3") is True
        assert f.is_correct_guess("妳好") is False

    def test_update_on_incorrect(self):
        ds = daily_stats.DailyStats.get_for_day()
        assert (ds.count_correct, ds.count_incorrect) == (0, 0)
        st = study_term.StudyTerm(
            uuid.uuid4(),
            "你好",
            "hello",
            "ni3 hao3",
        )
        f = flashcard.Flashcard(st, "translation")
        f.update_on_incorrect()
        assert (ds.count_correct, ds.count_incorrect) == (0, 1)
        assert (
            db.sql_query_single(
                f"""
            SELECT knowledge_factor
            FROM learning_log
            WHERE
                term_id = '{f.study_term.id}' AND
                quiz_type = '{f.quiz_type}' AND
                uid = '{self.test_user.uid}'
        """
            )["knowledge_factor"]
            == 0.5
        )

    def test_update_on_incorrect(self):
        ds = daily_stats.DailyStats.get_for_day()
        assert (ds.count_correct, ds.count_incorrect) == (0, 0)
        st = study_term.StudyTerm(
            uuid.uuid4(),
            "你好",
            "hello",
            "ni3 hao3",
        )
        st.save()
        f = flashcard.Flashcard(st, "translation")
        f.update_on_incorrect()
        ds = daily_stats.DailyStats.get_for_day()
        assert (ds.count_correct, ds.count_incorrect) == (0, 1)
        assert (
            db.sql_query_single(
                f"""
            SELECT knowledge_factor
            FROM learning_log
            WHERE
                term_id = '{f.study_term.id}' AND
                quiz_type = '{f.quiz_type}' AND
                uid = '{self.test_user.uid}'
        """
            )["knowledge_factor"]
            == 0.25
        )

    def test_update_on_correct(self):
        ds = daily_stats.DailyStats.get_for_day()
        assert (ds.count_correct, ds.count_incorrect) == (0, 0)
        st = study_term.StudyTerm(
            uuid.uuid4(),
            "你好",
            "hello",
            "ni3 hao3",
        )
        st.save()
        f = flashcard.Flashcard(st, "translation")
        f.update_on_correct()
        ds = daily_stats.DailyStats.get_for_day()
        assert (ds.count_correct, ds.count_incorrect) == (1, 0)
        assert (
            db.sql_query_single(
                f"""
            SELECT knowledge_factor
            FROM learning_log
            WHERE
                term_id = '{f.study_term.id}' AND
                quiz_type = '{f.quiz_type}' AND
                uid = '{self.test_user.uid}'
        """
            )["knowledge_factor"]
            == 2.0
        )

    def test_get_by_study_term_id_and_quiz_type(self):
        uuid1 = uuid.uuid4()
        st = study_term.StudyTerm(
            uuid1,
            "你好",
            "hello",
            "ni3 hao3",
        )
        st.save()

        f = flashcard.Flashcard.get_by_study_term_id_and_quiz_type(uuid1, "translation")
        assert f == flashcard.Flashcard(st, "translation")

    def test_to_from_dict(self):
        st = study_term.StudyTerm(
            uuid.uuid4(),
            "你好",
            "hello",
            "ni3 hao3",
        )
        dct = {"study_term": st.to_dict(), "quiz_type": "pronunciation"}
        f = flashcard.Flashcard.from_dict(dct)
        assert f == flashcard.Flashcard(st, "pronunciation")
        assert f.to_dict() == dct

    def teardown_method(self):
        self.test_user.delete_all_data_TESTS_ONLY()
