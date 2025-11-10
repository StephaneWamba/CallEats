import React from 'react';
import { Heart } from 'lucide-react';

export const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="border-t border-gray-200 bg-white/80 backdrop-blur">
      <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
          {/* Left: Copyright */}
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <span>© {currentYear} Restaurant Voice Assistant</span>
            <span className="hidden sm:inline">•</span>
            <span className="hidden sm:inline">All rights reserved</span>
          </div>

          {/* Right: Links */}
          <div className="flex items-center gap-6 text-sm">
            <a
              href="mailto:support@restaurant-voice-assistant.com"
              className="text-gray-600 transition-colors hover:text-primary"
            >
              Support
            </a>
            <a
              href="/privacy"
              className="text-gray-600 transition-colors hover:text-primary"
            >
              Privacy
            </a>
            <a
              href="/terms"
              className="text-gray-600 transition-colors hover:text-primary"
            >
              Terms
            </a>
            <div className="flex items-center gap-1 text-gray-500">
              <span>Made with</span>
              <Heart className="h-4 w-4 fill-error text-error" />
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

