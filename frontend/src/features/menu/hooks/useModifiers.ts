import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { listModifiers, createModifier, updateModifier, deleteModifier } from '@/api/modifiers';
import { useToast } from '@/contexts/ToastContext';
import { getErrorMessage } from '@/utils/errorHandler';
import type {
  ModifierResponse,
  CreateModifierRequest,
  UpdateModifierRequest,
} from '@/types/menu';
import { menuKeys } from './menuKeys';

/**
 * Get modifiers for a restaurant
 */
export const useModifiers = (restaurantId: string | undefined) => {
  return useQuery({
    queryKey: menuKeys.modifiers(restaurantId || ''),
    queryFn: async () => {
      if (!restaurantId) throw new Error('Restaurant ID is required');
      return await listModifiers(restaurantId);
    },
    enabled: !!restaurantId,
    retry: 1,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};

/**
 * Create modifier mutation with optimistic updates
 */
export const useCreateModifier = () => {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  return useMutation({
    mutationFn: async ({ restaurantId, data }: { restaurantId: string; data: CreateModifierRequest }) => {
      return await createModifier(restaurantId, data);
    },
    onMutate: async ({ restaurantId, data }) => {
      await queryClient.cancelQueries({ queryKey: menuKeys.modifiers(restaurantId) });

      const previousModifiers = queryClient.getQueryData<ModifierResponse[]>(
        menuKeys.modifiers(restaurantId)
      );

      // Optimistically add modifier
      const optimisticModifier: ModifierResponse = {
        id: `temp-${Date.now()}`,
        restaurant_id: restaurantId,
        name: data.name,
        description: data.description || null,
        price: data.price,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      queryClient.setQueryData<ModifierResponse[]>(
        menuKeys.modifiers(restaurantId),
        (old = []) => [...old, optimisticModifier]
      );

      return { previousModifiers };
    },
    onError: (error, variables, context) => {
      if (context?.previousModifiers) {
        queryClient.setQueryData(
          menuKeys.modifiers(variables.restaurantId),
          context.previousModifiers
        );
      }
      const errorMessage = getErrorMessage(error, 'Failed to create modifier');
      showToast(errorMessage, 'error');
    },
    onSuccess: (newModifier, variables) => {
      queryClient.setQueryData<ModifierResponse[]>(
        menuKeys.modifiers(variables.restaurantId),
        (old = []) =>
          old.map((mod) => (mod.id.startsWith('temp-') ? newModifier : mod))
      );
      showToast('Modifier created successfully!', 'success');
    },
    onSettled: (_, __, variables) => {
      queryClient.invalidateQueries({ queryKey: menuKeys.modifiers(variables.restaurantId) });
    },
  });
};

/**
 * Update modifier mutation with optimistic updates
 */
export const useUpdateModifier = () => {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  return useMutation({
    mutationFn: async ({
      restaurantId,
      modifierId,
      data,
    }: {
      restaurantId: string;
      modifierId: string;
      data: UpdateModifierRequest;
    }) => {
      return await updateModifier(restaurantId, modifierId, data);
    },
    onMutate: async ({ restaurantId, modifierId, data }) => {
      await queryClient.cancelQueries({ queryKey: menuKeys.modifiers(restaurantId) });

      const previousModifiers = queryClient.getQueryData<ModifierResponse[]>(
        menuKeys.modifiers(restaurantId)
      );

      // Optimistically update the modifier
      queryClient.setQueryData<ModifierResponse[]>(
        menuKeys.modifiers(restaurantId),
        (old = []) =>
          old.map((mod) =>
            mod.id === modifierId
              ? {
                  ...mod,
                  ...data,
                  updated_at: new Date().toISOString(),
                }
              : mod
          )
      );

      return { previousModifiers };
    },
    onError: (error, variables, context) => {
      if (context?.previousModifiers) {
        queryClient.setQueryData(
          menuKeys.modifiers(variables.restaurantId),
          context.previousModifiers
        );
      }
      const errorMessage = getErrorMessage(error, 'Failed to update modifier');
      showToast(errorMessage, 'error');
    },
    onSuccess: (updatedModifier, variables) => {
      queryClient.setQueryData<ModifierResponse[]>(
        menuKeys.modifiers(variables.restaurantId),
        (old = []) =>
          old.map((mod) => (mod.id === variables.modifierId ? updatedModifier : mod))
      );
      showToast('Modifier updated successfully!', 'success');
    },
    onSettled: (_, __, variables) => {
      queryClient.invalidateQueries({ queryKey: menuKeys.modifiers(variables.restaurantId) });
    },
  });
};

/**
 * Delete modifier mutation with optimistic updates
 */
export const useDeleteModifier = () => {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  return useMutation({
    mutationFn: async ({ restaurantId, modifierId }: { restaurantId: string; modifierId: string }) => {
      return await deleteModifier(restaurantId, modifierId);
    },
    onMutate: async ({ restaurantId, modifierId }) => {
      await queryClient.cancelQueries({ queryKey: menuKeys.modifiers(restaurantId) });

      const previousModifiers = queryClient.getQueryData<ModifierResponse[]>(
        menuKeys.modifiers(restaurantId)
      );

      // Optimistically remove the modifier
      queryClient.setQueryData<ModifierResponse[]>(
        menuKeys.modifiers(restaurantId),
        (old = []) => old.filter((mod) => mod.id !== modifierId)
      );

      return { previousModifiers };
    },
    onError: (error, variables, context) => {
      if (context?.previousModifiers) {
        queryClient.setQueryData(
          menuKeys.modifiers(variables.restaurantId),
          context.previousModifiers
        );
      }
      const errorMessage = getErrorMessage(error, 'Failed to delete modifier');
      showToast(errorMessage, 'error');
    },
    onSuccess: () => {
      showToast('Modifier deleted successfully!', 'success');
    },
    onSettled: (_, __, variables) => {
      queryClient.invalidateQueries({ queryKey: menuKeys.modifiers(variables.restaurantId) });
    },
  });
};

