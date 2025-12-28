export interface BuildingProperties {
  name: string;
  height: number;
  heatLevel: number;
  carbon: number;
}

export interface CampusFeature {
  type: "Feature";
  properties: BuildingProperties;
  geometry: {
    coordinates: number[][][];
    type: "Polygon";
  };
  id: number;
}

export interface CampusGeoJSON {
  type: "FeatureCollection";
  features: CampusFeature[];
}

export interface HistoricalDataPoint {
  date: string;
  carbon: number;
  buildings: number;
}

export interface ForecastDataPoint {
  hour: number;
  carbon: number;
  label: string;
}

export interface BuildingForecast {
  hour_offset: number;
  carbon_emission: number;
  heat_level: number;
}

export interface ForecastResponse {
  timestamp: string;
  forecasts: Record<string, { hourly: BuildingForecast[] }>;
}
