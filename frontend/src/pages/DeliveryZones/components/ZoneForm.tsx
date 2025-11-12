import React from 'react';
import { Modal } from '@/components/common/Modal';
import { Input } from '@/components/common/Input';
import { Button } from '@/components/common/Button';
import type {
  DeliveryZoneResponse,
  CreateDeliveryZoneRequest,
} from '@/types/delivery-zones';

interface ZoneFormProps {
  isOpen: boolean;
  editingZone: DeliveryZoneResponse | null;
  formData: CreateDeliveryZoneRequest;
  onClose: () => void;
  onSubmit: (e: React.FormEvent) => void;
  onFormDataChange: (data: CreateDeliveryZoneRequest) => void;
  isSubmitting: boolean;
}

export const ZoneForm: React.FC<ZoneFormProps> = ({
  isOpen,
  editingZone,
  formData,
  onClose,
  onSubmit,
  onFormDataChange,
  isSubmitting,
}) => {
  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={editingZone ? 'Edit Delivery Zone' : 'Create Delivery Zone'}
      size="md"
    >
      <form onSubmit={onSubmit} className="space-y-4">
        <Input
          label="Zone Name"
          value={formData.zone_name}
          onChange={(e) => onFormDataChange({ ...formData, zone_name: e.target.value })}
          required
          placeholder="e.g., Downtown, North Side"
        />

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Description (optional)
          </label>
          <textarea
            value={formData.description}
            onChange={(e) => onFormDataChange({ ...formData, description: e.target.value })}
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
            onFormDataChange({ ...formData, delivery_fee: parseFloat(e.target.value) || 0 })
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
            onFormDataChange({
              ...formData,
              min_order: e.target.value ? parseFloat(e.target.value) : undefined,
            })
          }
          placeholder="No minimum"
        />

        <div className="flex justify-end gap-3 pt-4">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" isLoading={isSubmitting}>
            {editingZone ? 'Update' : 'Create'} Zone
          </Button>
        </div>
      </form>
    </Modal>
  );
};

