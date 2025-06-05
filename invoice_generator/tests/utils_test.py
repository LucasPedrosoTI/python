import unittest
from invoice_generator.utils import calc_monthly_hours

class TestUtils(unittest.TestCase):

    def test_calc_monthly_hours(self):
        test_cases = [
            (2024, 1, 184),   # January 2024: 23 business days
            (2024, 2, 168),   # February 2024: 21 business days (leap year)
            (2023, 2, 160),   # February 2023: 20 business days (non-leap year)
            (2024, 3, 168),   # March 2024: 21 business days
            (2024, 4, 176),   # April 2024: 22 business days
            (2024, 5, 184),   # May 2024: 23 business days
            (2024, 6, 160),   # June 2024: 20 business days
            (2024, 7, 184),   # July 2024: 23 business days
            (2024, 8, 176),   # August 2024: 22 business days
            (2024, 9, 168),   # September 2024: 21 business days
            (2024, 10, 184),  # October 2024: 23 business days
            (2024, 11, 168),  # November 2024: 21 business days
            (2024, 12, 176),  # December 2024: 22 business days
        ]
        
        for year, month, expected_hours in test_cases:
            with self.subTest(year=year, month=month):
                self.assertEqual(calc_monthly_hours(year, month), expected_hours)
