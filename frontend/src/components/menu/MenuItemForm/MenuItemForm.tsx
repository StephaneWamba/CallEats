import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { X, Trash2 } from 'lucide-react';
import { useRestaurant } from '@/hooks/useRestaurant';
import {
  useCreateMenuItem,
  useUpdateMenuItem,
  useDeleteMenuItem,
} from '@/features/menu/hooks';
import {
  uploadMenuItemImage,
  deleteMenuItemImage,
  linkModifierToItem,
  unlinkModifierFromItem,
  getMenuItem,
} from '@/api/menuItems';
import { useToast } from '@/contexts/ToastContext';
import { Button } from '../../common/Button';
import { getErrorMessage } from '@/utils/errorHandler';
import {
  MenuItemFormFields,
  MenuItemModifiersSection,
  MenuItemDeleteConfirm,
  type MenuItemFormData,
} from './components';
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
  const { showToast } = useToast();
  const { data: restaurant } = useRestaurant();
  const createMenuItemMutation = useCreateMenuItem();
  const updateMenuItemMutation = useUpdateMenuItem();
  const deleteMenuItemMutation = useDeleteMenuItem();
  const [error, setError] = useState<string | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imageToDelete, setImageToDelete] = useState(false);
  const [linkedModifierIds, setLinkedModifierIds] = useState<string[]>([]);

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

      try {
        const fullItem = await getMenuItem(restaurant.id, item.id);
        // Extract modifier IDs from the modifiers array
        const modifierIds = fullItem.modifiers?.map(m => m.id) || [];
        setLinkedModifierIds(modifierIds);
      } catch (_err: any) {
        // If fetching fails, try to use modifiers from the item prop
        const modifierIds = item.modifiers?.map(m => m.id) || [];
        setLinkedModifierIds(modifierIds);
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

    try {
      // Ensure price is a number
      const price = typeof data.price === 'number' ? data.price : parseFloat(String(data.price || 0));
      
      if (isNaN(price) || price < 0) {
        setError('Please enter a valid price');
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
        savedItem = await updateMenuItemMutation.mutateAsync({
          restaurantId: restaurant.id,
          itemId: item.id,
          data: updateData,
        });
      } else {
        // Create new item
        const createData: CreateMenuItemRequest = {
          name: data.name,
          description: data.description || null,
          price: price,
          category_id: data.category_id || null,
          available: data.available ?? true,
        };
        savedItem = await createMenuItemMutation.mutateAsync({
          restaurantId: restaurant.id,
          data: createData,
        });
      }

      // Handle image upload (optional - don't fail if upload fails)
      if (selectedImage && savedItem) {
        try {
          await uploadMenuItemImage(restaurant.id, savedItem.id, selectedImage);
        } catch (_imageError) {
          // Don't fail the entire operation if image upload fails
          showToast('Menu item saved, but image upload failed. You can upload the image later.', 'warning');
        }
      }

      // Handle image deletion
      if (imageToDelete && item?.image_url && savedItem) {
        await deleteMenuItemImage(restaurant.id, savedItem.id);
      }

      onSuccess();
    } catch (err: unknown) {
      const errorMessage = getErrorMessage(err, 'Failed to save menu item. Please try again.');
      setError(errorMessage);
    }
  };

  const handleDelete = async () => {
    if (!restaurant || !item) return;

    setError(null);

    try {
      await deleteMenuItemMutation.mutateAsync({
        restaurantId: restaurant.id,
        itemId: item.id,
      });
      setShowDeleteConfirm(false);
      onSuccess();
    } catch (err: unknown) {
      const errorMessage = getErrorMessage(err, 'Failed to delete menu item. Please try again.');
      setError(errorMessage);
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
        showToast('Modifier removed successfully', 'success');
      } else {
        // Link modifier
        await linkModifierToItem(restaurant.id, item.id, {
          modifier_id: modifierId,
          is_required: false,
          display_order: linkedModifierIds.length,
        });
        setLinkedModifierIds(prev => [...prev, modifierId]);
        showToast('Modifier added successfully', 'success');
      }
    } catch (err: unknown) {
      const errorMessage = getErrorMessage(err, 'Failed to update modifier link');
      setError(errorMessage);
      showToast(errorMessage, 'error');
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

              <MenuItemFormFields
                register={register}
                errors={errors}
                categories={categories}
                item={item}
                imageToDelete={imageToDelete}
                onImageSelect={handleImageSelect}
                onImageDelete={handleImageDelete}
                isPending={createMenuItemMutation.isPending || updateMenuItemMutation.isPending}
                onImageError={(message) => showToast(message, 'error')}
              />

              {item && (
                <MenuItemModifiersSection
                  modifiers={modifiers}
                  linkedModifierIds={linkedModifierIds}
                  onToggleModifier={handleToggleModifier}
                />
              )}

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
                  disabled={createMenuItemMutation.isPending || updateMenuItemMutation.isPending}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  size="md"
                  isLoading={createMenuItemMutation.isPending || updateMenuItemMutation.isPending}
                >
                  {item ? 'Save Changes' : 'Create Item'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <MenuItemDeleteConfirm
        item={item}
        isOpen={showDeleteConfirm}
        isPending={deleteMenuItemMutation.isPending}
        onClose={() => setShowDeleteConfirm(false)}
        onConfirm={handleDelete}
      />
    </>
  );
};

