import { useMutation, useQueryClient } from '@tanstack/react-query';
import { bulkUpdateOperatingHours } from '@/api/operatingHours';
import { useToast } from '@/contexts/ToastContext';
import { getErrorMessage } from '@/utils/errorHandler';
import { operatingHoursKeys } from './operatingHoursKeys';
import type {
  OperatingHourResponse,
  BulkUpdateOperatingHoursRequest,
} from '@/types/operating-hours';

/**
 * Bulk update operating hours mutation with optimistic updates
 */
export const useUpdateOperatingHours = () => {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  return useMutation({
    mutationFn: async ({
      restaurantId,
      data,
    }: {
      restaurantId: string;
      data: BulkUpdateOperatingHoursRequest;
    }) => {
      return await bulkUpdateOperatingHours(restaurantId, data);
    },
    onMutate: async ({ restaurantId, data }) => {
      await queryClient.cancelQueries({ queryKey: operatingHoursKeys.list(restaurantId) });

      const previousHours = queryClient.getQueryData<OperatingHourResponse[]>(
        operatingHoursKeys.list(restaurantId)
      );

      // Optimistically update operating hours
      // Convert request format to response format
      const optimisticHours: OperatingHourResponse[] = data.hours.map((hour) => ({
        id: `temp-${Date.now()}-${hour.day_of_week}`,
        restaurant_id: restaurantId,
        day_of_week: hour.day_of_week,
        open_time: hour.open_time,
        close_time: hour.close_time,
        is_closed: hour.is_closed ?? false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }));

      queryClient.setQueryData<OperatingHourResponse[]>(
        operatingHoursKeys.list(restaurantId),
        optimisticHours
      );

      return { previousHours };
    },
    onError: (error, variables, context) => {
      if (context?.previousHours) {
        queryClient.setQueryData(
          operatingHoursKeys.list(variables.restaurantId),
          context.previousHours
        );
      }
      const errorMessage = getErrorMessage(error, 'Failed to update operating hours');
      showToast(errorMessage, 'error');
    },
    onSuccess: (updatedHours, variables) => {
      // Replace with server response
      queryClient.setQueryData<OperatingHourResponse[]>(
        operatingHoursKeys.list(variables.restaurantId),
        updatedHours
      );
      showToast('Operating hours updated successfully!', 'success');
    },
    onSettled: (_, __, variables) => {
      queryClient.invalidateQueries({ queryKey: operatingHoursKeys.list(variables.restaurantId) });
    },
  });
};

