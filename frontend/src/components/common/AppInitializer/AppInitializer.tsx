import React, { useState, useEffect, useRef } from 'react';
import { LoadingSpinner } from '../LoadingSpinner';

interface AppInitializerProps {
  children: React.ReactNode;
  onInitializationError?: (error: Error) => void;
}

type InitializationState = 'initializing' | 'ready' | 'error';

interface InitializationError {
  message: string;
  error?: Error;
}

/**
 * AppInitializer component handles the initialization sequence
 * and provides visible feedback during app startup
 */
export const AppInitializer: React.FC<AppInitializerProps> = ({
  children,
  onInitializationError,
}) => {
  const [state, setState] = useState<InitializationState>('initializing');
  const [error, setError] = useState<InitializationError | null>(null);
  const initializationTimeout = useRef<number | null>(null);
  const hasInitialized = useRef(false);

  useEffect(() => {
    if (hasInitialized.current) return;
    hasInitialized.current = true;

    // Set a timeout to detect if initialization is taking too long
    initializationTimeout.current = window.setTimeout(() => {
      // Some slow networks might need more time
    }, 10000); // 10 seconds timeout warning

    // Simulate initialization check
    // In a real scenario, this would check if all critical services are ready
    const initialize = async () => {
      try {
        // Check if critical APIs are available
        // This is a lightweight check - actual auth happens in AuthProvider
        await new Promise((resolve) => {
          // Give React time to mount and providers to initialize
          // This ensures we don't show loading unnecessarily
          setTimeout(resolve, 100);
        });

        setState('ready');
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Initialization failed');
        setError({ message: error.message, error });
        setState('error');
        
        if (onInitializationError) {
          onInitializationError(error);
        }
      } finally {
        if (initializationTimeout.current) {
          clearTimeout(initializationTimeout.current);
        }
      }
    };

    initialize();

    return () => {
      if (initializationTimeout.current) {
        clearTimeout(initializationTimeout.current);
      }
    };
  }, [state, onInitializationError]);

  // Loading state - show spinner with message
  if (state === 'initializing') {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-gray-50">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-sm text-gray-600">Initializing application...</p>
        </div>
      </div>
    );
  }

  // Error state - show error UI with retry option
  if (state === 'error') {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-gray-50 px-4">
        <div className="w-full max-w-md rounded-lg border border-red-200 bg-white p-6 shadow-sm">
          <div className="text-center">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-red-100">
              <svg
                className="h-6 w-6 text-red-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </div>
            <h1 className="mb-2 text-xl font-semibold text-gray-900">Initialization Error</h1>
            <p className="mb-4 text-sm text-gray-600">
              {error?.message || 'Failed to initialize the application'}
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => window.location.reload()}
                className="flex-1 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-primary/90"
              >
                Reload Page
              </button>
              {error?.error && (
                <button
                  onClick={() => {
                    const errorObj = error.error;
                    if (errorObj) {
                      alert(`Error details: ${errorObj.message}`);
                    }
                  }}
                  className="rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
                >
                  Details
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Ready state - render children
  return <>{children}</>;
};

