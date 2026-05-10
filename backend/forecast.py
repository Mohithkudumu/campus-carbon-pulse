import os
import json
import numpy as np
import pandas as pd
import joblib
from tensorflow.keras.models import load_model
from datetime import datetime

SEQ_LEN = 168  # 7 days * 24 hours
MODEL_DIR = "models"
DATA_PATH = "snuc_carbon_year_2025.csv"
OUTPUT_JSON = "emissions.json"

def generate_24h_forecast_json():
    """
    Real-time forecasting approach:
    1. Get current time and round to nearest hour
    2. Use last 168 hours from CSV as input (ending at current time)
    3. Forecast next 24 hours with real timestamps
    """
    # Load historical data
    df = pd.read_csv(DATA_PATH)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    df = df.sort_values(["Building_ID", "Timestamp"])
    
    # Get current time rounded to nearest hour
    now = datetime.now()
    current_hour = now.replace(minute=0, second=0, microsecond=0)
    
    print(f"Current time: {now}")
    print(f"Rounded to: {current_hour}")
    
    # Calculate the time window we need (last 168 hours ending at current time)
    start_time = current_hour - pd.Timedelta(hours=SEQ_LEN)
    
    print(f"Using data from {start_time} to {current_hour}")

    forecast_output = {}

    # Iterate through saved LSTM models
    for file in os.listdir(MODEL_DIR):
        if not file.startswith("lstm_") or not file.endswith(".keras"):
            continue

        building_id = file.replace("lstm_", "").replace(".keras", "")

        # Load model & scaler
        model = load_model(os.path.join(MODEL_DIR, file))
        scaler = joblib.load(
            os.path.join(MODEL_DIR, f"scaler_{building_id}.joblib")
        )

        # Extract time series for this building
        building_df = df[df["Building_ID"] == building_id].copy()
        
        # Filter to get last 168 hours ending at current time
        # We need data that exists in CSV up to current_hour
        building_df = building_df[building_df["Timestamp"] <= current_hour]
        
        # Get the last 168 data points
        if len(building_df) < SEQ_LEN:
            print(f"Warning: Not enough data for {building_id}. Need {SEQ_LEN}, have {len(building_df)}")
            continue
            
        series = building_df["Total_CO2e_kg"].values[-SEQ_LEN:].reshape(-1, 1)
        scaled_series = scaler.transform(series)

        # Prepare input window
        history = scaled_series.reshape(1, SEQ_LEN, 1)

        building_forecast = {}

        # Recursive 24-hour forecast starting from current hour
        for hour in range(1, 25):
            pred_scaled = model.predict(history, verbose=0)[0][0]
            pred_real = scaler.inverse_transform([[pred_scaled]])[0][0]

            # Generate timestamp for this forecast hour
            forecast_time = current_hour + pd.Timedelta(hours=hour)
            building_forecast[str(forecast_time)] = round(float(pred_real), 2)

            # Update rolling window
            history = np.roll(history, -1, axis=1)
            history[0, -1, 0] = pred_scaled

        forecast_output[building_id] = building_forecast
        print(f"Forecasted {building_id}: {hour} hours ahead")

    # Save JSON
    with open(OUTPUT_JSON, "w") as f:
        json.dump(forecast_output, f, indent=4)

    print(f"\nForecast saved to {OUTPUT_JSON}")
    print(f"Forecast period: {current_hour + pd.Timedelta(hours=1)} to {current_hour + pd.Timedelta(hours=24)}")
    return forecast_output

if __name__ == "__main__":
    generate_24h_forecast_json()
