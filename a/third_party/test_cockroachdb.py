from a.third_party import cockroachdb
import pytest

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
