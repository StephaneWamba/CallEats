import React from 'react';
import { Skeleton } from './Skeleton';

export const MenuItemSkeleton: React.FC = () => {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
      <div className="flex gap-4">
        <Skeleton variant="rectangular" width={80} height={80} className="rounded-lg" />
        <div className="flex-1 space-y-2">
          <Skeleton variant="rectangular" height={20} width="60%" />
          <Skeleton variant="text" height={16} width="100%" />
          <Skeleton variant="text" height={16} width="80%" />
          <div className="flex items-center gap-2 mt-2">
            <Skeleton variant="rectangular" height={24} width={60} />
            <Skeleton variant="rectangular" height={24} width={60} />
          </div>
        </div>
      </div>
    </div>
  );
};

