import React, { useEffect, useState, useRef } from 'react';
import { Phone, UtensilsCrossed, FolderTree, CheckCircle2 } from 'lucide-react';
import { useAppSelector, useAppDispatch } from '../../store/hooks';
import { setRestaurant, setStats } from '../../store/slices/restaurantSlice';
import { getMyRestaurant, getRestaurantStats } from '../../api/restaurants';
import { Layout } from '../../components/layout/Layout';
import { StatsCard } from '../../components/dashboard/StatsCard';
import { QuickActions } from '../../components/dashboard/QuickActions';
import { RecentCalls } from '../../components/dashboard/RecentCalls';
import { MenuPreview } from '../../components/dashboard/MenuPreview';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';

export const Dashboard: React.FC = () => {
  const dispatch = useAppDispatch();
  const { restaurant: currentRestaurant, stats } = useAppSelector((state) => state.restaurant);
  const [isLoading, setIsLoading] = useState(false);
  const [isInitialLoad, setIsInitialLoad] = useState(true);
  const hasFetched = useRef(false);

  useEffect(() => {
    // Only fetch once on mount if data is missing
    if (hasFetched.current) return;
    
    const fetchDashboardData = async () => {
      if (!currentRestaurant || !stats) {
        hasFetched.current = true;
        setIsLoading(true);
        try {
          // Fetch restaurant data
          const restaurant = await getMyRestaurant();
          dispatch(setRestaurant(restaurant));

          // Fetch stats
          const statsData = await getRestaurantStats(restaurant.id);
          dispatch(setStats(statsData));
        } catch (error: any) {
          // Handle 403 - user not associated with restaurant
          // Don't retry, just mark as loaded
          if (error?.response?.status === 403) {
            // User doesn't have a restaurant yet - this is expected for new accounts
            // Don't set error state, just continue without restaurant data
          }
          // For other errors, silently fail - component will show empty state
        } finally {
          setIsLoading(false);
          setIsInitialLoad(false);
        }
      } else {
        setIsInitialLoad(false);
      }
    };

    fetchDashboardData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (isInitialLoad && isLoading) {
    return (
      <Layout>
        <div className="flex min-h-[400px] items-center justify-center">
          <LoadingSpinner size="lg" />
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

