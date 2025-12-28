import os
import json
import numpy as np
import pandas as pd
import joblib
from tensorflow.keras.models import load_model

SEQ_LEN = 168
MODEL_DIR = "models"
DATA_PATH = "snuc_carbon_year_2025.csv"
OUTPUT_JSON = "emissions.json"

def generate_24h_forecast_json():
    # Load historical data
    df = pd.read_csv(DATA_PATH)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    df = df.sort_values(["Building_ID", "Timestamp"])

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

        # Extract time series
        series = df[df["Building_ID"] == building_id]["Total_CO2e_kg"].values.reshape(-1, 1)
        scaled_series = scaler.transform(series)

        # Prepare input window
        history = scaled_series[-SEQ_LEN:].reshape(1, SEQ_LEN, 1)
        last_time = df[df["Building_ID"] == building_id]["Timestamp"].iloc[-1]

        building_forecast = {}

        # Recursive 24-hour forecast
        for hour in range(1, 25):
            pred_scaled = model.predict(history, verbose=0)[0][0]
            pred_real = scaler.inverse_transform([[pred_scaled]])[0][0]

            timestamp = last_time + pd.Timedelta(hours=hour)
            building_forecast[str(timestamp)] = round(float(pred_real), 2)

            # Update rolling window
            history = np.roll(history, -1, axis=1)
            history[0, -1, 0] = pred_scaled

        forecast_output[building_id] = building_forecast

    # Save JSON
    with open(OUTPUT_JSON, "w") as f:
        json.dump(forecast_output, f, indent=4)

    print(f"✅ Forecast saved to {OUTPUT_JSON}")
    return forecast_output
if __name__ == "__main__":
    generate_24h_forecast_json()
