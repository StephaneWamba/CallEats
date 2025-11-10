import React from 'react';
import { Battery, Wifi, Signal } from 'lucide-react';

interface PhoneMockupProps {
  children: React.ReactNode;
}

export const PhoneMockup: React.FC<PhoneMockupProps> = ({ children }) => {
  return (
    <div className="relative mx-auto w-full max-w-[340px] sm:max-w-[380px]">
      {/* Phone outer frame */}
      <div className="relative rounded-[3rem] bg-linear-to-br from-gray-800 via-gray-900 to-black p-3 shadow-2xl">
        {/* Inner bezel */}
        <div className="relative overflow-hidden rounded-[2.5rem] bg-black">
          {/* Status bar */}
          <div className="relative z-20 flex h-12 items-center justify-between bg-white/95 px-6 pt-2">
            {/* Time */}
            <div className="text-sm font-semibold text-gray-900">
              {new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })}
            </div>
            
            {/* Notch spacer */}
            <div className="w-24" />
            
            {/* Status icons */}
            <div className="flex items-center gap-1">
              <Signal className="h-4 w-4 text-gray-900" strokeWidth={2.5} />
              <Wifi className="h-4 w-4 text-gray-900" strokeWidth={2.5} />
              <Battery className="h-4 w-4 text-gray-900" strokeWidth={2.5} />
            </div>
          </div>

          {/* Notch */}
          <div className="absolute left-1/2 top-0 z-30 h-7 w-40 -translate-x-1/2 rounded-b-3xl bg-black shadow-lg">
            <div className="absolute inset-x-8 top-3 flex items-center justify-center gap-2">
              {/* Camera */}
              <div className="h-2 w-2 rounded-full bg-gray-800 ring-1 ring-gray-700" />
              {/* Speaker */}
              <div className="h-1.5 w-12 rounded-full bg-gray-800" />
            </div>
          </div>

          {/* Screen content */}
          <div className="relative bg-white">
            {children}
          </div>

          {/* Home indicator */}
          <div className="relative z-20 flex h-8 items-center justify-center bg-white">
            <div className="h-1 w-32 rounded-full bg-gray-900/20" />
          </div>
        </div>

        {/* Power button */}
        <div className="absolute -right-1 top-32 h-16 w-1 rounded-l-sm bg-gray-700 shadow-inner" />
        
        {/* Volume buttons */}
        <div className="absolute -left-1 top-28 h-8 w-1 rounded-r-sm bg-gray-700 shadow-inner" />
        <div className="absolute -left-1 top-40 h-8 w-1 rounded-r-sm bg-gray-700 shadow-inner" />
        <div className="absolute -left-1 top-52 h-12 w-1 rounded-r-sm bg-gray-700 shadow-inner" />
      </div>

      {/* Reflection effect */}
      <div className="pointer-events-none absolute inset-0 rounded-[3rem] bg-linear-to-tr from-transparent via-white/5 to-transparent" />
    </div>
  );
};

