import React from 'react';
import { Button } from '@/components/common/Button';
import type { DeliveryZoneResponse } from '@/types/delivery-zones';

interface DeleteZoneModalProps {
  zone: DeliveryZoneResponse | null;
  isDeleting: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export const DeleteZoneModal: React.FC<DeleteZoneModalProps> = ({
  zone,
  isDeleting,
  onConfirm,
  onCancel,
}) => {
  if (!zone) return null;

  return (
    <>
      <div
        className="fixed inset-0 z-[60] bg-gray-900/50 backdrop-blur-sm"
        onClick={onCancel}
      />
      <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
        <div
          className="w-full max-w-sm rounded-2xl border border-gray-200 bg-white p-6 shadow-xl"
          onClick={(e) => e.stopPropagation()}
        >
          <h3 className="mb-2 text-lg font-bold text-gray-900">Delete Delivery Zone?</h3>
          <p className="mb-6 text-sm text-gray-600">
            This will permanently remove "{zone.zone_name}" from your delivery zones. This action cannot be undone.
          </p>
          <div className="flex gap-3">
            <Button
              variant="outline"
              size="md"
              onClick={onCancel}
              disabled={isDeleting}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              variant="danger"
              size="md"
              onClick={onConfirm}
              isLoading={isDeleting}
              className="flex-1"
            >
              Delete
            </Button>
          </div>
        </div>
      </div>
    </>
  );
};


