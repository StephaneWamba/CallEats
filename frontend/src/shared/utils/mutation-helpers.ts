/**
 * Shared utilities for React Query mutations
 * 
 * Common patterns for optimistic updates, error handling, and cache management
 */

import { QueryClient } from '@tanstack/react-query';
import { getErrorMessage } from '@/utils/errorHandler';
import type { ToastContextType } from '@/contexts/ToastContext';

export interface OptimisticUpdateContext<T> {
  previousData?: T;
}

export interface MutationConfig<TData, TVariables, TError = Error> {
  queryClient: QueryClient;
  showToast: ToastContextType['showToast'];
  queryKey: readonly unknown[];
  onMutate?: (variables: TVariables) => Promise<OptimisticUpdateContext<TData> | undefined>;
  onSuccess?: (data: TData, variables: TVariables) => void;
  onError?: (error: TError, variables: TVariables, context?: OptimisticUpdateContext<TData>) => void;
  successMessage?: string;
  errorMessage?: string;
}

/**
 * Create optimistic update handler
 */
export async function createOptimisticUpdate<TData, TVariables>(
  queryClient: QueryClient,
  queryKey: readonly unknown[],
  _optimisticData: (variables: TVariables, previousData?: TData) => TData,
  getPreviousData?: () => TData | undefined
): Promise<OptimisticUpdateContext<TData>> {
  await queryClient.cancelQueries({ queryKey });

  const previousData = getPreviousData?.() || queryClient.getQueryData<TData>(queryKey);

  return { previousData };
}

/**
 * Rollback optimistic update on error
 */
export function rollbackOptimisticUpdate<TData>(
  queryClient: QueryClient,
  queryKey: readonly unknown[],
  context?: OptimisticUpdateContext<TData>
): void {
  if (context?.previousData !== undefined) {
    queryClient.setQueryData(queryKey, context.previousData);
  }
}

/**
 * Standard mutation error handler
 */
export function handleMutationError<TData, TVariables, TError>(
  error: TError,
  _variables: TVariables,
  context: OptimisticUpdateContext<TData> | undefined,
  config: {
    queryClient: QueryClient;
    queryKey: readonly unknown[];
    showToast: ToastContextType['showToast'];
    errorMessage: string;
  }
): void {
  rollbackOptimisticUpdate(config.queryClient, config.queryKey, context);
  const errorMsg = getErrorMessage(error, config.errorMessage);
  config.showToast(errorMsg, 'error');
}

/**
 * Standard mutation success handler
 */
export function handleMutationSuccess<TData, TVariables>(
  data: TData,
  variables: TVariables,
  config: {
    queryClient: QueryClient;
    queryKey: readonly unknown[];
    showToast: ToastContextType['showToast'];
    successMessage: string;
    updateCache?: (oldData: TData | undefined, newData: TData, variables: TVariables) => TData;
  }
): void {
  if (config.updateCache) {
    const currentData = config.queryClient.getQueryData<TData>(config.queryKey);
    const updatedData = config.updateCache(currentData, data, variables);
    config.queryClient.setQueryData(config.queryKey, updatedData);
  }
  config.showToast(config.successMessage, 'success');
}

