from datetime import datetime, timedelta

class MonthlyHoursCalculator:
    """
    A class to calculate monthly working hours based on business days.
    Assumes 8 hours per business day (Monday to Friday).
    """
    
    def __init__(self, hours_per_day: int = 8):
        """
        Initialize the calculator with configurable hours per day.
        
        Args:
            hours_per_day (int): Number of hours per business day. Defaults to 8.
        """
        self.hours_per_day = hours_per_day
    
    def calc_monthly_hours(self, year: int, month: int) -> int:
        """
        Calculate the total working hours for a given month.
        
        Args:
            year (int): The year
            month (int): The month (1-12)
            
        Returns:
            int: Total working hours for the month
        """
        business_days = self.calc_business_days(year, month)
        return business_days * self.hours_per_day
    
    def calc_business_days(self, year: int, month: int) -> int:
        """
        Calculate the number of business days (Monday to Friday) in a given month.
        
        Args:
            year (int): The year
            month (int): The month (1-12)
            
        Returns:
            int: Number of business days in the month
        """
        # Get first day of month
        start_date = datetime(year, month, 1)
        # Get first day of next month
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        business_days = 0
        current_date = start_date
        while current_date < end_date:
            # Monday = 0, Sunday = 6
            if current_date.weekday() < 5:  # Monday to Friday
                business_days += 1
            current_date = current_date + timedelta(days=1)
        
        return business_days