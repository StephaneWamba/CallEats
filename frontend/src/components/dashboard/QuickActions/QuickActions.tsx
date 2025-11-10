import React from 'react';
import { Link } from 'react-router-dom';
import { UtensilsCrossed, Clock, MapPin, Settings as SettingsIcon } from 'lucide-react';
import { ROUTES } from '../../../config/routes';

const actions = [
  {
    to: ROUTES.MENU_BUILDER,
    icon: UtensilsCrossed,
    label: 'Manage Menu',
    description: 'Add, edit, or remove menu items',
    color: 'text-primary',
    bgColor: 'bg-primary/10',
  },
  {
    to: ROUTES.OPERATING_HOURS,
    icon: Clock,
    label: 'Set Hours',
    description: 'Update operating hours',
    color: 'text-secondary',
    bgColor: 'bg-secondary/10',
  },
  {
    to: ROUTES.DELIVERY_ZONES,
    icon: MapPin,
    label: 'Delivery Zones',
    description: 'Configure delivery areas',
    color: 'text-success',
    bgColor: 'bg-success/10',
  },
  {
    to: ROUTES.SETTINGS,
    icon: SettingsIcon,
    label: 'Settings',
    description: 'Manage account settings',
    color: 'text-gray-600',
    bgColor: 'bg-gray-100',
  },
];

export const QuickActions: React.FC = () => {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <h2 className="mb-4 text-lg font-semibold text-gray-900">Quick Actions</h2>
      <div className="grid gap-3 sm:grid-cols-2">
        {actions.map((action) => {
          const Icon = action.icon;
          return (
            <Link
              key={action.to}
              to={action.to}
              className="group flex items-center gap-4 rounded-lg border border-gray-200 bg-white p-4 transition-all hover:border-primary/30 hover:shadow-md"
            >
              <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${action.bgColor} transition-transform group-hover:scale-110`}>
                <Icon className={`h-5 w-5 ${action.color}`} />
              </div>
              <div className="flex-1">
                <h3 className="text-sm font-semibold text-gray-900">{action.label}</h3>
                <p className="text-xs text-gray-600">{action.description}</p>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
};

