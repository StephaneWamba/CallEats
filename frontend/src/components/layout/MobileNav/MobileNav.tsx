import React from 'react';
import { NavLink } from 'react-router-dom';
import { X, LayoutDashboard, UtensilsCrossed, Clock, MapPin, Phone, Settings as SettingsIcon } from 'lucide-react';
import { ROUTES } from '../../../config/routes';
import { Logo } from '../../common/Logo';

interface MobileNavProps {
  isOpen: boolean;
  onClose: () => void;
}

const navItems = [
  { to: ROUTES.DASHBOARD, icon: LayoutDashboard, label: 'Dashboard' },
  { to: ROUTES.MENU_BUILDER, icon: UtensilsCrossed, label: 'Menu Builder' },
  { to: ROUTES.OPERATING_HOURS, icon: Clock, label: 'Operating Hours' },
  { to: ROUTES.DELIVERY_ZONES, icon: MapPin, label: 'Delivery Zones' },
  { to: ROUTES.CALL_HISTORY, icon: Phone, label: 'Call History' },
  { to: ROUTES.SETTINGS, icon: SettingsIcon, label: 'Settings' },
];

export const MobileNav: React.FC<MobileNavProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-40 bg-gray-900/50 backdrop-blur-sm lg:hidden"
        onClick={onClose}
      />

      {/* Sidebar */}
      <aside className="fixed inset-y-0 left-0 z-50 w-64 border-r border-gray-200 bg-white shadow-xl lg:hidden">
        {/* Header */}
        <div className="flex h-16 items-center justify-between border-b border-gray-200 px-4">
          <Logo size="sm" showText={false} />
          <button
            onClick={onClose}
            className="rounded-lg p-2 text-gray-600 transition-colors hover:bg-gray-100"
            aria-label="Close menu"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex flex-1 flex-col gap-1 p-4">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={onClose}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-lg px-4 py-3 text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-primary/10 text-primary'
                      : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <Icon className={`h-5 w-5 ${isActive ? 'text-primary' : 'text-gray-500'}`} />
                    {item.label}
                  </>
                )}
              </NavLink>
            );
          })}
        </nav>
      </aside>
    </>
  );
};

