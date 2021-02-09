import pytest

# from ..db import SQLiteDB
from core.db import SQLiteDB


@pytest.fixture
def db():
    db = SQLiteDB(":memory:")
    db.connect()
    yield db
    db.close()

# @pytest.fixture
# def db():
#     return "this is the db"

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
