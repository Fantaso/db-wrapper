import datetime
import unittest
from sqlite3 import ProgrammingError
from unittest import TestCase

import pytest

from core.db import SQLiteDB
# Create table - CLIENTS
from core.queries import FilterLookupError

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


class TestManager(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.db = SQLiteDB(":memory:")
        cls.db.connect()

        # add some data to the db
        cls.db.execute(CREATE_MODEL)
        cls.db.executemany(INSERT_DATA, DATA)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.db.close()

    def test_can_retrieve_all_objects(self):
        results = self.db.manager.all(MODEL_NAME)
        self.assertEqual(len(results), 10)
        # check the first row matches with inserted data
        self.assertEqual(results[0], DATA[0])

    ## INTEGER
    # single field query
    def test_can_filter_an_integer_field_equality(self):
        # TODO: parametrize this test
        first_row = DATA[0]
        ## RETRIEVING ONLYE A SINGLE(1) OBJECT
        # given
        id = first_row[0]
        # when
        results = self.db.manager.filter(MODEL_NAME, id=id)
        # and
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], id)
        self.assertEqual(results[0], first_row)

        ## RETRIEVING ONLYE MULTIPLE(2) OBJECT
        # given
        rating = first_row[3]
        # when
        results = self.db.manager.filter(MODEL_NAME, rating=rating)
        # and
        # we have two results
        self.assertEqual(len(results), 2)
        # checking the first object
        self.assertEqual(results[0][3], rating)
        self.assertEqual(results[0], first_row)

        # checking the second object
        self.assertEqual(results[1][3], rating)

    def test_can_filter_integer_field_greater_than(self):
        # given a rating greater than
        rating = 12
        # when we filter by it
        results = self.db.manager.filter(MODEL_NAME, rating__gt=rating)
        # and we should get at 4 results
        self.assertEqual(len(results), 4)

        # TODO: we are just checking that the results
        #  has only rows containing ratings greater than 12.
        #  -- Test thorougher --
        for result in results:
            # the rating is in the index 3
            self.assertGreater(result[3], rating)

    def test_can_filter_integer_field_less_than(self):
        # given a rating less than
        rating = 12
        # when we filter by it
        results = self.db.manager.filter(MODEL_NAME, rating__lt=rating)
        # and we should get 6 results
        self.assertEqual(len(results), 6)

        # TODO: -- Test thorougher --
        for result in results:
            # the rating is in the index 3
            self.assertLess(result[3], rating)

    def test_can_filter_integer_field_equality_and_greater_than(self):
        # given a rating greater and equal than
        rating = 55
        # when we filter by it
        results = self.db.manager.filter(MODEL_NAME, rating__gte=rating)
        # and we should get 2 results
        self.assertEqual(len(results), 2)

        # TODO: -- Test thorougher. Its becoming predictable! --
        for result in results:
            # the rating is in the index 3
            self.assertGreaterEqual(result[3], rating)

    def test_can_filter_integer_field_equality_and_less_than(self):
        # given a rating less and equal than
        rating = 11
        # when we filter by it
        results = self.db.manager.filter(MODEL_NAME, rating__lte=rating)
        # and we should get 6 results
        self.assertEqual(len(results), 6)

        # TODO: -- Test thorougher. Its getting boring! --
        for result in results:
            # the rating is in the index 3
            self.assertLessEqual(result[3], rating)

    def test_can_filter_integer_field_in(self):
        # given a list of ratings
        ratings = [5, 10]
        # when we query the database for them
        results = self.db.manager.filter(MODEL_NAME, rating__in=ratings)
        # we should get 3 results as the rating "5" is twice in the model
        self.assertEqual(len(results), 3)
        # AND WE DON'T CHECK MORE THINGS BECAUSE ITS TAKING LONGER THAN EXPECTED
        #   AND WE CAN DISCUSS MORE ABOUT IT THAN WRITING THOROUGHER TESTS

    def test_can_filter_integer_field_not_in(self):
        # given a list of ratings
        ratings = [5, 10]
        # when we query the database for them
        results = self.db.manager.filter(MODEL_NAME, rating__not_in=ratings)
        # we should get 7 results
        self.assertEqual(len(results), 7)

    # multiple fields query
    def test_can_filter_multiple_integer_fields(self):
        pass

    ## STRING
    def test_can_filter_string_field_equality(self):
        url = "http://www.spoon.guru/bbq-recipes/"
        results = self.db.manager.filter(MODEL_NAME, url=url)
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertEqual(result[1], url)

    def test_can_filter_string_field_in(self):
        urls = [
            "http://www.spoon.guru/bbq-recipes/",
            "http://www.spoon.guru/contact-2/",
        ]
        results = self.db.manager.filter(MODEL_NAME, url__in=urls)
        # 'bbq-recipes' url is twice so results are 3
        self.assertEqual(len(results), 3)

    def test_can_not_filter_string_field_if_lookup_not_allowed(self):
        urls = [
            "http://www.spoon.guru/bbq-recipes/",
            "http://www.spoon.guru/contact-2/",
        ]
        with self.assertRaises(FilterLookupError):
            self.db.manager.filter(MODEL_NAME, url__gt=urls)

    ## DATE
    def test_can_filter_date_field_equality(self):
        date_obj = datetime.date(2021, 1, 5)
        results = self.db.manager.filter(MODEL_NAME, date=date_obj)
        self.assertEqual(len(results), 2)
        for result in results:
            # checking the id of the correct results
            self.assertIn(result[0], [5, 6])

    def test_can_filter_date_field_greater_than(self):
        date_obj = datetime.date(2021, 1, 5)
        results = self.db.manager.filter(MODEL_NAME, date__gt=date_obj)
        self.assertEqual(len(results), 4)

    def test_can_filter_date_field_less_than(self):
        date_obj = datetime.date(2021, 1, 2)
        results = self.db.manager.filter(MODEL_NAME, date__lt=date_obj)
        self.assertEqual(len(results), 1)

    def test_can_filter_date_field_equality_and_greater_than(self):
        date_obj = datetime.date(2021, 1, 5)
        results = self.db.manager.filter(MODEL_NAME, date__gte=date_obj)
        self.assertEqual(len(results), 6)

    def test_can_filter_date_field_equality_and_less_than(self):
        date_obj = datetime.date(2021, 1, 2)
        results = self.db.manager.filter(MODEL_NAME, date__lte=date_obj)
        self.assertEqual(len(results), 2)

    def test_can_filter_date_field_in(self):
        date_objs = [
            datetime.date(2021, 1, 5),
            datetime.date(2021, 1, 2),
        ]
        results = self.db.manager.filter(MODEL_NAME, date__in=date_objs)
        self.assertEqual(len(results), 3)

    def test_can_filter_date_field_not_in(self):
        date_objs = [
            datetime.date(2021, 1, 5),
            datetime.date(2021, 1, 2),
        ]
        results = self.db.manager.filter(MODEL_NAME, date__not_in=date_objs)
        self.assertEqual(len(results), 7)

    ## multiple conditions
    def test_can_filter_date_field_with_greater_and_less_than(self):
        date_from = datetime.date(2021, 2, 2)
        date_to = datetime.date(2021, 3, 16)
        results = self.db.manager.filter(
            MODEL_NAME,
            date__gt=date_from,
            date__lt=date_to,
        )
        self.assertEqual(len(results), 2)

    def test_filter_with_no_model_name(self):
        # for now the model (table) name is required
        with self.assertRaises(TypeError):
            self.db.manager.filter()

    def test_spoon_guru_test_case_type(self):
        """
        We may want all entries with:
          e.g. (2 < rating < 9) and (id in list) and (date > 1 Jan 2016)

        DATA:
            Just for reference in this complex query to
            visually check the resulted query.

         PK,  url,                                              date,            rating(0-100)
        (1,  "http://www.spoon.guru",                           "2021-01-01",      5 )
        (2,  "http://www.spoon.guru/solutions/",                "2021-01-02",      5 )
        (3,  "http://www.spoon.guru/retail-solutions/",         "2021-01-03",      10)
        (4,  "http://www.spoon.guru/blog/",                     "2021-01-04",      35)
        (5,  "http://www.spoon.guru/contact-2/",                "2021-01-05",      48)
        (6,  "http://www.spoon.guru/the-team/",                 "2021-01-05",      78)
        (7,  "http://www.spoon.guru/the-gut-brain-connection/", "2021-02-02",      55)
        (8,  "http://www.spoon.guru/how-it-works/",             "2021-02-15",      11)
        (9,  "http://www.spoon.guru/bbq-recipes/",              "2021-02-16",      3 )
        (10,    "http://www.spoon.guru/bbq-recipes/",           "2021-03-16",      3 )
        """

        date_from = datetime.date(2021, 1, 2)  # includes id>3
        ids = [1, 2, 6, 7, ]  # only id=[1,2,6,7]
        rating_from = 4  # only id=[3,4,5,6,7,8]
        rating_to = 78  # excludes  id=6
        # ----------------------
        # results id=[7] therefore DATA[6]

        results = self.db.manager.filter(
            MODEL_NAME,
            date__gt=date_from,
            id__in=ids,
            rating__gt=rating_from,
            rating__lt=rating_to,
        )

        self.assertEqual(len(results), 1)
        only_result = results[0]
        self.assertEqual(DATA[6], only_result)


if __name__ == '__main__':
    unittest.main()
