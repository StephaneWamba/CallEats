import React from 'react';
import { Edit2, Trash2, ImageOff } from 'lucide-react';
import type { MenuItemResponse, CategoryResponse } from '@/types/menu';

interface MenuItemCardProps {
  item: MenuItemResponse;
  categories: CategoryResponse[];
  onEdit: (item: MenuItemResponse) => void;
  onDelete: (item: MenuItemResponse) => void;
}

export const MenuItemCard: React.FC<MenuItemCardProps> = ({
  item,
  categories,
  onEdit,
  onDelete,
}) => {
  const category = categories.find((c) => c.id === item.category_id);

  return (
    <div className="group relative overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-md transition-all duration-300 hover:shadow-lg">
      {/* Image */}
      <div className="relative aspect-video w-full overflow-hidden bg-gray-100">
        {item.image_url ? (
          <img
            src={item.image_url}
            alt={item.name}
            className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center">
            <ImageOff className="h-12 w-12 text-gray-300" />
          </div>
        )}

        {/* Availability Badge */}
        <div className="absolute right-2 top-2">
          <span
            className={`rounded-full px-3 py-1 text-xs font-semibold shadow-md ${
              item.available
                ? 'bg-success text-white'
                : 'bg-error text-white'
            }`}
          >
            {item.available ? 'Available' : 'Unavailable'}
          </span>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        <div className="mb-2 flex items-start justify-between">
          <div className="flex-1">
            <h3 className="text-lg font-bold text-gray-900">{item.name}</h3>
            {category && (
              <span className="inline-block rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
                {category.name}
              </span>
            )}
          </div>
          <div className="text-lg font-bold text-primary">
            ${item.price.toFixed(2)}
          </div>
        </div>

        {item.description && (
          <p className="mb-4 line-clamp-2 text-sm text-gray-600">
            {item.description}
          </p>
        )}

        {/* Actions */}
        <div className="flex gap-2">
          <button
            onClick={() => onEdit(item)}
            className="flex flex-1 items-center justify-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:border-primary hover:bg-primary/5 hover:text-primary"
          >
            <Edit2 className="h-4 w-4" />
            Edit
          </button>
          <button
            onClick={() => onDelete(item)}
            className="flex flex-1 items-center justify-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:border-error hover:bg-error/5 hover:text-error"
          >
            <Trash2 className="h-4 w-4" />
            Delete
          </button>
        </div>
      </div>
    </div>
  );
};

