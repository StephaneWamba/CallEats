import React from 'react';
import { Skeleton } from './Skeleton';

export const PageSkeleton: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-2">
        <Skeleton variant="rectangular" height={32} width="40%" />
        <Skeleton variant="text" height={16} width="60%" />
      </div>

      {/* Content Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <Skeleton variant="rectangular" height={24} width="60%" className="mb-4" />
            <Skeleton variant="text" height={16} width="100%" className="mb-2" />
            <Skeleton variant="text" height={16} width="80%" />
          </div>
        ))}
      </div>
    </div>
  );
};

