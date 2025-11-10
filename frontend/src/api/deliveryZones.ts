import { apiClient } from './client';
import { API_ENDPOINTS } from './endpoints';
import type {
  DeliveryZoneResponse,
  CreateDeliveryZoneRequest,
  UpdateDeliveryZoneRequest,
} from '@/types/delivery-zones';

/**
 * List delivery zones for a restaurant
 */
export const listDeliveryZones = async (
  restaurantId: string
): Promise<DeliveryZoneResponse[]> => {
  const response = await apiClient.get<DeliveryZoneResponse[]>(
    API_ENDPOINTS.DELIVERY_ZONES.LIST(restaurantId)
  );
  return response.data;
};

/**
 * Create a new delivery zone
 */
export const createDeliveryZone = async (
  restaurantId: string,
  data: CreateDeliveryZoneRequest
): Promise<DeliveryZoneResponse> => {
  const response = await apiClient.post<DeliveryZoneResponse>(
    API_ENDPOINTS.DELIVERY_ZONES.CREATE(restaurantId),
    data
  );
  return response.data;
};

/**
 * Get a specific delivery zone by ID
 */
export const getDeliveryZone = async (
  restaurantId: string,
  zoneId: string
): Promise<DeliveryZoneResponse> => {
  const response = await apiClient.get<DeliveryZoneResponse>(
    API_ENDPOINTS.DELIVERY_ZONES.GET(restaurantId, zoneId)
  );
  return response.data;
};

/**
 * Update a delivery zone
 */
export const updateDeliveryZone = async (
  restaurantId: string,
  zoneId: string,
  data: UpdateDeliveryZoneRequest
): Promise<DeliveryZoneResponse> => {
  const response = await apiClient.put<DeliveryZoneResponse>(
    API_ENDPOINTS.DELIVERY_ZONES.UPDATE(restaurantId, zoneId),
    data
  );
  return response.data;
};

/**
 * Delete a delivery zone
 */
export const deleteDeliveryZone = async (
  restaurantId: string,
  zoneId: string
): Promise<{ success: boolean; message: string }> => {
  const response = await apiClient.delete<{ success: boolean; message: string }>(
    API_ENDPOINTS.DELIVERY_ZONES.DELETE(restaurantId, zoneId)
  );
  return response.data;
};

/**
 * Set geographic boundary for a delivery zone (GeoJSON)
 */
export const setZoneBoundary = async (
  restaurantId: string,
  zoneId: string,
  boundary: any // GeoJSON Polygon
): Promise<DeliveryZoneResponse> => {
  const response = await apiClient.post<DeliveryZoneResponse>(
    API_ENDPOINTS.DELIVERY_ZONES.SET_BOUNDARY(restaurantId, zoneId),
    { boundary }
  );
  return response.data;
};

/**
 * Get geographic boundary for a delivery zone
 */
export const getZoneBoundary = async (
  restaurantId: string,
  zoneId: string
): Promise<any> => {
  const response = await apiClient.get<any>(
    API_ENDPOINTS.DELIVERY_ZONES.GET_BOUNDARY(restaurantId, zoneId)
  );
  return response.data;
};

/**
 * Check if a point (lat, lng) is within any delivery zone
 */
export const checkPointInZones = async (
  restaurantId: string,
  latitude: number,
  longitude: number
): Promise<{ in_zone: boolean; zone_id?: string; zone_name?: string }> => {
  const response = await apiClient.post<{
    in_zone: boolean;
    zone_id?: string;
    zone_name?: string;
  }>(
    API_ENDPOINTS.DELIVERY_ZONES.CHECK_POINT(restaurantId),
    { latitude, longitude }
  );
  return response.data;
};

