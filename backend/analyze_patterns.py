import pandas as pd

# Load the CSV
df = pd.read_csv('snuc_carbon_year_2025.csv')
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df['Hour'] = df['Timestamp'].dt.hour

# Filter hostel data
hostel_data = df[df['Building_ID'].str.contains('Hostel')]

# Calculate average emissions by building and hour
hourly_avg = hostel_data.groupby(['Building_ID', 'Hour'])['Total_CO2e_kg'].mean().reset_index()

# Focus on 5 PM (hour 17)
print("=" * 80)
print("HOSTEL EMISSIONS AT 5 PM (Hour 17) - FROM TRAINING DATA")
print("=" * 80)
hour_17 = hourly_avg[hourly_avg['Hour'] == 17]
for _, row in hour_17.iterrows():
    print(f"{row['Building_ID']:25s}: {row['Total_CO2e_kg']:8.2f} kg CO2e")

print("\n" + "=" * 80)
print("HOSTEL EMISSIONS THROUGHOUT THE DAY - AVERAGE PATTERN")
print("=" * 80)

for building in sorted(hostel_data['Building_ID'].unique()):
    building_hourly = hourly_avg[hourly_avg['Building_ID'] == building]
    print(f"\n{building}:")
    print("Hour:     ", end="")
    for hour in [0, 6, 12, 17, 18, 20, 22]:
        print(f"{hour:>8d}", end="")
    print("\nEmission: ", end="")
    for hour in [0, 6, 12, 17, 18, 20, 22]:
        val = building_hourly[building_hourly['Hour'] == hour]['Total_CO2e_kg'].values
        if len(val) > 0:
            print(f"{val[0]:8.2f}", end="")
        else:
            print(f"{'N/A':>8s}", end="")
    print()
