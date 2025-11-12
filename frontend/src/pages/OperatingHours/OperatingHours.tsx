import React, { useEffect, useState, useRef } from 'react';
import { Clock, Save } from 'lucide-react';
import { useAppSelector, useAppDispatch } from '@/store/hooks';
import { showToast } from '@/store/slices/uiSlice';
import { listOperatingHours, bulkUpdateOperatingHours } from '@/api/operatingHours';
import { Layout } from '@/components/layout/Layout';
import { Button } from '@/components/common/Button';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { EmptyState } from '@/components/common/EmptyState';
import type { OperatingHourResponse, OperatingHourRequest } from '@/types/operating-hours';

const DAYS_OF_WEEK = [
  'Monday',
  'Tuesday',
  'Wednesday',
  'Thursday',
  'Friday',
  'Saturday',
  'Sunday',
] as const;

export const OperatingHours: React.FC = () => {
  const dispatch = useAppDispatch();
  const { restaurant } = useAppSelector((state) => state.restaurant);
  const [hours, setHours] = useState<OperatingHourResponse[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const lastFetchedRestaurantId = useRef<string | null>(null);

  // Initialize form data with default hours
  const [formData, setFormData] = useState<Record<string, OperatingHourRequest>>(() => {
    const defaultHours: Record<string, OperatingHourRequest> = {};
    DAYS_OF_WEEK.forEach((day) => {
      defaultHours[day] = {
        day_of_week: day,
        open_time: '09:00:00',
        close_time: '22:00:00',
        is_closed: false,
      };
    });
    return defaultHours;
  });

  // Fetch existing hours
  useEffect(() => {
    const restaurantId = restaurant?.id;
    
    // Only fetch if restaurant ID changed
    if (!restaurantId || restaurantId === lastFetchedRestaurantId.current) {
      return;
    }

    lastFetchedRestaurantId.current = restaurantId;

    const fetchHours = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await listOperatingHours(restaurantId);
        setHours(data);

        // Populate form with existing hours
        if (data.length > 0) {
          const hoursMap: Record<string, OperatingHourRequest> = {};
          data.forEach((hour) => {
            hoursMap[hour.day_of_week] = {
              day_of_week: hour.day_of_week,
              open_time: hour.open_time,
              close_time: hour.close_time,
              is_closed: hour.is_closed,
            };
          });
          setFormData((prev) => ({ ...prev, ...hoursMap }));
        }
      } catch (err: any) {
        // Handle 403 - user not associated with restaurant
        if (err?.response?.status === 403) {
          setError('You are not associated with a restaurant. Please contact support.');
        } else {
          setError('Failed to load operating hours');
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchHours();
  }, [restaurant?.id]);

  const handleDayChange = (day: string, field: keyof OperatingHourRequest, value: string | boolean) => {
    setFormData((prev) => ({
      ...prev,
      [day]: {
        ...prev[day],
        [field]: value,
      },
    }));
  };

  const handleSave = async () => {
    if (!restaurant) return;

    setIsSaving(true);
    setError(null);
    setSuccess(false);

    try {
      const hoursArray: OperatingHourRequest[] = DAYS_OF_WEEK.map((day) => formData[day]);
      await bulkUpdateOperatingHours(restaurant.id, { hours: hoursArray });

      // Refresh hours
      const updatedHours = await listOperatingHours(restaurant.id);
      setHours(updatedHours);
      setSuccess(true);
      dispatch(showToast({ message: 'Operating hours updated successfully!', type: 'success' }));
    } catch (err) {
      const errorMessage = 'Failed to save operating hours. Please try again.';
      setError(errorMessage);
      dispatch(showToast({ message: errorMessage, type: 'error' }));
    } finally {
      setIsSaving(false);
    }
  };

  if (!restaurant) {
    return (
      <Layout>
        <div className="flex min-h-[400px] items-center justify-center">
          <div className="text-center">
            <EmptyState
              icon={Clock}
              title="No restaurant found"
              description="You are not associated with a restaurant. Please contact support or create a restaurant account."
            />
          </div>
        </div>
      </Layout>
    );
  }

  if (isLoading) {
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
          <h1 className="text-2xl font-bold text-gray-900 sm:text-3xl">Operating Hours</h1>
          <p className="mt-1 text-sm text-gray-600">
            Set your restaurant's operating hours for each day of the week.
          </p>
        </div>

        {/* Success/Error Messages */}
        {success && (
          <div className="rounded-lg bg-success/10 border border-success p-4 text-success">
            Operating hours updated successfully!
          </div>
        )}
        {error && (
          <div className="rounded-lg bg-error/10 border border-error p-4 text-error">
            {error}
          </div>
        )}

        {/* Hours Form */}
        <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <div className="space-y-4">
            {DAYS_OF_WEEK.map((day) => {
              const dayData = formData[day];
              return (
                <div
                  key={day}
                  className="flex flex-col gap-4 rounded-lg border border-gray-200 p-4 sm:flex-row sm:items-center"
                >
                  <div className="flex-1">
                    <label className="block text-sm font-medium text-gray-900">{day}</label>
                  </div>

                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={!dayData.is_closed}
                      onChange={(e) => handleDayChange(day, 'is_closed', !e.target.checked)}
                      className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                    />
                    <span className="text-sm text-gray-700">Open</span>
                  </div>

                  {!dayData.is_closed && (
                    <>
                      <div className="flex-1">
                        <label className="mb-1 block text-xs font-medium text-gray-700">
                          Open Time
                        </label>
                        <input
                          type="time"
                          value={dayData.open_time.substring(0, 5)}
                          onChange={(e) =>
                            handleDayChange(day, 'open_time', `${e.target.value}:00`)
                          }
                          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
                        />
                      </div>

                      <div className="flex-1">
                        <label className="mb-1 block text-xs font-medium text-gray-700">
                          Close Time
                        </label>
                        <input
                          type="time"
                          value={dayData.close_time.substring(0, 5)}
                          onChange={(e) =>
                            handleDayChange(day, 'close_time', `${e.target.value}:00`)
                          }
                          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
                        />
                      </div>
                    </>
                  )}

                  {dayData.is_closed && (
                    <div className="flex-1 text-sm text-gray-500">Closed</div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Save Button */}
          <div className="mt-6 flex justify-end">
            <Button
              onClick={handleSave}
              variant="primary"
              size="md"
              isLoading={isSaving}
              disabled={isSaving}
            >
              <Save className="mr-2 h-4 w-4" />
              Save Hours
            </Button>
          </div>
        </div>
      </div>
    </Layout>
  );
};

