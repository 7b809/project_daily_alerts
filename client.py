"""
Async HTTP client for Groww F&O API

Handles:
- Batching (50 per request)
- Retry logic
- Timeout handling
- Batch merging (returns flat dict)
- Multi-exchange support
"""

import aiohttp
import asyncio
from typing import List, Tuple

from config import (
    BASE_URLS,
    COMMON_HEADERS,
    MAX_RETRIES,
    REQUEST_TIMEOUT
)
from payload import build_payload
from utils import chunk_list


# -------------------------------------------------------
# CORE RETRY FUNCTION
# -------------------------------------------------------

async def fetch_with_retry(
    session: aiohttp.ClientSession,
    url: str,
    headers: dict,
    payload: str,
    retries: int = MAX_RETRIES
):
    """
    Makes POST request with retry logic.
    """

    for attempt in range(1, retries + 1):
        try:
            async with session.post(
                url,
                headers=headers,
                data=payload,
                timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
            ) as response:

                if response.status == 200:
                    return await response.json()

                elif response.status == 422:
                    # Invalid contracts in batch
                    print("[SKIPPED] Invalid batch (422)")
                    return None

                else:
                    print(f"[HTTP ERROR] Status: {response.status}")

        except asyncio.TimeoutError:
            print(f"[TIMEOUT] Attempt {attempt}/{retries}")

        except aiohttp.ClientError as e:
            print(f"[CLIENT ERROR] Attempt {attempt}/{retries} -> {e}")

        except Exception as e:
            print(f"[UNKNOWN ERROR] Attempt {attempt}/{retries} -> {e}")

        await asyncio.sleep(1)

    print("[FAILED] All retries exhausted.")
    return None


# -------------------------------------------------------
# BATCH FETCH (MERGED RETURN)
# -------------------------------------------------------

async def fetch_prices_batched(
    exchange: str,
    symbols: List[str],
    batch_size: int = 50
):
    """
    Fetch prices in batches and return ONE merged dictionary.
    """

    if exchange not in BASE_URLS:
        raise ValueError(f"Invalid exchange: {exchange}")

    url = BASE_URLS[exchange]
    merged_data = {}

    async with aiohttp.ClientSession() as session:

        tasks = []

        for batch in chunk_list(symbols, batch_size):

            payload = build_payload(batch)

            task = fetch_with_retry(
                session=session,
                url=url,
                headers=COMMON_HEADERS,
                payload=payload
            )

            tasks.append(task)

        responses = await asyncio.gather(
            *tasks,
            return_exceptions=True
        )

        # Merge all successful batch responses
        for response in responses:
            if isinstance(response, dict):
                merged_data.update(response)
            elif isinstance(response, Exception):
                print(f"[BATCH ERROR] {response}")

    return merged_data


# -------------------------------------------------------
# MULTI EXCHANGE FETCH
# -------------------------------------------------------

async def fetch_multiple_requests(
    requests_data: List[Tuple[str, List[str]]],
    batch_size: int = 50
):
    """
    requests_data format:
    [
        ("NSE", [symbols]),
        ("BSE", [symbols])
    ]

    Returns:
    [
        {
            "exchange": "NSE",
            "data": { merged_dict }
        }
    ]
    """

    all_results = []

    for exchange, symbols in requests_data:

        try:
            data = await fetch_prices_batched(
                exchange=exchange,
                symbols=symbols,
                batch_size=batch_size
            )

            all_results.append({
                "exchange": exchange,
                "data": data   # ALWAYS dict now
            })

        except Exception as e:
            print(f"[EXCHANGE ERROR] {exchange} -> {e}")

    return all_results
