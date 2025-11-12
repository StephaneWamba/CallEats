import React from 'react';
import { Link } from 'react-router-dom';
import { UtensilsCrossed, ArrowRight } from 'lucide-react';
import { ROUTES } from '../../../config/routes';
import { EmptyState } from '../../common/EmptyState';
import { useAppSelector } from '@/store/hooks';

export const MenuPreview: React.FC = () => {
  const { menuItems } = useAppSelector((state) => state.menu);
  const previewItems = menuItems.slice(0, 5); // Show first 5 items

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">Menu Preview</h2>
        <Link
          to={ROUTES.MENU_BUILDER}
          className="flex items-center gap-1 text-sm font-medium text-primary hover:text-primary/80"
        >
          Manage menu
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>

      {menuItems.length === 0 ? (
        <EmptyState
          icon={UtensilsCrossed}
          title="No menu items yet"
          description="Start building your menu to help customers order"
        />
      ) : (
        <div className="space-y-3">
          {previewItems.map((item) => (
            <div
              key={item.id}
              className="flex items-center justify-between rounded-lg border border-gray-200 bg-gray-50 p-3 transition-colors hover:bg-gray-100"
            >
              <div className="flex items-center gap-3">
                {item.image_url ? (
                  <img
                    src={item.image_url}
                    alt={item.name}
                    className="h-12 w-12 rounded-lg object-cover"
                  />
                ) : (
                  <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-gray-200">
                    <UtensilsCrossed className="h-6 w-6 text-gray-400" />
                  </div>
                )}
                <div>
                  <h3 className="font-medium text-gray-900">{item.name}</h3>
                  {item.description && (
                    <p className="text-sm text-gray-500 line-clamp-1">{item.description}</p>
                  )}
                </div>
              </div>
              <div className="text-right">
                <div className="font-semibold text-gray-900">
                  ${typeof item.price === 'number' ? item.price.toFixed(2) : parseFloat(item.price || '0').toFixed(2)}
                </div>
                {!item.available && (
                  <div className="text-xs text-error">Unavailable</div>
                )}
              </div>
            </div>
          ))}
          {menuItems.length > 5 && (
            <Link
              to={ROUTES.MENU_BUILDER}
              className="block text-center text-sm font-medium text-primary hover:text-primary/80"
            >
              View all {menuItems.length} items →
            </Link>
          )}
        </div>
      )}
    </div>
  );
};

