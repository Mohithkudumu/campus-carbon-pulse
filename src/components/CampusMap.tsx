import { useEffect, useRef, useCallback, useState } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { CampusGeoJSON } from '@/types/campus';

interface CampusMapProps {
  geoJSON: CampusGeoJSON | null;
  onBuildingClick?: (properties: any) => void;
}

const CampusMap = ({ geoJSON, onBuildingClick }: CampusMapProps) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const popup = useRef<maplibregl.Popup | null>(null);
  const [isMapLoaded, setIsMapLoaded] = useState(false);

  // Initialize map
  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: {
        version: 8,
        sources: {
          'osm-tiles': {
            type: 'raster',
            tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
            tileSize: 256,
            attribution: '© OpenStreetMap contributors',
          },
        },
        layers: [
          {
            id: 'osm-layer',
            type: 'raster',
            source: 'osm-tiles',
            paint: {
              'raster-saturation': -0.6,
              'raster-contrast': 0.2,
              'raster-brightness-max': 0.4,
            },
          },
        ],
      },
      center: [80.198, 12.751],
      zoom: 17.2,
      pitch: 60,
      bearing: -17,
      antialias: true,
    });

    map.current.addControl(new maplibregl.NavigationControl(), 'top-left');

    map.current.on('load', () => {
      setIsMapLoaded(true);
    });

    return () => {
      popup.current?.remove();
      map.current?.remove();
      map.current = null;
    };
  }, []);

  // Add/update building layers when geoJSON changes
  useEffect(() => {
    if (!map.current || !isMapLoaded || !geoJSON) return;

    const sourceId = 'campus-buildings';
    const source = map.current.getSource(sourceId) as maplibregl.GeoJSONSource;

    if (source) {
      // Update existing source
      source.setData(geoJSON as any);
    } else {
      // Add new source and layers
      map.current.addSource(sourceId, {
        type: 'geojson',
        data: geoJSON as any,
      });

      // 3D Buildings Layer
      map.current.addLayer({
        id: '3d-buildings',
        source: sourceId,
        type: 'fill-extrusion',
        paint: {
          'fill-extrusion-height': ['get', 'height'],
          'fill-extrusion-base': 0,
          'fill-extrusion-color': [
            'interpolate',
            ['linear'],
            ['get', 'heatLevel'],
            0, '#00E676',
            50, '#FFEA00',
            100, '#FF1744',
          ],
          'fill-extrusion-opacity': 0.92,
        },
      });

      // Building Outlines
      map.current.addLayer({
        id: 'building-outlines',
        source: sourceId,
        type: 'line',
        paint: {
          'line-color': 'rgba(255, 255, 255, 0.3)',
          'line-width': 1,
        },
      });

      // Click handlers
      map.current.on('click', '3d-buildings', (e) => {
        if (!e.features?.length) return;
        
        const props = e.features[0].properties;
        
        if (onBuildingClick) {
          onBuildingClick(props);
        }

        // Show popup
        popup.current?.remove();
        popup.current = new maplibregl.Popup({
          closeButton: true,
          offset: 30,
        })
          .setLngLat(e.lngLat)
          .setHTML(`
            <div class="font-display text-secondary font-bold text-sm mb-2">
              ${props.name?.replace(/_/g, ' ') || 'Building'}
            </div>
            <div class="space-y-1 text-xs">
              <div class="flex justify-between gap-4">
                <span class="text-muted-foreground">Heat Level</span>
                <span class="font-semibold">${props.heatLevel}%</span>
              </div>
              <div class="flex justify-between gap-4">
                <span class="text-muted-foreground">Height</span>
                <span class="font-semibold">${props.height}m</span>
              </div>
              <div class="flex justify-between gap-4">
                <span class="text-muted-foreground">Carbon</span>
                <span class="font-semibold text-primary">${props.carbon?.toFixed(1)} kg/h</span>
              </div>
            </div>
          `)
          .addTo(map.current!);
      });

      // Cursor handlers
      map.current.on('mouseenter', '3d-buildings', () => {
        if (map.current) map.current.getCanvas().style.cursor = 'pointer';
      });

      map.current.on('mouseleave', '3d-buildings', () => {
        if (map.current) map.current.getCanvas().style.cursor = '';
      });
    }
  }, [geoJSON, isMapLoaded, onBuildingClick]);

  return (
    <div className="absolute inset-0">
      <div ref={mapContainer} className="w-full h-full" />
      {/* Gradient overlay for better UI visibility */}
      <div className="absolute inset-0 pointer-events-none bg-gradient-to-t from-background/60 via-transparent to-background/30" />
    </div>
  );
};

export default CampusMap;
