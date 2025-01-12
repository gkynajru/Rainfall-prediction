# Weather Prediction System

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A machine learning-based weather prediction system that forecasts rainfall for multiple locations in Vietnam using LSTM neural networks and real-time weather data.

## 📊 Demo

![image](https://github.com/user-attachments/assets/a9cc176e-3834-4ee9-bbde-2700db35de07)

## 🌟 Features

- Real-time weather data fetching from Open-Meteo API
- 24-hour rainfall predictions for 9 locations in Vietnam
- LSTM neural network for accurate forecasting
- Automated hourly updates using background scheduling
- RESTful API for data access
- Web interface for visualization
- Comprehensive data preprocessing and feature scaling

## 🏗️ Architecture

The system consists of several key components:

1. **Data Collection**
   - Weather data fetching from Open-Meteo API
   - Support for 17 weather features including temperature, humidity, wind speed, etc.
   - Automatic rate limiting and error handling

2. **Data Processing**
   - MinMax scaling for feature normalization
   - Sequence creation for LSTM input
   - Rainfall data transformation
   - Location encoding

3. **Model**
   - LSTM-based neural network
   - Batch normalization and dropout layers
   - Early stopping and learning rate reduction
   - Model checkpointing

4. **API & Storage**
   - Flask-based REST API
   - CSV-based database system
   - Background scheduling for updates
   - Historical data management

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/weather-prediction.git
cd weather-prediction

# Install dependencies
pip install -r requirements.txt

# Authenticate your ngrok agent.
ngrok config add-authtoken $YOUR_AUTHTOKEN
```

# 
## ⚙️ Configuration

The system uses a configuration dictionary that can be modified in `config.py`:

```python
CONFIG = {
    'input_steps': 24,
    'output_steps': 24,
    'stride': 1,
    'features': [
        "temperature_2m", "relative_humidity_2m", "dew_point_2m",
        "apparent_temperature", "weather_code", "pressure_msl",
        "surface_pressure", "cloud_cover", "cloud_cover_low",
        "cloud_cover_mid", "cloud_cover_high", "wind_speed_10m",
        "wind_speed_100m", "wind_direction_10m", "wind_direction_100m",
        "wind_gusts_10m"
    ],
    'target': 'rain',
    'batch_size': 32,
    'epochs': 20
}
```

## 🗺️ Supported Locations

The system currently supports predictions for the following locations in Vietnam:
![image](https://github.com/user-attachments/assets/71a567c6-3abe-471b-b217-48eee3779063)


## 📈 Model Performance

![__results___10_0](https://github.com/user-attachments/assets/dcb5406f-2922-4c4e-9319-ced62a07ecb3)

## 🖥️ Usage

### Starting the Server

```bash
python app.py
```

The server will start on `http://localhost:5000` or you can use ngrok tunnel displayed in the console.

### API Endpoints

#### GET /api/data
Returns prediction and actual data for a specified location.

Query Parameters:
- `location` (optional): Location name (defaults to "Ky Thuong")

Example Response:
```json
{
    "predictions": {
        "timestamps": ["2024-01-11T10:00", "2024-01-11T11:00"],
        "values": [0.5, 0.7]
    },
    "actual": {
        "timestamps": ["2024-01-11T10:00", "2024-01-11T11:00"],
        "values": [0.4, 0.6]
    }
}
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/gkynajru/Rainfall-prediction/blob/master/LICENSE.md) file for details.

## 📧 Contact

Nguyen Tran Gia Ky - [ntgiaky@gmail.com](mailto:ntgiaky@gmail.com)

Project Link: [https://github.com/gkynajru/Rainfall-prediction](https://github.com/gkynajru/Rainfall-prediction)

## 🙏 Acknowledgments

- [Open-Meteo](https://open-meteo.com/) for providing weather data
- [TensorFlow](https://www.tensorflow.org/) for the deep learning framework
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [Vrain](https://vrain.vn) for providing rain gauge data using a dedicated rain gauge system
