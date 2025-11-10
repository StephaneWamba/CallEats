import React, { useEffect, useState } from 'react';
import { Plus, MapPin, Edit2, Trash2, DollarSign, Package } from 'lucide-react';
import { useAppSelector } from '@/store/hooks';
import {
  listDeliveryZones,
  createDeliveryZone,
  updateDeliveryZone,
  deleteDeliveryZone,
} from '@/api/deliveryZones';
import { Layout } from '@/components/layout/Layout';
import { Button } from '@/components/common/Button';
import { Input } from '@/components/common/Input';
import { Modal } from '@/components/common/Modal';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { EmptyState } from '@/components/common/EmptyState';
import type {
  DeliveryZoneResponse,
  CreateDeliveryZoneRequest,
  UpdateDeliveryZoneRequest,
} from '@/types/delivery-zones';

export const DeliveryZones: React.FC = () => {
  const { restaurant } = useAppSelector((state) => state.restaurant);
  const [zones, setZones] = useState<DeliveryZoneResponse[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingZone, setEditingZone] = useState<DeliveryZoneResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  // Form state
  const [formData, setFormData] = useState<CreateDeliveryZoneRequest>({
    zone_name: '',
    description: '',
    delivery_fee: 0,
    min_order: undefined,
  });

  // Fetch zones
  useEffect(() => {
    const fetchZones = async () => {
      if (!restaurant) return;

      setIsLoading(true);
      setError(null);
      try {
        const data = await listDeliveryZones(restaurant.id);
        setZones(data);
      } catch (err) {
        console.error('Failed to fetch delivery zones:', err);
        setError('Failed to load delivery zones');
      } finally {
        setIsLoading(false);
      }
    };

    fetchZones();
  }, [restaurant]);

  const handleOpenForm = (zone?: DeliveryZoneResponse) => {
    if (zone) {
      setEditingZone(zone);
      setFormData({
        zone_name: zone.zone_name,
        description: zone.description || '',
        delivery_fee: zone.delivery_fee,
        min_order: zone.min_order || undefined,
      });
    } else {
      setEditingZone(null);
      setFormData({
        zone_name: '',
        description: '',
        delivery_fee: 0,
        min_order: undefined,
      });
    }
    setIsFormOpen(true);
    setError(null);
  };

  const handleCloseForm = () => {
    setIsFormOpen(false);
    setEditingZone(null);
    setFormData({
      zone_name: '',
      description: '',
      delivery_fee: 0,
      min_order: undefined,
    });
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!restaurant) return;

    setError(null);
    setIsLoading(true);

    try {
      if (editingZone) {
        const updateData: UpdateDeliveryZoneRequest = {
          zone_name: formData.zone_name,
          description: formData.description || undefined,
          delivery_fee: formData.delivery_fee,
          min_order: formData.min_order || undefined,
        };
        await updateDeliveryZone(restaurant.id, editingZone.id, updateData);
      } else {
        await createDeliveryZone(restaurant.id, formData);
      }

      // Refresh zones
      const updatedZones = await listDeliveryZones(restaurant.id);
      setZones(updatedZones);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
      handleCloseForm();
    } catch (err: any) {
      console.error('Failed to save delivery zone:', err);
      setError(err?.response?.data?.detail || 'Failed to save delivery zone');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (zoneId: string) => {
    if (!restaurant) return;
    if (!confirm('Are you sure you want to delete this delivery zone?')) return;

    setIsLoading(true);
    setError(null);

    try {
      await deleteDeliveryZone(restaurant.id, zoneId);
      const updatedZones = await listDeliveryZones(restaurant.id);
      setZones(updatedZones);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err: any) {
      console.error('Failed to delete delivery zone:', err);
      setError(err?.response?.data?.detail || 'Failed to delete delivery zone');
    } finally {
      setIsLoading(false);
    }
  };

  if (!restaurant) {
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
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 sm:text-3xl">Delivery Zones</h1>
            <p className="mt-1 text-sm text-gray-600">
              Manage delivery zones and their fees for your restaurant.
            </p>
          </div>
          <Button onClick={() => handleOpenForm()} variant="primary" size="md">
            <Plus className="mr-2 h-4 w-4" />
            Add Zone
          </Button>
        </div>

        {/* Success/Error Messages */}
        {success && (
          <div className="rounded-lg bg-success/10 border border-success p-4 text-success">
            Delivery zone {editingZone ? 'updated' : 'created'} successfully!
          </div>
        )}
        {error && (
          <div className="rounded-lg bg-error/10 border border-error p-4 text-error">{error}</div>
        )}

        {/* Zones List */}
        {isLoading && zones.length === 0 ? (
          <div className="flex min-h-[400px] items-center justify-center">
            <LoadingSpinner size="lg" />
          </div>
        ) : zones.length === 0 ? (
          <EmptyState
            icon={MapPin}
            title="No delivery zones"
            description="Create your first delivery zone to get started"
            action={
              <Button onClick={() => handleOpenForm()} variant="primary" size="md">
                <Plus className="mr-2 h-4 w-4" />
                Add Zone
              </Button>
            }
          />
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {zones.map((zone) => (
              <div
                key={zone.id}
                className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-md"
              >
                <div className="mb-4 flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900">{zone.zone_name}</h3>
                    {zone.description && (
                      <p className="mt-1 text-sm text-gray-600">{zone.description}</p>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleOpenForm(zone)}
                      className="rounded-lg p-2 text-gray-600 transition-colors hover:bg-gray-100 hover:text-primary"
                      aria-label="Edit zone"
                    >
                      <Edit2 className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(zone.id)}
                      className="rounded-lg p-2 text-gray-600 transition-colors hover:bg-gray-100 hover:text-error"
                      aria-label="Delete zone"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm">
                    <DollarSign className="h-4 w-4 text-gray-500" />
                    <span className="text-gray-600">Delivery Fee:</span>
                    <span className="font-semibold text-gray-900">
                      ${zone.delivery_fee.toFixed(2)}
                    </span>
                  </div>
                  {zone.min_order && (
                    <div className="flex items-center gap-2 text-sm">
                      <Package className="h-4 w-4 text-gray-500" />
                      <span className="text-gray-600">Min Order:</span>
                      <span className="font-semibold text-gray-900">
                        ${zone.min_order.toFixed(2)}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Create/Edit Modal */}
        <Modal
          isOpen={isFormOpen}
          onClose={handleCloseForm}
          title={editingZone ? 'Edit Delivery Zone' : 'Create Delivery Zone'}
          size="md"
        >
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Zone Name"
              value={formData.zone_name}
              onChange={(e) => setFormData({ ...formData, zone_name: e.target.value })}
              required
              placeholder="e.g., Downtown, North Side"
            />

            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Description (optional)
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
                placeholder="Describe the delivery area..."
              />
            </div>

            <Input
              label="Delivery Fee"
              type="number"
              step="0.01"
              min="0"
              value={formData.delivery_fee}
              onChange={(e) =>
                setFormData({ ...formData, delivery_fee: parseFloat(e.target.value) || 0 })
              }
              required
            />

            <Input
              label="Minimum Order (optional)"
              type="number"
              step="0.01"
              min="0"
              value={formData.min_order || ''}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  min_order: e.target.value ? parseFloat(e.target.value) : undefined,
                })
              }
              placeholder="No minimum"
            />

            {error && (
              <div className="rounded-lg bg-error/10 border border-error p-3 text-sm text-error">
                {error}
              </div>
            )}

            <div className="flex justify-end gap-3 pt-4">
              <Button type="button" variant="secondary" onClick={handleCloseForm}>
                Cancel
              </Button>
              <Button type="submit" variant="primary" isLoading={isLoading}>
                {editingZone ? 'Update' : 'Create'} Zone
              </Button>
            </div>
          </form>
        </Modal>
      </div>
    </Layout>
  );
};

