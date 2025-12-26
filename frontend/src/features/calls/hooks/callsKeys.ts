/**
 * Query keys for calls feature
 */
export const callsKeys = {
  all: ['calls'] as const,
  list: (restaurantId: string, limit?: number) => [...callsKeys.all, 'list', restaurantId, limit] as const,
  detail: (callId: string, restaurantId: string) => [...callsKeys.all, 'detail', callId, restaurantId] as const,
};


