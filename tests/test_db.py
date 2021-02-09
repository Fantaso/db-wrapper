from sqlite3 import ProgrammingError

import pytest

from tests.conftest import CREATE_MODEL, SELECT_ALL, INSERT_DATA, DATA


class SQLiteDBTests:
    def test_can_open_and_close_connection(self, empty_db):
        db = empty_db
        ## CONNECTION
        assert db.connected is True
        assert db.connect() is not None

        ## DISCONNECTION
        db.close()
        assert db.connected is False
        with pytest.raises(ProgrammingError):
            db.execute(CREATE_MODEL)

    def test_can_execute_query(self, empty_db):
        db = empty_db
        db.execute(CREATE_MODEL)
        cursor = db.execute(SELECT_ALL)
        assert cursor.fetchall() == []

    def test_can_execute_many_sql_queries(self, empty_db):
        db = empty_db
        db.execute(CREATE_MODEL)
        db.executemany(INSERT_DATA, DATA)
        cursor = db.execute(SELECT_ALL)
        assert len(cursor.fetchall()) == 10

    def test_can_commit(self):
        ...
