import React, { useEffect, useState, useRef } from 'react';
import { Settings as SettingsIcon, Building2, Phone, Lock, Save } from 'lucide-react';
import { useAppSelector, useAppDispatch } from '@/store/hooks';
import { setRestaurant } from '@/store/slices/restaurantSlice';
import { showToast } from '@/store/slices/uiSlice';
import { getMyRestaurant, updateRestaurant } from '@/api/restaurants';
import { changePassword } from '@/api/auth';
import { Layout } from '@/components/layout/Layout';
import { Button } from '@/components/common/Button';
import { Input } from '@/components/common/Input';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { EmptyState } from '@/components/common/EmptyState';
import type { UpdateRestaurantRequest } from '@/types/restaurant';
import type { ChangePasswordRequest } from '@/types/auth';

export const Settings: React.FC = () => {
  const dispatch = useAppDispatch();
  const { restaurant } = useAppSelector((state) => state.restaurant);
  const [isLoading, setIsLoading] = useState(false);
  const [isSavingRestaurant, setIsSavingRestaurant] = useState(false);
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Restaurant form state
  const [restaurantName, setRestaurantName] = useState('');
  const lastSyncedRestaurantId = useRef<string | null>(null);

  // Password form state
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });

  // Fetch restaurant data and sync name
  useEffect(() => {
    const restaurantId = restaurant?.id;
    
    const fetchRestaurant = async () => {
      if (!restaurantId) {
        if (lastSyncedRestaurantId.current === null) {
          setIsLoading(true);
          try {
            const data = await getMyRestaurant();
            dispatch(setRestaurant(data));
            setRestaurantName(data.name);
            lastSyncedRestaurantId.current = data.id;
          } catch (err) {
            setError('Failed to load restaurant settings');
          } finally {
            setIsLoading(false);
          }
        }
      } else if (restaurantId !== lastSyncedRestaurantId.current && restaurant) {
        // Restaurant changed (e.g., from another component), sync the name
        setRestaurantName(restaurant.name);
        lastSyncedRestaurantId.current = restaurantId;
      }
    };

    fetchRestaurant();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [restaurant?.id]);

  const handleUpdateRestaurant = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!restaurant) return;

    setIsSavingRestaurant(true);
    setError(null);
    setSuccess(null);

    try {
      const updateData: UpdateRestaurantRequest = {
        name: restaurantName,
      };
      const updated = await updateRestaurant(restaurant.id, updateData);
      dispatch(setRestaurant(updated));
      const successMessage = 'Restaurant name updated successfully!';
      setSuccess(successMessage);
      dispatch(showToast({ message: successMessage, type: 'success' }));
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      const errorMessage = err?.response?.data?.detail || 'Failed to update restaurant name';
      setError(errorMessage);
      dispatch(showToast({ message: errorMessage, type: 'error' }));
    } finally {
      setIsSavingRestaurant(false);
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();

    if (passwordData.new_password !== passwordData.confirm_password) {
      setError('New passwords do not match');
      return;
    }

    if (passwordData.new_password.length < 8) {
      setError('New password must be at least 8 characters long');
      return;
    }

    setIsChangingPassword(true);
    setError(null);
    setSuccess(null);

    try {
      const changePasswordData: ChangePasswordRequest = {
        current_password: passwordData.current_password,
        new_password: passwordData.new_password,
      };
      await changePassword(changePasswordData);
      const successMessage = 'Password changed successfully!';
      setSuccess(successMessage);
      dispatch(showToast({ message: successMessage, type: 'success' }));
      setPasswordData({
        current_password: '',
        new_password: '',
        confirm_password: '',
      });
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      const errorMessage = err?.response?.data?.detail || 'Failed to change password';
      setError(errorMessage);
      dispatch(showToast({ message: errorMessage, type: 'error' }));
    } finally {
      setIsChangingPassword(false);
    }
  };

  if (isLoading) {
    return (
      <Layout>
        <div className="flex min-h-[400px] items-center justify-center">
          <LoadingSpinner size="lg" />
        </div>
      </Layout>
    );
  }

  if (!restaurant) {
    return (
      <Layout>
        <div className="flex min-h-[400px] items-center justify-center">
          <div className="text-center">
            <EmptyState
              icon={SettingsIcon}
              title="No restaurant found"
              description="You are not associated with a restaurant. Please contact support or create a restaurant account."
            />
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
          <h1 className="text-2xl font-bold text-gray-900 sm:text-3xl">Settings</h1>
          <p className="mt-1 text-sm text-gray-600">
            Manage your restaurant settings and account preferences.
          </p>
        </div>

        {/* Success/Error Messages */}
        {success && (
          <div className="rounded-lg bg-success/10 border border-success p-4 text-success">
            {success}
          </div>
        )}
        {error && (
          <div className="rounded-lg bg-error/10 border border-error p-4 text-error">{error}</div>
        )}

        {/* Restaurant Information */}
        <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <div className="mb-4 flex items-center gap-2">
            <Building2 className="h-5 w-5 text-gray-500" />
            <h2 className="text-lg font-semibold text-gray-900">Restaurant Information</h2>
          </div>

          <div className="space-y-4">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Restaurant Name</label>
              <form onSubmit={handleUpdateRestaurant} className="flex gap-3">
                <Input
                  value={restaurantName}
                  onChange={(e) => setRestaurantName(e.target.value)}
                  placeholder="Restaurant name"
                  className="flex-1"
                  required
                />
                <Button type="submit" variant="primary" isLoading={isSavingRestaurant}>
                  <Save className="mr-2 h-4 w-4" />
                  Save
                </Button>
              </form>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="mb-1 block text-xs font-medium text-gray-500">Phone Number</label>
                <div className="flex items-center gap-2">
                  <Phone className="h-4 w-4 text-gray-400" />
                  <p className="text-sm text-gray-900">
                    {restaurant.phone_number || 'Not assigned'}
                  </p>
                </div>
              </div>

              <div>
                <label className="mb-1 block text-xs font-medium text-gray-500">Created At</label>
                <p className="text-sm text-gray-900">
                  {new Date(restaurant.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Change Password */}
        <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <div className="mb-4 flex items-center gap-2">
            <Lock className="h-5 w-5 text-gray-500" />
            <h2 className="text-lg font-semibold text-gray-900">Change Password</h2>
          </div>

          <form onSubmit={handleChangePassword} className="space-y-4">
            <Input
              label="Current Password"
              type="password"
              name="current-password"
              value={passwordData.current_password}
              onChange={(e) =>
                setPasswordData({ ...passwordData, current_password: e.target.value })
              }
              required
              placeholder="Enter current password"
            />

            <Input
              label="New Password"
              type="password"
              name="new-password"
              value={passwordData.new_password}
              onChange={(e) =>
                setPasswordData({ ...passwordData, new_password: e.target.value })
              }
              required
              placeholder="Enter new password (min 8 characters)"
              minLength={8}
            />

            <Input
              label="Confirm New Password"
              type="password"
              name="confirm-password"
              value={passwordData.confirm_password}
              onChange={(e) =>
                setPasswordData({ ...passwordData, confirm_password: e.target.value })
              }
              required
              placeholder="Confirm new password"
            />

            <div className="flex justify-end">
              <Button type="submit" variant="primary" isLoading={isChangingPassword}>
                <Lock className="mr-2 h-4 w-4" />
                Change Password
              </Button>
            </div>
          </form>
        </div>
      </div>
    </Layout>
  );
};

