import openmeteo_requests
import requests_cache
from retry_requests import retry
import pandas as pd
import time
import pytz

class WeatherDataFetcher:
    def __init__(self):
        self.cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        self.retry_session = retry(self.cache_session, retries=5, backoff_factor=0.2)
        self.openmeteo = openmeteo_requests.Client(session=self.retry_session)
        self.timezone = pytz.timezone('Asia/Bangkok')

        self.features = [
            "temperature_2m", "relative_humidity_2m", "dew_point_2m",
            "apparent_temperature", "weather_code", "pressure_msl",
            "surface_pressure", "cloud_cover", "cloud_cover_low",
            "cloud_cover_mid", "cloud_cover_high", "wind_speed_10m",
            "wind_speed_100m", "wind_direction_10m", "wind_direction_100m",
            "wind_gusts_10m", "rain"
        ]

        self.locations = {
            "Ky Thuong": {"latitude": 18.0316, "longitude": 106.109},
            "CC Thuy Loi": {"latitude": 18.312828, "longitude": 105.9082},
            "My Loc": {"latitude": 18.383127, "longitude": 105.747795},
            "Van Trach": {"latitude": 17.60984, "longitude": 106.450676},
            "Truong Xuan": {"latitude": 17.2751871, "longitude": 106.6334756},
            "Trooc Trau": {"latitude": 17.398945, "longitude": 106.57666},
            "Cua Tung": {"latitude": 17.047451, "longitude": 107.10173},
            "Huong Linh": {"latitude": 16.695957, "longitude": 106.762184},
            "Trieu Ai": {"latitude": 16.766256, "longitude": 107.12237}
        }

    def fetch_data(self):
        all_data = []

        for location, coords in self.locations.items():
            params = {
                **coords,
                "hourly": self.features,
                "timezone": "Asia/Bangkok",
                "past_days": 1,
                "forecast_days": 2
            }

            try:
                response = self.openmeteo.weather_api(
                    "https://api.open-meteo.com/v1/forecast",
                    params=params
                )[0]

                hourly = response.Hourly()

                time_data = pd.date_range(
                    start=pd.to_datetime(hourly.Time(), unit="s"),
                    end=pd.to_datetime(hourly.TimeEnd(), unit="s"),
                    freq=pd.Timedelta(seconds=hourly.Interval()),
                    inclusive="left"
                )

                # Localize the timestamps to Bangkok timezone
                time_data = time_data.tz_localize('UTC').tz_convert(self.timezone)
                hourly_data = {"time": time_data}

                # Add all features to hourly_data
                for idx, feature in enumerate(self.features):
                    hourly_data[feature] = hourly.Variables(idx).ValuesAsNumpy()

                df = pd.DataFrame(hourly_data)

                df["location"] = location
                all_data.append(df)
                time.sleep(10)  # Rate limiting

            except Exception as e:
                print(f"Error fetching data for {location}: {e}")
                continue

        if not all_data:
            raise Exception("No data was fetched from any location")

        return pd.concat(all_data, ignore_index=True)

    def get_latest_data(self):
        """Get the most recent 24 hours of data for prediction"""
        df = self.fetch_data()
        current_time = pd.Timestamp.now(tz=self.timezone)

        ifs_pred = df[
            (df['time'] > current_time) &
            (df['time'] <= current_time + pd.Timedelta(hours=24))
        ].copy()

        # Get last 24 hours of data
        recent_data = df[
            (df['time'] <= current_time) &
            (df['time'] > current_time - pd.Timedelta(hours=24))
        ].copy()

        if recent_data.empty:
            raise Exception("No recent data available")

        return recent_data.copy(), ifs_pred.copy()