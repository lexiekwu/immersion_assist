from datetime import datetime
from a.third_party import cockroachdb as db
from a.third_party import session_storage

today_dt = str(datetime.today().date())


class DailyStats:
    def __init__(self, dt, count_correct, count_incorrect, avg_knowledge_factor):
        self.dt = dt
        self.count_correct = count_correct
        self.count_incorrect = count_incorrect
        self.avg_knowledge_factor = (
            self._calculate_avg_knowledge_factor()
            if avg_knowledge_factor is None
            else avg_knowledge_factor
        )

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
            and session_storage.get("avg_knowledge_factor")
        ):
            return cls(
                dt,
                session_storage.get("count_correct"),
                session_storage.get("count_incorrect"),
                session_storage.get("avg_knowledge_factor"),
            )

        stats_dict = db.sql_query_single(
            f"""
                SELECT
                    count_incorrect,
                    count_correct,
                    avg_knowledge_factor
                FROM daily_stats
                WHERE
                    dt = '{dt}' AND
                    uid = '{session_storage.logged_in_user()}'
            """
        )

        # make a row for this day if there wasn't one
        if not stats_dict:
            new_stats_day = cls(dt, 0, 0, None)
            new_stats_day._save()
            return new_stats_day

        if dt == today_dt:
            session_storage.update(
                {
                    "dt": dt,
                    "count_correct": stats_dict["count_correct"],
                    "count_incorrect": stats_dict["count_incorrect"],
                    "avg_knowledge_factor": stats_dict["avg_knowledge_factor"],
                }
            )

        return cls(
            dt,
            stats_dict["count_correct"],
            stats_dict["count_incorrect"],
            stats_dict["avg_knowledge_factor"],
        )

    def update(self, is_correct):
        self.count_correct += int(is_correct)
        self.count_incorrect += 1 - int(is_correct)
        self._save()

    def _save(self):
        db.sql_update(
            f"""
            UPSERT INTO daily_stats (dt, uid, count_correct, count_incorrect, avg_knowledge_factor)
            VALUES (
                '{self.dt}',
                '{session_storage.logged_in_user()}',
                {self.count_correct},
                {self.count_incorrect},
                {self.avg_knowledge_factor}
            )
        """
        )
        if self.dt == today_dt:
            session_storage.update(
                {
                    "dt": self.dt,
                    "count_correct": self.count_correct,
                    "count_incorrect": self.count_incorrect,
                    "avg_knowledge_factor": self.avg_knowledge_factor,
                }
            )

    def _calculate_avg_knowledge_factor(self):
        entry = db.sql_query_single(
            f"""
            SELECT
                AVG(knowledge_factor) AS akf
            FROM learning_log
            WHERE uid = '{session_storage.logged_in_user()}'
            """
        )
        if entry and entry.get("akf"):
            return entry["akf"]

        # nothing yet logged for this user
        return 0
