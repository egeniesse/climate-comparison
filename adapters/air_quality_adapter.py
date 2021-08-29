import json
import os
import uuid

from adapters.base_adapter import BaseAdapter
from shared.utils import data_point
import shared.constants as constants

OPEN_WEATHER_MAP_AQI_URL="http://api.openweathermap.org/data/2.5/air_pollution/history"

class AQIAdapter(BaseAdapter):
    def __init__(self, http_client, db_client):
        self.type = "aqi_adapter"
        self.http_client = http_client
        self.db_client = db_client
        self.concurrent_tasks = 1
        self.granularity = 60 * 60 * 24 * 7
        self.version = 1
    
    async def process_tasks(self):
        while await self.process_task():
            pass

    async def process_task(self):
        next_task = self.get_tasks()
        if not next_task:
            return False
        job_data = next_task[0]["job_data"]
        query_params = {key: value for key, value in job_data.items() if key != "location"}
        query_params["appid"] = os.getenv("OPEN_WEATHER_API_KEY")
        response = await self.http_client.get(OPEN_WEATHER_MAP_AQI_URL, params=query_params)
        res_json = await response.json()
        
        location = job_data["location"]
        to_insert = [data_point(location, p["dt"], "aqi", p["main"]["aqi"]) for p in res_json["list"]]
        self.db_client.bulk_create_if_not_exists("datapoints", to_insert)
        self.mark_tasks_as_complete(next_task)
        return True
        

    def generate_tasks(self):
        tasks = []
        cur_time = constants.start_time
        while cur_time < constants.end_time:
            for location, metadata in constants.coords_by_location.items():
                job_data = json.dumps({
                    "lat": metadata["coords"]["lat"],
                    "lon": metadata["coords"]["lon"],
                    "location": location,
                    "start": cur_time,
                    "end": cur_time + constants.granularity,
                })
                tasks.append({
                    "state": "not_started",
                    "job_data": job_data,
                    "guid": str(uuid.uuid5(uuid.NAMESPACE_X500, job_data + "aqi_adapter")),
                    "adapter": "aqi_adapter",
                })
            cur_time += constants.granularity
        self.db_client.bulk_create_if_not_exists("tasks", tasks)
            

        