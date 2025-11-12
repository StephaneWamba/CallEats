import React, { createContext, useContext, useState, useCallback } from 'react';
import type { ReactNode } from 'react';

export type ToastType = 'success' | 'error' | 'info' | 'warning';

export interface ToastOptions {
  duration?: number; // Auto-dismiss duration in milliseconds (default: 5000)
}

interface Toast {
  message: string;
  type: ToastType;
  id: string;
  duration?: number;
}

export interface ToastContextType {
  toast: Toast | null;
  showToast: (message: string, type: ToastType, options?: ToastOptions) => void;
  hideToast: () => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

interface ToastProviderProps {
  children: ReactNode;
}

export const ToastProvider: React.FC<ToastProviderProps> = ({ children }) => {
  const [toast, setToast] = useState<Toast | null>(null);

  const showToast = useCallback((message: string, type: ToastType, options?: ToastOptions) => {
    setToast({
      message,
      type,
      id: Date.now().toString(),
      duration: options?.duration ?? 5000, // Default 5 seconds
    });
  }, []);

  const hideToast = useCallback(() => {
    setToast(null);
  }, []);

  return (
    <ToastContext.Provider value={{ toast, showToast, hideToast }}>
      {children}
    </ToastContext.Provider>
  );
};

