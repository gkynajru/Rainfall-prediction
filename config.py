# MQTT Configuration
BROKER = "mqtt.flespi.io"
PORT = 8883
TOPIC = "RAINFALL_FORCAST_SYSTEM"
TOKEN = "KBuTL4GcQIdeStibgS2YOd6YTJq1AydfcAde7ERrlOx1hJGaJjgPgAGe4GMqNVqc"

FEATURES = [
        "temperature_2m", "relative_humidity_2m", "dew_point_2m",
        "apparent_temperature", "weather_code", "pressure_msl",
        "surface_pressure", "cloud_cover", "cloud_cover_low",
        "cloud_cover_mid", "cloud_cover_high", "wind_speed_10m",
        "wind_speed_100m", "wind_direction_10m", "wind_direction_100m",
        "wind_gusts_10m", "rain"
    ]

# Open-Meteo API Parameters
PARAMS_FORCAST = {
    "Ky Thuong":
        {
            "latitude": 18.0316,
            "longitude": 106.109,
            "hourly": FEATURES,
            "timezone": "Asia/Bangkok",
            "past_days": 1,
            "forecast_days": 2
        },
    "CC Thuy_loi":
        {
            "latitude": 18.312828,
            "longitude": 105.9082,
            "hourly": FEATURES,
            "timezone": "Asia/Bangkok",
            "past_days": 1,
            "forecast_days": 2          
        },
    "My Loc":
        {
            "latitude": 18.383127,
            "longitude": 105.747795,
            "hourly": FEATURES,
            "timezone": "Asia/Bangkok",
            "past_days": 1,
            "forecast_days": 2                  
        },
    "Van Trach":
        {
            "latitude": 17.60984,
            "longitude": 106.450676,
            "hourly": FEATURES,
            "timezone": "Asia/Bangkok",
            "past_days": 1,
            "forecast_days": 2               
        },
    "Truong Xuan":
        {
            "latitude": 17.2751871,
            "longitude": 106.6334756,
            "hourly": FEATURES,
            "timezone": "Asia/Bangkok",
            "past_days": 1,
            "forecast_days": 2
        },
    "Ho Trooc Trau":
        {
            "latitude": 17.398945,
            "longitude": 106.57666,
            "hourly": FEATURES,
            "timezone": "Asia/Bangkok",
            "past_days": 1,
            "forecast_days": 2
        },
    "Cua Tung":
        {
            "latitude": 17.047451,
            "longitude": 107.10173,
            "hourly": FEATURES,
            "timezone": "Asia/Bangkok",
            "past_days": 1,
            "forecast_days": 2
        },
    "Huong Linh":
        {
            "latitude": 16.695957,
            "longitude": 106.762184,
            "hourly": FEATURES,
            "timezone": "Asia/Bangkok",
            "past_days": 1,
            "forecast_days": 2
        },
    "Trieu Ai":
        {
            "latitude": 16.766256,
            "longitude": 107.12237,
            "hourly": FEATURES,
            "timezone": "Asia/Bangkok",
            "past_days": 1,
            "forecast_days": 2
        }       
}

CONFIG = {
    'input_steps': 24,
    'output_steps': 24,
    'stride': 1,
    'features': [
        "temperature_2m", "relative_humidity_2m", "dew_point_2m",
        "apparent_temperature", "weather_code", "pressure_msl",
        "surface_pressure", "cloud_cover", "cloud_cover_low",
        "cloud_cover_mid", "cloud_cover_high", "wind_speed_10m",
        "wind_speed_100m", "wind_direction_10m", "wind_direction_100m",
        "wind_gusts_10m"
    ],
    'target': 'rain',
    'batch_size': 32,
    'epochs': 20
}