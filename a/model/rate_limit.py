from a.third_party import session_storage, cockroachdb as db
import time

TIME_SPAN_SECONDS = {"daily": 3600 * 24, "secondly": 1, "hourly": 3600, "minutely": 60}


def rate_limited_action(action, timespan, limit):
    time_span_secs = TIME_SPAN_SECONDS[timespan]
    now = int(time.time())
    time_span_bucket = int(now / time_span_secs)
    result = db.sql_query_single(
        f"""
        SELECT count
        FROM rate_limit
        WHERE
            action = '{action}' AND
            uid = '{session_storage.logged_in_user()}' AND
            bucket_type = {time_span_secs} AND
            bucket = {time_span_bucket}
    """
    )
    if result:
        assert (
            result["count"] < limit
        ), f"Rate limit for {action} exceeded. Try again later."

        db.sql_update(
            f"""
            UPDATE rate_limit
            SET count = count + 1
            WHERE
                action = '{action}' AND
                uid = '{session_storage.logged_in_user()}' AND
                bucket_type = {time_span_secs} AND
                bucket = {time_span_bucket}
        """
        )
    else:
        db.sql_update(
            f"""
            INSERT INTO rate_limit (
                action,
                uid,
                bucket_type,
                bucket,
                count
            )
            VALUES
                (
                    '{action}',
                    '{session_storage.logged_in_user()}',
                    {time_span_secs},
                    {time_span_bucket},
                    1
                )
        """
        )
