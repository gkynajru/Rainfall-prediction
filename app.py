from flask import Flask, jsonify, request, render_template
from apscheduler.schedulers.background import BackgroundScheduler
from utils.data_generator import WeatherDataFetcher
from utils.database_manager import DatabaseManager
from utils.DataPreprocessor import DataPreprocessor
from utils.mqtt_client import create_mqtt_client
import tensorflow as tf
from config import CONFIG
import pandas as pd
from datetime import datetime
import pytz
import numpy as np
import joblib
from pyngrok import ngrok

app = Flask(__name__)
ngrok_tunnel = ngrok.connect(5000)
print('Public URL:', ngrok_tunnel.public_url)

# Initialize components
fetcher = WeatherDataFetcher()
db_manager = DatabaseManager()
timezone = pytz.timezone('Asia/Bangkok')

#Load model_ifs and preprocessor_ifs
model_ifs = tf.saved_model.load('model_ifs')
infer = model_ifs.signatures["serving_default"] # Access the predict function within the Savedmodel_ifs
preprocessor_ifs = joblib.load('model_ifs/preprocessor_ifs.joblib')

#Load model_vrain and processor_vrain
model_vrain = tf.saved_model.load('model_vrain')
infer = model_vrain.signatures["serving_default"]
preprocessor_vrain = joblib.load('model_vrain/preprocessor_vrain.joblib')

def prepare_data_for_prediction(location_data, location):
    """Prepare data for prediction using the preprocessor_ifs"""
    try:
        # Sort by time
        location_data = location_data.sort_values('time')

        # Add encoded location
        location_data['location_encoded'] = preprocessor_ifs.label_encoder.transform([location])[0]

        # Scale features
        scaled_data = location_data.copy()
        scaled_data = preprocessor_ifs.scale_features(scaled_data, location, is_training=False)

        # Prepare data array
        data_array = scaled_data[preprocessor_ifs.config['features']].values

        # Create sequence
        input_seq = np.column_stack([
            data_array,
            np.full(len(data_array), location_data['location_encoded'].iloc[0])
        ])

        # Reshape for model_ifs input (batch_size, sequence_length, features+1)
        X = input_seq[-preprocessor_ifs.config['input_steps']:].reshape(1, preprocessor_ifs.config['input_steps'], -1)

        return X

    except Exception as e:
        print(f"Error preparing data for prediction: {e}")
        raise

def update_data():
    """Hourly update function"""
    try:
        # Fetch latest data
        recent_data, ifs_prediction = fetcher.get_latest_data()

        # Save actual values
        db_manager.save_ifs_predictions(ifs_prediction)

        recent_data["time"] = recent_data["time"].dt.strftime('%Y-%m-%dT%H:%M')
        recent_data["time"] = pd.to_datetime(recent_data["time"], format='ISO8601')

        # Make predictions of LSTM_ifs for each location
        ifs_lstm_predictions = {}
        for location in fetcher.locations.keys():
            location_data = recent_data[recent_data['location'] == location].copy()
            # print(location_data)
            if len(location_data) >= CONFIG['input_steps']:  # Ensure we have enough data points
                # Use classes_ to get the encoded value
                location_encoded = preprocessor_ifs.label_encoder.classes_.tolist().index(location)
                location_data['location_encoded'] = location_encoded

                # Prepare data for prediction
                X = prepare_data_for_prediction(location_data, location)
                # X = preprocessor_ifs.process_location(location_data, location, is_training=False)[0]

                # Make prediction
                pred = infer(tf.constant(X, dtype=tf.float32))['output_0']

                # Inverse transform the predictions
                rainfall_pred = preprocessor_ifs.inverse_transform_rainfall(pred[0])

                # Generate timestamps for predictions
                last_time = location_data['time'].max()
                timestamps = [
                    last_time + pd.Timedelta(hours=i+1)
                    for i in range(len(rainfall_pred))
                ]

                ifs_lstm_predictions[location] = {
                    'timestamps': timestamps,
                    'predictions': rainfall_pred.tolist()
                }
            else:
                print(f"Not enough data for {location}, skipping ifs lstm prediction.")

        # Make predictions of LSTM_ifs for each location
        vrain_lstm_predictions = {}
        for location in fetcher.locations.keys():
            vrain_location_data = recent_data[recent_data['location'] == location].copy()
            if len(location_data) >= CONFIG['input_steps']:
                location_vrain_encoded = preprocessor_vrain.label_encoder.classes_.tolist().index(location)
                vrain_location_data['location_encoded'] = location_vrain_encoded

                X = prepare_data_for_prediction(location_data, location)
                pred = infer(tf.constant(X, dtype=tf.float32))['output_0']
                rainfall_pred = preprocessor_ifs.inverse_transform_rainfall(pred[0])

                last_time = location_data['time'].max()
                timestamps = [
                    last_time + pd.Timedelta(hours=i+1)
                    for i in range(len(rainfall_pred))
                ]

                vrain_lstm_predictions[location] = {
                    'timestamps': timestamps,
                    'predictions': rainfall_pred.tolist()
                }
            else:
                print(f"Not enough data for {location}, skipping vrain lstm prediction.")    

        # Save predictions
        db_manager.save_lstm_predictions(ifs_lstm_predictions)
        db_manager.save_vrain_prediction(vrain_lstm_predictions)

        current_time = datetime.now(timezone)
        print(f"Data updated successfully at {current_time}")

    except Exception as e:
        print(f"Error updating data: {e}")
        import traceback
        print(traceback.format_exc())  # Print full traceback

# Set up scheduler
scheduler = BackgroundScheduler(timezone=timezone)
scheduler.add_job(update_data, 'interval', hours=1)
scheduler.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    try:
        location = request.args.get('location', 'Truong Xuan')
        print(f"Fetching data for location: {location}")  # Debug log
        
        lstm_pred, ifs_pred, vrain_pred = db_manager.get_comparison_data(location)
        
        response_data = {
            'lstm_predictions': {
                'timestamps': lstm_pred['time'].tolist(),
                'values': lstm_pred['value'].tolist()
            },
            'ifs_predictions': {
                'timestamps': ifs_pred['time'].tolist(),
                'values': ifs_pred['value'].tolist()
            },
            'vrain_predictions': {
                'timestamps': vrain_pred['time'].tolist(),
                'values': vrain_pred['value'].tolist()
            }
        }
        
        print(f"Successfully prepared data for {location}")  # Debug log
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error getting data: {str(e)}")  # Error log
        return jsonify({'error': str(e)}), 500
    
if __name__ == '__main__':
    # Initial update
    update_data()
    # Initial mqtt client
    create_mqtt_client()

    app.run(host='0.0.0.0', port=5000)
    # app.run(debug=True)