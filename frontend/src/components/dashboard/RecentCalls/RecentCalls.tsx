import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Phone, ArrowRight, Clock } from 'lucide-react';
import { ROUTES } from '../../../config/routes';
import { EmptyState } from '../../common/EmptyState';
import { useAppSelector } from '../../../store/hooks';
import { listCalls } from '../../../api/calls';
import type { CallResponse } from '../../../types/calls';

const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

const formatDuration = (seconds: number | null): string => {
  if (!seconds) return 'N/A';
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

export const RecentCalls: React.FC = () => {
  const { restaurant } = useAppSelector((state) => state.restaurant);
  const [calls, setCalls] = useState<CallResponse[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchCalls = async () => {
      if (!restaurant) return;

      setIsLoading(true);
      try {
        const data = await listCalls(restaurant.id, 5); // Get last 5 calls
        setCalls(data);
      } catch (err) {
        console.error('Failed to fetch recent calls:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchCalls();
  }, [restaurant]);

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
      ) : calls.length === 0 ? (
        <EmptyState
          icon={Phone}
          title="No calls yet"
          description="When customers call, you'll see recent calls here"
        />
      ) : (
        <div className="space-y-3">
          {calls.map((call) => (
            <Link
              key={call.id}
              to={ROUTES.CALL_HISTORY}
              className="block rounded-lg border border-gray-200 p-3 transition-colors hover:bg-gray-50"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">{call.caller}</p>
                  <p className="text-xs text-gray-500">{formatDate(call.started_at)}</p>
                </div>
                <div className="flex items-center gap-2 text-xs text-gray-600">
                  <Clock className="h-3 w-3" />
                  {formatDuration(call.duration_seconds)}
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};

