import React from 'react';
import { Search, Plus } from 'lucide-react';
import { Button } from '@/components/common/Button';

interface MenuSearchBarProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  onAddClick: () => void;
  className?: string;
}

export const MenuSearchBar: React.FC<MenuSearchBarProps> = ({
  searchQuery,
  onSearchChange,
  onAddClick,
  className = '',
}) => {
  return (
    <div className={`mb-6 flex gap-4 ${className}`}>
      <div className="relative flex-1">
        <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
        <input
          type="text"
          placeholder="Search menu items..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          className="w-full rounded-lg border border-gray-300 py-2 pl-10 pr-4 text-gray-900 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
        />
      </div>
      <Button
        variant="primary"
        size="md"
        onClick={onAddClick}
        className="gap-2"
      >
        <Plus className="h-5 w-5" />
        Add Item
      </Button>
    </div>
  );
};

