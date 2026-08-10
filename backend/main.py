import sys
import json
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
from dotenv import load_dotenv
from google import genai
from forecast import generate_24h_forecast_json
from dotenv import load_dotenv, find_dotenv
from database import get_db_connection, init_db

# Configure UTF-8 encoding for standard output and error to prevent UnicodeEncodeError on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

load_dotenv()

# Load environment variables from .env file
# Triggering reload
load_dotenv()

app = FastAPI()

def save_forecasts_to_db(forecast_data):
    """
    Saves the dictionary structure of predictions into the SQLite database
    and raises carbon alerts/warnings if critical thresholds are met.
    """
    if not forecast_data:
        return
    
    # Calculate global min/max across all predictions to scale them consistently [0-100]
    all_vals = []
    for building_emissions in forecast_data.values():
        all_vals.extend(building_emissions.values())
        
    global_min = min(all_vals) if all_vals else 0
    global_max = max(all_vals) if all_vals else 1
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Standard warning threshold limit
    limit_value = 120.0
    
    for building_id, timestamps in forecast_data.items():
        for ts_str, emission_val in timestamps.items():
            scaled = 0.0
            if global_max != global_min:
                scaled = ((emission_val - global_min) / (global_max - global_min)) * 100
            
            # Save into predicted_emissions
            cursor.execute('''
                INSERT OR REPLACE INTO predicted_emissions (building_id, timestamp, emission, scaled_emission)
                VALUES (?, ?, ?, ?)
            ''', (building_id, ts_str, round(emission_val, 2), round(scaled, 2)))
            
            # If emission exceeds safety threshold
            if emission_val > limit_value or scaled > 85.0:
                severity = "CRITICAL" if emission_val > 150.0 or scaled > 95.0 else "HIGH"
                alert_msg = f"Building {building_id} predicted to hit carbon peak of {emission_val:.2f} kg CO2e (scaled {scaled:.1f}%)."
                cursor.execute('''
                    INSERT OR REPLACE INTO peak_alerts (building_id, timestamp, emission, limit_value, alert_msg, severity, resolved)
                    VALUES (?, ?, ?, ?, ?, ?, 0)
                ''', (building_id, ts_str, round(emission_val, 2), limit_value, alert_msg, severity))
                
    conn.commit()
    conn.close()
    print("Forecast data and alert states persisted to SQLite Database.")

# Auto-generate forecasts on startup
@app.on_event("startup")
async def startup_event():
    # Force UTF-8 encoding on standard streams to prevent UnicodeEncodeError in Windows CMD/PowerShell
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

    print("\n" + "="*60)
    print("Starting Campus Carbon Pulse Backend...")
    print("="*60)
    
    # Initialize SQLite Database tables
    try:
        init_db()
        print("SQLite Database initialized (database.db)")
    except Exception as e:
        print(f"Error initializing SQLite DB: {e}")

    print("\nGenerating fresh forecasts aligned with current time...")
    try:
        forecast_output = generate_24h_forecast_json()
        print("\nForecasts generated successfully!")
        save_forecasts_to_db(forecast_output)
        print("Backend ready to serve requests.\n")
    except Exception as e:
        print(f"\nWarning: Failed to generate forecasts: {e}")
        # fallback to emissions.json if it exists
        if os.path.exists(EMISSIONS_FILE):
            try:
                with open(EMISSIONS_FILE, "r") as f:
                    forecast_output = json.load(f)
                save_forecasts_to_db(forecast_output)
                print("Backend loaded fallback emissions.json and setup DB successfully.\n")
            except Exception as fe:
                print(f"Failed to load fallback emissions.json: {fe}")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

EMISSIONS_FILE = "emissions.json"
# Point to the public folder in the parent directory so the frontend works with the updated file if we still rely on file updates
GEOJSON_FILE = "campus.json"

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
    # Force UTF-8 encoding on standard streams to prevent UnicodeEncodeError in Windows CMD/PowerShell
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

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
    
    print(f"Success: {updated_count} buildings updated with live data and fixed heights.")

@app.get("/get-emissions/{target_hour}")
async def get_emissions(target_hour: int):
    if not (0 <= target_hour <= 23):
        raise HTTPException(status_code=400, detail="Hour must be between 0 and 23")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM predicted_emissions")
    rows = cursor.fetchall()
    conn.close()

    extracted_results = []
    for row in rows:
        try:
            dt_obj = datetime.strptime(row['timestamp'], "%Y-%m-%d %H:%M:%S")
            if dt_obj.hour == target_hour:
                extracted_results.append({
                    "building_id": row['building_id'],
                    "total_emission": row['emission'],
                    "scaled_emission": row['scaled_emission']
                })
        except Exception:
            continue

    if not extracted_results:
        # Fallback to local file memory if DB query returned nothing
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
        all_emissions = []
        for timestamps in EMISSIONS_DATA.values():
            all_emissions.extend(timestamps.values())
        global_min = min(all_emissions) if all_emissions else 0
        global_max = max(all_emissions) if all_emissions else 1
        
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
        extracted_results = final_output

    # Trigger automation
    update_geojson_file(extracted_results)

    return {
        "hour": target_hour,
        "results": extracted_results
    }

@app.get("/get-historical-data/{days}")
async def get_historical_data(days: int):
    """
    Returns historical carbon emission data from the CSV file.
    Calculates daily average campus emissions from hourly data.
    """
    if not (1 <= days <= 365):
        raise HTTPException(status_code=400, detail="Days must be between 1 and 365")
    
    csv_file = "snuc_carbon_year_2025.csv"
    if not os.path.exists(csv_file):
        raise HTTPException(status_code=404, detail="Historical data file not found")
    
    # Load the CSV
    df = pd.read_csv(csv_file)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    
    # Get the most recent date in the dataset
    max_date = df['Timestamp'].max()
    
    # Filter for the last N days
    start_date = max_date - pd.Timedelta(days=days-1)
    filtered_df = df[df['Timestamp'] >= start_date].copy()
    
    # Extract date and hour
    filtered_df['Date'] = filtered_df['Timestamp'].dt.date
    filtered_df['Hour'] = filtered_df['Timestamp'].dt.hour
    
    # First, sum emissions across all buildings for each hour
    hourly_totals = filtered_df.groupby(['Date', 'Hour'])['Total_CO2e_kg'].sum().reset_index()
    
    # Then, calculate the average of the 24 hourly totals for each day
    daily_averages = hourly_totals.groupby('Date')['Total_CO2e_kg'].mean().reset_index()
    
    # Format the response
    historical_data = []
    for _, row in daily_averages.iterrows():
        historical_data.append({
            "date": row['Date'].strftime('%b %d'),  # e.g., "Jan 15"
            "carbon": round(row['Total_CO2e_kg'], 2),
            "buildings": 12  # Total number of buildings in campus
        })
    
    return {
        "days": days,
        "data": historical_data
    }

@app.get("/get-insights")
async def get_insights():
    """
    Generates AI insights from emissions data using Google Gemini API.
    Uses SQLite database as a cache to prevent duplicate Gemini API billing calls.
    """
    # SQLite caching lookup
    date_key = datetime.now().strftime("%Y-%m-%d")
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT insights_json FROM cached_insights WHERE date_key = ?", (date_key,))
        row = cursor.fetchone()
        if row:
            conn.close()
            print("Serving AI insights from SQLite cache")
            return {
                "success": True,
                "insights": json.loads(row['insights_json']),
                "cached": True
            }
    except Exception as dbe:
        print(f"Database cache check failed: {dbe}")

    # Check if emissions file exists
    if not os.path.exists(EMISSIONS_FILE):
        if conn:
            conn.close()
        raise HTTPException(status_code=404, detail="Emissions data file not found")
    
    try:
        # Read and parse emissions data
        with open(EMISSIONS_FILE, 'r', encoding='utf-8') as f:
            emissions_data = json.load(f)
        
        # Calculate statistics for better AI context
        all_emissions = []
        building_totals = {}
        hourly_totals = {}
        
        for building_id, timestamps in emissions_data.items():
            building_total = 0
            for ts_str, value in timestamps.items():
                dt_obj = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                hour = dt_obj.hour
                
                # Track building totals
                building_total += value
                
                # Track hourly totals
                if hour not in hourly_totals:
                    hourly_totals[hour] = 0
                hourly_totals[hour] += value
                
                all_emissions.append(value)
            
            building_totals[building_id] = building_total
        
        # Find peak hour
        peak_hour = max(hourly_totals, key=hourly_totals.get)
        peak_emission = hourly_totals[peak_hour]
        
        # Find top polluting buildings
        sorted_buildings = sorted(building_totals.items(), key=lambda x: x[1], reverse=True)
        top_3_buildings = sorted_buildings[:3]
        
        # Calculate total and average
        total_emissions = sum(all_emissions)
        avg_emission = total_emissions / len(all_emissions) if all_emissions else 0
        
        # Create structured summary
        summary = {
            "total_emissions": round(total_emissions, 2),
            "average_emission": round(avg_emission, 2),
            "peak_hour": peak_hour,
            "peak_emission": round(peak_emission, 2),
            "top_buildings": [{"name": name, "total": round(total, 2)} for name, total in top_3_buildings],
            "building_count": len(building_totals)
        }
        
        # Get API key from environment variable
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            if conn:
                conn.close()
            raise HTTPException(
                status_code=500,
                detail="GEMINI_API_KEY is not set in environment variables"
            )

        # Initialize Gemini client
        client = genai.Client(api_key=api_key)
        
        # Create enhanced prompt requesting JSON output
        prompt = f"""You are analyzing carbon emissions data for a university campus with {summary['building_count']} buildings.

DATA SUMMARY:
- Total Daily Emissions: {summary['total_emissions']} kg CO2e
- Average Hourly Emission: {summary['average_emission']} kg CO2e
- Peak Hour: {summary['peak_hour']}:00 with {summary['peak_emission']} kg CO2e
- Top 3 Polluting Buildings: {', '.join([f"{b['name']} ({b['total']} kg)" for b in summary['top_buildings']])}

TASK: Provide structured insights in JSON format with the following structure:

{{
  "summary": "A brief 2-3 sentence overview of the campus emissions situation",
  "categories": [
    {{
      "type": "peak_hours",
      "title": "Peak Emission Periods",
      "items": [
        {{
          "title": "Short title",
          "description": "Detailed explanation of when and why emissions peak",
          "value": "Specific metric or time"
        }}
      ]
    }},
    {{
      "type": "buildings",
      "title": "Building Analysis",
      "items": [
        {{
          "title": "Building name or pattern",
          "description": "Analysis of building emissions and patterns",
          "value": "Percentage or emission value"
        }}
      ]
    }},
    {{
      "type": "trends",
      "title": "Emission Trends",
      "items": [
        {{
          "title": "Trend name",
          "description": "Notable pattern across the day or between buildings",
          "value": "Relevant metric"
        }}
      ]
    }},
    {{
      "type": "recommendations",
      "title": "Recommended Actions",
      "items": [
        {{
          "title": "Action name",
          "description": "Detailed, actionable measure to reduce emissions (2-3 sentences)",
          "impact": "Estimated impact or benefit"
        }}
      ]
    }}
  ]
}}

REQUIREMENTS:
- Provide 2-3 items for peak_hours, buildings, and trends
- Provide 4-6 detailed, actionable recommendations
- Be specific and reference the actual data
- Make descriptions informative but concise
- Focus on practical, implementable solutions for a university campus
- Return ONLY valid JSON, no markdown formatting or code blocks"""
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        
        # Parse the JSON response
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        # Parse JSON
        insights_json = json.loads(response_text)
        
        # Save cache to SQLite
        try:
            cursor.execute("INSERT OR REPLACE INTO cached_insights (date_key, insights_json) VALUES (?, ?)",
                           (date_key, json.dumps(insights_json)))
            conn.commit()
        except Exception as dbe:
            print(f"Failed to cache insights in DB: {dbe}")
        finally:
            conn.close()
        
        return {
            "success": True,
            "insights": insights_json,
            "cached": False
        }
        
    except json.JSONDecodeError as e:
        if conn:
            conn.close()
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to parse AI response as JSON: {str(e)}"
        )
    except Exception as e:
        if conn:
            conn.close()
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate insights: {str(e)}"
        )

@app.get("/get-alerts")
async def get_alerts():
    """
    Returns un-resolved system warning alerts for buildings with anomalous CO2 spikes.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM peak_alerts WHERE resolved = 0 ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/resolve-alert/{alert_id}")
async def resolve_alert(alert_id: int):
    """
    Mark an active carbon alert as resolved.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE peak_alerts SET resolved = 1 WHERE id = ?", (alert_id,))
    conn.commit()
    rows = cursor.rowcount
    conn.close()
    if rows == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"success": True, "message": f"Alert {alert_id} marked as resolved"}

