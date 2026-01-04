import json
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
from google import genai
from forecast import generate_24h_forecast_json

app = FastAPI()

# Auto-generate forecasts on startup
@app.on_event("startup")
async def startup_event():
    print("\n" + "="*60)
    print("🚀 Starting Campus Carbon Pulse Backend...")
    print("="*60)
    print("\n📊 Generating fresh forecasts aligned with current time...")
    try:
        generate_24h_forecast_json()
        print("\n✅ Forecasts generated successfully!")
        print("🌐 Backend ready to serve requests.\n")
    except Exception as e:
        print(f"\n⚠️  Warning: Failed to generate forecasts: {e}")
        print("Backend will use existing emissions.json if available.\n")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080", "http://localhost:8081", "http://127.0.0.1:8081"],
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
    Returns structured JSON with categorized insights.
    """
    # Check if emissions file exists
    if not os.path.exists(EMISSIONS_FILE):
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
        api_key = os.getenv('GEMINI_API_KEY', '#replace here with ur gemeini api key')
        
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
            contents=prompt
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
        
        return {
            "success": True,
            "insights": insights_json
        }
        
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to parse AI response as JSON: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate insights: {str(e)}"
        )

