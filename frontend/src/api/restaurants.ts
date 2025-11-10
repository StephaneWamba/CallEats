import type { RestaurantResponse, RestaurantStatsResponse, UpdateRestaurantRequest } from '../types/restaurant';
import { apiClient } from './client';
import { API_ENDPOINTS } from '../config/env';

/**
 * Get the current user's restaurant
 */
export const getMyRestaurant = async (): Promise<RestaurantResponse> => {
  const response = await apiClient.get<RestaurantResponse>(API_ENDPOINTS.RESTAURANTS.ME);
  return response.data;
};

/**
 * Get a specific restaurant by ID
 */
export const getRestaurant = async (restaurantId: string): Promise<RestaurantResponse> => {
  const response = await apiClient.get<RestaurantResponse>(API_ENDPOINTS.RESTAURANTS.GET(restaurantId));
  return response.data;
};

/**
 * Update restaurant information
 */
export const updateRestaurant = async (
  restaurantId: string,
  data: UpdateRestaurantRequest
): Promise<RestaurantResponse> => {
  const response = await apiClient.put<RestaurantResponse>(
    API_ENDPOINTS.RESTAURANTS.UPDATE(restaurantId),
    data
  );
  return response.data;
};

/**
 * Get restaurant dashboard statistics
 */
export const getRestaurantStats = async (restaurantId: string): Promise<RestaurantStatsResponse> => {
  const response = await apiClient.get<RestaurantStatsResponse>(
    API_ENDPOINTS.RESTAURANTS.STATS(restaurantId)
  );
  return response.data;
};

/**
 * Delete a restaurant and all associated data
 */
export const deleteRestaurant = async (restaurantId: string): Promise<{ success: boolean; message: string }> => {
  const response = await apiClient.delete<{ success: boolean; message: string }>(
    API_ENDPOINTS.RESTAURANTS.DELETE(restaurantId)
  );
  return response.data;
};

