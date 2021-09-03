from sqlite3.dbapi2 import adapt
import aiohttp
import asyncio
import asyncio
import logging
import sys

from src.adapters.air_now_aqi_adapter import AirNowAQIAdapter
from src.adapters.noaa_weather_data_adapter import NOAAWeatherDataAdapter
from src.shared.throttled_http_client import ThrottledHttpClient
from config import api_rate_limits, adapter_config, db_config
from src.shared.db_client import DBClient

logger = logging.getLogger(__name__)

async def main():
    db_client = DBClient(db_config)
    async with aiohttp.ClientSession() as session:
        api_clients = {
            "air_now_client": ThrottledHttpClient(session, api_rate_limits["air_now"]),
            "noaa_weather_client": ThrottledHttpClient(session, api_rate_limits["noaa_weather_data"]),
        }

        adapters = [
            AirNowAQIAdapter(api_clients["air_now_client"], db_client, adapter_config),
            NOAAWeatherDataAdapter(api_clients["noaa_weather_client"], db_client, adapter_config),
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
