import React, { useEffect, useState, useRef } from 'react';
import { Plus, MapPin, Edit2, Trash2, DollarSign, Package, Map } from 'lucide-react';
import { useAppSelector, useAppDispatch } from '@/store/hooks';
import { showToast } from '@/store/slices/uiSlice';
import {
  listDeliveryZones,
  createDeliveryZone,
  updateDeliveryZone,
  deleteDeliveryZone,
  setZoneBoundary,
  getZoneBoundary,
} from '@/api/deliveryZones';
import { Layout } from '@/components/layout/Layout';
import { Button } from '@/components/common/Button';
import { Input } from '@/components/common/Input';
import { Modal } from '@/components/common/Modal';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { EmptyState } from '@/components/common/EmptyState';
import { DeliveryZoneMap } from '@/components/delivery-zones/DeliveryZoneMap';
import type {
  DeliveryZoneResponse,
  CreateDeliveryZoneRequest,
  UpdateDeliveryZoneRequest,
} from '@/types/delivery-zones';

export const DeliveryZones: React.FC = () => {
  const dispatch = useAppDispatch();
  const { restaurant } = useAppSelector((state) => state.restaurant);
  const [zones, setZones] = useState<DeliveryZoneResponse[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingZone, setEditingZone] = useState<DeliveryZoneResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [zoneToDelete, setZoneToDelete] = useState<DeliveryZoneResponse | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [selectedZone, setSelectedZone] = useState<DeliveryZoneResponse | null>(null);
  const [showMap, setShowMap] = useState(true);
  const lastFetchedRestaurantId = useRef<string | null>(null);

  // Form state
  const [formData, setFormData] = useState<CreateDeliveryZoneRequest>({
    zone_name: '',
    description: '',
    delivery_fee: 0,
    min_order: undefined,
  });

  // Fetch zones
  useEffect(() => {
    const restaurantId = restaurant?.id;
    
    // Only fetch if restaurant ID changed
    if (!restaurantId || restaurantId === lastFetchedRestaurantId.current) {
      return;
    }

    lastFetchedRestaurantId.current = restaurantId;

    const fetchZones = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await listDeliveryZones(restaurantId);
        // Fetch boundaries for zones that don't have them loaded
        const zonesWithBoundaries = await Promise.all(
          data.map(async (zone) => {
            if (!zone.boundary) {
              try {
                const boundary = await getZoneBoundary(restaurantId, zone.id);
                return { ...zone, boundary: boundary?.geometry || null };
              } catch {
                return zone;
              }
            }
            return zone;
          })
        );
        setZones(zonesWithBoundaries);
      } catch (err) {
        setError('Failed to load delivery zones');
      } finally {
        setIsLoading(false);
      }
    };

    fetchZones();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [restaurant?.id]);

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
      dispatch(showToast({ 
        message: `Delivery zone ${editingZone ? 'updated' : 'created'} successfully!`, 
        type: 'success' 
      }));
      handleCloseForm();
    } catch (err: any) {
      const errorMessage = err?.response?.data?.detail || 'Failed to save delivery zone';
      setError(errorMessage);
      dispatch(showToast({ message: errorMessage, type: 'error' }));
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = (zone: DeliveryZoneResponse) => {
    setZoneToDelete(zone);
  };

  const handleConfirmDelete = async () => {
    if (!restaurant || !zoneToDelete) return;

    setIsDeleting(true);
    setError(null);

    try {
      await deleteDeliveryZone(restaurant.id, zoneToDelete.id);
      const updatedZones = await listDeliveryZones(restaurant.id);
      setZones(updatedZones);
      setSuccess(true);
      dispatch(showToast({ 
        message: `"${zoneToDelete.zone_name}" has been deleted`, 
        type: 'success' 
      }));
      setZoneToDelete(null);
    } catch (err: any) {
      const errorMessage = err?.response?.data?.detail || 'Failed to delete delivery zone';
      setError(errorMessage);
      dispatch(showToast({ message: errorMessage, type: 'error' }));
    } finally {
      setIsDeleting(false);
    }
  };

  const handleCancelDelete = () => {
    setZoneToDelete(null);
  };

  const handleBoundaryChange = async (zoneId: string, boundary: any) => {
    if (!restaurant) return;

    try {
      await setZoneBoundary(restaurant.id, zoneId, boundary);
      // Refresh zones to get updated boundary
      const updatedZones = await listDeliveryZones(restaurant.id);
      setZones(updatedZones);
      
      // Update selected zone if it's the one being edited
      if (selectedZone?.id === zoneId) {
        const updatedZone = updatedZones.find((z) => z.id === zoneId);
        if (updatedZone) {
          setSelectedZone(updatedZone);
        }
      }

      dispatch(showToast({ 
        message: 'Zone boundary updated successfully!', 
        type: 'success' 
      }));
    } catch (err: any) {
      const errorMessage = err?.response?.data?.detail || 'Failed to update zone boundary';
      dispatch(showToast({ message: errorMessage, type: 'error' }));
    }
  };

  if (!restaurant) {
    return (
      <Layout>
        <div className="flex min-h-[400px] items-center justify-center">
          <EmptyState
            icon={MapPin}
            title="No restaurant found"
            description="You are not associated with a restaurant. Please contact support or create a restaurant account."
          />
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
          <div className="flex gap-2">
            <Button
              onClick={() => setShowMap(!showMap)}
              variant={showMap ? 'primary' : 'secondary'}
              size="md"
            >
              <Map className="mr-2 h-4 w-4" />
              {showMap ? 'Hide Map' : 'Show Map'}
            </Button>
            <Button onClick={() => handleOpenForm()} variant="primary" size="md">
              <Plus className="mr-2 h-4 w-4" />
              Add Zone
            </Button>
          </div>
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

        {/* Map Section */}
        {showMap && restaurant && (
          <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <DeliveryZoneMap
              zones={zones}
              selectedZone={selectedZone}
              onZoneSelect={setSelectedZone}
              onBoundaryChange={handleBoundaryChange}
              restaurantId={restaurant.id}
              center={restaurant.address ? undefined : [40.7128, -74.006]} // Default to NYC if no address
            />
          </div>
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
                className={`rounded-xl border-2 bg-white p-6 shadow-sm transition-shadow hover:shadow-md ${
                  selectedZone?.id === zone.id
                    ? 'border-primary bg-primary/5'
                    : 'border-gray-200'
                }`}
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
                      onClick={() => {
                        setSelectedZone(zone);
                        setShowMap(true);
                      }}
                      className={`rounded-lg p-2 transition-colors ${
                        selectedZone?.id === zone.id
                          ? 'bg-primary/10 text-primary'
                          : 'text-gray-600 hover:bg-gray-100 hover:text-primary'
                      }`}
                      aria-label="Select zone on map"
                      title="View on map"
                    >
                      <MapPin className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleOpenForm(zone)}
                      className="rounded-lg p-2 text-gray-600 transition-colors hover:bg-gray-100 hover:text-primary"
                      aria-label="Edit zone"
                    >
                      <Edit2 className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(zone)}
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

        {/* Delete Confirmation Modal */}
        {zoneToDelete && (
          <>
            <div
              className="fixed inset-0 z-[60] bg-gray-900/50 backdrop-blur-sm"
              onClick={handleCancelDelete}
            />
            <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
              <div
                className="w-full max-w-sm rounded-2xl border border-gray-200 bg-white p-6 shadow-xl"
                onClick={(e) => e.stopPropagation()}
              >
                <h3 className="mb-2 text-lg font-bold text-gray-900">Delete Delivery Zone?</h3>
                <p className="mb-6 text-sm text-gray-600">
                  This will permanently remove "{zoneToDelete.zone_name}" from your delivery zones. This action cannot be undone.
                </p>
                <div className="flex gap-3">
                  <Button
                    variant="outline"
                    size="md"
                    onClick={handleCancelDelete}
                    disabled={isDeleting}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                  <Button
                    variant="danger"
                    size="md"
                    onClick={handleConfirmDelete}
                    isLoading={isDeleting}
                    className="flex-1"
                  >
                    Delete
                  </Button>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </Layout>
  );
};

