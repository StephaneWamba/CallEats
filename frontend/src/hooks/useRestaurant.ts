import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getMyRestaurant, updateRestaurant, getRestaurantStats } from '@/api/restaurants';
import { useToast } from '@/contexts/ToastContext';
import { getErrorMessage } from '@/utils/errorHandler';
import type { RestaurantResponse, UpdateRestaurantRequest } from '@/types/restaurant';

// Query keys
export const restaurantKeys = {
  all: ['restaurant'] as const,
  current: () => [...restaurantKeys.all, 'current'] as const,
  detail: (restaurantId: string) => [...restaurantKeys.all, 'detail', restaurantId] as const,
  stats: (restaurantId: string) => [...restaurantKeys.all, 'stats', restaurantId] as const,
};

/**
 * Get the current user's restaurant
 */
export const useRestaurant = () => {
  return useQuery({
    queryKey: restaurantKeys.current(),
    queryFn: async () => {
      return await getMyRestaurant();
    },
    retry: 1,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

/**
 * Get restaurant statistics
 */
export const useRestaurantStats = (restaurantId: string | undefined) => {
  return useQuery({
    queryKey: restaurantKeys.stats(restaurantId || ''),
    queryFn: async () => {
      if (!restaurantId) throw new Error('Restaurant ID is required');
      return await getRestaurantStats(restaurantId);
    },
    enabled: !!restaurantId,
    retry: 1,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};

/**
 * Update restaurant mutation with optimistic updates
 */
export const useUpdateRestaurant = () => {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  return useMutation({
    mutationFn: async ({
      restaurantId,
      data,
    }: {
      restaurantId: string;
      data: UpdateRestaurantRequest;
    }) => {
      return await updateRestaurant(restaurantId, data);
    },
    onMutate: async ({ restaurantId, data }) => {
      await queryClient.cancelQueries({ queryKey: restaurantKeys.current() });
      await queryClient.cancelQueries({ queryKey: restaurantKeys.detail(restaurantId) });

      const previousRestaurant = queryClient.getQueryData<RestaurantResponse>(
        restaurantKeys.current()
      );
      const previousDetail = queryClient.getQueryData<RestaurantResponse>(
        restaurantKeys.detail(restaurantId)
      );

      // Optimistically update restaurant
      if (previousRestaurant) {
        queryClient.setQueryData<RestaurantResponse>(restaurantKeys.current(), {
          ...previousRestaurant,
          ...data,
          updated_at: new Date().toISOString(),
        });
      }
      if (previousDetail) {
        queryClient.setQueryData<RestaurantResponse>(restaurantKeys.detail(restaurantId), {
          ...previousDetail,
          ...data,
          updated_at: new Date().toISOString(),
        });
      }

      return { previousRestaurant, previousDetail };
    },
    onError: (error, variables, context) => {
      // Rollback on error
      if (context?.previousRestaurant) {
        queryClient.setQueryData(restaurantKeys.current(), context.previousRestaurant);
      }
      if (context?.previousDetail) {
        queryClient.setQueryData(
          restaurantKeys.detail(variables.restaurantId),
          context.previousDetail
        );
      }
      const errorMessage = getErrorMessage(error, 'Failed to update restaurant');
      showToast(errorMessage, 'error');
    },
    onSuccess: (updatedRestaurant, variables) => {
      // Replace with server response
      queryClient.setQueryData(restaurantKeys.current(), updatedRestaurant);
      queryClient.setQueryData(restaurantKeys.detail(variables.restaurantId), updatedRestaurant);
      showToast('Restaurant updated successfully!', 'success');
    },
    onSettled: (_, __, variables) => {
      queryClient.invalidateQueries({ queryKey: restaurantKeys.current() });
      queryClient.invalidateQueries({ queryKey: restaurantKeys.detail(variables.restaurantId) });
    },
  });
};

