import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { listCategories, createCategory, updateCategory, deleteCategory } from '@/api/categories';
import { useToast } from '@/contexts/ToastContext';
import { getErrorMessage } from '@/utils/errorHandler';
import type {
  CategoryResponse,
  CreateCategoryRequest,
  UpdateCategoryRequest,
} from '@/types/menu';
import { menuKeys } from './menuKeys';

/**
 * Get categories for a restaurant
 */
export const useCategories = (restaurantId: string | undefined) => {
  return useQuery({
    queryKey: menuKeys.categories(restaurantId || ''),
    queryFn: async () => {
      if (!restaurantId) throw new Error('Restaurant ID is required');
      return await listCategories(restaurantId);
    },
    enabled: !!restaurantId,
    retry: 1,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};

/**
 * Create category mutation with optimistic updates
 */
export const useCreateCategory = () => {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  return useMutation({
    mutationFn: async ({ restaurantId, data }: { restaurantId: string; data: CreateCategoryRequest }) => {
      return await createCategory(restaurantId, data);
    },
    onMutate: async ({ restaurantId, data }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: menuKeys.categories(restaurantId) });

      // Snapshot previous value
      const previousCategories = queryClient.getQueryData<CategoryResponse[]>(
        menuKeys.categories(restaurantId)
      );

      // Optimistically update cache
      const optimisticCategory: CategoryResponse = {
        id: `temp-${Date.now()}`,
        restaurant_id: restaurantId,
        name: data.name,
        description: data.description || null,
        display_order: data.display_order ?? 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      queryClient.setQueryData<CategoryResponse[]>(
        menuKeys.categories(restaurantId),
        (old = []) => [...old, optimisticCategory]
      );

      return { previousCategories };
    },
    onError: (error, variables, context) => {
      // Rollback on error
      if (context?.previousCategories) {
        queryClient.setQueryData(
          menuKeys.categories(variables.restaurantId),
          context.previousCategories
        );
      }
      const errorMessage = getErrorMessage(error, 'Failed to create category');
      showToast(errorMessage, 'error');
    },
    onSuccess: (newCategory, variables) => {
      // Replace optimistic item with real data
      queryClient.setQueryData<CategoryResponse[]>(
        menuKeys.categories(variables.restaurantId),
        (old = []) =>
          old.map((cat) => (cat.id.startsWith('temp-') ? newCategory : cat))
      );
      showToast('Category created successfully!', 'success');
    },
    onSettled: (_, __, variables) => {
      // Always refetch to ensure consistency
      queryClient.invalidateQueries({ queryKey: menuKeys.categories(variables.restaurantId) });
    },
  });
};

/**
 * Update category mutation with optimistic updates
 */
export const useUpdateCategory = () => {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  return useMutation({
    mutationFn: async ({
      restaurantId,
      categoryId,
      data,
    }: {
      restaurantId: string;
      categoryId: string;
      data: UpdateCategoryRequest;
    }) => {
      return await updateCategory(restaurantId, categoryId, data);
    },
    onMutate: async ({ restaurantId, categoryId, data }) => {
      await queryClient.cancelQueries({ queryKey: menuKeys.categories(restaurantId) });

      const previousCategories = queryClient.getQueryData<CategoryResponse[]>(
        menuKeys.categories(restaurantId)
      );

      // Optimistically update
      queryClient.setQueryData<CategoryResponse[]>(
        menuKeys.categories(restaurantId),
        (old = []) =>
          old.map((cat) =>
            cat.id === categoryId
              ? { ...cat, ...data, updated_at: new Date().toISOString() }
              : cat
          )
      );

      return { previousCategories };
    },
    onError: (error, variables, context) => {
      if (context?.previousCategories) {
        queryClient.setQueryData(
          menuKeys.categories(variables.restaurantId),
          context.previousCategories
        );
      }
      const errorMessage = getErrorMessage(error, 'Failed to update category');
      showToast(errorMessage, 'error');
    },
    onSuccess: (updatedCategory, variables) => {
      queryClient.setQueryData<CategoryResponse[]>(
        menuKeys.categories(variables.restaurantId),
        (old = []) =>
          old.map((cat) => (cat.id === variables.categoryId ? updatedCategory : cat))
      );
      showToast('Category updated successfully!', 'success');
    },
    onSettled: (_, __, variables) => {
      queryClient.invalidateQueries({ queryKey: menuKeys.categories(variables.restaurantId) });
    },
  });
};

/**
 * Delete category mutation with optimistic updates
 */
export const useDeleteCategory = () => {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  return useMutation({
    mutationFn: async ({ restaurantId, categoryId }: { restaurantId: string; categoryId: string }) => {
      return await deleteCategory(restaurantId, categoryId);
    },
    onMutate: async ({ restaurantId, categoryId }) => {
      await queryClient.cancelQueries({ queryKey: menuKeys.categories(restaurantId) });

      const previousCategories = queryClient.getQueryData<CategoryResponse[]>(
        menuKeys.categories(restaurantId)
      );

      // Optimistically remove
      queryClient.setQueryData<CategoryResponse[]>(
        menuKeys.categories(restaurantId),
        (old = []) => old.filter((cat) => cat.id !== categoryId)
      );

      return { previousCategories };
    },
    onError: (error, variables, context) => {
      if (context?.previousCategories) {
        queryClient.setQueryData(
          menuKeys.categories(variables.restaurantId),
          context.previousCategories
        );
      }
      const errorMessage = getErrorMessage(error, 'Failed to delete category');
      showToast(errorMessage, 'error');
    },
    onSuccess: () => {
      showToast('Category deleted successfully!', 'success');
    },
    onSettled: (_, __, variables) => {
      queryClient.invalidateQueries({ queryKey: menuKeys.categories(variables.restaurantId) });
    },
  });
};

