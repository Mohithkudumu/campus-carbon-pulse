import pandas as pd
import json

# Load training data
df = pd.read_csv('snuc_carbon_year_2025.csv')
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df['Hour'] = df['Timestamp'].dt.hour

# Load current forecast
with open('emissions.json', 'r') as f:
    forecast = json.load(f)

print("FORECAST AT 5 PM (17:00)")
print("-" * 60)

hostels = ['Large_Hostel_Boys', 'Large_Hostel_Girls', 'Small_Hostel_Boys', 'Small_Hostel_Girls']
academics = ['Academic_Block_Large', 'Academic_Block_Small']

hostel_emissions = []
academic_emissions = []

for building in sorted(forecast.keys()):
    for timestamp, value in forecast[building].items():
        if '17:00:00' in timestamp:
            print(f"{building:30s}: {value:8.2f} kg")
            if building in hostels:
                hostel_emissions.append(value)
            elif building in academics:
                academic_emissions.append(value)
            break

print("\n" + "=" * 60)
print(f"Total Hostel Emissions at 5 PM: {sum(hostel_emissions):.2f} kg")
print(f"Total Academic Emissions at 5 PM: {sum(academic_emissions):.2f} kg")
print(f"Ratio (Hostel/Academic): {sum(hostel_emissions)/sum(academic_emissions):.2f}x")

if sum(hostel_emissions) > sum(academic_emissions):
    print("\nPROBLEM: Hostels > Academics at 5 PM - UNREALISTIC!")
    print("Students should be in class, not in hostels.")
