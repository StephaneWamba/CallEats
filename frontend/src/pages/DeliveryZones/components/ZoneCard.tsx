import React from 'react';
import { MapPin, Edit2, Trash2, DollarSign, Package } from 'lucide-react';
import type { DeliveryZoneResponse } from '@/types/delivery-zones';

interface ZoneCardProps {
  zone: DeliveryZoneResponse;
  isSelected: boolean;
  onSelect: (zone: DeliveryZoneResponse) => void;
  onEdit: (zone: DeliveryZoneResponse) => void;
  onDelete: (zone: DeliveryZoneResponse) => void;
}

export const ZoneCard: React.FC<ZoneCardProps> = ({
  zone,
  isSelected,
  onSelect,
  onEdit,
  onDelete,
}) => {
  return (
    <div
      className={`rounded-xl border-2 bg-white p-6 shadow-sm transition-shadow hover:shadow-md ${
        isSelected
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
            onClick={() => onSelect(zone)}
            className={`rounded-lg p-2 transition-colors ${
              isSelected
                ? 'bg-primary/10 text-primary'
                : 'text-gray-600 hover:bg-gray-100 hover:text-primary'
            }`}
            aria-label="Select zone on map"
            title="View on map"
          >
            <MapPin className="h-4 w-4" />
          </button>
          <button
            onClick={() => onEdit(zone)}
            className="rounded-lg p-2 text-gray-600 transition-colors hover:bg-gray-100 hover:text-primary"
            aria-label="Edit zone"
          >
            <Edit2 className="h-4 w-4" />
          </button>
          <button
            onClick={() => onDelete(zone)}
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
            ${Number(zone.delivery_fee).toFixed(2)}
          </span>
        </div>
        {zone.min_order && (
          <div className="flex items-center gap-2 text-sm">
            <Package className="h-4 w-4 text-gray-500" />
            <span className="text-gray-600">Min Order:</span>
            <span className="font-semibold text-gray-900">
              ${Number(zone.min_order).toFixed(2)}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

