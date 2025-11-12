import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { X, Trash2 } from 'lucide-react';
import { useRestaurant } from '@/hooks/useRestaurant';
import { useCreateCategory, useUpdateCategory, useDeleteCategory } from '@/features/menu/hooks';
import { Button } from '../../common/Button';
import { Input } from '../../common/Input';
import { getErrorMessage } from '@/utils/errorHandler';
import type { CategoryResponse, CreateCategoryRequest, UpdateCategoryRequest } from '@/types/menu';

const categorySchema = z.object({
  name: z.string().min(1, 'Category name is required'),
  description: z.string().optional(),
  display_order: z.number().min(0, 'Display order must be 0 or greater').optional(),
});

type CategoryFormData = z.infer<typeof categorySchema>;

interface CategoryFormProps {
  category: CategoryResponse | null;
  onClose: () => void;
  onSuccess: () => void;
}

export const CategoryForm: React.FC<CategoryFormProps> = ({
  category,
  onClose,
  onSuccess,
}) => {
  const { data: restaurant } = useRestaurant();
  const createCategoryMutation = useCreateCategory();
  const updateCategoryMutation = useUpdateCategory();
  const deleteCategoryMutation = useDeleteCategory();
  const [error, setError] = useState<string | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CategoryFormData>({
    resolver: zodResolver(categorySchema),
    defaultValues: {
      name: category?.name || '',
      description: category?.description || '',
      display_order: category?.display_order ?? 0,
    },
  });

  const onSubmit = async (data: CategoryFormData) => {
    if (!restaurant) {
      setError('Restaurant not found');
      return;
    }

    setError(null);

    try {
      if (category) {
        // Update existing category
        const updateData: UpdateCategoryRequest = {
          name: data.name,
          description: data.description || null,
          display_order: data.display_order,
        };
        await updateCategoryMutation.mutateAsync({
          restaurantId: restaurant.id,
          categoryId: category.id,
          data: updateData,
        });
      } else {
        // Create new category
        const createData: CreateCategoryRequest = {
          name: data.name,
          description: data.description || null,
          display_order: data.display_order,
        };
        await createCategoryMutation.mutateAsync({
          restaurantId: restaurant.id,
          data: createData,
        });
      }
      onSuccess();
    } catch (err: unknown) {
      const errorMessage = getErrorMessage(err, 'Failed to save category. Please try again.');
      setError(errorMessage);
    }
  };

  const handleDelete = async () => {
    if (!restaurant || !category) return;

    setError(null);

    try {
      await deleteCategoryMutation.mutateAsync({
        restaurantId: restaurant.id,
        categoryId: category.id,
      });
      setShowDeleteConfirm(false);
      onSuccess();
    } catch (err: unknown) {
      const errorMessage = getErrorMessage(err, 'Failed to delete category. Please try again.');
      setError(errorMessage);
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
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div
          className="w-full max-w-md rounded-2xl border border-gray-200 bg-white shadow-xl"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between border-b border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900">
              {category ? 'Edit Category' : 'New Category'}
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

            <div className="space-y-4">
              <Input
                label="Category Name"
                placeholder="e.g., Appetizers, Main Courses"
                error={errors.name?.message}
                {...register('name')}
              />

              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">
                  Description (Optional)
                </label>
                <textarea
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
                  rows={3}
                  placeholder="Brief description of this category"
                  {...register('description')}
                />
                {errors.description && (
                  <p className="mt-1 text-sm text-error">{errors.description.message}</p>
                )}
              </div>

              <Input
                label="Display Order"
                type="number"
                placeholder="0"
                error={errors.display_order?.message}
                {...register('display_order', { valueAsNumber: true })}
              />
            </div>

            {/* Actions */}
            <div className="mt-6 flex gap-3">
              {category && (
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
                disabled={createCategoryMutation.isPending || updateCategoryMutation.isPending}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="primary"
                size="md"
                isLoading={createCategoryMutation.isPending || updateCategoryMutation.isPending}
              >
                {category ? 'Save Changes' : 'Create Category'}
              </Button>
            </div>
          </form>
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
              <h3 className="mb-2 text-lg font-bold text-gray-900">Delete Category?</h3>
              <p className="mb-6 text-sm text-gray-600">
                This will remove the category. Menu items in this category will become uncategorized.
              </p>
              <div className="flex gap-3">
                <Button
                  variant="outline"
                  size="md"
                  onClick={() => setShowDeleteConfirm(false)}
                  disabled={createCategoryMutation.isPending || updateCategoryMutation.isPending}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  variant="danger"
                  size="md"
                  onClick={handleDelete}
                  isLoading={createCategoryMutation.isPending || updateCategoryMutation.isPending}
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

