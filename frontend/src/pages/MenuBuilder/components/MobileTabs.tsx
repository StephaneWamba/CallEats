import React from 'react';

interface MobileTabsProps {
  activeTab: 'items' | 'categories' | 'modifiers';
  onTabChange: (tab: 'items' | 'categories' | 'modifiers') => void;
}

export const MobileTabs: React.FC<MobileTabsProps> = ({ activeTab, onTabChange }) => {
  return (
    <div className="mb-6 flex gap-2 overflow-x-auto border-b border-gray-200">
      <button
        onClick={() => onTabChange('items')}
        className={`whitespace-nowrap border-b-2 px-4 py-2 font-medium transition-colors ${
          activeTab === 'items'
            ? 'border-primary text-primary'
            : 'border-transparent text-gray-600 hover:text-gray-900'
        }`}
      >
        Menu Items
      </button>
      <button
        onClick={() => onTabChange('categories')}
        className={`whitespace-nowrap border-b-2 px-4 py-2 font-medium transition-colors ${
          activeTab === 'categories'
            ? 'border-primary text-primary'
            : 'border-transparent text-gray-600 hover:text-gray-900'
        }`}
      >
        Categories
      </button>
      <button
        onClick={() => onTabChange('modifiers')}
        className={`whitespace-nowrap border-b-2 px-4 py-2 font-medium transition-colors ${
          activeTab === 'modifiers'
            ? 'border-primary text-primary'
            : 'border-transparent text-gray-600 hover:text-gray-900'
        }`}
      >
        Modifiers
      </button>
    </div>
  );
};

