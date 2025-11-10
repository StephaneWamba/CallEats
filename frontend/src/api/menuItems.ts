import apiClient from './client';
import { API_ENDPOINTS } from './endpoints';
import type {
  MenuItemResponse,
  CreateMenuItemRequest,
  UpdateMenuItemRequest,
  LinkModifierRequest,
  MenuItemModifierLink,
} from '@/types/menu';

/**
 * List all menu items for a restaurant
 */
export const listMenuItems = async (
  restaurantId: string
): Promise<MenuItemResponse[]> => {
  const response = await apiClient.get<MenuItemResponse[]>(
    API_ENDPOINTS.MENU_ITEMS.LIST(restaurantId)
  );
  return response.data;
};

/**
 * Get a single menu item by ID
 */
export const getMenuItem = async (
  restaurantId: string,
  itemId: string
): Promise<MenuItemResponse> => {
  const response = await apiClient.get<MenuItemResponse>(
    API_ENDPOINTS.MENU_ITEMS.GET(restaurantId, itemId)
  );
  return response.data;
};

/**
 * Create a new menu item
 */
export const createMenuItem = async (
  restaurantId: string,
  data: CreateMenuItemRequest
): Promise<MenuItemResponse> => {
  const response = await apiClient.post<MenuItemResponse>(
    API_ENDPOINTS.MENU_ITEMS.CREATE(restaurantId),
    data
  );
  return response.data;
};

/**
 * Update a menu item
 */
export const updateMenuItem = async (
  restaurantId: string,
  itemId: string,
  data: UpdateMenuItemRequest
): Promise<MenuItemResponse> => {
  const response = await apiClient.put<MenuItemResponse>(
    API_ENDPOINTS.MENU_ITEMS.UPDATE(restaurantId, itemId),
    data
  );
  return response.data;
};

/**
 * Delete a menu item
 */
export const deleteMenuItem = async (
  restaurantId: string,
  itemId: string
): Promise<{ success: boolean; message: string }> => {
  const response = await apiClient.delete<{ success: boolean; message: string }>(
    API_ENDPOINTS.MENU_ITEMS.DELETE(restaurantId, itemId)
  );
  return response.data;
};

/**
 * Upload an image for a menu item
 */
export const uploadMenuItemImage = async (
  restaurantId: string,
  itemId: string,
  file: File
): Promise<{ image_url: string; message: string }> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post<{ image_url: string; message: string }>(
    API_ENDPOINTS.MENU_ITEMS.UPLOAD_IMAGE(restaurantId, itemId),
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  return response.data;
};

/**
 * Delete an image for a menu item
 */
export const deleteMenuItemImage = async (
  restaurantId: string,
  itemId: string
): Promise<{ success: boolean; message: string }> => {
  const response = await apiClient.delete<{ success: boolean; message: string }>(
    API_ENDPOINTS.MENU_ITEMS.DELETE_IMAGE(restaurantId, itemId)
  );
  return response.data;
};

/**
 * Link a modifier to a menu item
 */
export const linkModifierToItem = async (
  restaurantId: string,
  itemId: string,
  data: LinkModifierRequest
): Promise<MenuItemModifierLink> => {
  const response = await apiClient.post<MenuItemModifierLink>(
    API_ENDPOINTS.MODIFIERS.LINK_TO_ITEM(restaurantId, itemId),
    data
  );
  return response.data;
};

/**
 * Unlink a modifier from a menu item
 */
export const unlinkModifierFromItem = async (
  restaurantId: string,
  itemId: string,
  modifierId: string
): Promise<{ success: boolean; message: string }> => {
  const response = await apiClient.delete<{ success: boolean; message: string }>(
    API_ENDPOINTS.MODIFIERS.UNLINK_FROM_ITEM(restaurantId, itemId, modifierId)
  );
  return response.data;
};

