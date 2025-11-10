import { apiClient } from './client';
import { API_ENDPOINTS } from './endpoints';
import type { CallResponse, CallListResponse } from '@/types/calls';

/**
 * List call history for a restaurant
 */
export const listCalls = async (
  restaurantId: string,
  limit: number = 50
): Promise<CallResponse[]> => {
  const response = await apiClient.get<CallListResponse>(
    API_ENDPOINTS.CALLS.LIST(restaurantId, limit)
  );
  return response.data.data;
};

/**
 * Get a single call by ID
 */
export const getCall = async (
  callId: string,
  restaurantId: string
): Promise<CallResponse> => {
  const response = await apiClient.get<CallResponse>(
    API_ENDPOINTS.CALLS.GET(callId, restaurantId)
  );
  return response.data;
};

