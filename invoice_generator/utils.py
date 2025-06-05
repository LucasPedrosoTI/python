from datetime import datetime, timedelta

def calc_monthly_hours(year: int, month: int) -> int:
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
    
    return business_days * 8