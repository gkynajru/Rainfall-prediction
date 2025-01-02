import pandas as pd
import numpy as np
import joblib
import tensorflow as tf
from datetime import datetime, timedelta

class ModelDeployment:
    def __init__(self, config):
        self.config = config
        # Load the trained model and preprocessor
        self.ifs_lstm_model = tf.saved_model.load('..\model_ifs')
        self.ifs_lstm_preprocessor = joblib.load('..\model_ifs\preprocessor_ifs.joblib')
        self.vrain_model = tf.saved_model.load('..\model_vrain')
        self.vrain_preprocessor = joblib.load('..\model_vrain\preprocessor_vrain.joblib')
        self.ifs_infer = self.ifs_lstm_model.signatures["serving_default"] # Access the predict function within the Savedmodel
        self.vrain_infer = self.vrain_model.signatures["serving_default"] 

    def prepare_prediction_data(self, location_data, location, preprocessor):
        """Prepare data for prediction using the corresponding preprocessor"""
        try:
            # Sort by time
            location_data = location_data.sort_values('time')

            # Add encoded location
            location_data['location_encoded'] = preprocessor.label_encoder.transform([location])[0]

            # Scale features
            scaled_data = location_data.copy()
            scaled_data = preprocessor.scale_features(scaled_data, location, is_training=False)

            # Prepare data array
            data_array = scaled_data[preprocessor.config['features']].values

            # Create sequence
            input_seq = np.column_stack([
                data_array,
                np.full(len(data_array), location_data['location_encoded'].iloc[0])
            ])

            # Reshape for model_ifs input (batch_size, sequence_length, features+1)
            X = input_seq[-preprocessor.config['input_steps']:].reshape(1, preprocessor.config['input_steps'], -1)

            return X

        except Exception as e:
            print(f"Error preparing data for prediction: {e}")
            raise
        
    def predict_rainfall(self, df, location, preprocessor, model):
        """Make predictions for the next output_steps"""
        try:
            # Prepare the input data
            X = self.prepare_prediction_data(df, location, preprocessor)
            
            # Make predictions
            predictions = model.predict(X)
            
            # Inverse transform the predictions
            rainfall_predictions = self.preprocessor.inverse_transform_rainfall(predictions[0])
            
            # Generate timestamps for predictions
            last_time = df[df['location'] == location]['time'].max()
            timestamps = [
                (pd.to_datetime(last_time) + timedelta(hours=i+1)).strftime('%Y-%m-%d %H:%M')
                for i in range(len(rainfall_predictions))
            ]
            
            return {
                'timestamps': timestamps,
                'predictions': rainfall_predictions.tolist()
            }
            
        except Exception as e:
            return {'error ': str(e)}