from os import environ
import psycopg2
import psycopg2.extras

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

# init client
conn = psycopg2.connect(DB_URL, sslmode="prefer")


def _get_cur():
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


def sql_update(sql):
    with _get_cur() as cur:
        try:
            cur.execute(sql)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e


def sql_update_multi(sql_list):
    with _get_cur() as cur:
        try:
            for sql in sql_list:
                cur.execute(sql)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
