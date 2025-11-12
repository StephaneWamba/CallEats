import React, { lazy, Suspense } from 'react';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';

// Lazy load the heavy Leaflet map component with error handling
const DeliveryZoneMap = lazy(() => 
  import('./DeliveryZoneMap')
    .then(m => ({ default: m.DeliveryZoneMap }))
    .catch((error) => {
      console.error('Failed to load DeliveryZoneMap:', error);
      // Return a fallback component
      return {
        default: () => (
          <div className="flex h-[500px] items-center justify-center rounded-lg border border-gray-200 bg-gray-50">
            <div className="text-center">
              <p className="text-sm text-gray-600">Failed to load map. Please refresh the page.</p>
            </div>
          </div>
        ),
      };
    })
);

// Re-export the type for convenience
export type { DeliveryZoneMapProps } from './DeliveryZoneMap';

/**
 * Lazy-loaded wrapper for DeliveryZoneMap
 * Leaflet is a large library (~300KB), so we lazy load it
 * This component only loads when the map is actually needed
 */
export const LazyDeliveryZoneMap: React.FC<React.ComponentProps<typeof DeliveryZoneMap>> = (props) => {
  return (
    <Suspense
      fallback={
        <div className="flex h-[500px] items-center justify-center rounded-lg border border-gray-200 bg-gray-50">
          <LoadingSpinner size="lg" />
          <span className="ml-3 text-sm text-gray-600">Loading map...</span>
        </div>
      }
    >
      <DeliveryZoneMap {...props} />
    </Suspense>
  );
};

