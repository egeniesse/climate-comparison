import os
from time import time

adapter_config = {
    # Start time Jan 1st 2019. For additional dates,
    # see https://www.epochconverter.com/timestamp-list.
    "start_time": 1262304000,
    "end_time": time(),
    "granularity": 60 * 60 * 24,
    "concurrent_tasks": 1,
    "data_by_location": {
        # To fetch the NOAA city ID, you can use this API call:
        # https://www.ncdc.noaa.gov/cdo-web/api/v2/locations?limit=1000&datasetid=GHCND&sortfield=id&locationcategoryid=CITY&sortorder=desc
        "Bend": {
            "zip_code": 97703,
            "noaa_city_id": "CITY:US410001",
        },
        "Boise": {
            "zip_code": 83702,
            "noaa_city_id": "CITY:US160001",
        },
        "San Jose": {
            "zip_code": 95124,
            "noaa_city_id": "CITY:US060032",
        },
        "Seattle": {
            "zip_code": 98103,
            "noaa_city_id": "CITY:US530018",
        },
        "Denver": {
            "zip_code": 80014,
            "noaa_city_id": "CITY:US080004",
        },
    }
}

db_config = {
    "path": f"{os.path.expanduser('~')}/.cache/climate-comparison.db"
}

api_rate_limits = {
    # 500 requests per hour
    "air_now": (60 * 60) / 500,
    # 10,000 requests per day
    "noaa_weather_data": (60 * 60 * 24) / 10000,
}
