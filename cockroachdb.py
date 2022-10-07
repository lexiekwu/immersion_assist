from os import environ
import psycopg2
import psycopg2.extras

DB_URL = "".join(
    [
        "postgresql://",
        environ.get("COCKROACHDB_USER"),
        ":",
        environ.get("COCKROACHDB_PW"),
        "@free-tier4.aws-us-west-2.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full&options=--cluster%3D",
        environ.get("COCKROACHDB_CLUSTER"),
        #"?sslmode=prefer",
    ]
)

# init client
db_conn = psycopg2.connect(DB_URL, sslmode="prefer")
db_cursor = db_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


def sql_query(sql):
    try:
        db_cursor.execute(sql)
        db_conn.commit()
        result = db_cursor.fetchall()
        return result
    except psycopg2.Error as e:
        db_cursor.execute("ROLLBACK")
        raise e


def sql_update(sql):
    try:
        db_cursor.execute(sql)
        db_conn.commit()
    except psycopg2.Error as e:
        db_cursor.execute("ROLLBACK")
        raise e


def sql_update_multi(sql_list):
    try:
        for sql in sql_list:
            db_cursor.execute(sql)
        db_conn.commit()
    except psycopg2.Error as e:
        db_cursor.execute("ROLLBACK")
        raise e
