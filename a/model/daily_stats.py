from datetime import datetime
from a.third_party import cockroachdb as db
from a.third_party import session_storage

today_dt = str(datetime.today().date())


class DailyStats:
    def __init__(self, dt, count_correct, count_incorrect):
        self.dt = dt
        self.count_correct = count_correct
        self.count_incorrect = count_incorrect

    def get_accuracy(self):
        return (
            round(
                self.count_correct
                * 100.0
                / (self.count_correct + self.count_incorrect),
                1,
            )
            if (self.count_correct + self.count_incorrect) > 0
            else 0
        )

    @classmethod
    def get_for_day(cls, dt=today_dt):
        if (
            session_storage.get("count_correct")
            and session_storage.get("count_incorrect")
            and session_storage.get("dt") == dt
        ):
            return cls(
                dt,
                session_storage.get("count_correct"),
                session_storage.get("count_incorrect"),
            )

        stats_dict = db.sql_query_single(
            f"""
                SELECT
                    count_incorrect,
                    count_correct
                FROM daily_stats
                WHERE
                    dt = '{dt}' AND
                    uid = '{session_storage.logged_in_user()}'
            """
        )

        # make a row for this day if there wasn't one
        if not stats_dict:
            new_stats_day = cls(dt, 0, 0)
            new_stats_day._save()
            return new_stats_day

        if dt == today_dt:
            session_storage.update(
                {
                    "dt": dt,
                    "count_correct": stats_dict["count_correct"],
                    "count_incorrect": stats_dict["count_incorrect"],
                }
            )
        return cls(dt, stats_dict["count_correct"], stats_dict["count_incorrect"])

    def update(self, is_correct):
        self.count_correct += int(is_correct)
        self.count_incorrect += 1 - int(is_correct)
        self._save()

    def _save(self):
        db.sql_update(
            f"""
            UPSERT INTO daily_stats (dt, uid, count_correct, count_incorrect)
            VALUES ('{self.dt}', '{session_storage.logged_in_user()}', {self.count_correct}, {self.count_incorrect})
        """
        )
        if self.dt == today_dt:
            session_storage.update(
                {
                    "dt": self.dt,
                    "count_correct": self.count_correct,
                    "count_incorrect": self.count_incorrect,
                }
            )
