import yfinance as yf


def get_spot_price(ticker: str) -> float:
    """
    Fetch latest market price from Yahoo Finance
    """
    try:
        data = yf.Ticker(ticker)
        price = data.history(period="1d", interval="1m")

        if price.empty:
            raise ValueError(f"No data returned for {ticker}")

        return float(price["Close"].iloc[-1])

    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None


def get_nifty_spot():
    return get_spot_price("^NSEI")


def get_sensex_spot():
    return get_spot_price("^BSESN")
