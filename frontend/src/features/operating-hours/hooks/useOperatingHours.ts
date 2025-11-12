import { useQuery } from '@tanstack/react-query';
import { listOperatingHours } from '@/api/operatingHours';
import { operatingHoursKeys } from './operatingHoursKeys';

/**
 * Get operating hours for a restaurant
 */
export const useOperatingHours = (restaurantId: string | undefined) => {
  return useQuery({
    queryKey: operatingHoursKeys.list(restaurantId || ''),
    queryFn: async () => {
      if (!restaurantId) throw new Error('Restaurant ID is required');
      return await listOperatingHours(restaurantId);
    },
    enabled: !!restaurantId,
    retry: 1,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

