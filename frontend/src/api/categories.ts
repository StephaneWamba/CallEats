import apiClient from './client';
import { API_ENDPOINTS } from './endpoints';
import type {
  CategoryResponse,
  CreateCategoryRequest,
  UpdateCategoryRequest,
} from '@/types/menu';

/**
 * List all categories for a restaurant
 */
export const listCategories = async (
  restaurantId: string
): Promise<CategoryResponse[]> => {
  const response = await apiClient.get<CategoryResponse[]>(
    API_ENDPOINTS.CATEGORIES.LIST(restaurantId)
  );
  return response.data;
};

/**
 * Get a single category by ID
 */
export const getCategory = async (
  restaurantId: string,
  categoryId: string
): Promise<CategoryResponse> => {
  const response = await apiClient.get<CategoryResponse>(
    API_ENDPOINTS.CATEGORIES.GET(restaurantId, categoryId)
  );
  return response.data;
};

/**
 * Create a new category
 */
export const createCategory = async (
  restaurantId: string,
  data: CreateCategoryRequest
): Promise<CategoryResponse> => {
  const response = await apiClient.post<CategoryResponse>(
    API_ENDPOINTS.CATEGORIES.CREATE(restaurantId),
    data
  );
  return response.data;
};

/**
 * Update a category
 */
export const updateCategory = async (
  restaurantId: string,
  categoryId: string,
  data: UpdateCategoryRequest
): Promise<CategoryResponse> => {
  const response = await apiClient.put<CategoryResponse>(
    API_ENDPOINTS.CATEGORIES.UPDATE(restaurantId, categoryId),
    data
  );
  return response.data;
};

/**
 * Delete a category
 */
export const deleteCategory = async (
  restaurantId: string,
  categoryId: string
): Promise<{ success: boolean; message: string }> => {
  const response = await apiClient.delete<{ success: boolean; message: string }>(
    API_ENDPOINTS.CATEGORIES.DELETE(restaurantId, categoryId)
  );
  return response.data;
};

