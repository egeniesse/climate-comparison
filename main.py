from shared.throttled_http_client import ThrottledHttpClient
import aiohttp
import asyncio
import asyncio
import os

from adapters.air_quality_adapter import AQIAdapter
from shared.db_client import DBClient

SQLITE_DB_LOCATION = "/Users/ericgeniesse/.cache/climate-comparison.db"

api_keys = {
    "open_weather_api_key": os.getenv("OPEN_WEATHER_API_KEY"),
}

identifier_by_city = {
    "San Jose": "San Jose,CA,USA",
    "Seattle": "Seattle,WA,USA",
}



# Generate the list of data points we want to mine

async def main():
    db_client = DBClient(SQLITE_DB_LOCATION)
    async with aiohttp.ClientSession() as session:
        open_weather_map_client = ThrottledHttpClient(session, 1)
        aqi_adapter = AQIAdapter(open_weather_map_client, db_client)
        aqi_adapter.generate_tasks()
        await aqi_adapter.process_tasks()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

print(api_keys)