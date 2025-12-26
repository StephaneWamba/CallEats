import React from 'react';
import { Button } from '../../../common/Button';
import type { MenuItemResponse } from '@/types/menu';

interface MenuItemDeleteConfirmProps {
  item: MenuItemResponse | null;
  isOpen: boolean;
  isPending: boolean;
  onClose: () => void;
  onConfirm: () => void;
}

export const MenuItemDeleteConfirm: React.FC<MenuItemDeleteConfirmProps> = ({
  item,
  isOpen,
  isPending,
  onClose,
  onConfirm,
}) => {
  if (!isOpen) return null;

  return (
    <>
      <div
        className="fixed inset-0 z-[60] bg-gray-900/50 backdrop-blur-sm"
        onClick={onClose}
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
              onClick={onClose}
              disabled={isPending}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              variant="danger"
              size="md"
              onClick={onConfirm}
              isLoading={isPending}
              className="flex-1"
            >
              Delete
            </Button>
          </div>
        </div>
      </div>
    </>
  );
};


