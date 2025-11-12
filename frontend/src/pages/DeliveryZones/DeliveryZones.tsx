import React, { useState } from 'react';
import { Plus, MapPin, Map } from 'lucide-react';
import { useRestaurant } from '@/hooks/useRestaurant';
import {
  useDeliveryZones,
  useCreateDeliveryZone,
  useUpdateDeliveryZone,
  useDeleteDeliveryZone,
  useSetZoneBoundary,
} from '@/features/delivery-zones/hooks';
import { Layout } from '@/components/layout/Layout';
import { Button } from '@/components/common/Button';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { EmptyState } from '@/components/common/EmptyState';
import { LazyDeliveryZoneMap } from '@/components/delivery-zones/DeliveryZoneMap/LazyDeliveryZoneMap';
import type {
  DeliveryZoneResponse,
  CreateDeliveryZoneRequest,
  UpdateDeliveryZoneRequest,
} from '@/types/delivery-zones';
import { ZoneCard } from './components/ZoneCard';
import { ZoneForm } from './components/ZoneForm';
import { DeleteZoneModal } from './components/DeleteZoneModal';

export const DeliveryZones: React.FC = () => {
  const { data: restaurant } = useRestaurant();
  const { data: zones, isLoading } = useDeliveryZones(restaurant?.id);
  const zonesArray = zones || [];
  const createZoneMutation = useCreateDeliveryZone();
  const updateZoneMutation = useUpdateDeliveryZone();
  const deleteZoneMutation = useDeleteDeliveryZone();
  const setBoundaryMutation = useSetZoneBoundary();
  
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingZone, setEditingZone] = useState<DeliveryZoneResponse | null>(null);
  const [zoneToDelete, setZoneToDelete] = useState<DeliveryZoneResponse | null>(null);
  const [selectedZone, setSelectedZone] = useState<DeliveryZoneResponse | null>(null);
  const [showMap, setShowMap] = useState(true);

  // Form state
  const [formData, setFormData] = useState<CreateDeliveryZoneRequest>({
    zone_name: '',
    description: '',
    delivery_fee: 0,
    min_order: undefined,
  });

  const handleOpenForm = (zone?: DeliveryZoneResponse) => {
    if (zone) {
      setEditingZone(zone);
      setFormData({
        zone_name: zone.zone_name,
        description: zone.description || '',
        // Ensure delivery_fee and min_order are numbers (API might return strings)
        delivery_fee: typeof zone.delivery_fee === 'string' ? parseFloat(zone.delivery_fee) || 0 : Number(zone.delivery_fee) || 0,
        min_order: zone.min_order 
          ? (typeof zone.min_order === 'string' ? parseFloat(zone.min_order) : Number(zone.min_order))
          : undefined,
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
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!restaurant) return;

    try {
      if (editingZone) {
        const updateData: UpdateDeliveryZoneRequest = {
          zone_name: formData.zone_name,
          description: formData.description || undefined,
          delivery_fee: formData.delivery_fee,
          min_order: formData.min_order || undefined,
        };
        await updateZoneMutation.mutateAsync({
          restaurantId: restaurant.id,
          zoneId: editingZone.id,
          data: updateData,
        });
      } else {
        await createZoneMutation.mutateAsync({
          restaurantId: restaurant.id,
          data: formData,
        });
      }
      handleCloseForm();
    } catch (_error) {
      // Error handled by mutation
    }
  };

  const handleDelete = (zone: DeliveryZoneResponse) => {
    setZoneToDelete(zone);
  };

  const handleConfirmDelete = async () => {
    if (!restaurant || !zoneToDelete) return;

    try {
      await deleteZoneMutation.mutateAsync({
        restaurantId: restaurant.id,
        zoneId: zoneToDelete.id,
      });
      setZoneToDelete(null);
    } catch (_error) {
      // Error handled by mutation
    }
  };

  const handleCancelDelete = () => {
    setZoneToDelete(null);
  };

  const handleBoundaryChange = async (zoneId: string, boundary: any) => {
    if (!restaurant) return;

    try {
      await setBoundaryMutation.mutateAsync({
        restaurantId: restaurant.id,
        zoneId,
        boundary,
      });
      
      // Update selected zone if it's the one being edited
      if (selectedZone?.id === zoneId) {
        const updatedZone = zonesArray.find((z) => z.id === zoneId);
        if (updatedZone) {
          setSelectedZone(updatedZone);
        }
      }
    } catch (_error) {
      // Error handled by mutation
    }
  };

  const handleZoneSelect = (zone: DeliveryZoneResponse) => {
    setSelectedZone(zone);
    setShowMap(true);
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

        {/* Map Section */}
        {showMap && restaurant && (
          <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <LazyDeliveryZoneMap
              zones={zonesArray}
              selectedZone={selectedZone}
              onZoneSelect={setSelectedZone}
              onBoundaryChange={handleBoundaryChange}
              restaurantId={restaurant.id}
              center={[40.7128, -74.006]} // Default to NYC
            />
          </div>
        )}

        {/* Zones List */}
        {isLoading && zonesArray.length === 0 ? (
          <div className="flex min-h-[400px] items-center justify-center">
            <LoadingSpinner size="lg" />
          </div>
        ) : zonesArray.length === 0 ? (
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
            {zonesArray.map((zone) => (
              <ZoneCard
                key={zone.id}
                zone={zone}
                isSelected={selectedZone?.id === zone.id}
                onSelect={handleZoneSelect}
                onEdit={handleOpenForm}
                onDelete={handleDelete}
              />
            ))}
          </div>
        )}

        {/* Create/Edit Form */}
        <ZoneForm
          isOpen={isFormOpen}
          editingZone={editingZone}
          formData={formData}
          onClose={handleCloseForm}
          onSubmit={handleSubmit}
          onFormDataChange={setFormData}
          isSubmitting={createZoneMutation.isPending || updateZoneMutation.isPending}
        />
        
        {/* Hide map controls when modal is open */}
        {isFormOpen && (
          <style>{`
            .leaflet-control-container,
            .leaflet-draw,
            .leaflet-top,
            .leaflet-bottom {
              z-index: 100 !important;
            }
          `}</style>
        )}

        {/* Delete Confirmation Modal */}
        <DeleteZoneModal
          zone={zoneToDelete}
          isDeleting={deleteZoneMutation.isPending}
          onConfirm={handleConfirmDelete}
          onCancel={handleCancelDelete}
        />
      </div>
    </Layout>
  );
};
