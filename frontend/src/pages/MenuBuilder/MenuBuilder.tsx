import React, { useEffect, useState, useRef } from 'react';
import { Plus, Search } from 'lucide-react';
import { useAppSelector, useAppDispatch } from '@/store/hooks';
import {
  setCategories,
  setMenuItems,
  setModifiers,
  setSelectedCategory,
} from '@/store/slices/menuSlice';
import { setRestaurant } from '@/store/slices/restaurantSlice';
import { showToast } from '@/store/slices/uiSlice';
import { listCategories } from '@/api/categories';
import { listMenuItems, deleteMenuItem } from '@/api/menuItems';
import { listModifiers } from '@/api/modifiers';
import { getMyRestaurant } from '@/api/restaurants';
import { Layout } from '@/components/layout/Layout';
import { CategoryList } from '@/components/menu/CategoryList';
import { MenuItemCard } from '@/components/menu/MenuItemCard';
import { MenuItemForm } from '@/components/menu/MenuItemForm';
import { ModifierList } from '@/components/menu/ModifierList';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { EmptyState } from '@/components/common/EmptyState';
import { Button } from '@/components/common/Button';
import { UtensilsCrossed } from 'lucide-react';
import type { MenuItemResponse } from '@/types/menu';

export const MenuBuilder: React.FC = () => {
  const dispatch = useAppDispatch();
  const { restaurant } = useAppSelector((state) => state.restaurant);
  const { categories, menuItems, modifiers, selectedCategoryId } = useAppSelector(
    (state) => state.menu
  );

  const [isLoading, setIsLoading] = useState(false);
  const [isInitialLoad, setIsInitialLoad] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [isItemFormOpen, setIsItemFormOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<MenuItemResponse | null>(null);
  const [mobileActiveTab, setMobileActiveTab] = useState<'items' | 'categories' | 'modifiers'>('items');
  const [itemToDelete, setItemToDelete] = useState<MenuItemResponse | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const lastFetchedRestaurantId = useRef<string | null>(null);
  const hasFetchedRestaurant = useRef(false);

  // Fetch restaurant data if missing
  useEffect(() => {
    const fetchRestaurant = async () => {
      if (restaurant || hasFetchedRestaurant.current) return;

      hasFetchedRestaurant.current = true;
      try {
        const restaurantData = await getMyRestaurant();
        dispatch(setRestaurant(restaurantData));
      } catch (error: any) {
        // Handle 403 - user not associated with restaurant
        if (error?.response?.status === 403) {
          // User doesn't have a restaurant yet
          // Don't set error state, just continue
        }
        // For other errors, silently fail
      }
    };

    fetchRestaurant();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Fetch all data
  const fetchAllData = async () => {
    if (!restaurant) return;

    setIsLoading(true);
    try {
      const [categoriesData, itemsData, modifiersData] = await Promise.all([
        listCategories(restaurant.id),
        listMenuItems(restaurant.id),
        listModifiers(restaurant.id),
      ]);

      dispatch(setCategories(categoriesData));
      dispatch(setMenuItems(itemsData));
      dispatch(setModifiers(modifiersData));
    } catch (error) {
      // Error handled by error state
    } finally {
      setIsLoading(false);
      setIsInitialLoad(false);
    }
  };

  useEffect(() => {
    const restaurantId = restaurant?.id;
    
    // Only fetch if restaurant ID changed and we haven't fetched for this ID yet
    if (!restaurantId || restaurantId === lastFetchedRestaurantId.current) {
      return;
    }

    lastFetchedRestaurantId.current = restaurantId;
    fetchAllData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [restaurant?.id]);

  // Filter menu items
  const filteredItems = menuItems.filter((item) => {
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
    dispatch(setSelectedCategory(categoryId));
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

    setIsDeleting(true);
    try {
      await deleteMenuItem(restaurant.id, itemToDelete.id);
      await fetchAllData();
      setItemToDelete(null);
      dispatch(showToast({ message: `"${itemToDelete.name}" has been deleted`, type: 'success' }));
    } catch (error) {
      dispatch(showToast({ message: 'Failed to delete menu item. Please try again.', type: 'error' }));
    } finally {
      setIsDeleting(false);
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
    fetchAllData();
    handleItemFormClose();
  };

  const handleDataRefresh = () => {
    fetchAllData();
  };

  if (isInitialLoad && isLoading) {
    return (
      <Layout>
        <div className="flex min-h-[400px] items-center justify-center">
          <LoadingSpinner size="lg" />
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
            categories={categories}
            selectedCategoryId={selectedCategoryId}
            onSelectCategory={handleCategorySelect}
            onCategoryCreated={handleDataRefresh}
            onCategoryUpdated={handleDataRefresh}
            onCategoryDeleted={handleDataRefresh}
          />
        </div>

        {/* Main Content - Menu Items */}
        <div className="flex flex-col">
          {/* Search and Add Button */}
          <div className="mb-6 flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search menu items..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full rounded-lg border border-gray-300 py-2 pl-10 pr-4 text-gray-900 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
              />
            </div>
            <Button
              variant="primary"
              size="md"
              onClick={handleAddItem}
              className="gap-2"
            >
              <Plus className="h-5 w-5" />
              Add Item
            </Button>
          </div>

          {/* Menu Items Grid */}
          {filteredItems.length === 0 ? (
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
                  <Button variant="primary" size="md" onClick={handleAddItem}>
                    Add First Item
                  </Button>
                )
              }
            />
          ) : (
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-3">
              {filteredItems.map((item) => (
                <MenuItemCard
                  key={item.id}
                  item={item}
                  categories={categories}
                  onEdit={handleEditItem}
                  onDelete={handleDeleteItem}
                />
              ))}
            </div>
          )}
        </div>

        {/* Right Sidebar - Modifiers */}
        <div className="h-[calc(100vh-250px)]">
          <ModifierList
            modifiers={modifiers}
            onModifierCreated={handleDataRefresh}
            onModifierUpdated={handleDataRefresh}
            onModifierDeleted={handleDataRefresh}
          />
        </div>
      </div>

      {/* Mobile/Tablet Layout */}
      <div className="lg:hidden">
        {/* Tabs */}
        <div className="mb-6 flex gap-2 overflow-x-auto border-b border-gray-200">
          <button
            onClick={() => setMobileActiveTab('items')}
            className={`whitespace-nowrap border-b-2 px-4 py-2 font-medium transition-colors ${
              mobileActiveTab === 'items'
                ? 'border-primary text-primary'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            Menu Items
          </button>
          <button
            onClick={() => setMobileActiveTab('categories')}
            className={`whitespace-nowrap border-b-2 px-4 py-2 font-medium transition-colors ${
              mobileActiveTab === 'categories'
                ? 'border-primary text-primary'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            Categories
          </button>
          <button
            onClick={() => setMobileActiveTab('modifiers')}
            className={`whitespace-nowrap border-b-2 px-4 py-2 font-medium transition-colors ${
              mobileActiveTab === 'modifiers'
                ? 'border-primary text-primary'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            Modifiers
          </button>
        </div>

        {/* Menu Items Tab Content */}
        {mobileActiveTab === 'items' && (
          <>
            {/* Search and Add Button */}
            <div className="mb-6 flex flex-col gap-4 sm:flex-row">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search menu items..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full rounded-lg border border-gray-300 py-2 pl-10 pr-4 text-gray-900 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
                />
              </div>
              <Button
                variant="primary"
                size="md"
                onClick={handleAddItem}
                className="w-full gap-2 sm:w-auto"
              >
                <Plus className="h-5 w-5" />
                Add Item
              </Button>
            </div>

            {/* Category Filter Pills */}
            <div className="mb-6 flex gap-2 overflow-x-auto pb-2">
              <button
                onClick={() => handleCategorySelect(null)}
                className={`whitespace-nowrap rounded-full px-4 py-2 text-sm font-medium transition-colors ${
                  selectedCategoryId === null
                    ? 'bg-primary text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                All Items
              </button>
              {categories.map((category) => (
                <button
                  key={category.id}
                  onClick={() => handleCategorySelect(category.id)}
                  className={`whitespace-nowrap rounded-full px-4 py-2 text-sm font-medium transition-colors ${
                    selectedCategoryId === category.id
                      ? 'bg-primary text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {category.name}
                </button>
              ))}
            </div>

            {/* Menu Items Grid */}
            {filteredItems.length === 0 ? (
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
                    <Button variant="primary" size="md" onClick={handleAddItem}>
                      Add First Item
                    </Button>
                  )
                }
              />
            ) : (
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                {filteredItems.map((item) => (
                  <MenuItemCard
                    key={item.id}
                    item={item}
                    categories={categories}
                    onEdit={handleEditItem}
                    onDelete={handleDeleteItem}
                  />
                ))}
              </div>
            )}
          </>
        )}

        {/* Categories Tab Content */}
        {mobileActiveTab === 'categories' && (
          <div className="max-w-2xl">
            <CategoryList
              categories={categories}
              selectedCategoryId={selectedCategoryId}
              onSelectCategory={handleCategorySelect}
              onCategoryCreated={handleDataRefresh}
              onCategoryUpdated={handleDataRefresh}
              onCategoryDeleted={handleDataRefresh}
            />
          </div>
        )}

        {/* Modifiers Tab Content */}
        {mobileActiveTab === 'modifiers' && (
          <div className="max-w-2xl">
            <ModifierList
              modifiers={modifiers}
              onModifierCreated={handleDataRefresh}
              onModifierUpdated={handleDataRefresh}
              onModifierDeleted={handleDataRefresh}
            />
          </div>
        )}
      </div>

      {/* Menu Item Form Modal */}
      {isItemFormOpen && (
        <MenuItemForm
          item={editingItem}
          categories={categories}
          modifiers={modifiers}
          onClose={handleItemFormClose}
          onSuccess={handleItemFormSuccess}
        />
      )}

      {/* Delete Confirmation Modal */}
      {itemToDelete && (
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
              <h3 className="mb-2 text-lg font-bold text-gray-900">Delete Menu Item?</h3>
              <p className="mb-6 text-sm text-gray-600">
                This will permanently remove "{itemToDelete.name}" from your menu. This action cannot be undone.
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
    </Layout>
  );
};

