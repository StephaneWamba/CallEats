import { useEffect } from 'react';
import { useMap } from 'react-leaflet';

interface MapClickHandlerProps {
  onMapClick: (e: L.LeafletMouseEvent) => void;
}

export const MapClickHandler: React.FC<MapClickHandlerProps> = ({ onMapClick }) => {
  const map = useMap();

  useEffect(() => {
    if (!map) return;

    map.on('click', onMapClick);

    return () => {
      map.off('click', onMapClick);
    };
  }, [map, onMapClick]);

  return null;
};



