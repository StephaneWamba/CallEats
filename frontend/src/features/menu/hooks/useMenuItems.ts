import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { listMenuItems, createMenuItem, updateMenuItem, deleteMenuItem } from '@/api/menuItems';
import { useToast } from '@/contexts/ToastContext';
import { getErrorMessage } from '@/utils/errorHandler';
import type {
  MenuItemResponse,
  CreateMenuItemRequest,
  UpdateMenuItemRequest,
} from '@/types/menu';
import { menuKeys } from './menuKeys';

/**
 * Get menu items for a restaurant
 */
export const useMenuItems = (restaurantId: string | undefined) => {
  return useQuery({
    queryKey: menuKeys.menuItems(restaurantId || ''),
    queryFn: async () => {
      if (!restaurantId) throw new Error('Restaurant ID is required');
      return await listMenuItems(restaurantId);
    },
    enabled: !!restaurantId,
    retry: 1,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};

/**
 * Create menu item mutation with optimistic updates
 */
export const useCreateMenuItem = () => {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  return useMutation({
    mutationFn: async ({ restaurantId, data }: { restaurantId: string; data: CreateMenuItemRequest }) => {
      return await createMenuItem(restaurantId, data);
    },
    onMutate: async ({ restaurantId, data }) => {
      await queryClient.cancelQueries({ queryKey: menuKeys.menuItems(restaurantId) });

      const previousItems = queryClient.getQueryData<MenuItemResponse[]>(
        menuKeys.menuItems(restaurantId)
      );

      // Optimistically add menu item
      const optimisticItem: MenuItemResponse = {
        id: `temp-${Date.now()}`,
        restaurant_id: restaurantId,
        name: data.name,
        description: data.description || null,
        price: data.price,
        category_id: data.category_id || null,
        available: data.available ?? true,
        image_url: null,
        modifiers: [],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      queryClient.setQueryData<MenuItemResponse[]>(
        menuKeys.menuItems(restaurantId),
        (old = []) => [...old, optimisticItem]
      );

      return { previousItems };
    },
    onError: (error, variables, context) => {
      if (context?.previousItems) {
        queryClient.setQueryData(
          menuKeys.menuItems(variables.restaurantId),
          context.previousItems
        );
      }
      const errorMessage = getErrorMessage(error, 'Failed to create menu item');
      showToast(errorMessage, 'error');
    },
    onSuccess: (newItem, variables) => {
      queryClient.setQueryData<MenuItemResponse[]>(
        menuKeys.menuItems(variables.restaurantId),
        (old = []) =>
          old.map((item) => (item.id.startsWith('temp-') ? newItem : item))
      );
      showToast('Menu item created successfully!', 'success');
    },
    onSettled: (_, __, variables) => {
      queryClient.invalidateQueries({ queryKey: menuKeys.menuItems(variables.restaurantId) });
    },
  });
};

/**
 * Update menu item mutation with optimistic updates
 */
export const useUpdateMenuItem = () => {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  return useMutation({
    mutationFn: async ({
      restaurantId,
      itemId,
      data,
    }: {
      restaurantId: string;
      itemId: string;
      data: UpdateMenuItemRequest;
    }) => {
      return await updateMenuItem(restaurantId, itemId, data);
    },
    onMutate: async ({ restaurantId, itemId, data }) => {
      await queryClient.cancelQueries({ queryKey: menuKeys.menuItems(restaurantId) });

      const previousItems = queryClient.getQueryData<MenuItemResponse[]>(
        menuKeys.menuItems(restaurantId)
      );

      // Optimistically update the menu item
      queryClient.setQueryData<MenuItemResponse[]>(
        menuKeys.menuItems(restaurantId),
        (old = []) =>
          old.map((item) =>
            item.id === itemId
              ? {
                  ...item,
                  ...data,
                  updated_at: new Date().toISOString(),
                }
              : item
          )
      );

      return { previousItems };
    },
    onError: (error, variables, context) => {
      if (context?.previousItems) {
        queryClient.setQueryData(
          menuKeys.menuItems(variables.restaurantId),
          context.previousItems
        );
      }
      const errorMessage = getErrorMessage(error, 'Failed to update menu item');
      showToast(errorMessage, 'error');
    },
    onSuccess: (updatedItem, variables) => {
      queryClient.setQueryData<MenuItemResponse[]>(
        menuKeys.menuItems(variables.restaurantId),
        (old = []) =>
          old.map((item) => (item.id === variables.itemId ? updatedItem : item))
      );
      showToast('Menu item updated successfully!', 'success');
    },
    onSettled: (_, __, variables) => {
      queryClient.invalidateQueries({ queryKey: menuKeys.menuItems(variables.restaurantId) });
    },
  });
};

/**
 * Delete menu item mutation with optimistic updates
 */
export const useDeleteMenuItem = () => {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  return useMutation({
    mutationFn: async ({ restaurantId, itemId }: { restaurantId: string; itemId: string }) => {
      return await deleteMenuItem(restaurantId, itemId);
    },
    onMutate: async ({ restaurantId, itemId }) => {
      await queryClient.cancelQueries({ queryKey: menuKeys.menuItems(restaurantId) });

      const previousItems = queryClient.getQueryData<MenuItemResponse[]>(
        menuKeys.menuItems(restaurantId)
      );

      // Optimistically remove the menu item
      queryClient.setQueryData<MenuItemResponse[]>(
        menuKeys.menuItems(restaurantId),
        (old = []) => old.filter((item) => item.id !== itemId)
      );

      return { previousItems };
    },
    onError: (error, variables, context) => {
      if (context?.previousItems) {
        queryClient.setQueryData(
          menuKeys.menuItems(variables.restaurantId),
          context.previousItems
        );
      }
      const errorMessage = getErrorMessage(error, 'Failed to delete menu item');
      showToast(errorMessage, 'error');
    },
    onSuccess: () => {
      showToast('Menu item deleted successfully!', 'success');
    },
    onSettled: (_, __, variables) => {
      queryClient.invalidateQueries({ queryKey: menuKeys.menuItems(variables.restaurantId) });
    },
  });
};

