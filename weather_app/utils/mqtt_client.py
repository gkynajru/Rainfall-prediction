import paho.mqtt.client as mqtt
import threading
import json
from config import BROKER, PORT, TOPIC
import pandas as pd

rain_data = {}

def on_message(client, userdata, message):
    global rain_data
    payload = json.loads(message.payload.decode("utf-8"))
    location = payload["location"]
    if location not in rain_data:
        rain_data[location] = []
    rain_data[location].append({"time": pd.to_datetime(payload["timestamp"], unit="s"), "rain": payload["rain"]})

def start_mqtt_client():
    client = mqtt.Client()
    client.connect(BROKER, PORT)
    client.subscribe(TOPIC)
    client.on_message = on_message
    thread = threading.Thread(target=client.loop_forever, daemon=True)
    thread.start()
