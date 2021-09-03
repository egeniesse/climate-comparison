import datetime
import logging
import os

from src.adapters.base_adapter import BaseAdapter
from src.shared.utils import data_point

logger = logging.getLogger(__name__)
AIR_NOW_AQI_URL = "https://www.airnowapi.org/aq/observation/zipCode/historical/"
AIR_NOW_AQI_API_KEY = os.getenv("AIR_NOW_API_KEY")

class AirNowAQIAdapter(BaseAdapter):
    def __init__(self, http_client, db_client, config):
        self.type = "air_now_aqi_adapter"
        self.version = 1

        self.http_client = http_client
        self.db_client = db_client
        self.config = config
    
    async def _process_task(self, job_data):
        params_to_keep = {"date", "zipCode"}
        query_params = {key: value for key, value in job_data.items() if key in params_to_keep}
        query_params.update({
            "API_KEY": AIR_NOW_AQI_API_KEY,
            "format": "application/json",
        })
        response = await self.http_client.get(AIR_NOW_AQI_URL, params=query_params)
        res_json = await response.json()
        
        location, date = job_data["location"], job_data["date_timestamp"]
        datapoints = []
        for data in res_json:
            point_date, param, value = date + (data["HourObserved"]*360), f'aqi-{data["ParameterName"]}', data["AQI"]
            datapoints.append(data_point(location, point_date, param, value, self.version))
        return datapoints
        

    def _create_job_data(self, location, metadata, cur_time):
        date_string = datetime.datetime.fromtimestamp(cur_time).strftime("%Y-%m-%dT00-0000")
        job_data = {
            "zipCode": metadata["zip_code"],
            "date_timestamp": cur_time - (cur_time % (60 * 60 * 24)),
            "date": date_string,
            "location": location,
        }
        return job_data
