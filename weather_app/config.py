# MQTT Configuration
BROKER = "mqtt.eclipse.org"
PORT = 1883
TOPIC = "weather/rain_data"

# Open-Meteo API Parameters
LOCATIONS = {
    "Ky Thuong":
        {
            "latitude": 18.0316,
            "longitude": 106.109,
            "hourly": "rain",
            "forecast_days": 1
        },
    "CC Thuy_loi":
        {
            "latitude": 18.312828,
            "longitude": 105.9082,
            "hourly": "rain",
            "forecast_days": 1          
        },
    "My Loc":
        {
            "latitude": 18.383127,
            "longitude": 105.747795,
            "hourly": "rain",
            "forecast_days": 1                  
        },
    "Van Trach":
        {
            "latitude": 17.60984,
            "longitude": 106.450676,
            "hourly": "rain",
            "forecast_days": 1               
        },
    "Truong Xuan":
        {
            "latitude": 17.2751871,
            "longitude": 106.6334756,
            "hourly": "rain",
            "forecast_days": 1
        },
    "Ho Trooc Trau":
        {
            "latitude": 17.398945,
            "longitude": 106.57666,
            "hourly": "rain",
            "forecast_days": 1
        },
    "Cua Tung":
        {
            "latitude": 17.047451,
            "longitude": 107.10173,
            "hourly": "rain",
            "forecast_days": 1
        },
    "Huong Linh":
        {
            "latitude": 16.695957,
            "longitude": 106.762184,
            "hourly": "rain",
            "forecast_days": 1 
        },
    "Trieu Ai":
        {
            "latitude": 16.766256,
            "longitude": 107.12237,
            "hourly": "rain",
            "forecast_days": 1
        }       
}
