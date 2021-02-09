from datetime import date

from tests.conftest import MODEL_NAME, DATA


class SpoonGuruTests:
    def test_spoon_guru_test_case_type(self, db):
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

        date_from = date(2021, 1, 2)    # includes id>3
        ids = [1, 2, 6, 7, ]            # only id=[1,2,6,7]
        rating_from = 4                 # only id=[3,4,5,6,7,8]
        rating_to = 78                  # excludes  id=6
                                        # ----------------------
                                        # results id=[7] therefore DATA[6]

        results = db.manager.filter(
            MODEL_NAME,
            date__gt=date_from,
            id__in=ids,
            rating__gt=rating_from,
            rating__lt=rating_to,
        )

        assert len(results) == 1
        only_result = results[0]
        assert DATA[6] == only_result
