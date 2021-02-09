from sqlite3 import ProgrammingError

import pytest

MODEL_NAME = "spoon_product"
MODEL_FIELDS = ["id", "url", "date", "rating"]

CREATE_MODEL = f"""
                CREATE TABLE IF NOT EXISTS {MODEL_NAME} (
                {MODEL_FIELDS[0]} integer PRIMARY KEY,
                {MODEL_FIELDS[1]} text NOT NULL,
                {MODEL_FIELDS[2]} text,
                {MODEL_FIELDS[3]} integer);"""
INSERT_DATA = f"INSERT INTO {MODEL_NAME} VALUES (?,?,?,?)"
SELECT_ALL = f"SELECT * FROM {MODEL_NAME}"
COUNT_ROWS = f"SELECT COUNT(*) FROM {MODEL_NAME}"

DATA = [
    # [PK, url, date, rating(0-100)]
    (1, "http://www.spoon.guru", "2021-01-01", 5),
    (2, "http://www.spoon.guru/solutions/", "2021-01-02", 5),
    (3, "http://www.spoon.guru/retail-solutions/", "2021-01-03", 10),
    (4, "http://www.spoon.guru/blog/", "2021-01-04", 35),
    (5, "http://www.spoon.guru/contact-2/", "2021-01-05", 48),
    (6, "http://www.spoon.guru/the-team/", "2021-01-05", 78),
    (7, "http://www.spoon.guru/the-gut-brain-connection/", "2021-02-02", 55),
    (8, "http://www.spoon.guru/how-it-works/", "2021-02-15", 11),
    (9, "http://www.spoon.guru/bbq-recipes/", "2021-02-16", 3),
    (10, "http://www.spoon.guru/bbq-recipes/", "2021-03-16", 3),
]


class SQLiteDBTests:
    def test_can_open_and_close_connection(self, db):
        ## CONNECTION
        assert db.connected is True
        assert db.connect() is not None

        ## DISCONNECTION
        # close connection
        db.close()

        # make sure you are no longer connected
        assert db.connected is False
        with pytest.raises(ProgrammingError):
            db.execute(CREATE_MODEL)

    def test_can_execute_query(self, db):
        db.execute(CREATE_MODEL)
        cursor = db.execute(SELECT_ALL)
        assert cursor.fetchall() == []

    def test_can_execute_many_sql_queries(self, db):
        db.execute(CREATE_MODEL)
        db.executemany(INSERT_DATA, DATA)
        cursor = db.execute(SELECT_ALL)
        assert len(cursor.fetchall()) == 10
