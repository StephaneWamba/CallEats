import React, { useState } from 'react';
import { Plus, Edit2, Tag } from 'lucide-react';
import { Button } from '../../common/Button';
import { ModifierForm } from '../ModifierForm';
import type { ModifierResponse } from '@/types/menu';

interface ModifierListProps {
  modifiers: ModifierResponse[];
  onModifierCreated: () => void;
  onModifierUpdated: () => void;
  onModifierDeleted?: () => void;
}

export const ModifierList: React.FC<ModifierListProps> = ({
  modifiers,
  onModifierCreated,
  onModifierUpdated,
}) => {
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingModifier, setEditingModifier] = useState<ModifierResponse | null>(null);

  const handleEdit = (modifier: ModifierResponse, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingModifier(modifier);
    setIsFormOpen(true);
  };

  const handleFormClose = () => {
    setIsFormOpen(false);
    setEditingModifier(null);
  };

  const handleFormSuccess = () => {
    if (editingModifier) {
      onModifierUpdated();
    } else {
      onModifierCreated();
    }
    handleFormClose();
  };

  return (
    <div className="flex h-full flex-col rounded-2xl border border-gray-200 bg-white shadow-md">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-200 p-4">
        <h2 className="text-lg font-semibold text-gray-900">Modifiers</h2>
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

      {/* Modifier List */}
      <div className="flex-1 overflow-y-auto p-2">
        {modifiers.length === 0 ? (
          <div className="py-8 text-center text-sm text-gray-500">
            No modifiers yet. Create add-ons like "Extra Cheese" or "No Onions".
          </div>
        ) : (
          modifiers.map((modifier) => (
            <div
              key={modifier.id}
              className="group mb-1 flex cursor-pointer items-center justify-between rounded-lg px-3 py-2 text-gray-700 transition-colors hover:bg-gray-100"
            >
              <div className="flex items-center gap-3">
                <Tag className="h-4 w-4 text-primary" />
                <div>
                  <div className="font-medium">{modifier.name}</div>
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <span>
                      +${typeof modifier.price === 'number' ? modifier.price.toFixed(2) : parseFloat(modifier.price || '0').toFixed(2)}
                    </span>
                    {modifier.description && (
                      <>
                        <span>•</span>
                        <span className="line-clamp-1">{modifier.description}</span>
                      </>
                    )}
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-1 opacity-0 transition-opacity group-hover:opacity-100">
                <button
                  onClick={(e) => handleEdit(modifier, e)}
                  className="rounded p-1 text-gray-600 hover:bg-primary/10 hover:text-primary"
                  aria-label="Edit modifier"
                >
                  <Edit2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Modifier Form Modal */}
      {isFormOpen && (
        <ModifierForm
          modifier={editingModifier}
          onClose={handleFormClose}
          onSuccess={handleFormSuccess}
        />
      )}
    </div>
  );
};

