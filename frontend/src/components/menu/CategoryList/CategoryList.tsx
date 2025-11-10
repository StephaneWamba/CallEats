import React, { useState } from 'react';
import { Plus, Edit2, Folder } from 'lucide-react';
import { Button } from '../../common/Button';
import { CategoryForm } from '../CategoryForm';
import type { CategoryResponse } from '@/types/menu';

interface CategoryListProps {
  categories: CategoryResponse[];
  selectedCategoryId: string | null;
  onSelectCategory: (categoryId: string | null) => void;
  onCategoryCreated: () => void;
  onCategoryUpdated: () => void;
  onCategoryDeleted?: () => void;
}

export const CategoryList: React.FC<CategoryListProps> = ({
  categories,
  selectedCategoryId,
  onSelectCategory,
  onCategoryCreated,
  onCategoryUpdated,
}) => {
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingCategory, setEditingCategory] = useState<CategoryResponse | null>(null);

  const handleEdit = (category: CategoryResponse, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingCategory(category);
    setIsFormOpen(true);
  };

  const handleFormClose = () => {
    setIsFormOpen(false);
    setEditingCategory(null);
  };

  const handleFormSuccess = () => {
    if (editingCategory) {
      onCategoryUpdated();
    } else {
      onCategoryCreated();
    }
    handleFormClose();
  };

  return (
    <div className="flex h-full flex-col rounded-2xl border border-gray-200 bg-white shadow-md">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-200 p-4">
        <h2 className="text-lg font-semibold text-gray-900">Categories</h2>
        <Button
          variant="primary"
          size="sm"
          onClick={() => setIsFormOpen(true)}
          className="gap-2"
        >
          <Plus className="h-4 w-4" />
          Add
        </Button>
      </div>

      {/* Category List */}
      <div className="flex-1 overflow-y-auto p-2">
        {/* All Items */}
        <button
          onClick={() => onSelectCategory(null)}
          className={`mb-1 flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left transition-colors ${
            selectedCategoryId === null
              ? 'bg-primary/10 text-primary font-semibold'
              : 'text-gray-700 hover:bg-gray-100'
          }`}
        >
          <Folder className="h-5 w-5" />
          <span>All Items</span>
        </button>

        {/* Categories */}
        {categories.length === 0 ? (
          <div className="py-8 text-center text-sm text-gray-500">
            No categories yet. Create one to organize your menu items.
          </div>
        ) : (
          categories.map((category) => (
            <div
              key={category.id}
              onClick={() => onSelectCategory(category.id)}
              className={`group mb-1 flex cursor-pointer items-center justify-between rounded-lg px-3 py-2 transition-colors ${
                selectedCategoryId === category.id
                  ? 'bg-primary/10 text-primary font-semibold'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <div className="flex items-center gap-3">
                <Folder className="h-5 w-5" />
                <div>
                  <div className="font-medium">{category.name}</div>
                  {category.description && (
                    <div className="text-xs text-gray-500">{category.description}</div>
                  )}
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-1 opacity-0 transition-opacity group-hover:opacity-100">
                <button
                  onClick={(e) => handleEdit(category, e)}
                  className="rounded p-1 text-gray-600 hover:bg-primary/10 hover:text-primary"
                  aria-label="Edit category"
                >
                  <Edit2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Category Form Modal */}
      {isFormOpen && (
        <CategoryForm
          category={editingCategory}
          onClose={handleFormClose}
          onSuccess={handleFormSuccess}
        />
      )}
    </div>
  );
};

