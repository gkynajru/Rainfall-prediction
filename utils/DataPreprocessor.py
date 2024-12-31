import gc
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
import numpy as np
import pandas as pd

class DataPreprocessor:
    def __init__(self, config):
        self.config = config
        self.scalers = {}
        self.label_encoder = LabelEncoder()

    def transform_rainfall(self, data):
        """Log transform rainfall data"""
        return np.log1p(data)

    def inverse_transform_rainfall(self, data):
        """Inverse transform log-transformed rainfall data"""
        return np.expm1(data)

    def load_and_prepare_data(self, filepath):
        """Load data from CSV and prepare initial dataframe"""
        print("Loading data...")
        df = pd.read_csv(filepath)
        df['time'] = pd.to_datetime(df['time'])
        df['location_encoded'] = self.label_encoder.fit_transform(df['location'])
        print("Label and number: ", list(zip(self.label_encoder.classes_, range(len(self.label_encoder.classes_)))))
        return df

    def scale_features(self, location_data, location, is_training=True):
        """Scale features for a specific location"""
        if is_training:
            self.scalers[location] = {
                feature: MinMaxScaler() for feature in self.config['features']
            }
            # Fit and transform
            for feature in self.config['features']:
                location_data[feature] = self.scalers[location][feature].fit_transform(
                    location_data[feature].values.reshape(-1, 1)
                )
        else:
            # Transform only
            for feature in self.config['features']:
                location_data[feature] = self.scalers[location][feature].transform(
                    location_data[feature].values.reshape(-1, 1)
                )

        return location_data

    def create_sequences(self, data, location_encoded):
        """Create sequences for a single location"""
        input_steps = self.config['input_steps']
        output_steps = self.config['output_steps']
        feature_count = len(self.config['features'])

        X, y = [], []

        for i in range(0, len(data) - input_steps - output_steps + 1, self.config['stride']):
            # Input sequence
            input_seq = np.column_stack([
                data[i:i + input_steps, :feature_count],
                np.full(input_steps, location_encoded)
            ])

            # Target sequence
            target_seq = data[
                i + input_steps:i + input_steps + output_steps,
                -1
            ]

            X.append(input_seq)
            y.append(target_seq)

            # Free memory periodically
            if len(X) % 1000 == 0:
                gc.collect()

        return np.array(X), np.array(y)

    def process_location(self, df, location, is_training=True):
        """Process data for a single location"""
        print(f"Processing location: {location}")

        # Get data for this location
        location_data = df[df['location'] == location].copy()
        location_data = location_data.sort_values('time')

        # Scale features
        location_data = self.scale_features(location_data, location, is_training)

        # Transform rainfall
        location_data['rain_transformed'] = self.transform_rainfall(
            location_data[self.config['target']].values
        )

        # Prepare data array
        data_array = location_data[
            self.config['features'] + ['rain_transformed']
        ].values

        # Create sequences
        X, y = self.create_sequences(
            data_array,
            location_data['location_encoded'].iloc[0]
        )

        return X, y, location_data.index

    def split_data(self, X, y, train_ratio=0.8):
        """Split data into training and testing sets"""
        split_idx = int(len(X) * train_ratio)

        X_train = X[:split_idx]
        X_test = X[split_idx:]
        y_train = y[:split_idx]
        y_test = y[split_idx:]

        return X_train, X_test, y_train, y_test

    def process_all_locations(self, df, train_ratio=0.8):
        """Process all locations and combine data"""
        X_train_all = []
        X_test_all = []
        y_train_all = []
        y_test_all = []

        locations = df['location'].unique()

        for location in locations:
            # Process location data
            X, y, _ = self.process_location(df, location)

            # Split data
            X_train, X_test, y_train, y_test = self.split_data(X, y, train_ratio)

            # Append to lists
            X_train_all.append(X_train)
            X_test_all.append(X_test)
            y_train_all.append(y_train)
            y_test_all.append(y_test)

            # Clear memory
            gc.collect()

        # Combine all data
        X_train = np.vstack(X_train_all)
        X_test = np.vstack(X_test_all)
        y_train = np.vstack(y_train_all)
        y_test = np.vstack(y_test_all)

        return X_train, X_test, y_train, y_test