import React from 'react';
import { UtensilsCrossed } from 'lucide-react';
import { MenuItemCard } from '@/components/menu/MenuItemCard';
import { EmptyState } from '@/components/common/EmptyState';
import { Button } from '@/components/common/Button';
import type { MenuItemResponse, CategoryResponse } from '@/types/menu';

interface MenuItemsGridProps {
  items: MenuItemResponse[];
  categories: CategoryResponse[];
  searchQuery: string;
  selectedCategoryId: string | null;
  onEdit: (item: MenuItemResponse) => void;
  onDelete: (item: MenuItemResponse) => void;
  onAddClick: () => void;
  className?: string;
}

export const MenuItemsGrid: React.FC<MenuItemsGridProps> = ({
  items,
  categories,
  searchQuery,
  selectedCategoryId,
  onEdit,
  onDelete,
  onAddClick,
  className = '',
}) => {
  if (items.length === 0) {
    return (
      <EmptyState
        icon={UtensilsCrossed}
        title="No menu items yet"
        description={
          searchQuery
            ? "No items match your search. Try different keywords."
            : selectedCategoryId
            ? "No items in this category. Add some to get started."
            : "Start building your menu by adding your first item."
        }
        action={
          !searchQuery && (
            <Button variant="primary" size="md" onClick={onAddClick}>
              Add First Item
            </Button>
          )
        }
      />
    );
  }

  return (
    <div className={`grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-3 ${className}`}>
      {items.map((item) => (
        <MenuItemCard
          key={item.id}
          item={item}
          categories={categories}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
};


