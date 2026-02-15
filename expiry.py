"""
Expiry calculation logic for index options.

Rules:
- NIFTY  → Weekly expiry = Tuesday
- SENSEX → Weekly expiry = Thursday

Logic:
If today is expiry day:
    - Before 7:00 PM → Use today's expiry
    - After 7:00 PM  → Use next week's expiry
"""

from datetime import datetime, timedelta
import pytz


# -------------------------------------------------------
# CONFIG
# -------------------------------------------------------

IST = pytz.timezone("Asia/Kolkata")
EXPIRY_SWITCH_HOUR = 19  # 7:00 PM IST


# -------------------------------------------------------
# GENERIC EXPIRY HELPER
# -------------------------------------------------------

def get_expiry_for_weekday(target_weekday: int):
    """
    target_weekday:
        Tuesday = 1
        Thursday = 3
    """

    now = datetime.now(IST)
    today_weekday = now.weekday()

    days_ahead = (target_weekday - today_weekday) % 7

    expiry_date = now + timedelta(days=days_ahead)

    # If today is expiry day
    if today_weekday == target_weekday:

        # If before 7 PM → use today
        if now.hour < EXPIRY_SWITCH_HOUR:
            expiry_date = now

        # After 7 PM → move to next week
        else:
            expiry_date = now + timedelta(days=7)

    return expiry_date


# -------------------------------------------------------
# EXPIRY FORMATTER
# -------------------------------------------------------

def format_expiry(index_name: str):

    index_name = index_name.upper()

    if index_name == "NIFTY":
        expiry = get_expiry_for_weekday(1)   # Tuesday

    elif index_name == "SENSEX":
        expiry = get_expiry_for_weekday(3)   # Thursday

    else:
        expiry = get_expiry_for_weekday(1)

    year = str(expiry.year)[-2:]
    month = str(expiry.month)        # No leading zero
    day = f"{expiry.day:02d}"

    return year + month + day
