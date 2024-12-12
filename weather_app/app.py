from flask import Flask, render_template, request
from utils.mqtt_client import start_mqtt_client, rain_data
from utils.data_crawler import fetch_weather_data
import pandas as pd

app = Flask(__name__)

# Index route to display the rainfall graph
@app.route("/")
def index():
    location = request.args.get("location", "Ky Thuong")
    data = rain_data.get(location, [])
    return render_template("index.html", data=data, location=location, locations=rain_data.keys())

if __name__ == "__main__":
    # Start MQTT client in a separate thread
    start_mqtt_client()
    # Start Flask app
    app.run(debug=True)
