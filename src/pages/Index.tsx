import { useState, useEffect, useCallback } from 'react';
import CampusMap from '@/components/CampusMap';
import TimeSlider from '@/components/TimeSlider';
import AnalyticsPanel from '@/components/AnalyticsPanel';
import DashboardHeader from '@/components/DashboardHeader';
import { CampusGeoJSON } from '@/types/campus';
import { updateBuildingData, calculateTotalCarbon, generateForecastData } from '@/lib/mockData';

const Index = () => {
  const [originalGeoJSON, setOriginalGeoJSON] = useState<CampusGeoJSON | null>(null);
  const [displayGeoJSON, setDisplayGeoJSON] = useState<CampusGeoJSON | null>(null);
  const [forecastHour, setForecastHour] = useState(0);
  const [totalCarbon, setTotalCarbon] = useState(0);
  const [buildingCount, setBuildingCount] = useState(0);
  const [forecastData] = useState(generateForecastData);

  // Load campus data
  useEffect(() => {
    fetch('/campus.json')
      .then((res) => res.json())
      .then((data: CampusGeoJSON) => {
        setOriginalGeoJSON(data);
        setDisplayGeoJSON(data);
        setBuildingCount(data.features.length);
        setTotalCarbon(calculateTotalCarbon(data));
      })
      .catch((err) => console.error('Failed to load campus data:', err));
  }, []);

  // Update building data when forecast hour changes
  useEffect(() => {
    if (!originalGeoJSON) return;

    // Fetch live data from backend
    fetch(`http://localhost:8000/get-emissions/${forecastHour}`)
      .then(res => {
        if (!res.ok) throw new Error("Failed to fetch");
        return res.json();
      })
      .then((data) => {
        const updatedFeatures = originalGeoJSON.features.map(feature => {
          const bId = feature.properties.name || (feature.properties as any).Name;
          const buildingData = data.results.find((b: any) => b.building_id === bId);
          if (buildingData) {
            return {
              ...feature,
              properties: {
                ...feature.properties,
                carbon: buildingData.total_emission,
                heatLevel: buildingData.scaled_emission
              }
            };
          }
          return feature;
        });

        const updatedGeoJSON = {
          ...originalGeoJSON,
          features: updatedFeatures
        };

        setDisplayGeoJSON(updatedGeoJSON);

        // Calculate total carbon from the response
        const newTotal = data.results.reduce((acc: number, curr: any) => acc + curr.total_emission, 0);
        setTotalCarbon(newTotal);
      })
      .catch(err => {
        console.error("Error fetching emissions:", err);
        // Fallback to mock data if backend is down? Or just log error.
        // For now, let's keep it simple and just log.
      });
  }, [forecastHour, originalGeoJSON]);

  const handleBuildingClick = useCallback((properties: any) => {
    console.log('Building clicked:', properties);
  }, []);

  const handleSliderChange = useCallback((value: number) => {
    setForecastHour(value);
  }, []);

  return (
    <div className="relative w-full h-screen overflow-hidden bg-background">
      {/* 3D Map Background */}
      <CampusMap
        geoJSON={displayGeoJSON}
        onBuildingClick={handleBuildingClick}
      />

      {/* Top Left - Header */}
      <div className="absolute top-5 left-5 z-20">
        <DashboardHeader />
      </div>

      {/* Right Side - Analytics Panel */}
      <div className="absolute top-5 right-5 bottom-24 z-20 overflow-y-auto">
        <AnalyticsPanel
          totalCarbon={totalCarbon}
          buildingCount={buildingCount}
          currentHour={forecastHour}
        />
      </div>

      {/* Bottom Center - Time Slider */}
      <div className="absolute bottom-5 left-1/2 -translate-x-1/2 z-20 w-full max-w-2xl px-5">
        <TimeSlider
          value={forecastHour}
          onChange={handleSliderChange}
          forecastData={forecastData}
        />
      </div>

      {/* Scanlines Effect (subtle) */}
      <div className="absolute inset-0 pointer-events-none scanlines opacity-30" />
    </div>
  );
};

export default Index;
