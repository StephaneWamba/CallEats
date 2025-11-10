import React from 'react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  isLoading = false,
  children,
  className = '',
  disabled,
  ...props
}) => {
  const baseClasses = 'font-semibold rounded-lg transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 active:scale-95 inline-flex items-center justify-center';
  
  const variantClasses = {
    primary: 'bg-gradient-to-r from-primary to-primary/90 text-white hover:shadow-lg hover:shadow-primary/30 hover:-translate-y-0.5 focus:ring-primary shadow-md',
    secondary: 'bg-gradient-to-r from-secondary to-secondary/90 text-white hover:shadow-lg hover:shadow-secondary/30 hover:-translate-y-0.5 focus:ring-secondary shadow-md',
    danger: 'bg-gradient-to-r from-error to-error/90 text-white hover:shadow-lg hover:shadow-error/30 hover:-translate-y-0.5 focus:ring-error shadow-md',
    outline: 'border-2 border-gray-300 text-gray-700 hover:border-primary hover:text-primary hover:bg-primary/5 hover:shadow-md focus:ring-primary backdrop-blur',
  };

  const sizeClasses = {
    sm: 'px-4 py-2 text-sm min-h-[32px] gap-2',
    md: 'px-6 py-2.5 text-base min-h-[44px] gap-2',
    lg: 'px-8 py-3.5 text-lg min-h-[48px] gap-3',
  };

  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className} ${
        (disabled || isLoading) ? 'opacity-50 cursor-not-allowed hover:transform-none hover:shadow-none' : ''
      }`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <>
          <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Loading...
        </>
      ) : children}
    </button>
  );
};

