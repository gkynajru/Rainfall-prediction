from flask import Flask, jsonify, render_template
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt
from flask_mqtt import Mqtt
import os
import re
import numpy as np
from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import pandas as pd

app = Flask(__name__)
#MQTT setting
app.config['MQTT_BROKER_URL'] = 'mqtt.flespi.io'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = 'nwpShgwFRrWGUKUTS2AMzZKhqDXEgCCtYS93WwwDLi8uQQdzJB98qHdG80aeqBwc'
app.config['MQTT_PASSWORD'] = 'secret'
app.config['MQTT_KEEPALIVE'] = 300
app.config['MQTT_TLS_ENABLED'] = False
app.config['MQTT_REFRESH_TIME'] = 1.0 # refresh time in seconds
mqtt = Mqtt(app)
socketio = SocketIO(app)

# # Load the model and scaler
model = load_model('..\model_lstm.h5')
scaler =  MinMaxScaler()

# Create sequences
def create_sequences(data, seq_length):
    sequences = []
    labels = []
    for i in range(len(data) - seq_length):
        seq = data[i:i + seq_length]
        label = data[i + seq_length][-1]  # Predict the precipitation value
        sequences.append(seq)
        labels.append(label)
    return np.array(sequences), np.array(labels)

# Simulated data storage
data = pd.read_csv('database\database.csv', on_bad_lines='skip')
data['time'] = pd.to_datetime(data['time'])
date_time = data['time'].astype('str').tolist()
data.set_index('time', inplace=True)
data.dropna()

# Sequences input
data = data[['temperature_2m (°C)', 'surface_pressure (hPa)', 'relative_humidity_2m (%)', 'precipitation (mm)']]
scaled_data = scaler.fit_transform(data)
X_app, y_app = create_sequences(scaled_data, 48)

temperature = data['temperature_2m (°C)'].tolist()
pressure = data['surface_pressure (hPa)'].tolist()
humidity = data['relative_humidity_2m (%)'].tolist()
precipitation = data['precipitation (mm)'].tolist()

data_point = {
    'temperature': temperature[:48],
    'humidity': humidity[:48],
    'pressure': pressure[:48],
    'pred_precipitation': [],
    'timestamps_history' : date_time[:48],
    'timestamps_pred': date_time[48:96]
}

# @mqtt.on_connect()
# def handle_connect(client, userdata, flags, rc):
#     print('Connect with result code ' + str(rc))
#     global subscribed
#     client.subscribe('Data')
#     if not subscribed:
#         mqtt.subscribe('Data')  # Use your MQTT topic
#         subscribed = True

# @mqtt.on_message()
# def handle_mqtt_message(client, userdata, message):
#     global mqtt_data, processed_messages, date_time
#     payload = message.payload.decode()
#     print(f"Received message: {payload}")
#     match = re.match(r"temp: (\d+), press: (\d+), humid: (\d+), time: (\S)", payload)
#     if match:
#         temperature = int(match.group(2))
#         humidity = int(match.group(1))
#         mqtt_data.append({'Temperature': temperature, 'Humidity': humidity})
#         time_data.append(time.strftime("%H:%M:%S"))
#         socketio.emit('update', {'Temperature': temperature, 'Humidity': humidity, 'time': time_data[-1]})

#         #add data to database
#         date_time = time.strftime("%Y-%m-%d %H:%M:%S")
#         db = sqlite3.connect(database_path)
#         cur2 = db.cursor()
#         a = cur2.execute("SELECT COUNT(*) FROM data")
#         db.commit()
#         id = a.fetchall()[0][0] + 1
#         cur1 = db.cursor()
#         cur1.execute("INSERT INTO data VALUES (?,?,?,?)", (id, date_time, temperature, humidity))
#         db.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def get_data():
    # Predict future precipitation
    future_precipitation = model.predict(X_app)
    future_precipitation_inverse = scaler.inverse_transform(np.concatenate((X_app[:, 0, :-1], future_precipitation), axis=1))[:, -1]
    # y_app_inverse = scaler.inverse_transform(np.concatenate((X_app[:, -1, :-1], y_app.reshape(-1, 1)), axis=1))[:, -1]
    list_pred = future_precipitation_inverse.tolist()
    data_point['precipitation'] = list_pred[:48]
    # Update data storage
    # for key in data_point.keys():
    #     # data_point[key].append(new_data[key])
    #     if len(data_point[key]) > 48:
    #         data_point[key].pop(0)

    return jsonify(data_point)

if __name__ == '__main__':
    if not os.path.exists('static'):
        os.makedirs('static')
    socketio.run(app, debug=False)
