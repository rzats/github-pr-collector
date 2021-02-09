import unittest
import datetime

from github_collector import utils


class TestUtils(unittest.TestCase):

    def test_unix_2_utc(self):
        self.assertEqual(utils.unix_2_utc(1612000000), "2021-01-30T09:46:40Z")

    def test_utc_2_datetime(self):
        self.assertEqual(utils.utc_2_datetime("2021-01-30T09:46:40Z"),
                         datetime.datetime(2021, 1, 30, 9, 46, 40))

    def test_seconds_2_human(self):
        self.assertEqual(utils.seconds_2_human(0),
                         "0 day(s), 0 hour(s), 0 minute(s), 0 second(s)")

        self.assertEqual(utils.seconds_2_human(2000),
                         "0 day(s), 0 hour(s), 33 minute(s), 20 second(s)")

        self.assertEqual(utils.seconds_2_human(20000),
                         "0 day(s), 5 hour(s), 33 minute(s), 20 second(s)")

        self.assertEqual(utils.seconds_2_human(200000),
                         "2 day(s), 7 hour(s), 33 minute(s), 20 second(s)")


if __name__ == '__main__':
    unittest.main()
