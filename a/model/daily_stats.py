from datetime import datetime, timedelta
from a.third_party import session_storage, cockroachdb as db
from a.model.rate_limit import rate_limited_action
from a.model.study_term import get_count

today_dt = str(datetime.today().date())


class DailyStats:
    def __init__(
        self,
        dt,
        count_correct,
        count_incorrect,
        avg_knowledge_factor=None,
        num_terms=None,
    ):
        self.dt = dt
        self.count_correct = count_correct
        self.count_incorrect = count_incorrect
        self.avg_knowledge_factor = (
            self._calculate_avg_knowledge_factor()
            if avg_knowledge_factor is None
            else avg_knowledge_factor
        )
        self.num_terms = get_count() if num_terms is None else num_terms

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
            and session_storage.get("num_terms")
        ):
            return cls(
                dt,
                session_storage.get("count_correct"),
                session_storage.get("count_incorrect"),
                session_storage.get("avg_knowledge_factor"),
                session_storage.get("num_terms"),
            )

        rate_limited_action("get_stats_for_day", "minutely", 200)
        stats_dict = db.sql_query_single(
            f"""
                SELECT *
                FROM daily_stats
                WHERE
                    dt = '{dt}' AND
                    uid = '{session_storage.logged_in_user()}'
            """
        )

        if not stats_dict:
            # only create a new entry if it's today
            if dt == today_dt:
                new_stats_day = cls(dt, 0, 0, None)
                new_stats_day._save()
                return new_stats_day
            return None

        if dt == today_dt:
            session_storage.update(
                {
                    "dt": dt,
                    "count_correct": stats_dict["count_correct"],
                    "count_incorrect": stats_dict["count_incorrect"],
                    "avg_knowledge_factor": stats_dict["avg_knowledge_factor"],
                    "num_terms": stats_dict["num_terms"],
                }
            )

        return cls(
            dt,
            stats_dict["count_correct"],
            stats_dict["count_incorrect"],
            stats_dict["avg_knowledge_factor"],
            stats_dict["num_terms"],
        )

    @classmethod
    def get_recent(cls, count):
        rate_limited_action("get_recent_stats", "minutely", 10)
        min_dt = str((datetime.today() - timedelta(count)).date())
        rows = db.sql_query(
            f"""
        SELECT *
        FROM daily_stats
        WHERE
            uid = '{session_storage.logged_in_user()}' AND
            dt >= '{min_dt}'
        """
        )
        return [
            cls(
                row["dt"],
                row["count_correct"],
                row["count_incorrect"],
                row["avg_knowledge_factor"],
                row["num_terms"],
            )
            for row in rows
        ]

    def update(self, is_correct):
        rate_limited_action("update_stats", "minutely", 50)
        self.count_correct += int(is_correct)
        self.count_incorrect += 1 - int(is_correct)
        self._save()

    def _save(self):
        db.sql_update(
            f"""
            UPSERT INTO daily_stats (
                dt, 
                uid, 
                count_correct, 
                count_incorrect, 
                avg_knowledge_factor,
                num_terms
            )
            VALUES (
                '{self.dt}',
                '{session_storage.logged_in_user()}',
                {self.count_correct},
                {self.count_incorrect},
                {self.avg_knowledge_factor},
                {self.num_terms}
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
                    "num_terms": self.num_terms,
                }
            )

    def _calculate_avg_knowledge_factor(self):
        rate_limited_action("calculate_avg_knowledge_factor_stats", "minutely", 10)
        entry = db.sql_query_single(
            f"""
            SELECT
                AVG(
                    LOG(2, knowledge_factor)
                ) AS akf
            FROM learning_log
            WHERE uid = '{session_storage.logged_in_user()}'
            """
        )
        if entry and entry.get("akf"):
            return entry["akf"]

        # nothing yet logged for this user
        return 0
