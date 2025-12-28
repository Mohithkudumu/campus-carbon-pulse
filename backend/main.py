import json
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os

app = FastAPI()

# --- CONFIGURATION ---
# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

EMISSIONS_FILE = "emissions.json"
# Point to the public folder in the parent directory so the frontend works with the updated file if we still rely on file updates
GEOJSON_FILE = "../public/campus.json"

# Load the model output once when the server starts
def load_data():
    if not os.path.exists(EMISSIONS_FILE):
        return {}
    with open(EMISSIONS_FILE, "r") as f:
        return json.load(f)

EMISSIONS_DATA = load_data()

def update_geojson_file(results):
    """
    Injects API results and standardized heights into the GeoJSON file.
    Ensures compatibility with the index.html (lowercase keys).
    """
    if not os.path.exists(GEOJSON_FILE):
        print(f"Warning: {GEOJSON_FILE} not found. Skipping GeoJSON update.")
        return

    # 1. Load the existing GeoJSON
    with open(GEOJSON_FILE, "r") as f:
        geojson_data = json.load(f)

    # 2. Create a lookup map for faster processing
    data_map = {
        item['building_id']: {
            'carbon': item['total_emission'],
            'heatLevel': item['scaled_emission']
        } for item in results
    }

    # 3. Standard Height Mapping (FIXES THE HEIGHT MISTAKES)
    # This ensures buildings look proportional on the map
    standard_heights = {
        "Large_Hostel_Boys": 35,
        "Large_Hostel_Girls": 35,
        "Academic_Block_Large": 25,
        "Academic_Block_Small": 20,
        "Library": 22,
        "Boys_Mess": 15,
        "Girls_Mess": 15,
        "Canteen": 12,
        "Clinic": 12,
        "Sports_Complex": 18,
        "Small_Hostel_Boys": 25,
        "Small_Hostel_Girls": 25
    }

    # 4. Update features in the GeoJSON
    updated_count = 0
    for feature in geojson_data.get('features', []):
        # Handle original uppercase "Name" or lowercase "name"
        building_name = feature['properties'].get('Name') or feature['properties'].get('name')
        
        # --- FIX: PROPERTY NAMES (Lowercase for HTML Compatibility) ---
        # We set lowercase keys so index.html works perfectly
        feature['properties']['name'] = building_name
        
        # Set standardized height
        feature['properties']['height'] = standard_heights.get(building_name, 15)

        if building_name in data_map:
            # Inject live data
            feature['properties']['carbon'] = data_map[building_name]['carbon']
            feature['properties']['heatLevel'] = data_map[building_name]['heatLevel']
            updated_count += 1

    # 5. Overwrite the GeoJSON file
    with open(GEOJSON_FILE, "w") as f:
        json.dump(geojson_data, f, indent=4)
    
    print(f"✅ Success: {updated_count} buildings updated with live data and fixed heights.")

@app.get("/get-emissions/{target_hour}")
async def get_emissions(target_hour: int):
    if not (0 <= target_hour <= 23):
        raise HTTPException(status_code=400, detail="Hour must be between 0 and 23")

    extracted_results = []

    for building_id, timestamps in EMISSIONS_DATA.items():
        for ts_str, value in timestamps.items():
            dt_obj = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
            if dt_obj.hour == target_hour:
                extracted_results.append({
                    "building_id": building_id,
                    "total_emission": value
                })
                break

    if not extracted_results:
        raise HTTPException(status_code=404, detail="No data found for this hour")

    df = pd.DataFrame(extracted_results)
    
    # Calculate global min/max across ALL hours and buildings for consistent color scaling
    all_emissions = []
    for timestamps in EMISSIONS_DATA.values():
        all_emissions.extend(timestamps.values())
    
    global_min = min(all_emissions)
    global_max = max(all_emissions)
    
    if global_max == global_min:
        df['scaled_emission'] = 0.0
    else:
        df['scaled_emission'] = ((df['total_emission'] - global_min) / (global_max - global_min)) * 100

    final_output = []
    for _, row in df.iterrows():
        final_output.append({
            "building_id": row['building_id'],
            "total_emission": round(row['total_emission'], 2),
            "scaled_emission": round(row['scaled_emission'], 2)
        })

    # Trigger automation
    update_geojson_file(final_output)

    return {
        "hour": target_hour,
        "results": final_output
    }