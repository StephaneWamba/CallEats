import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { X, Trash2 } from 'lucide-react';
import { useAppSelector } from '@/store/hooks';
import { createModifier, updateModifier, deleteModifier } from '@/api/modifiers';
import { Button } from '../../common/Button';
import { Input } from '../../common/Input';
import type { ModifierResponse, CreateModifierRequest, UpdateModifierRequest } from '@/types/menu';

const modifierSchema = z.object({
  name: z.string().min(1, 'Modifier name is required'),
  description: z.string().optional(),
  price: z.number().min(0, 'Price must be 0 or greater'),
});

type ModifierFormData = z.infer<typeof modifierSchema>;

interface ModifierFormProps {
  modifier: ModifierResponse | null;
  onClose: () => void;
  onSuccess: () => void;
}

export const ModifierForm: React.FC<ModifierFormProps> = ({
  modifier,
  onClose,
  onSuccess,
}) => {
  const { restaurant } = useAppSelector((state) => state.restaurant);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ModifierFormData>({
    resolver: zodResolver(modifierSchema),
    defaultValues: {
      name: modifier?.name || '',
      description: modifier?.description || '',
      price: modifier?.price || 0,
    },
  });

  // Reset form when modifier changes
  React.useEffect(() => {
    reset({
      name: modifier?.name || '',
      description: modifier?.description || '',
      price: modifier?.price || 0,
    });
    setError(null);
  }, [modifier, reset]);

  const onSubmit = async (data: ModifierFormData) => {
    if (!restaurant) {
      setError('Restaurant not found');
      return;
    }

    setError(null);
    setIsLoading(true);

    try {
      if (modifier) {
        // Update existing modifier
        const updateData: UpdateModifierRequest = {
          name: data.name,
          description: data.description || null,
          price: data.price,
        };
        await updateModifier(restaurant.id, modifier.id, updateData);
      } else {
        // Create new modifier
        const createData: CreateModifierRequest = {
          name: data.name,
          description: data.description || null,
          price: data.price,
        };
        await createModifier(restaurant.id, createData);
      }
      onSuccess();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to save modifier. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!restaurant || !modifier) return;

    setError(null);
    setIsLoading(true);

    try {
      await deleteModifier(restaurant.id, modifier.id);
      onSuccess();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to delete modifier. Please try again.');
      }
    } finally {
      setIsLoading(false);
      setShowDeleteConfirm(false);
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
              {modifier ? 'Edit Modifier' : 'New Modifier'}
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
                label="Modifier Name"
                placeholder="e.g., Extra Cheese, No Onions"
                error={errors.name?.message}
                {...register('name')}
              />

              <Input
                label="Additional Price ($)"
                type="number"
                step="0.01"
                placeholder="0.00"
                error={errors.price?.message}
                {...register('price', { valueAsNumber: true })}
              />

              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">
                  Description (Optional)
                </label>
                <textarea
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
                  rows={2}
                  placeholder="Brief description of this modifier"
                  {...register('description')}
                />
                {errors.description && (
                  <p className="mt-1 text-sm text-error">{errors.description.message}</p>
                )}
              </div>
            </div>

            {/* Actions */}
            <div className="mt-6 flex gap-3">
              {modifier && (
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
                disabled={isLoading}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="primary"
                size="md"
                isLoading={isLoading}
              >
                {modifier ? 'Save Changes' : 'Create Modifier'}
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
              <h3 className="mb-2 text-lg font-bold text-gray-900">Delete Modifier?</h3>
              <p className="mb-6 text-sm text-gray-600">
                This will permanently remove "{modifier?.name}". Menu items using this modifier will no longer have it available.
              </p>
              <div className="flex gap-3">
                <Button
                  variant="outline"
                  size="md"
                  onClick={() => setShowDeleteConfirm(false)}
                  disabled={isLoading}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  variant="danger"
                  size="md"
                  onClick={handleDelete}
                  isLoading={isLoading}
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

