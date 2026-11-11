from datetime import date, datetime, timedelta

def get_date_input(prompt, default_date=None):
    """
    Prompts the user for a date input and returns a datetime.date object.
    If the user enters nothing, it returns the default_date.
    """
    while True:
        date_str = input(f"{prompt} (YYYY-MM-DD) ")
        if not date_str:
            if default_date:
                return default_date
            else:
                print("Date cannot be empty if no default is set.")
                continue
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")

# Using datetime objects
default_date = datetime(2024, 8, 20)
datetime2 = datetime.now()
datetime1 = get_date_input("Enter start date", default_date)
difference_datetime = datetime2 - datetime(datetime1.year, datetime1.month, datetime1.day)
weeks = round(difference_datetime.days/7)
months = round(weeks / 4)
print(f"Days: {difference_datetime.days}") 
print(f"Weeks: {weeks}")  # Output: 2
print(f"Months: {months}")   # Output: 80730 (22 hours, 25 minutes, 30 seconds in seconds)