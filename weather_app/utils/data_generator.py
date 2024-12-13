import openmeteo_requests
import requests_cache
from retry_requests import retry
import pandas as pd
from config import PARAMS

def fetch_weather_data(location):
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    params = PARAMS[location]
    responses = openmeteo.weather_api("https://api.open-meteo.com/v1/forecast", params=params)
    response = responses[0]

    hourly = response.Hourly()
    hourly_rain = hourly.Variables(0).ValuesAsNumpy()
    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        ),
        "rain": hourly_rain,
    }
    hourly_dataframe = pd.DataFrame(data = hourly_data)
    hourly_data["date"] = hourly_dataframe["date"].dt.strftime('%Y-%m-%dT%H:%M')

    return pd.DataFrame(data=hourly_data)
