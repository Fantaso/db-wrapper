from tests.conftest import MODEL_NAME, DATA


class SQLiteManagerAllTests:
    def test_can_retrieve_all_objects(self, db):
        results = db.manager.all(MODEL_NAME)
        assert len(results) == 10
        assert results[0] == DATA[0]
