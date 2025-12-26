import React from 'react';
import { CheckCircle2, XCircle, Clock } from 'lucide-react';
import type { CallResponse } from '@/types/calls';

interface CallDetailsProps {
  call: CallResponse;
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

export const CallDetails: React.FC<CallDetailsProps> = ({ call }) => {
  return (
    <div className="space-y-6">
      {/* Call Info */}
      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label className="text-xs font-medium text-gray-500">Caller</label>
          <p className="mt-1 text-sm font-semibold text-gray-900">{call.caller}</p>
        </div>
        <div>
          <label className="text-xs font-medium text-gray-500">Outcome</label>
          <div className="mt-1 flex items-center gap-2">
            {getOutcomeIcon(call.outcome)}
            <p className={`text-sm font-semibold ${getOutcomeColor(call.outcome)}`}>
              {call.outcome}
            </p>
          </div>
        </div>
        <div>
          <label className="text-xs font-medium text-gray-500">Started</label>
          <p className="mt-1 text-sm text-gray-900">{formatDate(call.started_at)}</p>
        </div>
        {call.ended_at && (
          <div>
            <label className="text-xs font-medium text-gray-500">Ended</label>
            <p className="mt-1 text-sm text-gray-900">{formatDate(call.ended_at)}</p>
          </div>
        )}
        <div>
          <label className="text-xs font-medium text-gray-500">Duration</label>
          <p className="mt-1 text-sm text-gray-900">
            {formatDuration(call.duration_seconds)}
          </p>
        </div>
        {call.cost !== null && (
          <div>
            <label className="text-xs font-medium text-gray-500">Cost</label>
            <p className="mt-1 text-sm text-gray-900">${call.cost.toFixed(2)}</p>
          </div>
        )}
      </div>

      {/* Messages */}
      {call.messages && call.messages.length > 0 && (
        <div>
          <label className="mb-3 block text-sm font-semibold text-gray-900">
            Conversation
          </label>
          <div className="max-h-96 space-y-3 overflow-y-auto rounded-lg border border-gray-200 p-4">
            {call.messages.map((message, index) => (
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
  );
};


