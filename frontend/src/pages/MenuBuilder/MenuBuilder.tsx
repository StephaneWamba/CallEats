import React, { useState } from 'react';
import { UtensilsCrossed } from 'lucide-react';
import { useRestaurant } from '@/hooks/useRestaurant';
import { useCategories, useMenuItems, useModifiers, useDeleteMenuItem } from '@/features/menu/hooks';
import { Layout } from '@/components/layout/Layout';
import { CategoryList } from '@/components/menu/CategoryList';
import { MenuItemForm } from '@/components/menu/MenuItemForm';
import { ModifierList } from '@/components/menu/ModifierList';
import { PageSkeleton } from '@/components/common/Skeleton';
import { EmptyState } from '@/components/common/EmptyState';
import type { MenuItemResponse } from '@/types/menu';
import { MenuSearchBar } from './components/MenuSearchBar';
import { CategoryFilter } from './components/CategoryFilter';
import { MenuItemsGrid } from './components/MenuItemsGrid';
import { MobileTabs } from './components/MobileTabs';
import { DeleteConfirmModal } from './components/DeleteConfirmModal';

export const MenuBuilder: React.FC = () => {
  const { data: restaurant, isLoading: isLoadingRestaurant } = useRestaurant();
  const { data: categories } = useCategories(restaurant?.id);
  const { data: menuItems } = useMenuItems(restaurant?.id);
  const { data: modifiers } = useModifiers(restaurant?.id);
  const deleteMenuItemMutation = useDeleteMenuItem();
  
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategoryId, setSelectedCategoryId] = useState<string | null>(null);
  const [isItemFormOpen, setIsItemFormOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<MenuItemResponse | null>(null);
  const [mobileActiveTab, setMobileActiveTab] = useState<'items' | 'categories' | 'modifiers'>('items');
  const [itemToDelete, setItemToDelete] = useState<MenuItemResponse | null>(null);

  // Filter menu items
  const filteredItems = (menuItems || []).filter((item) => {
    // Filter by category
    if (selectedCategoryId && item.category_id !== selectedCategoryId) {
      return false;
    }

    // Filter by search
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        item.name.toLowerCase().includes(query) ||
        item.description?.toLowerCase().includes(query)
      );
    }

    return true;
  });

  // Handlers
  const handleCategorySelect = (categoryId: string | null) => {
    setSelectedCategoryId(categoryId);
  };

  const handleAddItem = () => {
    setEditingItem(null);
    setIsItemFormOpen(true);
  };

  const handleEditItem = (item: MenuItemResponse) => {
    setEditingItem(item);
    setIsItemFormOpen(true);
  };

  const handleDeleteItem = (item: MenuItemResponse) => {
    setItemToDelete(item);
  };

  const handleConfirmDelete = async () => {
    if (!restaurant || !itemToDelete) return;

    try {
      await deleteMenuItemMutation.mutateAsync({
        restaurantId: restaurant.id,
        itemId: itemToDelete.id,
      });
      setItemToDelete(null);
    } catch (_error) {
      // Error handled by mutation
    }
  };

  const handleCancelDelete = () => {
    setItemToDelete(null);
  };

  const handleItemFormClose = () => {
    setIsItemFormOpen(false);
    setEditingItem(null);
  };

  const handleItemFormSuccess = () => {
    handleItemFormClose();
  };

  if (isLoadingRestaurant) {
    return (
      <Layout>
        <PageSkeleton />
      </Layout>
    );
  }

  if (!restaurant) {
    return (
      <Layout>
        <div className="flex min-h-[400px] items-center justify-center">
          <EmptyState
            icon={UtensilsCrossed}
            title="No restaurant found"
            description="You are not associated with a restaurant. Please contact support or create a restaurant account."
          />
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Menu Builder</h1>
        <p className="text-gray-600">
          Manage your menu items, categories, and modifiers
        </p>
      </div>

      {/* Desktop Layout */}
      <div className="hidden lg:grid lg:grid-cols-[250px_1fr_250px] lg:gap-6">
        {/* Left Sidebar - Categories */}
        <div className="h-[calc(100vh-250px)]">
          <CategoryList
            categories={categories || []}
            selectedCategoryId={selectedCategoryId}
            onSelectCategory={handleCategorySelect}
            onCategoryCreated={() => {}}
            onCategoryUpdated={() => {}}
            onCategoryDeleted={() => {}}
          />
        </div>

        {/* Main Content - Menu Items */}
        <div className="flex flex-col">
          <MenuSearchBar
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            onAddClick={handleAddItem}
          />

          <MenuItemsGrid
            items={filteredItems}
                  categories={categories || []}
            searchQuery={searchQuery}
            selectedCategoryId={selectedCategoryId}
                  onEdit={handleEditItem}
                  onDelete={handleDeleteItem}
            onAddClick={handleAddItem}
                />
        </div>

        {/* Right Sidebar - Modifiers */}
        <div className="h-[calc(100vh-250px)]">
          <ModifierList
            modifiers={modifiers || []}
            onModifierCreated={() => {}}
            onModifierUpdated={() => {}}
            onModifierDeleted={() => {}}
          />
        </div>
      </div>

      {/* Mobile/Tablet Layout */}
      <div className="lg:hidden">
        <MobileTabs activeTab={mobileActiveTab} onTabChange={setMobileActiveTab} />

        {/* Menu Items Tab Content */}
        {mobileActiveTab === 'items' && (
          <>
            <MenuSearchBar
              searchQuery={searchQuery}
              onSearchChange={setSearchQuery}
              onAddClick={handleAddItem}
              className="flex-col sm:flex-row"
            />

            <CategoryFilter
              categories={categories || []}
              selectedCategoryId={selectedCategoryId}
              onSelectCategory={handleCategorySelect}
            />

            <MenuItemsGrid
              items={filteredItems}
                    categories={categories || []}
              searchQuery={searchQuery}
              selectedCategoryId={selectedCategoryId}
                    onEdit={handleEditItem}
                    onDelete={handleDeleteItem}
              onAddClick={handleAddItem}
              className="grid-cols-1 sm:grid-cols-2"
                  />
          </>
        )}

        {/* Categories Tab Content */}
        {mobileActiveTab === 'categories' && (
          <div className="max-w-2xl">
            <CategoryList
              categories={categories || []}
              selectedCategoryId={selectedCategoryId}
              onSelectCategory={handleCategorySelect}
              onCategoryCreated={() => {}}
              onCategoryUpdated={() => {}}
              onCategoryDeleted={() => {}}
            />
          </div>
        )}

        {/* Modifiers Tab Content */}
        {mobileActiveTab === 'modifiers' && (
          <div className="max-w-2xl">
            <ModifierList
              modifiers={modifiers || []}
              onModifierCreated={() => {}}
              onModifierUpdated={() => {}}
              onModifierDeleted={() => {}}
            />
          </div>
        )}
      </div>

      {/* Menu Item Form Modal */}
      {isItemFormOpen && (
        <MenuItemForm
          item={editingItem}
          categories={categories || []}
          modifiers={modifiers || []}
          onClose={handleItemFormClose}
          onSuccess={handleItemFormSuccess}
        />
      )}

      {/* Delete Confirmation Modal */}
      <DeleteConfirmModal
        item={itemToDelete}
        isDeleting={deleteMenuItemMutation.isPending}
        onConfirm={handleConfirmDelete}
        onCancel={handleCancelDelete}
      />
    </Layout>
  );
};
