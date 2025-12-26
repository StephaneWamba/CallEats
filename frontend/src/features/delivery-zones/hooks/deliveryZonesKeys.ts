/**
 * Query keys for delivery zones feature
 */
export const deliveryZonesKeys = {
  all: ['deliveryZones'] as const,
  list: (restaurantId: string) => [...deliveryZonesKeys.all, 'list', restaurantId] as const,
  detail: (restaurantId: string, zoneId: string) =>
    [...deliveryZonesKeys.all, 'detail', restaurantId, zoneId] as const,
  boundary: (restaurantId: string, zoneId: string) =>
    [...deliveryZonesKeys.detail(restaurantId, zoneId), 'boundary'] as const,
};


