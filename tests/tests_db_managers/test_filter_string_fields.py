import pytest

from tests.conftest import MODEL_NAME


class FilterStringFieldTests:
    @pytest.mark.parametrize(
        "filter, field, value, queryset_results_len",
        [["filter", "url", "http://www.spoon.guru/bbq-recipes/", 2],
         ["filter", "url", "http://www.spoon.guru/solutions/", 1]],
        indirect=["filter"],
    )
    def test_can_filter_field_equality(self, filter, field, value, queryset_results_len):
        """
        GIVEN a model name with a field name and its value
        WHEN the db.manager.filter('table_name', field=value)
             method is call to query and filter down the entries in the db table
        THEN we check that the quantity of results returned match the expected queryset_results_len
             and that the field returned match the value filtered.
        """
        queryset_results = filter(MODEL_NAME, **{field: value})
        assert len(queryset_results) == queryset_results_len
        for qs_r in queryset_results:
            assert qs_r[1] == value  # url is in index 1

    URLS = ["http://www.spoon.guru/bbq-recipes/",
            "http://www.spoon.guru/contact-2/", ]

    @pytest.mark.parametrize(
        "filter, lookup, lookup_list, queryset_results_len",
        [
            ["filter", "url__in", URLS, 3],  # 'bbq-recipes' url is twice in db
        ],
        indirect=["filter"],
    )
    def test_can_filter_fields_with_in_and_not_in_conditions(self, filter, lookup, lookup_list, queryset_results_len):
        queryset_results = filter(MODEL_NAME, **{lookup: lookup_list})
        assert len(queryset_results) == queryset_results_len
