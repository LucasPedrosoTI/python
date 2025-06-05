import unittest
from invoice_generator.monthly_hours_calculator import MonthlyHoursCalculator

class TestMonthlyHoursCalculator(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures."""
        self.calculator = MonthlyHoursCalculator()
        self.custom_calculator = MonthlyHoursCalculator(hours_per_day=6)

    def test_calc_monthly_hours_class(self):
        """Test the MonthlyHoursCalculator class with default 8 hours per day."""
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
                self.assertEqual(self.calculator.calc_monthly_hours(year, month), expected_hours)

    def test_calc_monthly_hours_custom_hours_per_day(self):
        """Test the MonthlyHoursCalculator class with custom hours per day."""
        # Test with 6 hours per day
        # January 2024: 23 business days * 6 hours = 138 hours
        self.assertEqual(self.custom_calculator.calc_monthly_hours(2024, 1), 138)
        # February 2024: 21 business days * 6 hours = 126 hours
        self.assertEqual(self.custom_calculator.calc_monthly_hours(2024, 2), 126)

    def test_calc_business_days(self):
        """Test the business days calculation method."""
        test_cases = [
            (2024, 1, 23),   # January 2024: 23 business days
            (2024, 2, 21),   # February 2024: 21 business days (leap year)
            (2023, 2, 20),   # February 2023: 20 business days (non-leap year)
            (2024, 6, 20),   # June 2024: 20 business days
        ]
        
        for year, month, expected_days in test_cases:
            with self.subTest(year=year, month=month):
                self.assertEqual(self.calculator.calc_business_days(year, month), expected_days)
