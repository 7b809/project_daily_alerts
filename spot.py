import requests
from typing import Dict, Optional


GROWW_URL = "https://groww.in/v1/api/stocks_data/v1/aggregated_stocks_market_today"

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-IN,en;q=0.9",
    "cache-control": "no-cache",
    "content-type": "application/json",
    "pragma": "no-cache",
    "x-app-id": "growwWeb",
    "x-device-type": "desktop",
    "x-platform": "web",
    "referer": "https://groww.in/"
}

PAYLOAD = {}


def fetch_market_data() -> Optional[dict]:
    """
    Fetch aggregated market data from Groww
    """
    try:
        session = requests.Session()
        response = session.post(GROWW_URL, headers=HEADERS, json=PAYLOAD, timeout=10)

        if response.status_code != 200:
            print("Error:", response.status_code)
            return None

        return response.json()

    except Exception as e:
        print("Fetch Error:", e)
        return None


def extract_indices(data: dict, symbols: list) -> Dict[str, float]:
    """
    Extract given index symbols from Groww response
    """
    result = {}

    try:
        # NSE indices
        nse_map = data["indexData"]["exchangeAggRespMap"]["NSE"]["indexLivePointsMap"]

        # BSE indices
        bse_map = data["indexData"]["exchangeAggRespMap"]["BSE"]["indexLivePointsMap"]

        # Merge both exchanges
        combined = {**nse_map, **bse_map}

        for symbol in symbols:
            if symbol in combined:
                result[symbol] = combined[symbol]["value"]

    except Exception as e:
        print("Extraction Error:", e)

    return result


# ---------------------------
# Public Functions
# ---------------------------

def get_indices_spot() -> Dict[str, float]:
    """
    Returns spot prices of major indices.
    Easily extendable.
    """
    data = fetch_market_data()
    if not data:
        return {}

    symbols = [
        "NIFTY",
        "BANKNIFTY",
        "FINNIFTY",
        "NIFTYMIDSELECT",
        "1",   # BSE SENSEX symbol in Groww response
    ]

    raw = extract_indices(data, symbols)

    # Rename keys for clarity
    formatted = {
        "NIFTY": raw.get("NIFTY"),
        "BANKNIFTY": raw.get("BANKNIFTY"),
        "FINNIFTY": raw.get("FINNIFTY"),
        "MIDCAP_SELECT": raw.get("NIFTYMIDSELECT"),
        "SENSEX": raw.get("1"),   # BSE index symbol "1"
    }

    return formatted


def get_nifty_spot():
    return get_indices_spot().get("NIFTY")


def get_sensex_spot():
    return get_indices_spot().get("SENSEX")
