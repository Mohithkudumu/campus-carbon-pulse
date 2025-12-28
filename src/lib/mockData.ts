import { HistoricalDataPoint, ForecastDataPoint, CampusGeoJSON, ForecastResponse } from "@/types/campus";

// Generate realistic historical carbon data with patterns
export const generateHistoricalData = (days: number): HistoricalDataPoint[] => {
  const data: HistoricalDataPoint[] = [];
  const now = new Date();

  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);

    // Base carbon with weekly patterns (weekends lower)
    const dayOfWeek = date.getDay();
    const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
    const baseLine = isWeekend ? 1200 : 1800;

    // Add some randomness
    const variance = Math.random() * 400 - 200;

    // Seasonal pattern (higher in summer months)
    const month = date.getMonth();
    const seasonalFactor = month >= 4 && month <= 8 ? 1.2 : 1.0;

    data.push({
      date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      carbon: Math.round((baseLine + variance) * seasonalFactor),
      buildings: Math.floor(Math.random() * 10) + 35,
    });
  }

  return data;
};

// Generate 24-hour forecast data
export const generateForecastData = (): ForecastDataPoint[] => {
  const data: ForecastDataPoint[] = [];
  const now = new Date();
  const currentHour = now.getHours();

  for (let i = 0; i <= 24; i++) {
    const hour = (currentHour + i) % 24;

    // Simulate daily carbon patterns
    // Low at night, peaks during business hours
    let baseCarbon: number;
    if (hour >= 0 && hour < 6) {
      baseCarbon = 800 + Math.random() * 200; // Night - low
    } else if (hour >= 6 && hour < 9) {
      baseCarbon = 1000 + (hour - 6) * 200 + Math.random() * 150; // Morning ramp up
    } else if (hour >= 9 && hour < 17) {
      baseCarbon = 1600 + Math.random() * 400; // Peak hours
    } else if (hour >= 17 && hour < 21) {
      baseCarbon = 1400 - (hour - 17) * 100 + Math.random() * 150; // Evening decline
    } else {
      baseCarbon = 900 + Math.random() * 200; // Late night
    }

    const label = i === 0 ? 'Now' : `+${i}h`;

    data.push({
      hour: i,
      carbon: Math.round(baseCarbon),
      label,
    });
  }

  return data;
};

// Update building heat levels based on forecast hour
export const updateBuildingData = (
  geoJSON: CampusGeoJSON,
  hour: number
): CampusGeoJSON => {
  const updatedFeatures = geoJSON.features.map((feature, index) => {
    // Create deterministic but varying patterns per building
    const seed = (index * 17 + hour * 31) % 100;

    // Time-based factor (0-1)
    const timeFactor = Math.sin((hour / 24) * Math.PI * 2 - Math.PI / 2) * 0.5 + 0.5;

    // Building-specific base (some buildings are always higher)
    const buildingBase = (seed % 30) + 20;

    // Calculate new heat level (0-100)
    const newHeatLevel = Math.min(100, Math.max(0,
      buildingBase + timeFactor * 50 + (Math.random() * 20 - 10)
    ));

    // Carbon correlates with heat level
    const newCarbon = (newHeatLevel * 2.5) + (Math.random() * 30);

    return {
      ...feature,
      properties: {
        ...feature.properties,
        heatLevel: Math.round(newHeatLevel * 10) / 10,
        carbon: Math.round(newCarbon * 100) / 100,
      },
    };
  });

  return {
    ...geoJSON,
    features: updatedFeatures,
  };
};

// Calculate total campus carbon
export const calculateTotalCarbon = (geoJSON: CampusGeoJSON): number => {
  return geoJSON.features.reduce((total, feature) => {
    return total + (feature.properties.carbon || 0);
  }, 0);
};

// Get carbon level classification
export const getCarbonLevel = (value: number): 'low' | 'mid' | 'critical' => {
  if (value < 1200) return 'low';
  if (value < 2000) return 'mid';
  return 'critical';
};

// Format carbon value for display
export const formatCarbon = (value: number): string => {
  if (value >= 1000) {
    return `${(value / 1000).toFixed(2)}k`;
  }
  return value.toFixed(1);
};
