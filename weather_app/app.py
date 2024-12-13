from flask import Flask, render_template, request
from utils.data_generator import fetch_weather_data
import paho.mqtt.client as mqtt
import threading
import json
from config import BROKER, PORT, TOPIC, TOKEN
import pandas as pd
import ssl
from datetime import datetime, timedelta

app = Flask(__name__)

global location_temp
global data

location_temp = "Ky Thuong"
data = fetch_weather_data(location_temp)
new_df = data

t = datetime.now()
if t.minute != 0:
    t = t.replace(minute=0, second=0, microsecond=0)
t_1h = (t + timedelta(hours = 1)).strftime('%Y-%m-%dT%H:%M')
t_2h = (t + timedelta(hours = 2)).strftime('%Y-%m-%dT%H:%M')
t_3h = (t + timedelta(hours = 3)).strftime('%Y-%m-%dT%H:%M')

new_df_filtered = new_df[new_df["date"].isin([t_1h, t_2h, t_3h])]["rain"]
msg = ', '.join(new_df_filtered.astype(str))

rain_data = {}

def on_connect(client, userdata, flags, rc):
    print('Connect with result code ' + str(rc))
    if rc == 0:
        client.subscribe(TOPIC)
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, message):
    print(f"Message received: {message.payload.decode()}")

def publish_message(client, msg):
    try:
        client.publish(TOPIC, msg)
        print(f"Message sent: {msg}")
    except Exception as e:
        print(f"Error publishing message: {e}")

def create_mqtt_client():
    client = mqtt.Client()
    client.username_pw_set(TOKEN, "") 
    client.tls_set_context(ssl.create_default_context())
    client.on_connect = on_connect
    client.on_message = on_message
    client.publish_message = publish_message
    client.connect(BROKER, PORT, 60)
    threading.Thread(target=client.loop_forever, daemon=True).start()
    return client

# Index route to display the rainfall graph
@app.route("/")
def index():
    location = request.args.get("location", location_temp)
    
    client = create_mqtt_client()
    client.publish_message(client, msg)

    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    json_str = df.to_json(orient='records', date_format='iso')
    return render_template("index.html", data=json_str, location=location, locations=rain_data.keys())

if __name__ == "__main__":
    # # Start MQTT client in a separate thread
    # create_mqtt_client()
    # Start Flask app
    app.run(debug=True)
