import os

os.environ["PYTEST_CURRENT_TEST"] = "setup"

from a.third_party import cockroachdb as db

tables = ["test"]


def _run_command(command):
    print(f"RUNNING '{command}'")
    os.system(command)


def _setup_test_db():
    db.sql_update_multi(
        [
            """
        CREATE TABLE IF NOT EXISTS daily_stats (
        dt VARCHAR(20) NOT NULL,
        count_correct INT8 NULL,
        count_incorrect INT8 NOT NULL,
        uid UUID NULL,
        avg_knowledge_factor FLOAT8 NULL,
        CONSTRAINT daily_stats_pkey PRIMARY KEY (uid ASC, dt ASC)
        )""",
            """
        CREATE TABLE IF NOT EXISTS learning_log (
        id UUID NOT NULL,
        term_id UUID NULL,
        quiz_type VARCHAR(20) NULL,
        knowledge_factor DECIMAL NULL,
        last_review INT8 NULL,
        uid UUID NULL,
        CONSTRAINT learning_log_pkey PRIMARY KEY (id ASC)
        )""",
            """
        CREATE TABLE IF NOT EXISTS study_term (
        id UUID NOT NULL,
        term VARCHAR(128) NULL,
        translated_term VARCHAR(128) NULL,
        pronunciation VARCHAR(128) NULL,
        uid UUID NULL,
        time_added INT8 NULL,
        CONSTRAINT study_term_pkey PRIMARY KEY (id ASC),
        UNIQUE INDEX term_unique (uid ASC, term ASC)
        )""",
            """
        CREATE TABLE IF NOT EXISTS users (
        uid UUID NOT NULL,
        email VARCHAR(48) NOT NULL,
        hashed_password VARCHAR(100) NOT NULL,
        name VARCHAR(48) NOT NULL,
        home_language VARCHAR(8) NOT NULL,
        learning_language VARCHAR(8) NOT NULL,
        CONSTRAINT uid_pkey PRIMARY KEY (uid ASC),
        UNIQUE INDEX email_ukey (email ASC)
        )
        """,
            """
        CREATE TABLE IF NOT EXISTS api_wrap (
        api_enum INT2 NULL,
        args_json VARCHAR(128) NULL,
        response_json VARCHAR(256) NULL,
        rowid INT8 NOT VISIBLE NOT NULL DEFAULT unique_rowid(),
        CONSTRAINT api_wrap_pkey PRIMARY KEY (rowid ASC),
        UNIQUE INDEX lookup_unique (api_enum ASC, args_json ASC)
        )
        """,
        ]
    )


def _teardown_test_db():
    assert "testdb" in db.DB_URL, "STOPPING -- attempted to drop tables from real db"
    db.sql_update_multi(
        [
            f"DROP TABLE {table}"
            for table in ["users", "study_term", "learning_log", "daily_stats"]
        ]
    )


_setup_test_db()
_run_command("coverage run -m pytest")
_run_command("coverage report")
_teardown_test_db()
