import pandas as pd
from datetime import datetime
import os
import pytz

class DatabaseManager:
    def __init__(self, database_path='database'):
        self.database_path = database_path
        self.predictions_file = os.path.join(database_path, 'lstm_predictions.csv')
        self.ifs_predictions_file = os.path.join(database_path, 'ifs_predictions.csv')
        self.vrain_prediction_file = os.path.join(database_path, 'vrain_prediction.csv')
        self.timezone = pytz.timezone('Asia/Bangkok')
        
        os.makedirs(database_path, exist_ok=True)
        
        for file in [self.predictions_file, self.ifs_predictions_file]:
            if not os.path.exists(file):
                pd.DataFrame(columns=['time', 'location', 'value']).to_csv(
                    file, index=False
                )

    def save_lstm_predictions(self, predictions_dict):
        """Save LSTM model predictions to database"""
        new_data = []
        for location, pred_data in predictions_dict.items():
            for timestamp, value in zip(pred_data['timestamps'], pred_data['predictions']):
                new_data.append({
                    'time': timestamp.strftime('%Y-%m-%dT%H:%M'),
                    'location': location,
                    'value': value
                })
        
        new_df = pd.DataFrame(new_data)
        if os.path.exists(self.predictions_file):
            existing_df = pd.read_csv(self.predictions_file)
            existing_df['time'] = pd.to_datetime(existing_df['time'])
            new_df['time'] = pd.to_datetime(new_df['time'])
            
            updated_df = pd.concat([existing_df, new_df], ignore_index=True)
            updated_df = updated_df.drop_duplicates(subset=['time', 'location'], keep='last')
        else:
            updated_df = new_df

        updated_df['time'] = pd.to_datetime(updated_df['time'])
        updated_df['time'] = updated_df['time'].dt.strftime('%Y-%m-%dT%H:%M')            
        updated_df.to_csv(self.predictions_file, index=False)

    def save_vrain_prediction(self, predictions_dict):
        new_data = []
        for location, pred_data in predictions_dict.items():
            for timestamp, value in zip(pred_data['timestamps'], pred_data['predictions']):
                new_data.append({
                    'time': timestamp.strftime('%Y-%m-%dT%H:%M'),
                    'location': location,
                    'value': value
                })
        
        new_df = pd.DataFrame(new_data)
        if os.path.exists(self.vrain_prediction_file):
            existing_df = pd.read_csv(self.vrain_prediction_file)
            existing_df['time'] = pd.to_datetime(existing_df['time'])
            new_df['time'] = pd.to_datetime(new_df['time'])
            
            updated_df = pd.concat([existing_df, new_df], ignore_index=True)
            updated_df = updated_df.drop_duplicates(subset=['time', 'location'], keep='last')
        else:
            updated_df = new_df

        updated_df['time'] = pd.to_datetime(updated_df['time'])
        updated_df['time'] = updated_df['time'].dt.strftime('%Y-%m-%dT%H:%M')            
        updated_df.to_csv(self.vrain_prediction_file, index=False)

    def save_ifs_predictions(self, weather_data):
        """Save IFS model predictions from Open-Meteo"""
        new_data = []
        current_time = pd.Timestamp.now(tz=self.timezone)
        # Filter for future predictions only (next 24 hours)
        future_data = weather_data[
            (weather_data['time'] > current_time) &
            (weather_data['time'] <= current_time + pd.Timedelta(hours=24))
        ]

        for _, row in future_data.iterrows():
            new_data.append({
                'time': row['time'].strftime('%Y-%m-%dT%H:%M'),
                'location': row['location'],
                'value': row['rain']
            })
            
        new_df = pd.DataFrame(new_data)
        if os.path.exists(self.ifs_predictions_file):
            existing_df = pd.read_csv(self.ifs_predictions_file)
            existing_df['time'] = pd.to_datetime(existing_df['time'])
            new_df['time'] = pd.to_datetime(new_df['time'])
            
            updated_df = pd.concat([existing_df, new_df], ignore_index=True)
            updated_df = updated_df.drop_duplicates(subset=['time', 'location'], keep='last')
        else:
            updated_df = new_df

        updated_df['time'] = pd.to_datetime(updated_df['time'])
        updated_df['time'] = updated_df['time'].dt.strftime('%Y-%m-%dT%H:%M')            
        updated_df.to_csv(self.ifs_predictions_file, index=False)

    def get_comparison_data(self, location, hours=48):
        """Get recent LSTM, IFS predictions and Vrain prediction for comparison"""
        lstm_pred = pd.read_csv(self.predictions_file)
        ifs_pred = pd.read_csv(self.ifs_predictions_file)
        vrain_pred = pd.read_csv(self.vrain_prediction_file)

        # Convert to datetime and localize
        lstm_pred['time'] = pd.to_datetime(lstm_pred['time']).dt.tz_localize(self.timezone)
        ifs_pred['time'] = pd.to_datetime(ifs_pred['time']).dt.tz_localize(self.timezone)
        vrain_pred['time'] = pd.to_datetime(vrain_pred['time']).dt.tz_localize(self.timezone)

        recent_time = pd.Timestamp.now(tz=self.timezone) - pd.Timedelta(hours=hours)
        
        recent_lstm = lstm_pred[
            (lstm_pred['location'] == location) & 
            (lstm_pred['time'] > recent_time)
        ].copy()

        recent_ifs = ifs_pred[
            (ifs_pred['location'] == location) & 
            (ifs_pred['time'] > recent_time)
        ].copy()
        
        recent_vrain = vrain_pred[
            (vrain_pred['location'] == location) &
            (vrain_pred['time'] > recent_time)
        ].copy()

        recent_lstm['time'] = recent_lstm['time'].dt.strftime('%Y-%m-%dT%H:%M')
        recent_ifs['time'] = recent_ifs['time'].dt.strftime('%Y-%m-%dT%H:%M')
        recent_vrain['time'] = recent_vrain['time'].dt.strftime('%Y-%m-%dT%H:%M')

        return recent_lstm, recent_ifs, recent_vrain