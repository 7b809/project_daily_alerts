def generate_strikes(
    index_name: str,
    strike_prices: list,
    option_types=("CE", "PE")
):
    """
    Example output:
    NIFTY2621725250PE
    """

    from expiry import format_expiry

    expiry_part = format_expiry(index_name)

    contracts = []

    for strike in strike_prices:
        for opt in option_types:
            symbol = f"{index_name}{expiry_part}{strike}{opt}"
            contracts.append(symbol)

    return contracts
