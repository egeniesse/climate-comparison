from time import time

def adapter_config(overrides=None):
    now_time = time()
    defaults = {
        "start_time": now_time - 60 * 60,
        "end_time": now_time,
        "granularity": 60 * 60 * 24,
        "concurrent_tasks": 1,
        "data_by_location": {
            "Bend": {
                "zip_code": 97703,
                "noaa_city_id": "CITY:US410001",
            }
        }
    }
    return {**defaults, **(overrides or {})}
