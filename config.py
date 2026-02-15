"""
Configuration file for Groww Index Project
Loads environment variables if available.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# --------------------------------------------------
# API BASE URLS
# --------------------------------------------------

BASE_URLS = {
    "NSE": "https://groww.in/v1/api/stocks_fo_data/v1/tr_live_prices/exchange/NSE/segment/FNO/latest_prices_batch",
    "BSE": "https://groww.in/v1/api/stocks_fo_data/v1/tr_live_prices/exchange/BSE/segment/FNO/latest_prices_batch",
}

# --------------------------------------------------
# HEADERS
# --------------------------------------------------

COMMON_HEADERS = {
    "accept": "application/json, text/plain, */*",
    "content-type": "application/json",
    "x-app-id": os.getenv("APP_ID", "growwWeb"),
    "x-device-id": os.getenv("DEVICE_ID", ""),
    "x-device-type": os.getenv("DEVICE_TYPE", "desktop"),
    "x-platform": os.getenv("PLATFORM", "web"),
}

# --------------------------------------------------
# REQUEST CONFIG
# --------------------------------------------------

MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 10))
