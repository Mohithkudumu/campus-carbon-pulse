import pandas as pd
import json

# Load training data
print("Loading training data...")
df = pd.read_csv('snuc_carbon_year_2025.csv')
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df['Hour'] = df['Timestamp'].dt.hour

# Load current forecast
with open('emissions.json', 'r') as f:
    forecast = json.load(f)

print("\n" + "="*80)
print("COMPARISON: TRAINING DATA vs CURRENT FORECAST AT 5 PM (17:00)")
print("="*80)

# Get training data averages for hour 17
hour_17_training = df[df['Hour'] == 17].groupby('Building_ID')['Total_CO2e_kg'].mean()

# Get forecast for hour 17
print(f"\n{'Building':<25} {'Training Avg':<15} {'Current Forecast':<20} {'Difference'}")
print("-"*80)

for building in sorted(forecast.keys()):
    # Find the 17:00 timestamp in forecast
    forecast_val = None
    for timestamp, value in forecast[building].items():
        if '17:00:00' in timestamp:
            forecast_val = value
            break
    
    training_val = hour_17_training.get(building, 0)
    diff = forecast_val - training_val if forecast_val else 0
    
    print(f"{building:<25} {training_val:>12.2f} kg  {forecast_val:>15.2f} kg  {diff:>+10.2f}")

# Check realistic patterns
print("\n" + "="*80)
print("REALISTIC EMISSION PATTERNS CHECK")
print("="*80)

print("\nExpected behavior at 5 PM:")
print("- Hostels: LOW (students in classes/library)")
print("- Academic blocks: MEDIUM-HIGH (classes in session)")
print("- Mess/Canteen: MEDIUM (dinner prep starting)")
print("- Library: MEDIUM-HIGH (students studying)")

print("\nActual forecast at 5 PM:")
hostels = ['Large_Hostel_Boys', 'Large_Hostel_Girls', 'Small_Hostel_Boys', 'Small_Hostel_Girls']
academics = ['Academic_Block_Large', 'Academic_Block_Small']

hostel_total = sum([forecast[b].get([k for k in forecast[b].keys() if '17:00:00' in k][0], 0) for b in hostels])
academic_total = sum([forecast[b].get([k for k in forecast[b].keys() if '17:00:00' in k][0], 0) for b in academics])

print(f"  Total Hostel Emissions: {hostel_total:.2f} kg")
print(f"  Total Academic Emissions: {academic_total:.2f} kg")
print(f"  Ratio (Hostel/Academic): {hostel_total/academic_total:.2f}x")

if hostel_total > academic_total:
    print("\n⚠️  WARNING: Hostels have HIGHER emissions than academics at 5 PM!")
    print("   This is UNREALISTIC - students should be in class, not in hostels.")
