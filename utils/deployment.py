import pandas as pd
import numpy as np
import joblib
import tensorflow as tf
from datetime import datetime, timedelta

class ModelDeployment:
    def __init__(self, config):
        self.config = config
        # Load the trained model and preprocessor
        self.model = tf.keras.models.load_model('best_model.h5')
        self.preprocessor = joblib.load('preprocessor.joblib')
        
    def prepare_prediction_data(self, df, location):
        """Prepare data for prediction"""
        # Get the last input_steps worth of data
        recent_data = df[df['location'] == location].tail(self.config['input_steps'])
        
        if len(recent_data) < self.config['input_steps']:
            raise ValueError(f"Not enough data for location {location}. Need at least {self.config['input_steps']} records.")
            
        # Process the data using the saved preprocessor
        X, _, _ = self.preprocessor.process_location(
            recent_data, 
            location, 
            is_training=False
        )
        
        return X[-1:]  # Return the last sequence
        
    def predict_rainfall(self, df, location):
        """Make predictions for the next output_steps"""
        try:
            # Prepare the input data
            X = self.prepare_prediction_data(df, location)
            
            # Make predictions
            predictions = self.model.predict(X)
            
            # Inverse transform the predictions
            rainfall_predictions = self.preprocessor.inverse_transform_rainfall(predictions[0])
            
            # Generate timestamps for predictions
            last_time = df[df['location'] == location]['time'].max()
            timestamps = [
                (pd.to_datetime(last_time) + timedelta(hours=i+1)).strftime('%Y-%m-%d %H:%M:%S')
                for i in range(len(rainfall_predictions))
            ]
            
            return {
                'timestamps': timestamps,
                'predictions': rainfall_predictions.tolist()
            }
            
        except Exception as e:
            return {'error': str(e)}