from a.third_party import cockroachdb, session_storage
import pytest
import uuid

# All the success states are tested by the existing model tests
# so this will only test failure states
# and I am lazy ok?


def test_sql_query_failure():
    with pytest.raises(Exception):
        cockroachdb.sql_query("SELECT * FROM unknown_table")


def test_sql_query_single_failure():
    with pytest.raises(Exception):
        cockroachdb.sql_query_single("SELECT * FROM unknown_table LIMIT 1")


def test_sql_query_update_failure():
    with pytest.raises(Exception):
        cockroachdb.sql_update("UPDATE unknown_table SET column_name=1")


def test_sql_query_update_multi_failure():
    with pytest.raises(Exception):
        cockroachdb.sql_update_multi(
            [
                "UPDATE unknown_table SET column_name=1",
                "UPDATE unknown_table2 SET column_name=1",
            ]
        )


def test_escape():
    uid = uuid.uuid4()
    name = "Joseph La'Croix"
    cockroachdb.sql_update(
        f"""
        INSERT INTO users (uid, name, email, 
            hashed_password, home_language, learning_language)
        VALUES ('{uid}', '{name}', '{"joetest@gmail.com"}', 
            '___', '__', '__')
        """,
        inputs_to_escape=[name],
    )
    pulled = cockroachdb.sql_query_single(f"SELECT name FROM users WHERE uid='{uid}'")
    assert name == pulled["name"]
    cockroachdb.sql_update(f"DELETE FROM users WHERE uid='{uid}'")


def test_log():
    session_storage.set("uid", uuid.uuid4())
    # just a check it doesn't break
    cockroachdb.log("test", {"cows": 10})
