import apiClient from './client';
import { API_ENDPOINTS } from './endpoints';
import type {
  ModifierResponse,
  CreateModifierRequest,
  UpdateModifierRequest,
} from '@/types/menu';

/**
 * List all modifiers for a restaurant
 */
export const listModifiers = async (
  restaurantId: string
): Promise<ModifierResponse[]> => {
  const response = await apiClient.get<ModifierResponse[]>(
    API_ENDPOINTS.MODIFIERS.LIST(restaurantId)
  );
  return response.data;
};

/**
 * Get a single modifier by ID
 */
export const getModifier = async (
  restaurantId: string,
  modifierId: string
): Promise<ModifierResponse> => {
  const response = await apiClient.get<ModifierResponse>(
    API_ENDPOINTS.MODIFIERS.GET(restaurantId, modifierId)
  );
  return response.data;
};

/**
 * Create a new modifier
 */
export const createModifier = async (
  restaurantId: string,
  data: CreateModifierRequest
): Promise<ModifierResponse> => {
  const response = await apiClient.post<ModifierResponse>(
    API_ENDPOINTS.MODIFIERS.CREATE(restaurantId),
    data
  );
  return response.data;
};

/**
 * Update a modifier
 */
export const updateModifier = async (
  restaurantId: string,
  modifierId: string,
  data: UpdateModifierRequest
): Promise<ModifierResponse> => {
  const response = await apiClient.put<ModifierResponse>(
    API_ENDPOINTS.MODIFIERS.UPDATE(restaurantId, modifierId),
    data
  );
  return response.data;
};

/**
 * Delete a modifier
 */
export const deleteModifier = async (
  restaurantId: string,
  modifierId: string
): Promise<{ success: boolean; message: string }> => {
  const response = await apiClient.delete<{ success: boolean; message: string }>(
    API_ENDPOINTS.MODIFIERS.DELETE(restaurantId, modifierId)
  );
  return response.data;
};

