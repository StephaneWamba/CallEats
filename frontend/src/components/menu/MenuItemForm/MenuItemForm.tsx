import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { X, Trash2, Plus, Tag, Minus } from 'lucide-react';
import { useAppSelector, useAppDispatch } from '@/store/hooks';
import { showToast } from '@/store/slices/uiSlice';
import {
  createMenuItem,
  updateMenuItem,
  deleteMenuItem,
  uploadMenuItemImage,
  deleteMenuItemImage,
  linkModifierToItem,
  unlinkModifierFromItem,
  getMenuItem,
} from '@/api/menuItems';
import { Button } from '../../common/Button';
import { Input } from '../../common/Input';
import { ImageUpload } from '../../common/ImageUpload';
import type {
  MenuItemResponse,
  CreateMenuItemRequest,
  UpdateMenuItemRequest,
  CategoryResponse,
  ModifierResponse,
} from '@/types/menu';

const menuItemSchema = z.object({
  name: z.string().min(1, 'Item name is required'),
  description: z.string().optional(),
  price: z.number().min(0, 'Price must be 0 or greater'),
  category_id: z.string().optional(),
  available: z.boolean().optional(),
});

type MenuItemFormData = z.infer<typeof menuItemSchema>;

interface MenuItemFormProps {
  item: MenuItemResponse | null;
  categories: CategoryResponse[];
  modifiers: ModifierResponse[]; // All available modifiers
  onClose: () => void;
  onSuccess: () => void;
}

export const MenuItemForm: React.FC<MenuItemFormProps> = ({
  item,
  categories,
  modifiers,
  onClose,
  onSuccess,
}) => {
  const dispatch = useAppDispatch();
  const { restaurant } = useAppSelector((state) => state.restaurant);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imageToDelete, setImageToDelete] = useState(false);
  const [linkedModifierIds, setLinkedModifierIds] = useState<string[]>([]);
  const [isLoadingModifiers, setIsLoadingModifiers] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<MenuItemFormData>({
    resolver: zodResolver(menuItemSchema),
    defaultValues: {
      name: item?.name || '',
      description: item?.description || '',
      price: item?.price || 0,
      category_id: item?.category_id || '',
      available: item?.available ?? true,
    },
  });

  // Fetch full item with modifiers when form opens for editing
  React.useEffect(() => {
    const fetchItemModifiers = async () => {
      if (!item || !restaurant) return;

      setIsLoadingModifiers(true);
      try {
        const fullItem = await getMenuItem(restaurant.id, item.id);
        // Extract modifier IDs from the modifiers array
        const modifierIds = fullItem.modifiers?.map(m => m.id) || [];
        setLinkedModifierIds(modifierIds);
      } catch (err: any) {
        // If fetching fails, try to use modifiers from the item prop
        const modifierIds = item.modifiers?.map(m => m.id) || [];
        setLinkedModifierIds(modifierIds);
        console.warn('Failed to fetch item modifiers:', err);
      } finally {
        setIsLoadingModifiers(false);
      }
    };

    fetchItemModifiers();
  }, [item?.id, restaurant?.id]);

  const onSubmit = async (data: MenuItemFormData) => {
    if (!restaurant) {
      setError('Restaurant not found');
      return;
    }

    setError(null);
    setIsLoading(true);

    try {
      // Ensure price is a number
      const price = typeof data.price === 'number' ? data.price : parseFloat(String(data.price || 0));
      
      if (isNaN(price) || price < 0) {
        setError('Please enter a valid price');
        setIsLoading(false);
        return;
      }

      let savedItem: MenuItemResponse;

      if (item) {
        // Update existing item
        const updateData: UpdateMenuItemRequest = {
          name: data.name,
          description: data.description || null,
          price: price,
          category_id: data.category_id || null,
          available: data.available,
        };
        savedItem = await updateMenuItem(restaurant.id, item.id, updateData);
      } else {
        // Create new item
        const createData: CreateMenuItemRequest = {
          name: data.name,
          description: data.description || null,
          price: price,
          category_id: data.category_id || null,
          available: data.available ?? true,
        };
        savedItem = await createMenuItem(restaurant.id, createData);
      }

      // Handle image upload (optional - don't fail if upload fails)
      if (selectedImage && savedItem) {
        try {
          await uploadMenuItemImage(restaurant.id, savedItem.id, selectedImage);
        } catch (imageError) {
          // Log error but don't fail the entire operation
          console.warn('Failed to upload image:', imageError);
          dispatch(showToast({ 
            message: 'Menu item saved, but image upload failed. You can upload the image later.', 
            type: 'warning' 
          }));
        }
      }

      // Handle image deletion
      if (imageToDelete && item?.image_url && savedItem) {
        await deleteMenuItemImage(restaurant.id, savedItem.id);
      }

      onSuccess();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to save menu item. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!restaurant || !item) return;

    setError(null);
    setIsLoading(true);

    try {
      await deleteMenuItem(restaurant.id, item.id);
      onSuccess();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to delete menu item. Please try again.');
      }
    } finally {
      setIsLoading(false);
      setShowDeleteConfirm(false);
    }
  };

  const handleImageSelect = (file: File | null) => {
    setSelectedImage(file);
    setImageToDelete(false);
  };

  const handleImageDelete = () => {
    setImageToDelete(true);
    setSelectedImage(null);
  };

  const handleToggleModifier = async (modifierId: string) => {
    if (!item || !restaurant) return; // Only allow linking for existing items

    const isLinked = linkedModifierIds.includes(modifierId);

    try {
      if (isLinked) {
        // Unlink modifier
        await unlinkModifierFromItem(restaurant.id, item.id, modifierId);
        setLinkedModifierIds(prev => prev.filter(id => id !== modifierId));
        dispatch(showToast({ 
          message: 'Modifier removed successfully', 
          type: 'success' 
        }));
      } else {
        // Link modifier
        await linkModifierToItem(restaurant.id, item.id, {
          modifier_id: modifierId,
          is_required: false,
          display_order: linkedModifierIds.length,
        });
        setLinkedModifierIds(prev => [...prev, modifierId]);
        dispatch(showToast({ 
          message: 'Modifier added successfully', 
          type: 'success' 
        }));
      }
    } catch (err: any) {
      const errorMessage = err?.response?.data?.detail || err?.message || 'Failed to update modifier link';
      setError(errorMessage);
      dispatch(showToast({ 
        message: errorMessage, 
        type: 'error' 
      }));
    }
  };

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-50 bg-gray-900/50 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="fixed inset-0 z-50 overflow-y-auto">
        <div className="flex min-h-full items-center justify-center p-4">
          <div
            className="w-full max-w-2xl rounded-2xl border border-gray-200 bg-white shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-center justify-between border-b border-gray-200 p-6">
              <h2 className="text-xl font-bold text-gray-900">
                {item ? 'Edit Menu Item' : 'New Menu Item'}
              </h2>
              <button
                onClick={onClose}
                className="rounded-lg p-2 text-gray-600 transition-colors hover:bg-gray-100"
                aria-label="Close"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit(onSubmit)} className="p-6">
              {error && (
                <div className="mb-4 rounded-lg border border-error bg-error/10 p-3 text-sm text-error">
                  {error}
                </div>
              )}

              <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
                {/* Image Upload */}
                <div className="md:col-span-1">
                  <label className="mb-2 block text-sm font-medium text-gray-700">
                    Item Image
                  </label>
                  <ImageUpload
                    currentImageUrl={imageToDelete ? null : item?.image_url}
                    onImageSelect={handleImageSelect}
                    onImageDelete={handleImageDelete}
                    disabled={isLoading}
                    onError={(message) => dispatch(showToast({ message, type: 'error' }))}
                  />
                </div>

                {/* Form Fields */}
                <div className="space-y-4 md:col-span-1">
                  <Input
                    label="Item Name"
                    placeholder="e.g., Margherita Pizza"
                    error={errors.name?.message}
                    {...register('name')}
                  />

                  <Input
                    label="Price ($)"
                    type="number"
                    step="0.01"
                    placeholder="0.00"
                    error={errors.price?.message}
                    {...register('price', { valueAsNumber: true })}
                  />

                  <div>
                    <label className="mb-1 block text-sm font-medium text-gray-700">
                      Category
                    </label>
                    <select
                      className="w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
                      {...register('category_id')}
                    >
                      <option value="">No Category</option>
                      {categories.map((category) => (
                        <option key={category.id} value={category.id}>
                          {category.name}
                        </option>
                      ))}
                    </select>
                    {errors.category_id && (
                      <p className="mt-1 text-sm text-error">{errors.category_id.message}</p>
                    )}
                  </div>

                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      id="available"
                      className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                      {...register('available')}
                    />
                    <label
                      htmlFor="available"
                      className="text-sm font-medium text-gray-700"
                    >
                      Available for ordering
                    </label>
                  </div>
                </div>

                {/* Description - Full Width */}
                <div className="md:col-span-2">
                  <label className="mb-1 block text-sm font-medium text-gray-700">
                    Description
                  </label>
                  <textarea
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
                    rows={3}
                    placeholder="Describe the dish, ingredients, etc."
                    {...register('description')}
                  />
                  {errors.description && (
                    <p className="mt-1 text-sm text-error">{errors.description.message}</p>
                  )}
                </div>

                {/* Modifiers - Full Width (only for existing items) */}
                {item && (
                  <div className="md:col-span-2">
                    <label className="mb-2 block text-sm font-medium text-gray-700">
                      Modifiers
                    </label>
                    {modifiers.length === 0 ? (
                      <p className="text-sm text-gray-500">No modifiers available. Create modifiers first.</p>
                    ) : (
                      <div className="rounded-lg border border-gray-200 p-3">
                        <p className="mb-3 text-xs text-gray-600">
                          Select which modifiers customers can add to this item
                        </p>
                        <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                          {modifiers.map((modifier) => {
                            const isLinked = linkedModifierIds.includes(modifier.id);
                            return (
                              <button
                                key={modifier.id}
                                type="button"
                                onClick={() => handleToggleModifier(modifier.id)}
                                className={`flex items-center justify-between rounded-lg border px-3 py-2 text-left text-sm transition-all hover:shadow-sm ${
                                  isLinked
                                    ? 'border-primary bg-primary/10 text-primary'
                                    : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
                                }`}
                              >
                                <span className="flex items-center gap-2">
                                  <Tag className="h-4 w-4" />
                                  <span className="font-medium">{modifier.name}</span>
                                  {(typeof modifier.price === 'number' ? modifier.price : parseFloat(modifier.price || '0')) > 0 && (
                                    <span className="text-xs">
                                      +${typeof modifier.price === 'number' ? modifier.price.toFixed(2) : parseFloat(modifier.price || '0').toFixed(2)}
                                    </span>
                                  )}
                                </span>
                                {isLinked ? (
                                  <Minus className="h-4 w-4" />
                                ) : (
                                  <Plus className="h-4 w-4" />
                                )}
                              </button>
                            );
                          })}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="mt-6 flex gap-3">
                {item && (
                  <Button
                    type="button"
                    variant="danger"
                    size="md"
                    onClick={() => setShowDeleteConfirm(true)}
                    className="gap-2"
                  >
                    <Trash2 className="h-4 w-4" />
                    Delete
                  </Button>
                )}
                <div className="flex-1" />
                <Button
                  type="button"
                  variant="outline"
                  size="md"
                  onClick={onClose}
                  disabled={isLoading}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  size="md"
                  isLoading={isLoading}
                >
                  {item ? 'Save Changes' : 'Create Item'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <>
          <div
            className="fixed inset-0 z-[60] bg-gray-900/50 backdrop-blur-sm"
            onClick={() => setShowDeleteConfirm(false)}
          />
          <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
            <div
              className="w-full max-w-sm rounded-2xl border border-gray-200 bg-white p-6 shadow-xl"
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="mb-2 text-lg font-bold text-gray-900">Delete Menu Item?</h3>
              <p className="mb-6 text-sm text-gray-600">
                This will permanently remove "{item?.name}" from your menu.
              </p>
              <div className="flex gap-3">
                <Button
                  variant="outline"
                  size="md"
                  onClick={() => setShowDeleteConfirm(false)}
                  disabled={isLoading}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  variant="danger"
                  size="md"
                  onClick={handleDelete}
                  isLoading={isLoading}
                  className="flex-1"
                >
                  Delete
                </Button>
              </div>
            </div>
          </div>
        </>
      )}
    </>
  );
};

