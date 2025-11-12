import React, { useEffect } from 'react';
import { X, CheckCircle2, AlertCircle, Info, AlertTriangle } from 'lucide-react';
import { useAppSelector, useAppDispatch } from '@/store/hooks';
import { hideToast } from '@/store/slices/uiSlice';

export const Toast: React.FC = () => {
  const dispatch = useAppDispatch();
  const toast = useAppSelector((state) => state.ui.toast);

  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => {
        dispatch(hideToast());
      }, 5000); // Auto-hide after 5 seconds

      return () => clearTimeout(timer);
    }
  }, [toast, dispatch]);

  if (!toast) return null;

  const icons = {
    success: CheckCircle2,
    error: AlertCircle,
    info: Info,
    warning: AlertTriangle,
  };

  const colors = {
    success: 'bg-success text-white',
    error: 'bg-error text-white',
    info: 'bg-primary text-white',
    warning: 'bg-warning text-white',
  };

  const Icon = icons[toast.type];

  return (
    <div className="fixed top-4 right-4 z-[100] animate-slide-down">
      <div
        className={`flex items-center gap-3 rounded-lg shadow-lg p-4 min-w-[300px] max-w-[500px] ${colors[toast.type]}`}
      >
        <Icon className="h-5 w-5 flex-shrink-0" />
        <p className="flex-1 text-sm font-medium">{toast.message}</p>
        <button
          onClick={() => dispatch(hideToast())}
          className="flex-shrink-0 rounded p-1 hover:bg-black/20 transition-colors"
          aria-label="Close toast"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
};

