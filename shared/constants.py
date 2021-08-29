# Start time Jan 1st 2019. For additional dates,
# see https://www.epochconverter.com/timestamp-list.
start_time = 1262304000
end_time = 1630188275

data_by_location = {
    "San Jose": {
        "coords": {
            "lat": 37.3394,
            "lon": 121.895,
        },
        "zip_code": 95124,
    },
    "Seattle": {
        "zip_code": 98103,
    },
}

api_rate_limits = {
    # 500 requests per hour
    "air_now": (60 * 60) / 500,
}