import { useQuery } from '@tanstack/react-query';
import { listCalls, getCall } from '@/api/calls';
import { callsKeys } from './callsKeys';

/**
 * Get calls for a restaurant
 */
export const useCalls = (restaurantId: string | undefined, limit: number = 50) => {
  return useQuery({
    queryKey: callsKeys.list(restaurantId || '', limit),
    queryFn: async () => {
      if (!restaurantId) throw new Error('Restaurant ID is required');
      return await listCalls(restaurantId, limit);
    },
    enabled: !!restaurantId,
    retry: 1,
    staleTime: 1 * 60 * 1000, // 1 minute
  });
};

/**
 * Get a single call by ID
 */
export const useCall = (callId: string | undefined, restaurantId: string | undefined) => {
  return useQuery({
    queryKey: callsKeys.detail(callId || '', restaurantId || ''),
    queryFn: async () => {
      if (!callId || !restaurantId) throw new Error('Call ID and Restaurant ID are required');
      return await getCall(callId, restaurantId);
    },
    enabled: !!callId && !!restaurantId,
    retry: 1,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};


