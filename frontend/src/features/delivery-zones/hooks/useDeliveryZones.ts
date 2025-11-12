import { useQuery } from '@tanstack/react-query';
import { listDeliveryZones, getZoneBoundary } from '@/api/deliveryZones';
import { deliveryZonesKeys } from './deliveryZonesKeys';
import type { DeliveryZoneResponse } from '@/types/delivery-zones';

/**
 * Get delivery zones for a restaurant
 */
export const useDeliveryZones = (restaurantId: string | undefined) => {
  return useQuery<DeliveryZoneResponse[]>({
    queryKey: deliveryZonesKeys.list(restaurantId || ''),
    queryFn: async () => {
      if (!restaurantId) throw new Error('Restaurant ID is required');
      const zones = await listDeliveryZones(restaurantId);
      // Fetch boundaries for zones that don't have them and normalize numeric fields
      const zonesWithBoundaries = await Promise.all(
        zones.map(async (zone) => {
          // Normalize numeric fields (API might return strings)
          const normalizedZone: DeliveryZoneResponse = {
            ...zone,
            delivery_fee: typeof zone.delivery_fee === 'string' 
              ? parseFloat(zone.delivery_fee) || 0 
              : Number(zone.delivery_fee) || 0,
            min_order: zone.min_order 
              ? (typeof zone.min_order === 'string' 
                  ? parseFloat(zone.min_order) 
                  : Number(zone.min_order))
              : null,
          };

          if (!normalizedZone.boundary) {
            try {
              const boundary = await getZoneBoundary(restaurantId, zone.id);
              return { ...normalizedZone, boundary: boundary?.geometry || null };
            } catch {
              return normalizedZone;
            }
          }
          return normalizedZone;
        })
      );
      return zonesWithBoundaries;
    },
    enabled: !!restaurantId,
    retry: 1,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

