/**
 * Query keys for operating hours feature
 */
export const operatingHoursKeys = {
  all: ['operatingHours'] as const,
  list: (restaurantId: string) => [...operatingHoursKeys.all, 'list', restaurantId] as const,
};


