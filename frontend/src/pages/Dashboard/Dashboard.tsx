import React from 'react';
import { Phone, UtensilsCrossed, FolderTree, CheckCircle2 } from 'lucide-react';
import { Layout } from '../../components/layout/Layout';
import { StatsCard } from '../../components/dashboard/StatsCard';
import { QuickActions } from '../../components/dashboard/QuickActions';
import { RecentCalls } from '../../components/dashboard/RecentCalls';
import { MenuPreview } from '../../components/dashboard/MenuPreview';
import { PageSkeleton } from '../../components/common/Skeleton';
import { useRestaurant, useRestaurantStats } from '../../hooks/useRestaurant';
import { isForbiddenError } from '../../utils/errorHandler';

export const Dashboard: React.FC = () => {
  const { data: restaurant, isLoading: isLoadingRestaurant, error: restaurantError } = useRestaurant();
  const { data: stats, isLoading: isLoadingStats } = useRestaurantStats(restaurant?.id);

  const isLoading = isLoadingRestaurant || isLoadingStats;

  if (isLoading) {
    return (
      <Layout>
        <PageSkeleton />
      </Layout>
    );
  }

  // Handle case where user doesn't have a restaurant (403 error)
  if (restaurantError && isForbiddenError(restaurantError)) {
    return (
      <Layout>
        <div className="flex min-h-[400px] items-center justify-center">
          <div className="text-center">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">No restaurant found</h2>
            <p className="text-gray-600">
              You are not associated with a restaurant. Please contact support or create a restaurant account.
            </p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900 sm:text-3xl">Dashboard</h1>
          <p className="mt-1 text-sm text-gray-600">
            Welcome back! Here's what's happening with your restaurant today.
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatsCard
            title="Calls Today"
            value={stats?.total_calls_today ?? 0}
            icon={Phone}
            iconColor="text-primary"
            bgColor="bg-primary/10"
          />
          <StatsCard
            title="Menu Items"
            value={stats?.menu_items_count ?? 0}
            icon={UtensilsCrossed}
            iconColor="text-secondary"
            bgColor="bg-secondary/10"
          />
          <StatsCard
            title="Categories"
            value={stats?.categories_count ?? 0}
            icon={FolderTree}
            iconColor="text-success"
            bgColor="bg-success/10"
          />
          <StatsCard
            title="Phone Status"
            value={stats?.phone_status === 'active' ? 'Active' : 'Inactive'}
            icon={CheckCircle2}
            iconColor={stats?.phone_status === 'active' ? 'text-success' : 'text-gray-400'}
            bgColor={stats?.phone_status === 'active' ? 'bg-success/10' : 'bg-gray-100'}
          />
        </div>

        {/* Quick Actions */}
        <QuickActions />

        {/* Recent Activity Grid */}
        <div className="grid gap-6 lg:grid-cols-2">
          <RecentCalls />
          <MenuPreview />
        </div>
      </div>
    </Layout>
  );
};

