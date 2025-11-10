import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Menu, User, LogOut, Settings as SettingsIcon } from 'lucide-react';
import { useAppSelector, useAppDispatch } from '../../../store/hooks';
import { logout } from '../../../store/slices/authSlice';
import { ROUTES } from '../../../config/routes';
import { Logo } from '../../common/Logo';

interface HeaderProps {
  onMenuToggle: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onMenuToggle }) => {
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const dispatch = useAppDispatch();
  const { user } = useAppSelector((state) => state.auth);
  const { restaurant: currentRestaurant } = useAppSelector((state) => state.restaurant);

  const handleLogout = () => {
    dispatch(logout());
  };

  return (
    <header className="sticky top-0 z-40 border-b border-gray-200 bg-white/95 shadow-sm backdrop-blur-sm">
      <div className="flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Left: Menu button (mobile) + Logo */}
        <div className="flex items-center gap-3 sm:gap-4">
          <button
            onClick={onMenuToggle}
            className="rounded-lg p-2 text-gray-600 transition-colors hover:bg-gray-100 lg:hidden"
            aria-label="Toggle menu"
          >
            <Menu className="h-6 w-6" />
          </button>

          <Link to={ROUTES.DASHBOARD} className="flex items-center">
            <Logo size="sm" showText={false} />
            <span className="ml-2 hidden text-xl font-bold text-gray-900 sm:inline">
              Voice Assistant
            </span>
          </Link>
        </div>

        {/* Center: Restaurant name (hidden on mobile) */}
        {currentRestaurant && (
          <div className="hidden items-center gap-2 text-sm md:flex">
            <span className="font-medium text-gray-900">{currentRestaurant.name}</span>
            {currentRestaurant.phone_number && (
              <span className="rounded-full bg-success/10 px-2 py-1 text-xs font-medium text-success">
                {currentRestaurant.phone_number}
              </span>
            )}
          </div>
        )}

        {/* Right: User menu */}
        <div className="relative">
          <button
            onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
            className="flex items-center gap-2 rounded-lg p-2 text-gray-700 hover:bg-gray-100"
            aria-label="User menu"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-primary">
              <User className="h-4 w-4" />
            </div>
            <span className="hidden text-sm font-medium sm:inline">{user?.email}</span>
          </button>

          {/* Dropdown menu */}
          {isUserMenuOpen && (
            <>
              {/* Backdrop */}
              <div
                className="fixed inset-0 z-40"
                onClick={() => setIsUserMenuOpen(false)}
              />

              {/* Menu */}
              <div className="absolute right-0 top-full mt-2 w-56 rounded-lg border border-gray-200 bg-white shadow-lg z-50">
                <div className="border-b border-gray-100 p-3">
                  <p className="text-sm font-medium text-gray-900">{user?.email}</p>
                  {currentRestaurant && (
                    <p className="mt-1 text-xs text-gray-500">{currentRestaurant.name}</p>
                  )}
                </div>

                <div className="p-2">
                  <Link
                    to={ROUTES.SETTINGS}
                    onClick={() => setIsUserMenuOpen(false)}
                    className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <SettingsIcon className="h-4 w-4" />
                    Settings
                  </Link>

                  <button
                    onClick={() => {
                      setIsUserMenuOpen(false);
                      handleLogout();
                    }}
                    className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm text-error hover:bg-error/5"
                  >
                    <LogOut className="h-4 w-4" />
                    Sign Out
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  );
};

