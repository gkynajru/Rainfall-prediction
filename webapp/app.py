from flask import Flask, request, jsonify, render_template
import numpy as np
from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import pandas as pd

app = Flask(__name__)

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
date_time = pd.to_datetime(data['time'], format='%d-%m-%Y %H:%M:%S')
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
    'precipitation': precipitation[:48]
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def get_data():
    # Simulate new data points
    # new_data = {
    #     'temperature': random.uniform(15, 30),
    #     'humidity': random.uniform(30, 70),
    #     'pressure': random.uniform(950, 1050),
    #     'precipitation': random.uniform(0, 10),
    # }
    
    # Predict future precipitation
    future_precipitation = model.predict(X_app)
    future_precipitation_inverse = scaler.inverse_transform(np.concatenate((X_app[:, 0, :-1], future_precipitation), axis=1))[:, -1]
    # y_app_inverse = scaler.inverse_transform(np.concatenate((X_app[:, -1, :-1], y_app.reshape(-1, 1)), axis=1))[:, -1]
    data_point['precipitation'] = future_precipitation_inverse.tolist()

    # Update data storage
    # for key in data_point.keys():
    #     # data_point[key].append(new_data[key])
    #     if len(data_point[key]) > 48:
    #         data_point[key].pop(0)

    return jsonify(data_point)

if __name__ == '__main__':
    app.run(debug=False)
