import paho.mqtt.client as mqtt
import threading
import json
from config import BROKER, PORT, TOPIC, TOKEN
import pandas as pd
import ssl

rain_data = {}

def on_connect(client, userdata, flags, rc):
    print('Connect with result code ' + str(rc))
    if rc == 0:
        client.subscribe(TOPIC)
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, message):
    global rain_data
    payload = json.loads(message.payload.decode("utf-8"))
    location = payload["location"]
    if location not in rain_data:
        rain_data[location] = []
    rain_data[location].append({"time": pd.to_datetime(payload["timestamp"], unit="s"), "rain": payload["rain"]})

def publish_message(client, message):
    try:
        client.publish(TOPIC, message)
        print(f"Message sent: {message}")
    except Exception as e:
        print(f"Error publishing message: {e}")

def create_mqtt_client(msg):
    client = mqtt.Client()
    client.username_pw_set(TOKEN, "") 
    client.tls_set_context(ssl.create_default_context())
    client.on_connect = on_connect
    client.on_message = on_message
    client.publish_message = lambda msg: publish_message(client, msg) 
    client.connect(BROKER, PORT, 60)
    threading.Thread(target=client.loop_forever, daemon=True).start()
    return client