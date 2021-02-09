import pytest

# from ..db import SQLiteDB
from core.db import SQLiteDB

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


#
# @pytest.fixture
# def model_name() -> str:
#     MODEL_NAME = "spoon_product"
#     return MODEL_NAME
#
#
# @pytest.fixture
# def model_fields() -> List:
#     MODEL_FIELDS = ["id", "url", "date", "rating"]
#     return MODEL_FIELDS
#
#
# @pytest.fixture
# def create_model_sql() -> List:
#     CREATE_MODEL = f"""
#                     CREATE TABLE IF NOT EXISTS {MODEL_NAME} (
#                     {MODEL_FIELDS[0]} integer PRIMARY KEY,
#                     {MODEL_FIELDS[1]} text NOT NULL,
#                     {MODEL_FIELDS[2]} text,
#                     {MODEL_FIELDS[3]} integer);"""
#     return CREATE_MODEL
#
#
# @pytest.fixture
# def insert_data_sql() -> List:
#     INSERT_DATA = f"INSERT INTO {MODEL_NAME} VALUES (?,?,?,?)"
#     return INSERT_DATA


@pytest.fixture
def empty_db():
    db = SQLiteDB(":memory:")
    db.connect()
    yield db
    db.close()


@pytest.fixture
def db(empty_db):
    db = empty_db
    db.execute(CREATE_MODEL)
    db.executemany(INSERT_DATA, DATA)
    db.commit()
    yield db


@pytest.fixture(scope="session")
def filter():
    db = SQLiteDB(":memory:")
    db.connect()
    db.execute(CREATE_MODEL)
    db.executemany(INSERT_DATA, DATA)
    db.commit()
    yield db.manager.filter
    db.close()

# @pytest.fixture
# def another_base_request(db):
#     return BaseRequest.objects.create(
#         method=BaseRequestMethod.POST,
#         path="http://shop.fantaso.de/",
#         json_body='{"message":"another body"}',
#     )
#
#
# @pytest.fixture
# def one_time_job(db, base_request):
#     return Job.objects.create(
#         title="one time request",
#         start_time=FEB_27_2021_3_PM,
#         request=base_request,
#     )
