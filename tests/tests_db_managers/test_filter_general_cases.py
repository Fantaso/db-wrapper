import pytest

from core.formats import FilterLookupError
from tests.conftest import MODEL_NAME


class FilterGeneralTests:
    def test_can_not_filter_with_no_model_name(self, db):
        with pytest.raises(TypeError):
            db.manager.filter()

    def test_can_not_filter_field_if_lookup_not_allowed(self, db):
        """
        GIVEN the wrong or not supported lookup (field__xx) for a specific field type (str, date, int, ...)
        WHEN the db.manager.filter('table_name', field__xx=anything) and the method is call
        THEN a exception error should be raised.
        """
        url = "it does not matters"  # a string field does not support gt, lt, gte, lte
        with pytest.raises(FilterLookupError):
            db.manager.filter(MODEL_NAME, url__gt=url)
