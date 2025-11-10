import { apiClient } from './client';
import { API_ENDPOINTS } from './endpoints';
import type {
  OperatingHourResponse,
  BulkUpdateOperatingHoursRequest,
} from '@/types/operating-hours';

/**
 * List operating hours for a restaurant
 */
export const listOperatingHours = async (
  restaurantId: string
): Promise<OperatingHourResponse[]> => {
  const response = await apiClient.get<OperatingHourResponse[]>(
    API_ENDPOINTS.OPERATING_HOURS.LIST(restaurantId)
  );
  return response.data;
};

/**
 * Bulk update operating hours (replaces all hours)
 */
export const bulkUpdateOperatingHours = async (
  restaurantId: string,
  data: BulkUpdateOperatingHoursRequest
): Promise<OperatingHourResponse[]> => {
  const response = await apiClient.put<OperatingHourResponse[]>(
    API_ENDPOINTS.OPERATING_HOURS.BULK_UPDATE(restaurantId),
    data
  );
  return response.data;
};

/**
 * Delete all operating hours for a restaurant
 */
export const deleteAllOperatingHours = async (
  restaurantId: string
): Promise<{ success: boolean; message: string }> => {
  const response = await apiClient.delete<{ success: boolean; message: string }>(
    API_ENDPOINTS.OPERATING_HOURS.DELETE_ALL(restaurantId)
  );
  return response.data;
};

