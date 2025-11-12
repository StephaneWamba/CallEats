import React, { useState } from 'react';
import { Phone } from 'lucide-react';
import { useRestaurant } from '@/hooks/useRestaurant';
import { useCalls, useCall } from '@/features/calls/hooks';
import { Layout } from '@/components/layout/Layout';
import { PageSkeleton, Skeleton } from '@/components/common/Skeleton';
import { EmptyState } from '@/components/common/EmptyState';
import { Modal } from '@/components/common/Modal';
import type { CallResponse } from '@/types/calls';
import { CallCard } from './components/CallCard';
import { CallDetails } from './components/CallDetails';

export const CallHistory: React.FC = () => {
  const { data: restaurant, isLoading: isLoadingRestaurant } = useRestaurant();
  const { data: calls, isLoading } = useCalls(restaurant?.id, 100);
  const [selectedCallId, setSelectedCallId] = useState<string | null>(null);
  const { data: selectedCall, isLoading: isLoadingDetails } = useCall(
    selectedCallId || undefined,
    restaurant?.id
  );

  const handleViewDetails = (call: CallResponse) => {
    setSelectedCallId(call.id);
  };

  if (isLoadingRestaurant) {
    return (
      <Layout>
        <PageSkeleton />
      </Layout>
    );
  }

  if (!restaurant) {
    return (
      <Layout>
        <div className="flex min-h-[400px] items-center justify-center">
          <EmptyState
            icon={Phone}
            title="No restaurant found"
            description="You are not associated with a restaurant. Please contact support or create a restaurant account."
          />
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900 sm:text-3xl">Call History</h1>
          <p className="mt-1 text-sm text-gray-600">
            View and manage all customer calls to your restaurant.
          </p>
        </div>

        {/* Calls List */}
        {isLoading ? (
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
                <div className="flex items-center gap-4">
                  <Skeleton variant="circular" width={48} height={48} />
                  <div className="flex-1 space-y-2">
                    <Skeleton variant="rectangular" height={20} width="40%" />
                    <Skeleton variant="text" height={16} width="60%" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : !calls || calls.length === 0 ? (
          <EmptyState
            icon={Phone}
            title="No calls yet"
            description="When customers call your restaurant, call history will appear here"
          />
        ) : (
          <div className="space-y-4">
            {calls.map((call) => (
              <CallCard key={call.id} call={call} onViewDetails={handleViewDetails} />
            ))}
          </div>
        )}

        {/* Call Details Modal */}
        <Modal
          isOpen={!!selectedCallId}
          onClose={() => setSelectedCallId(null)}
          title="Call Details"
          size="lg"
        >
          {isLoadingDetails ? (
            <div className="space-y-4">
              <Skeleton variant="rectangular" height={24} width="60%" />
              <Skeleton variant="text" height={16} width="100%" />
              <Skeleton variant="text" height={16} width="80%" />
            </div>
          ) : selectedCall ? (
            <CallDetails call={selectedCall} />
          ) : null}
        </Modal>
      </div>
    </Layout>
  );
};
