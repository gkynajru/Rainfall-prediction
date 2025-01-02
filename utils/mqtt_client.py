import paho.mqtt.client as mqtt_client
import threading
from utils.data_generator import WeatherDataFetcher
from utils.database_manager import DatabaseManager
from config import BROKER, PORT, TOPIC, TOKEN
import numpy as np
import ssl
from datetime import datetime, timedelta
import pytz
import pandas as pd

LOCATION_GROUPS = {
    '110': ['Ky Thuong', 'CC Thuy Loi', 'My Loc'],
    '111': ['Van Trach', 'Truong Xuan', 'Trooc Trau'],
    '112': ['Cua Tung', 'Huong Linh', 'Trieu Ai']
}

# replace_dict = {'Ha Tinh': '110', 'Quang Binh': '111','Quang Tri': '112'}

timezone = pytz.timezone('Asia/Bangkok')
fetcher = WeatherDataFetcher()
db_manager = DatabaseManager()

def on_connect(client, userdata, flags, rc, properties):
    print('Connect with result code ' + str(rc))
    if rc == 0:
        client.subscribe(TOPIC)
    else:
        print(f"Failed to connect, return code {rc}")

def calculate_average_predictions(predictions, locations):
    """Calculate average predictions for a group of locations"""
    group_preds = []
    for location in locations:
        if location in predictions:
            group_preds.append(predictions[location])
    return np.mean(group_preds, axis=0) if group_preds else None

def format_mqtt_message(location, ifs_pred, lstm_pred, vrain_pred):
    """Format prediction data for MQTT message"""
    return f"{location}||{ifs_pred[0]}|{ifs_pred[1]}|{ifs_pred[2]}|{lstm_pred[0]}|{lstm_pred[1]}|{lstm_pred[2]}|{vrain_pred[0]}|{vrain_pred[1]}|{vrain_pred[2]}|"

def on_mqtt_message(client, userdata, message):
    if message.payload.decode() == "START":
        current_time = datetime.now(timezone)
        formatted_time = current_time.strftime('%d.%m.%Y - %H:%M')
        client.publish(TOPIC, f'100||{formatted_time}|')        
        forecast_hours = [1, 6, 24]
        
        # Get predictions for each model
        all_predictions = {}
        for location in fetcher.locations:
            # Get predictions for forecast hours
            location_preds = {
                    'lstm': [],
                    'ifs': [],
                    'vrain': []
                }
            
            for hour in forecast_hours:
                target_time = current_time + timedelta(hours=hour)
                
                # Get predictions for each model at this time horizon
                lstm_pred, ifs_pred, vrain_pred = db_manager.get_comparison_data(location)
                lstm_pred['time'] = pd.to_datetime(lstm_pred['time']).dt.tz_localize(timezone)
                target_idx = (lstm_pred['time'] - target_time).abs().argmin()
                
                location_preds['lstm'].append(lstm_pred['value'].iloc[target_idx])
                location_preds['ifs'].append(ifs_pred['value'].iloc[target_idx])
                location_preds['vrain'].append(vrain_pred['value'].iloc[target_idx])
        
            all_predictions[location] = location_preds        

        # Calculate and send averages for each region
        for region, locations in LOCATION_GROUPS.items():
            region_preds = {
                'ifs': np.zeros(3),
                'lstm': np.zeros(3),
                'vrain': np.zeros(3)
            } 

            # Calculate average for each model and time horizon
            for location in locations:
                for model in ['ifs', 'lstm', 'vrain']:
                    region_preds[model] += np.array(all_predictions[location][model])

            # Average over number of locations
            for model in region_preds:
                region_preds[model] /= len(locations)

            # Format and send message
            message = format_mqtt_message(
                region,
                region_preds['ifs'].round(1),
                region_preds['lstm'].round(1),
                region_preds['vrain'].round(1)
            )
            client.publish(TOPIC, message)

def publish_message(client, message):
    try:
        client.publish(TOPIC, message)
        print(f"Message sent: {message}")
    except Exception as e:
        print(f"Error publishing message: {e}")

def create_mqtt_client():
    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2)
    client.username_pw_set(TOKEN, "") 
    client.tls_set_context(ssl.create_default_context())
    client.on_connect = on_connect
    client.on_message = on_mqtt_message
    client.connect(BROKER, PORT, 60)
    threading.Thread(target=client.loop_forever, daemon=True).start()
    return client

