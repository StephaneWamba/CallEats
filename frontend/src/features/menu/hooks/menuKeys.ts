/**
 * Query keys for menu feature
 * Centralized query key management
 */

export const menuKeys = {
  all: ['menu'] as const,
  categories: (restaurantId: string) => [...menuKeys.all, 'categories', restaurantId] as const,
  menuItems: (restaurantId: string) => [...menuKeys.all, 'menuItems', restaurantId] as const,
  modifiers: (restaurantId: string) => [...menuKeys.all, 'modifiers', restaurantId] as const,
};

