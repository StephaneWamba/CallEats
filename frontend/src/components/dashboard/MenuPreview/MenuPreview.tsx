import React from 'react';
import { Link } from 'react-router-dom';
import { UtensilsCrossed, ArrowRight } from 'lucide-react';
import { ROUTES } from '../../../config/routes';
import { EmptyState } from '../../common/EmptyState';

export const MenuPreview: React.FC = () => {
  // TODO: Replace with actual API call in Phase 4
  const menuItems = [];

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
          {/* TODO: Map actual menu items in Phase 4 */}
        </div>
      )}
    </div>
  );
};

