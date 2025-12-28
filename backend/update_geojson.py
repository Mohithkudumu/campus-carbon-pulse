import json

def update_map_data(api_response, geojson_file_path, output_file_path):
    # 1. Create a lookup dictionary for easy mapping
    # Maps building_id -> {carbon: X, heat: Y}
    emissions_lookup = {
        item['building_id']: {
            'carbon': item['total_emission'],
            'HeatLevel': item['scaled_emission']
        } 
        for item in api_response['results']
    }

    # 2. Load your existing GeoJSON file
    with open(geojson_file_path, 'r') as f:
        geojson_data = json.load(f)

    # 3. Iterate through features and update properties
    for feature in geojson_data.get('features', []):
        building_name = feature['properties'].get('Name')
        
        # Check if we have emission data for this building name
        if building_name in emissions_lookup:
            data = emissions_lookup[building_name]
            
            # Update the properties with new keys
            feature['properties']['carbon'] = data['carbon']
            feature['properties']['HeatLevel'] = data['HeatLevel']
            
            print(f"Updated {building_name}: Carbon={data['carbon']}, HeatLevel={data['HeatLevel']}")

    # 4. Save the updated GeoJSON to a new file
    with open(output_file_path, 'w') as f:
        json.dump(geojson_data, f, indent=2)
    
    print(f"\nSuccessfully saved updated GeoJSON to: {output_file_path}")

# --- EXAMPLE USAGE ---

# This is the response you shared from your FastAPI
api_data = {
    "hour": 8,
    "results": [
        {"building_id": "Academic_Block_Large", "total_emission": 29.88, "scaled_emission": 16.21},
        {"building_id": "Library", "total_emission": 17.96, "scaled_emission": 7.31},
        # ... include all other buildings here
    ]
}

# Run the update
update_map_data(
    api_response=api_data, 
    geojson_file_path="campus_map.geojson", # Your original file
    output_file_path="updated_campus_map.geojson" # The new file to use in your map
)