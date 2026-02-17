import requests
from typing import Dict, Optional

import yfinance as yf

# Use Ticker objects for better reliability
nifty = yf.Ticker("^NSEI")
sensex = yf.Ticker("^BSESN")

# Fetch 1-day history with 1-minute interval
# Using tail(1) or iloc[-1] on a forward-filled dataframe
nifty_data = nifty.history(period="1d", interval="1m").ffill()
sensex_data = sensex.history(period="1d", interval="1m").ffill()

nifty_spot = nifty_data['Close'].iloc[-1]
sensex_spot = sensex_data['Close'].iloc[-1]


def get_nifty_spot():
    return nifty_spot if nifty_spot else None


def get_sensex_spot():
    return sensex_spot if sensex_spot else None
