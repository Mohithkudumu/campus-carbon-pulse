import pandas as pd

# Load CSV
df = pd.read_csv('snuc_carbon_year_2025.csv')
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df['Hour'] = df['Timestamp'].dt.hour

# Filter for 5 PM (hour 17)
hour_17 = df[df['Hour'] == 17].copy()

# Calculate average emissions by building type
print("="*80)
print("AVERAGE EMISSIONS AT 5 PM (17:00) - FROM TRAINING DATA")
print("="*80)

building_avg = hour_17.groupby('Building_ID')['Total_CO2e_kg'].mean().sort_values(ascending=False)

print("\nBuilding                   Avg Emission at 5 PM")
print("-"*60)
for building, emission in building_avg.items():
    print(f"{building:30s} {emission:>10.2f} kg CO2e")

# Compare hostels vs academics
hostels = ['Large_Hostel_Boys', 'Large_Hostel_Girls', 'Small_Hostel_Boys', 'Small_Hostel_Girls']
academics = ['Academic_Block_Large', 'Academic_Block_Small']

hostel_avg = building_avg[building_avg.index.isin(hostels)].mean()
academic_avg = building_avg[building_avg.index.isin(academics)].mean()

print("\n" + "="*80)
print(f"Average Hostel Emissions at 5 PM:    {hostel_avg:.2f} kg CO2e")
print(f"Average Academic Emissions at 5 PM:  {academic_avg:.2f} kg CO2e")
print(f"Ratio (Hostel/Academic):              {hostel_avg/academic_avg:.2f}x")

if hostel_avg > academic_avg:
    print("\nPROBLEM: Training data shows hostels > academics at 5 PM!")
    print("This is UNREALISTIC for a university campus.")
else:
    print("\nTraining data is realistic - academics > hostels at 5 PM")
