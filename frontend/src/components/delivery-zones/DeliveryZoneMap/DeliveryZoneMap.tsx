import React, { useEffect, useRef, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import { MapClickHandler } from './MapClickHandler';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
// @ts-ignore - leaflet-draw doesn't have types
import 'leaflet-draw';
import 'leaflet-draw/dist/leaflet.draw.css';
import { MapPin, Search } from 'lucide-react';
import { geocodeAddress, reverseGeocode } from '@/utils/geocoding';
import { Button } from '@/components/common/Button';
import { Input } from '@/components/common/Input';
import type { DeliveryZoneResponse } from '@/types/delivery-zones';

// Fix for default marker icons in Leaflet with Vite
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

const DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

L.Marker.prototype.options.icon = DefaultIcon;

export interface DeliveryZoneMapProps {
  zones: DeliveryZoneResponse[];
  selectedZone?: DeliveryZoneResponse | null;
  onZoneSelect?: (zone: DeliveryZoneResponse | null) => void;
  onBoundaryChange?: (zoneId: string, boundary: any) => void;
  restaurantId: string;
  center?: [number, number];
  zoom?: number;
}

// Component to set map ref for external access
const MapRefSetter: React.FC<{ mapRef: React.MutableRefObject<L.Map | null> }> = ({ mapRef }) => {
  const map = useMap();
  
  useEffect(() => {
    if (map) {
      mapRef.current = map;
      // Trigger map invalidateSize to ensure proper rendering after container is ready
      const timer = setTimeout(() => {
        map.invalidateSize();
      }, 200);
      return () => clearTimeout(timer);
    }
  }, [map, mapRef]);
  
  return null;
};

// Component to handle drawing on the map
const DrawingHandler: React.FC<{
  selectedZone: DeliveryZoneResponse | null;
  onBoundaryChange: (zoneId: string, boundary: any) => void;
  restaurantId: string;
}> = ({ selectedZone, onBoundaryChange }) => {
  const map = useMap();
  const drawControlRef = useRef<L.Control.Draw | null>(null);
  const drawnLayerRef = useRef<L.FeatureGroup | null>(null);

  useEffect(() => {
    if (!map) return;

    // Remove existing control and layers if they exist
    if (drawControlRef.current) {
      map.removeControl(drawControlRef.current);
    }
    if (drawnLayerRef.current) {
      map.removeLayer(drawnLayerRef.current);
    }

    // Only show drawing tools if a zone is selected
    if (!selectedZone) {
      return;
    }

    // Create a feature group to store drawn layers
    const drawnLayers = new L.FeatureGroup();
    map.addLayer(drawnLayers);
    drawnLayerRef.current = drawnLayers;

    // Load existing boundary if zone has one
    if (selectedZone.boundary) {
      try {
        const geoJsonLayer = L.geoJSON(selectedZone.boundary as any, {
          style: {
            color: '#3b82f6',
            fillColor: '#3b82f6',
            fillOpacity: 0.2,
            weight: 2,
          },
        });
        drawnLayers.addLayer(geoJsonLayer);
        map.fitBounds(geoJsonLayer.getBounds());
      } catch (_error) {
        // Error loading boundary, ignore
      }
    }

    // Initialize draw control
    const drawControl = new (L.Control.Draw as any)({
      draw: {
        polygon: {
          allowIntersection: false,
          showArea: true,
        },
        polyline: false,
        rectangle: false,
        circle: false,
        marker: false,
        circlemarker: false,
      },
      edit: {
        featureGroup: drawnLayers,
        remove: true,
      },
    });

    map.addControl(drawControl);
    drawControlRef.current = drawControl;

    // Handle drawing events
    const handleDrawCreated = (e: any) => {
      const layer = e.layer;
      // Clear existing layers first
      drawnLayers.clearLayers();
      drawnLayers.addLayer(layer);

      if (selectedZone) {
        // Convert Leaflet layer to GeoJSON
        const geoJson = layer.toGeoJSON();
        if (geoJson.geometry && geoJson.geometry.type === 'Polygon') {
          onBoundaryChange(selectedZone.id, geoJson.geometry);
        }
      }
    };

    const handleDrawEdited = (e: any) => {
      const layers = e.layers;
      layers.eachLayer((layer: any) => {
        if (selectedZone) {
          const geoJson = layer.toGeoJSON();
          if (geoJson.geometry && geoJson.geometry.type === 'Polygon') {
            onBoundaryChange(selectedZone.id, geoJson.geometry);
          }
        }
      });
    };

    const handleDrawDeleted = () => {
      if (selectedZone) {
        onBoundaryChange(selectedZone.id, null);
      }
    };

    map.on((L.Draw as any).Event.CREATED, handleDrawCreated);
    map.on((L.Draw as any).Event.EDITED, handleDrawEdited);
    map.on((L.Draw as any).Event.DELETED, handleDrawDeleted);

    return () => {
      map.off((L.Draw as any).Event.CREATED, handleDrawCreated);
      map.off((L.Draw as any).Event.EDITED, handleDrawEdited);
      map.off((L.Draw as any).Event.DELETED, handleDrawDeleted);
      if (drawControlRef.current) {
        map.removeControl(drawControlRef.current);
      }
      if (drawnLayerRef.current) {
        map.removeLayer(drawnLayerRef.current);
      }
    };
  }, [map, selectedZone, onBoundaryChange]);

  return null;
};

export const DeliveryZoneMap: React.FC<DeliveryZoneMapProps> = ({
  zones,
  selectedZone,
  onZoneSelect,
  onBoundaryChange,
  restaurantId,
  center = [40.7128, -74.006], // Default to NYC
  zoom = 13,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [mapCenter, setMapCenter] = useState<[number, number]>(center);
  const [mapZoom, setMapZoom] = useState(zoom);
  const mapRef = useRef<L.Map | null>(null);

  // Update map center/zoom when props change
  useEffect(() => {
    if (mapRef.current) {
      mapRef.current.setView(center, zoom);
    } else {
      setMapCenter(center);
      setMapZoom(zoom);
    }
  }, [center, zoom]);

  // Handle window resize to ensure map renders correctly
  useEffect(() => {
    const handleResize = () => {
      if (mapRef.current) {
        setTimeout(() => {
          mapRef.current?.invalidateSize();
        }, 100);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Zone colors for different zones
  const zoneColors = [
    '#3b82f6', // blue
    '#10b981', // green
    '#f59e0b', // amber
    '#ef4444', // red
    '#8b5cf6', // purple
    '#ec4899', // pink
  ];

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    try {
      const result = await geocodeAddress(searchQuery);
      if (result) {
        setMapCenter([result.lat, result.lng]);
        setMapZoom(15);
        if (mapRef.current) {
          mapRef.current.setView([result.lat, result.lng], 15);
        }
      }
    } catch (_error) {
      // Search error, ignore
    } finally {
      setIsSearching(false);
    }
  };

  const handleMapClick = async (e: L.LeafletMouseEvent) => {
    const { lat, lng } = e.latlng;
    try {
      const result = await reverseGeocode(lat, lng);
      if (result) {
        // You could show a popup or update UI with the address
      }
    } catch (_error) {
      // Reverse geocode error, ignore
    }
  };

  return (
    <div className="space-y-4">
      {/* Search Bar */}
      <div className="flex gap-2">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search for an address..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                handleSearch();
              }
            }}
            className="pl-10"
          />
        </div>
        <Button
          variant="primary"
          onClick={handleSearch}
          isLoading={isSearching}
          disabled={!searchQuery.trim()}
        >
          Search
        </Button>
      </div>

      {/* Map */}
      <div className="relative h-[600px] w-full rounded-lg border border-gray-300 overflow-hidden">
        <MapContainer
          center={mapCenter}
          zoom={mapZoom}
          style={{ height: '100%', width: '100%', zIndex: 0 }}
          scrollWheelZoom={true}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <MapRefSetter mapRef={mapRef} />
          <MapClickHandler onMapClick={handleMapClick} />

          {/* Draw existing zone boundaries */}
          {zones.map((zone, index) => {
            if (!zone.boundary || zone.id === selectedZone?.id) return null;

            return (
              <GeoJSON
                key={zone.id}
                data={zone.boundary as any}
                style={{
                  color: zoneColors[index % zoneColors.length],
                  fillColor: zoneColors[index % zoneColors.length],
                  fillOpacity: 0.2,
                  weight: 2,
                }}
                eventHandlers={{
                  click: () => {
                    if (onZoneSelect) {
                      onZoneSelect(zone);
                    }
                  },
                }}
              />
            );
          })}

          {/* Drawing handler for selected zone */}
          {selectedZone && onBoundaryChange && (
            <DrawingHandler
              selectedZone={selectedZone}
              onBoundaryChange={onBoundaryChange}
              restaurantId={restaurantId}
            />
          )}
        </MapContainer>

        {/* Zone Legend */}
        {zones.length > 0 && (
          <div className="absolute top-4 right-4 bg-white rounded-lg shadow-lg p-4 z-[400] max-w-xs">
            <h3 className="text-sm font-semibold text-gray-900 mb-2">Delivery Zones</h3>
            <div className="space-y-1">
              {zones.map((zone, index) => (
                <button
                  key={zone.id}
                  onClick={() => onZoneSelect?.(zone)}
                  className={`w-full text-left px-2 py-1 rounded text-sm transition-colors ${
                    selectedZone?.id === zone.id
                      ? 'bg-primary/10 text-primary font-semibold'
                      : 'hover:bg-gray-100 text-gray-700'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{
                        backgroundColor: zoneColors[index % zoneColors.length],
                      }}
                    />
                    <span>{zone.zone_name}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Instructions */}
      <div className="rounded-lg bg-blue-50 border border-blue-200 p-4 text-sm text-blue-900">
        <div className="flex items-start gap-2">
          <MapPin className="h-5 w-5 mt-0.5 flex-shrink-0" />
          <div>
            <p className="font-semibold mb-1">How to use the map:</p>
            <ul className="list-disc list-inside space-y-1 text-blue-800">
              <li>Search for an address to navigate to a location</li>
              <li>Select a zone from the list to edit its boundary</li>
              <li>Use the drawing tools to create or edit zone boundaries</li>
              <li>Click on the map to see the address at that location</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

