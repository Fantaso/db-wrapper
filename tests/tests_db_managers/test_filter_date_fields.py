from datetime import date
from operator import gt, lt, ge, le

import pytest

from tests.conftest import MODEL_NAME


class FilterDateFieldsTests:
    def test_can_filter_a_single_field_equality(self, db):
        """
        GIVEN a field date type and its value (datetime.date object)
        WHEN the db.manager.filter('table_name', field=datetime.date) and the method is call
        THEN the results that match the date object should match the quantity of entries in the db table
             and we check that the ids of those entries are the correct ones.
        """
        date_obj = date(2021, 1, 5)
        queryset_results = db.manager.filter(MODEL_NAME, date=date_obj)
        assert len(queryset_results) == 2

        expected_ids = [5, 6]
        for qs_r in queryset_results:
            assert qs_r[0] in expected_ids  # checking the id (index 0) of the correct results

    @pytest.mark.parametrize(
        "filter, lookup, lookup_date, queryset_results_len, operator",
        [["filter", "date__gt", date(2021, 1, 5), 4, gt],
         ["filter", "date__gte", date(2021, 1, 5), 6, ge],
         ["filter", "date__lt", date(2021, 1, 2), 1, lt],
         ["filter", "date__lte", date(2021, 1, 2), 2, le]],
        indirect=["filter"],
    )
    def test_can_filter_fields_with_operators_conditions(
            self,
            filter,
            lookup,
            lookup_date,
            queryset_results_len,
            operator
    ):
        """
        GIVEN a model name with a lookup date condition and its value
        WHEN the db.manager.filter('table_name', field__lookup=lookup_date)
             method is call to query and filter down the entries in the db table
        THEN we check that the quantity of results returned match the expected queryset_results_len
             and check that all entries returned match the operator condition.
        """

        queryset_results = filter(MODEL_NAME, **{lookup: lookup_date})
        assert len(queryset_results) == queryset_results_len
        # The returned date value is string type.
        #   We are not mapping the model to a python object.
        for qs_r in queryset_results:
            assert operator(qs_r[2], lookup_date.strftime('%Y-%m-%d'))  # date field is in index 2

    DATES = [
        date(2021, 1, 5),
        date(2021, 1, 2),
    ]

    @pytest.mark.parametrize(
        "filter, lookup, date_list, queryset_results_len",
        [["filter", "date__in", DATES, 3],
         ["filter", "date__not_in", DATES, 7]],
        indirect=["filter"],
    )
    def test_can_filter_fields_with_in_and_not_in_conditions(self, filter, lookup, date_list, queryset_results_len):
        """
        GIVEN a model name with a lookup condition and a list of date objects
        WHEN the db.manager.filter('table_name', field__lookup=[date objects])
             method is call to query and filter down the entries in the db table
        THEN we check that the quantity of results returned match the expected queryset_results_len.
        """
        queryset_results = filter(MODEL_NAME, **{lookup: date_list})
        assert len(queryset_results) == queryset_results_len

    def test_can_filter_date_range(self, db):
        date_from = date(2021, 2, 2)
        date_to = date(2021, 3, 16)
        queryset_results = db.manager.filter(
            MODEL_NAME,
            date__gt=date_from,
            date__lt=date_to,
        )
        assert len(queryset_results) == 2
