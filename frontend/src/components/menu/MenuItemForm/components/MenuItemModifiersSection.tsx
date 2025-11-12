import React from 'react';
import { Plus, Tag, Minus } from 'lucide-react';
import type { ModifierResponse } from '@/types/menu';

interface MenuItemModifiersSectionProps {
  modifiers: ModifierResponse[];
  linkedModifierIds: string[];
  onToggleModifier: (modifierId: string) => void;
}

export const MenuItemModifiersSection: React.FC<MenuItemModifiersSectionProps> = ({
  modifiers,
  linkedModifierIds,
  onToggleModifier,
}) => {
  if (modifiers.length === 0) {
    return (
      <div className="md:col-span-2">
        <label className="mb-2 block text-sm font-medium text-gray-700">
          Modifiers
        </label>
        <p className="text-sm text-gray-500">No modifiers available. Create modifiers first.</p>
      </div>
    );
  }

  return (
    <div className="md:col-span-2">
      <label className="mb-2 block text-sm font-medium text-gray-700">
        Modifiers
      </label>
      <div className="rounded-lg border border-gray-200 p-3">
        <p className="mb-3 text-xs text-gray-600">
          Select which modifiers customers can add to this item
        </p>
        <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
          {modifiers.map((modifier) => {
            const isLinked = linkedModifierIds.includes(modifier.id);
            const modifierPrice = typeof modifier.price === 'number' 
              ? modifier.price 
              : parseFloat(modifier.price || '0');
            
            return (
              <button
                key={modifier.id}
                type="button"
                onClick={() => onToggleModifier(modifier.id)}
                className={`flex items-center justify-between rounded-lg border px-3 py-2 text-left text-sm transition-all hover:shadow-sm ${
                  isLinked
                    ? 'border-primary bg-primary/10 text-primary'
                    : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
                }`}
              >
                <span className="flex items-center gap-2">
                  <Tag className="h-4 w-4" />
                  <span className="font-medium">{modifier.name}</span>
                  {modifierPrice > 0 && (
                    <span className="text-xs">
                      +${modifierPrice.toFixed(2)}
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
    </div>
  );
};

