
import { ForecastDataPoint, ForecastResponse } from "@/types/campus";
import { CampusGeoJSON } from "@/types/campus";

// Merge real forecast data with GeoJSON
export const mergeForecastWithGeoJSON = (
    geoJSON: CampusGeoJSON,
    forecastData: ForecastResponse,
    hour: number
): CampusGeoJSON => {
    const updatedFeatures = geoJSON.features.map((feature) => {
        const buildingName = feature.properties.name || feature.properties.Name; // Handle case sensitivity
        const buildingForecast = forecastData.forecasts[buildingName];

        if (buildingForecast && buildingForecast.hourly[hour]) {
            const hourlyData = buildingForecast.hourly[hour];
            return {
                ...feature,
                properties: {
                    ...feature.properties,
                    heatLevel: hourlyData.heat_level,
                    carbon: hourlyData.carbon_emission,
                },
            };
        }

        // Fallback if no specific forecast found (keep existing or set to 0)
        return feature;
    });

    return {
        ...geoJSON,
        features: updatedFeatures,
    };
};

export const convertForecastToChartData = (forecastData: ForecastResponse): ForecastDataPoint[] => {
    // Aggregate data across all buildings for each hour
    const hourlyTotals: Record<number, number> = {};

    // Initialize totals
    for (let i = 0; i < 24; i++) {
        hourlyTotals[i] = 0;
    }

    Object.values(forecastData.forecasts).forEach(building => {
        building.hourly.forEach(point => {
            if (hourlyTotals[point.hour_offset] !== undefined) {
                hourlyTotals[point.hour_offset] += point.carbon_emission;
            }
        });
    });

    return Object.entries(hourlyTotals).map(([hour, carbon]) => ({
        hour: Number(hour),
        carbon: Math.round(carbon),
        label: Number(hour) === 0 ? 'Now' : `+${hour}h`
    }));
};
