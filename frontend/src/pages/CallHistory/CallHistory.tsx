import React, { useEffect, useState, useRef } from 'react';
import { Phone, Clock, DollarSign, CheckCircle2, XCircle, MessageSquare } from 'lucide-react';
import { useAppSelector, useAppDispatch } from '@/store/hooks';
import { showToast } from '@/store/slices/uiSlice';
import { listCalls, getCall } from '@/api/calls';
import { Layout } from '@/components/layout/Layout';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { EmptyState } from '@/components/common/EmptyState';
import { Modal } from '@/components/common/Modal';
import type { CallResponse } from '@/types/calls';

const formatDuration = (seconds: number | null): string => {
  if (!seconds) return 'N/A';
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

const getOutcomeIcon = (outcome: string) => {
  switch (outcome.toLowerCase()) {
    case 'completed':
    case 'success':
      return <CheckCircle2 className="h-4 w-4 text-success" />;
    case 'failed':
    case 'error':
      return <XCircle className="h-4 w-4 text-error" />;
    default:
      return <Clock className="h-4 w-4 text-gray-400" />;
  }
};

const getOutcomeColor = (outcome: string): string => {
  switch (outcome.toLowerCase()) {
    case 'completed':
    case 'success':
      return 'text-success';
    case 'failed':
    case 'error':
      return 'text-error';
    default:
      return 'text-gray-600';
  }
};

export const CallHistory: React.FC = () => {
  const dispatch = useAppDispatch();
  const { restaurant } = useAppSelector((state) => state.restaurant);
  const [calls, setCalls] = useState<CallResponse[]>([]);
  const [selectedCall, setSelectedCall] = useState<CallResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingDetails, setIsLoadingDetails] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const lastFetchedRestaurantId = useRef<string | null>(null);

  // Fetch calls
  useEffect(() => {
    const restaurantId = restaurant?.id;
    
    // Only fetch if restaurant ID changed
    if (!restaurantId || restaurantId === lastFetchedRestaurantId.current) {
      return;
    }

    lastFetchedRestaurantId.current = restaurantId;

    const fetchCalls = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await listCalls(restaurantId, 100);
        setCalls(data);
      } catch (err) {
        const errorMessage = 'Failed to load call history';
        setError(errorMessage);
        dispatch(showToast({ message: errorMessage, type: 'error' }));
      } finally {
        setIsLoading(false);
      }
    };

    fetchCalls();
  }, [restaurant?.id, dispatch]);

  const handleViewDetails = async (call: CallResponse) => {
    if (!restaurant) return;

    setIsLoadingDetails(true);
    try {
      const fullCall = await getCall(call.id, restaurant.id);
      setSelectedCall(fullCall);
    } catch (err) {
      const errorMessage = 'Failed to load call details';
      setError(errorMessage);
      dispatch(showToast({ message: errorMessage, type: 'error' }));
    } finally {
      setIsLoadingDetails(false);
    }
  };

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
          <div className="flex min-h-[400px] items-center justify-center">
            <LoadingSpinner size="lg" />
          </div>
        ) : calls.length === 0 ? (
          <EmptyState
            icon={Phone}
            title="No calls yet"
            description="When customers call your restaurant, call history will appear here"
          />
        ) : (
          <div className="space-y-4">
            {calls.map((call) => (
              <div
                key={call.id}
                className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-md cursor-pointer"
                onClick={() => handleViewDetails(call)}
              >
                <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <Phone className="h-5 w-5 text-gray-500" />
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">{call.caller}</h3>
                        <p className="text-sm text-gray-600">{formatDate(call.started_at)}</p>
                      </div>
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-4 text-sm">
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4 text-gray-500" />
                      <span className="text-gray-700">
                        {formatDuration(call.duration_seconds)}
                      </span>
                    </div>

                    {call.cost !== null && (
                      <div className="flex items-center gap-2">
                        <DollarSign className="h-4 w-4 text-gray-500" />
                        <span className="text-gray-700">${call.cost.toFixed(2)}</span>
                      </div>
                    )}

                    <div className="flex items-center gap-2">
                      {getOutcomeIcon(call.outcome)}
                      <span className={getOutcomeColor(call.outcome)}>{call.outcome}</span>
                    </div>

                    {call.messages && call.messages.length > 0 && (
                      <div className="flex items-center gap-2">
                        <MessageSquare className="h-4 w-4 text-gray-500" />
                        <span className="text-gray-700">{call.messages.length} messages</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Call Details Modal */}
        <Modal
          isOpen={!!selectedCall}
          onClose={() => setSelectedCall(null)}
          title="Call Details"
          size="lg"
        >
          {isLoadingDetails ? (
            <div className="flex min-h-[200px] items-center justify-center">
              <LoadingSpinner size="md" />
            </div>
          ) : selectedCall ? (
            <div className="space-y-6">
              {/* Call Info */}
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label className="text-xs font-medium text-gray-500">Caller</label>
                  <p className="mt-1 text-sm font-semibold text-gray-900">{selectedCall.caller}</p>
                </div>
                <div>
                  <label className="text-xs font-medium text-gray-500">Outcome</label>
                  <div className="mt-1 flex items-center gap-2">
                    {getOutcomeIcon(selectedCall.outcome)}
                    <p className={`text-sm font-semibold ${getOutcomeColor(selectedCall.outcome)}`}>
                      {selectedCall.outcome}
                    </p>
                  </div>
                </div>
                <div>
                  <label className="text-xs font-medium text-gray-500">Started</label>
                  <p className="mt-1 text-sm text-gray-900">{formatDate(selectedCall.started_at)}</p>
                </div>
                {selectedCall.ended_at && (
                  <div>
                    <label className="text-xs font-medium text-gray-500">Ended</label>
                    <p className="mt-1 text-sm text-gray-900">{formatDate(selectedCall.ended_at)}</p>
                  </div>
                )}
                <div>
                  <label className="text-xs font-medium text-gray-500">Duration</label>
                  <p className="mt-1 text-sm text-gray-900">
                    {formatDuration(selectedCall.duration_seconds)}
                  </p>
                </div>
                {selectedCall.cost !== null && (
                  <div>
                    <label className="text-xs font-medium text-gray-500">Cost</label>
                    <p className="mt-1 text-sm text-gray-900">${selectedCall.cost.toFixed(2)}</p>
                  </div>
                )}
              </div>

              {/* Messages */}
              {selectedCall.messages && selectedCall.messages.length > 0 && (
                <div>
                  <label className="mb-3 block text-sm font-semibold text-gray-900">
                    Conversation
                  </label>
                  <div className="max-h-96 space-y-3 overflow-y-auto rounded-lg border border-gray-200 p-4">
                    {selectedCall.messages.map((message, index) => (
                      <div
                        key={index}
                        className={`rounded-lg p-3 ${
                          message.role === 'user'
                            ? 'bg-primary/10 ml-8'
                            : message.role === 'assistant'
                              ? 'bg-gray-100 mr-8'
                              : 'bg-gray-50'
                        }`}
                      >
                        <div className="mb-1 flex items-center justify-between">
                          <span className="text-xs font-medium text-gray-600 capitalize">
                            {message.role}
                          </span>
                          <span className="text-xs text-gray-500">
                            {formatDate(message.timestamp)}
                          </span>
                        </div>
                        <p className="text-sm text-gray-900">{message.content}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : null}
        </Modal>
      </div>
    </Layout>
  );
};

