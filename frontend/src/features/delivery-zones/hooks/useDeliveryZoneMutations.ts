import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  createDeliveryZone,
  updateDeliveryZone,
  deleteDeliveryZone,
  setZoneBoundary,
} from '@/api/deliveryZones';
import { useToast } from '@/contexts/ToastContext';
import { getErrorMessage } from '@/utils/errorHandler';
import { deliveryZonesKeys } from './deliveryZonesKeys';
import type {
  DeliveryZoneResponse,
  CreateDeliveryZoneRequest,
  UpdateDeliveryZoneRequest,
} from '@/types/delivery-zones';

/**
 * Create delivery zone mutation with optimistic updates
 */
export const useCreateDeliveryZone = () => {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  return useMutation({
    mutationFn: async ({
      restaurantId,
      data,
    }: {
      restaurantId: string;
      data: CreateDeliveryZoneRequest;
    }) => {
      return await createDeliveryZone(restaurantId, data);
    },
    onMutate: async ({ restaurantId, data }) => {
      await queryClient.cancelQueries({ queryKey: deliveryZonesKeys.list(restaurantId) });

      const previousZones = queryClient.getQueryData<DeliveryZoneResponse[]>(
        deliveryZonesKeys.list(restaurantId)
      );

      // Optimistically add delivery zone
      const optimisticZone: DeliveryZoneResponse = {
        id: `temp-${Date.now()}`,
        restaurant_id: restaurantId,
        zone_name: data.zone_name,
        description: data.description || null,
        delivery_fee: data.delivery_fee,
        min_order: data.min_order || null,
        boundary: null,
        created_at: new Date().toISOString(),
        updated_at: null,
      };

      queryClient.setQueryData<DeliveryZoneResponse[]>(
        deliveryZonesKeys.list(restaurantId),
        (old = []) => [...old, optimisticZone]
      );

      return { previousZones };
    },
    onError: (error, variables, context) => {
      if (context?.previousZones) {
        queryClient.setQueryData(
          deliveryZonesKeys.list(variables.restaurantId),
          context.previousZones
        );
      }
      const errorMessage = getErrorMessage(error, 'Failed to create delivery zone');
      showToast(errorMessage, 'error');
    },
    onSuccess: (newZone, variables) => {
      queryClient.setQueryData<DeliveryZoneResponse[]>(
        deliveryZonesKeys.list(variables.restaurantId),
        (old = []) =>
          old.map((zone) => (zone.id.startsWith('temp-') ? newZone : zone))
      );
      showToast('Delivery zone created successfully!', 'success');
    },
    onSettled: (_, __, variables) => {
      queryClient.invalidateQueries({ queryKey: deliveryZonesKeys.list(variables.restaurantId) });
    },
  });
};

/**
 * Update delivery zone mutation with optimistic updates
 */
export const useUpdateDeliveryZone = () => {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  return useMutation({
    mutationFn: async ({
      restaurantId,
      zoneId,
      data,
    }: {
      restaurantId: string;
      zoneId: string;
      data: UpdateDeliveryZoneRequest;
    }) => {
      return await updateDeliveryZone(restaurantId, zoneId, data);
    },
    onMutate: async ({ restaurantId, zoneId, data }) => {
      await queryClient.cancelQueries({ queryKey: deliveryZonesKeys.list(restaurantId) });
      await queryClient.cancelQueries({
        queryKey: deliveryZonesKeys.detail(restaurantId, zoneId),
      });

      const previousZones = queryClient.getQueryData<DeliveryZoneResponse[]>(
        deliveryZonesKeys.list(restaurantId)
      );

      // Optimistically update the delivery zone
      queryClient.setQueryData<DeliveryZoneResponse[]>(
        deliveryZonesKeys.list(restaurantId),
        (old = []) =>
          old.map((zone) =>
            zone.id === zoneId
              ? {
                  ...zone,
                  ...data,
                  updated_at: new Date().toISOString(),
                }
              : zone
          )
      );

      return { previousZones };
    },
    onError: (error, variables, context) => {
      if (context?.previousZones) {
        queryClient.setQueryData(
          deliveryZonesKeys.list(variables.restaurantId),
          context.previousZones
        );
      }
      const errorMessage = getErrorMessage(error, 'Failed to update delivery zone');
      showToast(errorMessage, 'error');
    },
    onSuccess: (updatedZone, variables) => {
      queryClient.setQueryData<DeliveryZoneResponse[]>(
        deliveryZonesKeys.list(variables.restaurantId),
        (old = []) =>
          old.map((zone) => (zone.id === variables.zoneId ? updatedZone : zone))
      );
      showToast('Delivery zone updated successfully!', 'success');
    },
    onSettled: (_, __, variables) => {
      queryClient.invalidateQueries({ queryKey: deliveryZonesKeys.list(variables.restaurantId) });
      queryClient.invalidateQueries({
        queryKey: deliveryZonesKeys.detail(variables.restaurantId, variables.zoneId),
      });
    },
  });
};

/**
 * Delete delivery zone mutation with optimistic updates
 */
export const useDeleteDeliveryZone = () => {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  return useMutation({
    mutationFn: async ({ restaurantId, zoneId }: { restaurantId: string; zoneId: string }) => {
      return await deleteDeliveryZone(restaurantId, zoneId);
    },
    onMutate: async ({ restaurantId, zoneId }) => {
      await queryClient.cancelQueries({ queryKey: deliveryZonesKeys.list(restaurantId) });

      const previousZones = queryClient.getQueryData<DeliveryZoneResponse[]>(
        deliveryZonesKeys.list(restaurantId)
      );

      // Optimistically remove the delivery zone
      queryClient.setQueryData<DeliveryZoneResponse[]>(
        deliveryZonesKeys.list(restaurantId),
        (old = []) => old.filter((zone) => zone.id !== zoneId)
      );

      return { previousZones };
    },
    onError: (error, variables, context) => {
      if (context?.previousZones) {
        queryClient.setQueryData(
          deliveryZonesKeys.list(variables.restaurantId),
          context.previousZones
        );
      }
      const errorMessage = getErrorMessage(error, 'Failed to delete delivery zone');
      showToast(errorMessage, 'error');
    },
    onSuccess: () => {
      showToast('Delivery zone deleted successfully!', 'success');
    },
    onSettled: (_, __, variables) => {
      queryClient.invalidateQueries({ queryKey: deliveryZonesKeys.list(variables.restaurantId) });
    },
  });
};

/**
 * Set zone boundary mutation with optimistic updates
 */
export const useSetZoneBoundary = () => {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  return useMutation({
    mutationFn: async ({
      restaurantId,
      zoneId,
      boundary,
    }: {
      restaurantId: string;
      zoneId: string;
      boundary: any;
    }) => {
      return await setZoneBoundary(restaurantId, zoneId, boundary);
    },
    onMutate: async ({ restaurantId, zoneId, boundary }) => {
      await queryClient.cancelQueries({ queryKey: deliveryZonesKeys.list(restaurantId) });
      await queryClient.cancelQueries({
        queryKey: deliveryZonesKeys.detail(restaurantId, zoneId),
      });

      const previousZones = queryClient.getQueryData<DeliveryZoneResponse[]>(
        deliveryZonesKeys.list(restaurantId)
      );

      // Optimistically update the boundary
      queryClient.setQueryData<DeliveryZoneResponse[]>(
        deliveryZonesKeys.list(restaurantId),
        (old = []) =>
          old.map((zone) =>
            zone.id === zoneId
              ? {
                  ...zone,
                  boundary: boundary?.geometry || boundary,
                  updated_at: new Date().toISOString(),
                }
              : zone
          )
      );

      return { previousZones };
    },
    onError: (error, variables, context) => {
      if (context?.previousZones) {
        queryClient.setQueryData(
          deliveryZonesKeys.list(variables.restaurantId),
          context.previousZones
        );
      }
      const errorMessage = getErrorMessage(error, 'Failed to update zone boundary');
      showToast(errorMessage, 'error');
    },
    onSuccess: () => {
      showToast('Zone boundary updated successfully!', 'success');
    },
    onSettled: (_, __, variables) => {
      queryClient.invalidateQueries({ queryKey: deliveryZonesKeys.list(variables.restaurantId) });
      queryClient.invalidateQueries({
        queryKey: deliveryZonesKeys.detail(variables.restaurantId, variables.zoneId),
      });
      queryClient.invalidateQueries({
        queryKey: deliveryZonesKeys.boundary(variables.restaurantId, variables.zoneId),
      });
    },
  });
};


