from os import environ
import psycopg2
import psycopg2.extras
import time
from threading import Thread
from a.third_party import session_storage
from flask import request, copy_current_request_context

DB_URL = "".join(
    [
        "postgresql://",
        environ.get("COCKROACHDB_USER"),
        ":",
        environ.get("COCKROACHDB_PW"),
        "@free-tier4.aws-us-west-2.cockroachlabs.cloud:26257/",
        "testdb" if "PYTEST_CURRENT_TEST" in environ else "defaultdb",
        "?sslmode=verify-full&options=--cluster%3D",
        environ.get("COCKROACHDB_CLUSTER"),
    ]
)
global conn
conn = None


def _get_cur():
    global conn
    if conn is None:
        conn = psycopg2.connect(DB_URL, sslmode="prefer")

    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


def sql_query(sql):
    with _get_cur() as cur:
        try:
            cur.execute(sql)
            conn.commit()
            result = cur.fetchall()
            return result
        except Exception as e:
            conn.rollback()
            raise e


def sql_query_single(sql):
    result = sql_query(sql)
    return result[0] if result else None


def sql_update(sql, inputs_to_escape=[]):
    sql = _simple_escape_inputs(sql, inputs_to_escape)
    with _get_cur() as cur:
        try:
            cur.execute(sql)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e


def sql_update_multi(sql_list, inputs_to_escape=[]):
    sql_list = [_simple_escape_inputs(sql, inputs_to_escape) for sql in sql_list]
    with _get_cur() as cur:
        try:
            for sql in sql_list:
                cur.execute(sql)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e


def log(action, data):
    def _get_user_agent():
        try:
            return request.user_agent.string
        except RuntimeError:
            return "no_user_agent"

    def _log(action, data):
        now = time.time()
        user_agent = _get_user_agent()
        data = str(data)
        sql_update(
            f"""
            INSERT INTO log (
                action,
                time,
                uid,
                user_agent,
                extra_data
            )
            VALUES (
                '{action}',
                {now},
                '{session_storage.get_identifier()}',
                '{user_agent}',
                '{data}'
            )
        """,
            inputs_to_escape=[data, user_agent],
        )

    if "PYTEST_CURRENT_TEST" in environ:
        Thread(target=_log, args=(action, data)).start()
    else:

        @copy_current_request_context
        def _log_with_context(action, data):
            _log(action, data)

        Thread(target=_log_with_context, args=(action, data)).start()


def _simple_escape_str(str):
    return str.replace("'", "''")


def _simple_escape_inputs(sql, inputs_to_escape):
    for input in inputs_to_escape:
        sql = sql.replace(input, _simple_escape_str(input))
    return sql
