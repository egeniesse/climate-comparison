from shared.throttled_http_client import ThrottledHttpClient
import aiohttp
import asyncio
import asyncio
import logging
import sys

from adapters.air_now_aqi_adapter import AirNowAQIAdapter
from shared.constants import api_rate_limits
from shared.db_client import DBClient

logger = logging.getLogger(__name__)
SQLITE_DB_LOCATION = "/Users/ericgeniesse/.cache/climate-comparison.db"


async def main():
    db_client = DBClient(SQLITE_DB_LOCATION)
    async with aiohttp.ClientSession() as session:
        api_clients = {
            "air_now_client": ThrottledHttpClient(session, api_rate_limits["air_now"]),
        }

        adapters = [
            AirNowAQIAdapter(api_clients["air_now_client"], db_client)
        ]
        logger.info(f"Generating tasks for {len(adapters)} adapters")
        [adapter.generate_tasks() for adapter in adapters]
        logger.info(f"Processing tasks for {len(adapters)} adapters")
        await asyncio.gather(*[adapter.process_tasks() for adapter in adapters])


if __name__ == "__main__":
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
