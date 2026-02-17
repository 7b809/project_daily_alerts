"""
Scheduler Engine for Index Early Alerts

Features:
- Backfill yesterday if missing
- Daily 5PM snapshot save
- 9:17 AM momentum comparison
- Telegram alert for top gainers
- 🔥 On startup → ALWAYS run momentum scan (forced)
"""

import pytz
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from mongodb import save_snapshot, collection
from client import fetch_multiple_requests
from strikes import generate_strikes
from utils import generate_strike_window, round_to_step
from spot import get_nifty_spot, get_sensex_spot
from analytics import compare_with_yesterday, get_yesterday_snapshot
from telegram_service import send_telegram_message


IST = pytz.timezone("Asia/Kolkata")


# -------------------------------------------------------
# 🔥 STARTUP FORCE RUN
# -------------------------------------------------------

async def ensure_today_momentum_sent():
    """
    On every app startup:
    ALWAYS run morning momentum scan.
    Ignore database flags.
    """

    print("🔥 Running startup momentum scan (forced)...")

    await morning_momentum_job()

    print("✅ Startup momentum scan completed.")


# -------------------------------------------------------
# CORE SNAPSHOT FETCH
# -------------------------------------------------------

async def fetch_and_save_for_date(date_obj):

    date_str = date_obj.strftime("%Y-%m-%d")
    print(f"[FETCHING] Snapshot for {date_str}")

    nifty_spot = get_nifty_spot()
    sensex_spot = get_sensex_spot()

    if not nifty_spot or not sensex_spot:
        print("Spot fetch failed")
        return

    nifty_spot = round_to_step(nifty_spot, 50)
    sensex_spot = round_to_step(sensex_spot, 100)

    nifty_strikes = generate_strike_window(nifty_spot, 50, 1000)
    sensex_strikes = generate_strike_window(sensex_spot, 100, 1000)

    nifty_symbols = generate_strikes("NIFTY", nifty_strikes)
    sensex_symbols = generate_strikes("SENSEX", sensex_strikes)

    requests_data = [
        ("NSE", nifty_symbols),
        ("BSE", sensex_symbols),
    ]

    results = await fetch_multiple_requests(requests_data)

    for result in results:
        exchange = result["exchange"]
        data = result["data"]

        if data:
            save_snapshot(date_str, exchange, data)


# -------------------------------------------------------
# BACKFILL CHECK
# -------------------------------------------------------

async def check_and_backfill():

    now = datetime.now(IST)
    yesterday = now - timedelta(days=1)
    yesterday_str = yesterday.strftime("%Y-%m-%d")

    for exchange in ["NSE", "BSE"]:

        existing = collection.find_one({
            "date": yesterday_str,
            "exchange": exchange
        })

        if not existing:
            print(f"[BACKFILL] Missing {exchange} for {yesterday_str}")
            await fetch_and_save_for_date(yesterday)
        else:
            print(f"[OK] {exchange} already saved for {yesterday_str}")


# -------------------------------------------------------
# DAILY 5PM SNAPSHOT JOB
# -------------------------------------------------------

async def daily_5pm_job():
    now = datetime.now(IST)
    print("[5PM JOB] Saving daily snapshot...")
    await fetch_and_save_for_date(now)


# -------------------------------------------------------
# MORNING MOMENTUM SCAN (9:17 AM)
# -------------------------------------------------------

def format_option_symbol(symbol: str):

    if symbol.startswith("NIFTY"):
        base = symbol.replace("NIFTY", "")
    elif symbol.startswith("SENSEX"):
        base = symbol.replace("SENSEX", "")
    else:
        base = symbol

    strike = base[:-2]
    strike_price = strike[5:]
    option_type = symbol[-2:]

    return f"{strike_price} {option_type}"


async def morning_momentum_job():

    now = datetime.now(IST)
    yesterday_str = (now - timedelta(days=1)).strftime("%Y-%m-%d")

    print("[9:17 AM] Running full momentum scan...")

    nifty_spot = get_nifty_spot()
    sensex_spot = get_sensex_spot()

    if not nifty_spot or not sensex_spot:
        print("Spot fetch failed")
        return

    nifty_spot = round_to_step(nifty_spot, 50)
    sensex_spot = round_to_step(sensex_spot, 100)

    nifty_strikes = generate_strike_window(nifty_spot, 50, 1000)
    sensex_strikes = generate_strike_window(sensex_spot, 100, 1000)

    nifty_symbols = generate_strikes("NIFTY", nifty_strikes)
    sensex_symbols = generate_strikes("SENSEX", sensex_strikes)

    requests_data = [
        ("NSE", nifty_symbols),
        ("BSE", sensex_symbols),
    ]

    results = await fetch_multiple_requests(requests_data)

    for result in results:

        exchange = result["exchange"]
        today_data = result["data"]

        yesterday_doc = get_yesterday_snapshot(yesterday_str, exchange)
        comparison = compare_with_yesterday(yesterday_doc, today_data)

        if not comparison:
            continue

        increasing_options = [
            c for c in comparison if c["change"] > 0
        ]

        if not increasing_options:
            continue

        message = f"<b>🔥 {exchange} Morning Rising Options</b>\n"
        message += "<pre>\n"
        message += f"{'Symbol':<20}{'Yest':<12}{'Now':<12}{'%':<12}\n"
        message += "-" * 50 + "\n"

        for item in increasing_options:

            formatted_symbol = format_option_symbol(item["symbol"])

            message += (
                f"{formatted_symbol:<15}"
                f"{item['yesterday_ltp']:<8.1f}"
                f"{item['today_ltp']:<8.1f}"
                f"{item['change_perc']:<8.2f}\n"
            )

        message += "</pre>"

        send_telegram_message(message)

        print(f"[TABLE SENT] {exchange}")


# -------------------------------------------------------
# START SCHEDULER
# -------------------------------------------------------

def start_scheduler():

    scheduler = AsyncIOScheduler(timezone=IST)

    scheduler.add_job(
        daily_5pm_job,
        "cron",
        hour=17,
        minute=0
    )

    scheduler.add_job(
        morning_momentum_job,
        "cron",
        hour=9,
        minute=17
    )

    scheduler.start()

    print("Scheduler started.")
    print("• 5 PM → Daily snapshot save")
    print("• 9:17 AM → Morning momentum scan")
