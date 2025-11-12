import React from 'react';
import type { UseFormRegister, FieldErrors } from 'react-hook-form';
import { Input } from '../../../common/Input';
import { ImageUpload } from '../../../common/ImageUpload';
import type { CategoryResponse, MenuItemResponse } from '@/types/menu';

export interface MenuItemFormData {
  name: string;
  description?: string;
  price: number;
  category_id?: string;
  available?: boolean;
}

interface MenuItemFormFieldsProps {
  register: UseFormRegister<MenuItemFormData>;
  errors: FieldErrors<MenuItemFormData>;
  categories: CategoryResponse[];
  item: MenuItemResponse | null;
  imageToDelete: boolean;
  onImageSelect: (file: File | null) => void;
  onImageDelete: () => void;
  isPending: boolean;
  onImageError: (message: string) => void;
}

export const MenuItemFormFields: React.FC<MenuItemFormFieldsProps> = ({
  register,
  errors,
  categories,
  item,
  imageToDelete,
  onImageSelect,
  onImageDelete,
  isPending,
  onImageError,
}) => {
  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
      {/* Image Upload */}
      <div className="md:col-span-1">
        <label className="mb-2 block text-sm font-medium text-gray-700">
          Item Image
        </label>
        <ImageUpload
          currentImageUrl={imageToDelete ? null : item?.image_url}
          onImageSelect={onImageSelect}
          onImageDelete={onImageDelete}
          disabled={isPending}
          onError={onImageError}
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
    </div>
  );
};

