"""
Main runner for Index Early Alerts Project

Modes:
1. Manual run → Fetch live data immediately
2. Scheduler mode → Auto save snapshot daily at 5 PM IST
"""

import asyncio

from strikes import generate_strikes
from client import fetch_multiple_requests
from utils import generate_strike_window, round_to_step
from spot import get_nifty_spot, get_sensex_spot
from scheduler import start_scheduler, check_and_backfill


# -------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------

NIFTY_STEP = 50
SENSEX_STEP = 100
STRIKE_RANGE = 1000
BATCH_SIZE = 50


# -------------------------------------------------------
# MANUAL FETCH (Optional Testing)
# -------------------------------------------------------

async def manual_fetch():

    print("Fetching live spot prices...\n")

    nifty_spot = get_nifty_spot()
    sensex_spot = get_sensex_spot()

    if nifty_spot is None or sensex_spot is None:
        print("❌ Failed to fetch spot prices.")
        return

    print(f"Raw NIFTY Spot   : {nifty_spot}")
    print(f"Raw SENSEX Spot  : {sensex_spot}\n")

    nifty_spot = round_to_step(nifty_spot, NIFTY_STEP)
    sensex_spot = round_to_step(sensex_spot, SENSEX_STEP)

    nifty_strikes = generate_strike_window(nifty_spot, NIFTY_STEP, STRIKE_RANGE)
    sensex_strikes = generate_strike_window(sensex_spot, SENSEX_STEP, STRIKE_RANGE)

    nifty_symbols = generate_strikes("NIFTY", nifty_strikes)
    sensex_symbols = generate_strikes("SENSEX", sensex_strikes)

    requests_data = [
        ("NSE", nifty_symbols),
        ("BSE", sensex_symbols),
    ]

    results = await fetch_multiple_requests(
        requests_data=requests_data,
        batch_size=BATCH_SIZE
    )

    print("\n==============================")
    print("      FETCH SUMMARY")
    print("==============================\n")

    for result in results:
        exchange = result.get("exchange")
        data = result.get("data")

        if data:
            print(f"{exchange} → Total Contracts Received: {len(data)}")
        else:
            print(f"{exchange} → No data returned")

    print("\nManual Fetch Completed.\n")


# -------------------------------------------------------
# APP RUNNER (Scheduler Mode)
# -------------------------------------------------------

async def run_app():

    print("Starting Index Early Alerts Engine...\n")

    # 🔥 Backfill yesterday if missing
    await check_and_backfill()

    # Start daily 5PM scheduler
    start_scheduler()

    print("Scheduler running forever...\n")

    # Keep loop alive
    while True:
        await asyncio.sleep(3600)


# -------------------------------------------------------
# ENTRY POINT
# -------------------------------------------------------

if __name__ == "__main__":
    asyncio.run(run_app())
