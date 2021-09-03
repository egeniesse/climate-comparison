import collections
import datetime
import logging
import os

from src.adapters.base_adapter import BaseAdapter
from src.shared.utils import data_point, mean

NOAA_DATASET_IDS = {
    "GHCND": "Daily Summaries",
}

NOAA_DATA_TYPE_IDS = {
    "AWND": "Average Wind Speed",
    "PRCP": "Percipitation",
    "SNOW": "Snowfall",
    "TAVG": "Average Temperature",
    "TMAX": "Max Temperature",
    "TMIN": "Min Temperature",
    # "WSF2": "Fastest 2 Minute Wind Speed",
    # "WT01": "Fog, ice fog, or freezing fog (may include heavy fog)",
    # "WT02": "Heavy fog or heaving freezing fog (not always distinguished from fog)",
    # "WT03": "Thunder",
    # "WT08": "Smoke or Haze",
    # "WT14": "Drizzle",
    # "WT16": "Rain",
}

logger = logging.getLogger(__name__)
NOAA_WEATHER_DATA_URL = "https://www.ncdc.noaa.gov/cdo-web/api/v2/data"
NOAA_WEATHER_DATA_API_KEY = os.getenv("NOAA_WEATHER_SUMMARY_API_KEY")

class NOAAWeatherDataAdapter(BaseAdapter):
    def __init__(self, http_client, db_client, config):
        self.type = "noaa_weather_data"
        self.version = 3

        self.http_client = http_client
        self.db_client = db_client
        self.config = config
    
    async def _process_task(self, job_data):
        weather_data = await self._fetch_data(job_data)
        filtered_data = [data for data in weather_data if data["datatype"] in NOAA_DATA_TYPE_IDS]
        location, date = job_data["location"], job_data["date"]
        data_by_type = self._condense_data(filtered_data)
        datapoints = []
        for data_type, data in data_by_type.items():
            datapoints.append(data_point(location, date, f"NOAA-{data_type}", data, self.version))
        return datapoints
    
    async def _fetch_data(self, job_data):
        params_to_keep = {"startdate", "enddate", "locationid"}
        page_size = 1000
        query_params = {key: value for key, value in job_data.items() if key in params_to_keep}
        query_params.update({
            "limit": page_size,
            "datasetid": "GHCND",
            "units": "standard",
            "offset": 1,
        })
        headers = {"token": NOAA_WEATHER_DATA_API_KEY}
        results = []
        while True:
            logger.debug(f"Fetching weather data in batches of: {page_size}")
            response = await self.http_client.get(NOAA_WEATHER_DATA_URL, params=query_params, headers=headers)
            res_json = await response.json()
            results.extend(res_json.get("results", []))
            if len(res_json.get("results", [])) < page_size:
                return results
            query_params["offset"] += page_size
    
    def _condense_data(self, weather_data):
        points_by_type = collections.defaultdict(list)
        for point in weather_data:
            points_by_type[point["datatype"]].append(point["value"])
        mean_points_by_type = {}
        for key, points in points_by_type.items():
            mean_points_by_type[key] = mean(points)
        return mean_points_by_type
    
    def _create_job_data(self, location, metadata, cur_time):
        return {
            "date": cur_time,
            "startdate": datetime.datetime.fromtimestamp(cur_time).strftime("%Y-%m-%d"),
            "enddate": datetime.datetime.fromtimestamp(cur_time + self.config["granularity"]).strftime("%Y-%m-%d"),
            "locationid": metadata["noaa_city_id"],
            "location": location,
        }
