"""
Utility helpers for strike generation, rounding,
and batching logic for Groww F&O project.
"""


def round_to_step(value: float, step: int) -> int:
    """
    Round value to nearest strike step.

    Example:
    25241.7 with step 50 -> 25250
    83012.4 with step 100 -> 83000
    """
    return int(round(value / step) * step)


def generate_strike_range(spot_price: int, step: int, count: int = 5) -> list:
    """
    Generates symmetric strikes around spot.

    Example:
    spot=25250, step=50, count=2
    -> [25150, 25200, 25250, 25300, 25350]
    """
    strikes = []
    for i in range(-count, count + 1):
        strikes.append(spot_price + (i * step))

    return strikes


def generate_strike_window(spot: int, step: int, range_points: int = 1000) -> list:
    """
    Generates strikes from:
    spot - range_points  to  spot + range_points

    Example:
    spot=25250, step=50, range_points=1000
    -> 24250 to 26250
    """
    lower = spot - range_points
    upper = spot + range_points

    strikes = list(range(lower, upper + step, step))
    return strikes


def chunk_list(data: list, chunk_size: int):
    """
    Split list into batches of size chunk_size.

    Example:
    chunk_list([1,2,3,4,5], 2)
    -> [1,2], [3,4], [5]
    """
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]


def validate_strikes(strikes: list) -> list:
    """
    Ensures all strikes are positive integers.
    Filters invalid values.
    """
    valid = []
    for s in strikes:
        try:
            s = int(s)
            if s > 0:
                valid.append(s)
        except:
            continue
    return valid


def calculate_window_size(range_points: int, step: int) -> int:
    """
    Returns total strike count (single side) for logging/debug.

    Example:
    range_points=1000, step=50
    -> 41 strikes
    """
    return int((range_points * 2) / step) + 1
