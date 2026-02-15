from mongodb import collection


def get_yesterday_snapshot(date_str: str, exchange: str):
    return collection.find_one({
        "date": date_str,
        "exchange": exchange
    })


def compare_with_yesterday(yesterday_doc: dict, today_data: dict):

    if not yesterday_doc:
        return []

    yesterday_map = {
        c["symbol"]: c
        for c in yesterday_doc.get("contracts", [])
    }

    comparison = []

    for symbol, info in today_data.items():

        if symbol not in yesterday_map:
            continue

        yesterday_ltp = yesterday_map[symbol]["ltp"]
        today_ltp = info.get("ltp")

        if not yesterday_ltp or not today_ltp:
            continue

        change = today_ltp - yesterday_ltp
        change_perc = (change / yesterday_ltp) * 100

        comparison.append({
            "symbol": symbol,
            "yesterday_ltp": yesterday_ltp,
            "today_ltp": today_ltp,
            "change": round(change, 2),
            "change_perc": round(change_perc, 2)
        })

    # Sort descending by % change
    comparison.sort(key=lambda x: x["change_perc"], reverse=True)

    return comparison
