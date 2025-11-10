// Delivery Zones Types
export interface DeliveryZoneResponse {
  id: string;
  restaurant_id: string;
  zone_name: string;
  description?: string | null;
  delivery_fee: number;
  min_order?: number | null;
  boundary?: any | null; // GeoJSON Polygon
  created_at: string;
  updated_at: string | null;
}

export interface CreateDeliveryZoneRequest {
  zone_name: string;
  description?: string;
  delivery_fee: number;
  min_order?: number;
}

export interface UpdateDeliveryZoneRequest {
  zone_name?: string;
  description?: string;
  delivery_fee?: number;
  min_order?: number;
}

export interface SetZoneBoundaryRequest {
  boundary: {
    type: 'Polygon';
    coordinates: number[][][];
  };
}

export interface ZoneBoundaryResponse {
  type: 'Polygon';
  coordinates: number[][][];
}

export interface CheckPointInZoneRequest {
  lat: number;
  lng: number;
}

export interface CheckPointInZoneResponse {
  in_zone: boolean;
  zone_id?: string;
  zone_name?: string;
}

