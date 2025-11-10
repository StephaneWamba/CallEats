import React from 'react';
import { Phone } from 'lucide-react';

interface LogoProps {
  size?: 'sm' | 'md' | 'lg';
  showText?: boolean;
}

export const Logo: React.FC<LogoProps> = ({ size = 'md', showText = true }) => {
  const sizeClasses = {
    sm: 'h-8 w-8',
    md: 'h-10 w-10',
    lg: 'h-12 w-12',
  };

  const textSizeClasses = {
    sm: 'text-lg',
    md: 'text-xl',
    lg: 'text-2xl',
  };

  return (
    <div className="flex items-center gap-3">
      {/* Logo Icon */}
      <div className={`${sizeClasses[size]} flex items-center justify-center rounded-xl bg-gradient-to-br from-primary to-primary/80 shadow-lg shadow-primary/30`}>
        <Phone className="h-5 w-5 text-white" strokeWidth={2.5} />
      </div>

      {/* Logo Text */}
      {showText && (
        <span className={`${textSizeClasses[size]} font-bold text-gray-900`}>
          Restaurant Voice Assistant
        </span>
      )}
    </div>
  );
};

