from datetime import datetime
from flask import session
import cockroachdb as db

today_dt = str(datetime.today().date())

class DailyStats:
    def __init__(self, dt, count_correct, count_incorrect):
        self.dt = dt
        self.count_correct = count_correct
        self.count_incorrect = count_incorrect

    def accuracy(self):
        return round(
            self.count_correct * 100.0 
            / (self.count_correct + self.count_incorrect), 
        1) if (self.count_correct + self.count_incorrect) > 0 else 0

    @classmethod
    def get_for_day(cls, dt=today_dt):
        stats_dicts = db.sql_query(
            f"""
                SELECT
                    count_incorrect,
                    count_correct
                FROM daily_stats
                WHERE
                    dt = '{dt}' AND
                    uid = '{session["uid"]}'
            """
        )

        # make a row for this day if there wasn't one
        if not stats_dicts:
            new_stats_day = cls(dt, 0, 0)
            new_stats_day._save()
            return new_stats_day

        return cls(
            dt,
            stats_dicts[0]["count_correct"],
            stats_dicts[0]["count_incorrect"]
        )

    def update(self, is_correct):
        self.count_correct += int(is_correct)
        self.count_incorrect += 1 - int(is_correct)
        self._save()

    def _save(self):
        db.sql_update(f"""
            UPSERT INTO daily_stats (dt, uid, count_correct, count_incorrect)
            VALUES ('{self.dt}', '{session["uid"]}', {self.count_correct}, {self.count_incorrect})
        """)