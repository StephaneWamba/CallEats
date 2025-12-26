import React from 'react';
import { Phone, Clock, DollarSign, MessageSquare, CheckCircle2, XCircle } from 'lucide-react';
import type { CallResponse } from '@/types/calls';

interface CallCardProps {
  call: CallResponse;
  onViewDetails: (call: CallResponse) => void;
}

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

const formatDuration = (seconds: number | null): string => {
  if (!seconds) return 'N/A';
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
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

export const CallCard: React.FC<CallCardProps> = ({ call, onViewDetails }) => {
  return (
    <div
      className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-md cursor-pointer"
      onClick={() => onViewDetails(call)}
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
  );
};


