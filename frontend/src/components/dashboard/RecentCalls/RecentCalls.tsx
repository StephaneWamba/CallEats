import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Phone, ArrowRight, Clock, ChevronDown, ChevronUp, MessageSquare } from 'lucide-react';
import { ROUTES } from '../../../config/routes';
import { EmptyState } from '../../common/EmptyState';
import { useRestaurant } from '../../../hooks/useRestaurant';
import { useCalls, useCall } from '@/features/calls/hooks';
import { Skeleton } from '../../common/Skeleton';

const formatDate = (dateString: string | null | undefined): string => {
  if (!dateString) return 'N/A';
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) {
      return 'Invalid Date';
    }
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch (error) {
    return 'Invalid Date';
  }
};

const formatMessageDate = (dateString: string | null | undefined): string => {
  if (!dateString) return 'N/A';
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) {
      return 'Invalid Date';
    }
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch (error) {
    return 'Invalid Date';
  }
};

const formatDuration = (seconds: number | null): string => {
  if (!seconds) return 'N/A';
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

interface ExpandedCallProps {
  callId: string;
  restaurantId: string;
}

const ExpandedCall: React.FC<ExpandedCallProps> = ({ callId, restaurantId }) => {
  const { data: call, isLoading } = useCall(callId, restaurantId);

  if (isLoading) {
    return (
      <div className="mt-3 space-y-2 border-t border-gray-200 pt-3">
        <Skeleton variant="rectangular" height={20} width="40%" />
        <Skeleton variant="text" height={16} width="100%" />
        <Skeleton variant="text" height={16} width="80%" />
      </div>
    );
  }

  if (!call) {
    return (
      <div className="mt-3 border-t border-gray-200 pt-3 text-sm text-gray-500">
        Failed to load call details
      </div>
    );
  }

  return (
    <div className="mt-3 space-y-3 border-t border-gray-200 pt-3">
      {/* Call Info Summary */}
      <div className="grid grid-cols-2 gap-3 text-xs">
        <div>
          <span className="text-gray-500">Duration:</span>{' '}
          <span className="font-medium text-gray-900">{formatDuration(call.duration_seconds)}</span>
        </div>
        {call.cost !== null && (
          <div>
            <span className="text-gray-500">Cost:</span>{' '}
            <span className="font-medium text-gray-900">${call.cost.toFixed(2)}</span>
          </div>
        )}
      </div>

      {/* Messages */}
      {call.messages && call.messages.length > 0 ? (
        <div>
          <div className="mb-2 flex items-center gap-2 text-xs font-semibold text-gray-700">
            <MessageSquare className="h-3 w-3" />
            Conversation ({call.messages.length} messages)
          </div>
          <div className="max-h-64 space-y-2 overflow-y-auto rounded-lg border border-gray-200 bg-gray-50 p-3">
            {call.messages.map((message, index) => (
              <div
                key={index}
                className={`rounded-lg p-2.5 text-xs ${
                  message.role === 'user'
                    ? 'bg-primary/10 ml-4'
                    : message.role === 'assistant'
                      ? 'bg-white mr-4 border border-gray-200'
                      : 'bg-gray-100'
                }`}
              >
                <div className="mb-1 flex items-center justify-between">
                  <span className="font-medium text-gray-700 capitalize">{message.role}</span>
                  <span className="text-gray-500">{formatMessageDate(message.timestamp)}</span>
                </div>
                <p className="text-gray-900">{message.content}</p>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="text-xs text-gray-500">No messages available</div>
      )}
    </div>
  );
};

export const RecentCalls: React.FC = () => {
  const { data: restaurant } = useRestaurant();
  const { data: calls, isLoading } = useCalls(restaurant?.id, 5);
  const [expandedCallId, setExpandedCallId] = useState<string | null>(null);

  const handleCallClick = (callId: string) => {
    if (expandedCallId === callId) {
      setExpandedCallId(null);
    } else {
      setExpandedCallId(callId);
    }
  };

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">Recent Calls</h2>
        <Link
          to={ROUTES.CALL_HISTORY}
          className="flex items-center gap-1 text-sm font-medium text-primary hover:text-primary/80"
        >
          View all
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>

      {isLoading ? (
        <div className="flex min-h-[100px] items-center justify-center">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        </div>
      ) : !calls || calls.length === 0 ? (
        <EmptyState
          icon={Phone}
          title="No calls yet"
          description="When customers call, you'll see recent calls here"
        />
      ) : (
        <div className="space-y-3">
          {(calls || []).map((call) => {
            const isExpanded = expandedCallId === call.id;
            return (
              <div
                key={call.id}
                className="rounded-lg border border-gray-200 transition-colors hover:bg-gray-50"
              >
                <button
                  onClick={() => handleCallClick(call.id)}
                  className="flex w-full items-center justify-between p-3 text-left"
                >
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{call.caller}</p>
                    <p className="text-xs text-gray-500">{formatDate(call.started_at)}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="flex items-center gap-2 text-xs text-gray-600">
                      <Clock className="h-3 w-3" />
                      {formatDuration(call.duration_seconds)}
                    </div>
                    {isExpanded ? (
                      <ChevronUp className="h-4 w-4 text-gray-400" />
                    ) : (
                      <ChevronDown className="h-4 w-4 text-gray-400" />
                    )}
                  </div>
                </button>

                {isExpanded && restaurant?.id && (
                  <ExpandedCall
                    callId={call.id}
                    restaurantId={restaurant.id}
                  />
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

