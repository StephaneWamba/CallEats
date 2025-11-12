import React from 'react';
import { Skeleton } from './Skeleton';

export const ZoneCardSkeleton: React.FC = () => {
  return (
    <div className="rounded-xl border-2 border-gray-200 bg-white p-6 shadow-sm">
      <div className="mb-4 flex items-start justify-between">
        <div className="flex-1">
          <Skeleton variant="rectangular" height={24} width="60%" className="mb-2" />
          <Skeleton variant="text" height={16} width="80%" />
        </div>
        <div className="flex gap-2">
          <Skeleton variant="circular" width={32} height={32} />
          <Skeleton variant="circular" width={32} height={32} />
          <Skeleton variant="circular" width={32} height={32} />
        </div>
      </div>
      <div className="space-y-2">
        <Skeleton variant="text" height={20} width="70%" />
        <Skeleton variant="text" height={20} width="60%" />
      </div>
    </div>
  );
};

