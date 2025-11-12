import React from 'react';
import type { CategoryResponse } from '@/types/menu';

interface CategoryFilterProps {
  categories: CategoryResponse[];
  selectedCategoryId: string | null;
  onSelectCategory: (categoryId: string | null) => void;
}

export const CategoryFilter: React.FC<CategoryFilterProps> = ({
  categories,
  selectedCategoryId,
  onSelectCategory,
}) => {
  return (
    <div className="mb-6 flex gap-2 overflow-x-auto pb-2">
      <button
        onClick={() => onSelectCategory(null)}
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
          onClick={() => onSelectCategory(category.id)}
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
  );
};

