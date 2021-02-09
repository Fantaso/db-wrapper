from operator import gt, ge, lt, le

import pytest

from tests.conftest import MODEL_NAME, DATA


class FilterIntegerFieldTests:
    def test_can_filter_field_equality_single_result(self, db):
        first_row = DATA[0]

        ## RETRIEVING ONLYE A SINGLE(1) OBJECT
        id = first_row[0]
        results = db.manager.filter(MODEL_NAME, id=id)
        assert len(results) == 1
        assert results[0][0] == id
        assert results[0] == first_row

    def test_can_filter_field_equality_multiple_results(self, db):
        first_row = DATA[0]
        second_row = DATA[1]

        assert first_row[3] == second_row[3]  # making sure rating in both rows match

        rating = first_row[3]
        results = db.manager.filter(MODEL_NAME, rating=rating)

        assert len(results) == 2
        # checking the first object
        assert results[0][3] == rating
        assert results[0] == first_row
        # checking the second object
        assert results[1][3] == rating
        assert results[1] == second_row

    @pytest.mark.parametrize(
        "filter, lookup, lookup_value, queryset_results_len, operator",
        [["filter", "rating__gt", 12, 4, gt],
         ["filter", "rating__gte", 55, 2, ge],
         ["filter", "rating__lt", 12, 6, lt],
         ["filter", "rating__lte", 11, 6, le]],
        indirect=["filter"],
    )
    def test_can_filter_fields_with_operators_conditions(
            self,
            filter,
            lookup,
            lookup_value,
            queryset_results_len,
            operator,
    ):
        """
        GIVEN a model name with a lookup condition and its value
        WHEN the db.manager.filter('table_name', field__lookup=lookup_value)
             method is call to query and filter down the entries in the db table
        THEN we check that the quantity of results returned match the expected queryset_results_len
             and check that all entries returned match the operator condition.
        """
        queryset_results = filter(MODEL_NAME, **{lookup: lookup_value})
        assert len(queryset_results) == queryset_results_len
        for qs_r in queryset_results:
            assert operator(qs_r[3], lookup_value)  # rating is in index 3

    @pytest.mark.parametrize(
        "filter, lookup, lookup_list, queryset_results_len",
        [["filter", "rating__in", [5, 10], 3],
         ["filter", "rating__not_in", [5, 10], 7]],
        indirect=["filter"],
    )
    def test_can_filter_fields_with_in_and_not_in_conditions(self, filter, lookup, lookup_list, queryset_results_len):
        """
        GIVEN a model name with a lookup condition and a list of integer values
        WHEN the db.manager.filter('table_name', field__lookup=[integer values])
             method is call to query and filter down the entries in the db table
        THEN we check that the quantity of results returned match the expected queryset_results_len.
        """
        queryset_results = filter(MODEL_NAME, **{lookup: lookup_list})
        assert len(queryset_results) == queryset_results_len

    # multiple fields query
    def est_can_filter_multiple_fields(self):
        pass
