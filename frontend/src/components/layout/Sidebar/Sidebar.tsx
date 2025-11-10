import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, UtensilsCrossed, Clock, MapPin, Phone, Settings as SettingsIcon } from 'lucide-react';
import { ROUTES } from '../../../config/routes';
import { Logo } from '../../common/Logo';

const navItems = [
  { to: ROUTES.DASHBOARD, icon: LayoutDashboard, label: 'Dashboard' },
  { to: ROUTES.MENU_BUILDER, icon: UtensilsCrossed, label: 'Menu Builder' },
  { to: ROUTES.OPERATING_HOURS, icon: Clock, label: 'Operating Hours' },
  { to: ROUTES.DELIVERY_ZONES, icon: MapPin, label: 'Delivery Zones' },
  { to: ROUTES.CALL_HISTORY, icon: Phone, label: 'Call History' },
  { to: ROUTES.SETTINGS, icon: SettingsIcon, label: 'Settings' },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col lg:border-r lg:border-gray-200 lg:bg-white/50 lg:pt-16 lg:backdrop-blur-sm">
      {/* Logo in sidebar (optional branding) */}
      <div className="border-b border-gray-200 p-4">
        <Logo size="sm" showText={false} />
      </div>

      <nav className="flex flex-1 flex-col gap-1 p-4">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
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
  );
};

