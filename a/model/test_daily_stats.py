from datetime import datetime
from a.model import daily_stats, user, study_term
import uuid


class TestDailyStats:
    def setup_method(self):
        self.test_dt = str(datetime(1989, 9, 19).date())
        self.today_dt = str(datetime.today().date())
        self.test_user = user.User.new("Testley", "testley@aol.com", "iLikeTests")
        self.test_user.login("iLikeTests")

    def test_accuracy(self):

        ds = daily_stats.DailyStats(self.test_dt, 2, 3, None)
        assert ds.get_accuracy() == 40

        ds = daily_stats.DailyStats(self.test_dt, 10, 0, None)
        assert ds.get_accuracy() == 100

        ds = daily_stats.DailyStats(self.test_dt, 1, 2, 5)
        assert ds.get_accuracy() == 33.3

        ds = daily_stats.DailyStats(self.test_dt, 0, 0, 5)
        assert ds.get_accuracy() == 0

    def test_get_for_day(self):
        tds = daily_stats.DailyStats.get_for_day(self.test_dt)
        assert tds is None

        daily_stats.DailyStats(self.test_dt, 5, 10, None).update(False)
        daily_stats.DailyStats(self.today_dt, 6, 8, None).update(True)
        assert daily_stats.DailyStats.get_for_day(self.test_dt).count_correct == 5
        assert (
            daily_stats.DailyStats.get_for_day(self.test_dt).count_incorrect == 10 + 1
        )
        assert daily_stats.DailyStats.get_for_day(self.test_dt).dt == self.test_dt

        assert daily_stats.DailyStats.get_for_day().count_correct == 7
        assert daily_stats.DailyStats.get_for_day().count_incorrect == 8

        assert daily_stats.DailyStats.get_for_day().dt == self.today_dt

    def test_update(self):

        ds = daily_stats.DailyStats(self.test_dt, 5, 10, None)
        assert (ds.count_correct, ds.count_incorrect) == (5, 10)

        ds.update(True)
        assert (ds.count_correct, ds.count_incorrect) == (6, 10)

        ds.update(False)
        assert (ds.count_correct, ds.count_incorrect) == (6, 11)

        ds.update(False)
        assert (ds.count_correct, ds.count_incorrect) == (6, 12)

        ds = daily_stats.DailyStats(self.today_dt, 2, 3, None)
        assert (ds.count_correct, ds.count_incorrect) == (2, 3)

        ds.update(True)
        assert (ds.count_correct, ds.count_incorrect) == (3, 3)

        ds.update(True)
        assert (ds.count_correct, ds.count_incorrect) == (4, 3)

        ds.update(False)
        assert (ds.count_correct, ds.count_incorrect) == (4, 4)

    def test_avg_knowledge_factor_and_num_terms(self):
        ds = daily_stats.DailyStats(self.test_dt, 5, 10, None)
        assert ds.avg_knowledge_factor == 0  # default to 0
        assert ds.num_terms == 0  # none added

        def _get_numbered_term(i):
            return study_term.StudyTerm(uuid.uuid4(), f"你好{i}", f"hello{i}", "ni3 hao3")

        _get_numbered_term(0).save()
        _get_numbered_term(1).save()
        ds = daily_stats.DailyStats(self.today_dt, 5, 10)
        assert ds.avg_knowledge_factor == 0
        assert ds.num_terms == 2

    def test_get_recent(self):
        daily_stats.DailyStats(self.test_dt, 5, 10, None).update(False)
        daily_stats.DailyStats(self.today_dt, 6, 8, None).update(True)

        recent = daily_stats.DailyStats.get_recent(10)
        assert len(recent) == 1
        assert (recent[0].count_correct, recent[0].count_incorrect) == (7, 8)

    def teardown_method(self):
        self.test_user.delete_all_data_TESTS_ONLY()
