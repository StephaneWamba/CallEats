/**
 * Environment variable validation
 * Validates required environment variables and provides helpful error messages
 */
function validateEnv() {
  const errors: string[] = [];
  const warnings: string[] = [];

  // API_BASE_URL is required in production
  if (import.meta.env.PROD && !import.meta.env.VITE_API_BASE_URL) {
    errors.push('VITE_API_BASE_URL is required in production');
  }

  // Warn if Sentry DSN is missing (in any environment)
  if (!import.meta.env.VITE_SENTRY_DSN) {
    warnings.push('VITE_SENTRY_DSN is not set - error tracking will be disabled');
  }

  if (errors.length > 0) {
    throw new Error(
      `Environment validation failed:\n${errors.join('\n')}\n\n` +
      'Please check your .env file and ensure all required variables are set.'
    );
  }

  // Show warnings in the environment where they're detected
  if (warnings.length > 0) {
    console.warn('Environment warnings:', warnings.join(', '));
  }
}

// Validate environment variables on module load
try {
  validateEnv();
} catch (error) {
  // In development, log the error but don't block
  if (import.meta.env.DEV) {
    console.error(error);
  } else {
    // In production, throw to prevent app from starting with invalid config
    throw error;
  }
}

// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Sentry Configuration
export const SENTRY_DSN = import.meta.env.VITE_SENTRY_DSN;
export const SENTRY_ENVIRONMENT = import.meta.env.VITE_SENTRY_ENVIRONMENT || import.meta.env.MODE || 'development';
export const SENTRY_ENABLED = import.meta.env.VITE_SENTRY_ENABLED !== 'false'; // Enabled by default unless explicitly disabled

// API Endpoints
export const API_ENDPOINTS = {
  // Auth
  AUTH: {
    LOGIN: '/api/auth/login',
    REGISTER: '/api/auth/register',
    REGISTER_WITH_RESTAURANT: '/api/auth/register-with-restaurant',
    RESET_PASSWORD: '/api/auth/reset-password',
    CHANGE_PASSWORD: '/api/auth/change-password',
    REFRESH_TOKEN: '/api/auth/refresh',
    ME: '/api/auth/me',
    LOGOUT: '/api/auth/logout',
  },
  // Restaurants
  RESTAURANTS: {
    ME: '/api/restaurants/me',
    GET: (id: string) => `/api/restaurants/${id}`,
    STATS: (id: string) => `/api/restaurants/${id}/stats`,
    UPDATE: (id: string) => `/api/restaurants/${id}`,
    DELETE: (id: string) => `/api/restaurants/${id}`,
  },
  // Categories
  CATEGORIES: {
    LIST: (restaurantId: string) => `/api/restaurants/${restaurantId}/categories`,
    CREATE: (restaurantId: string) => `/api/restaurants/${restaurantId}/categories`,
    GET: (restaurantId: string, categoryId: string) => `/api/restaurants/${restaurantId}/categories/${categoryId}`,
    UPDATE: (restaurantId: string, categoryId: string) => `/api/restaurants/${restaurantId}/categories/${categoryId}`,
    DELETE: (restaurantId: string, categoryId: string) => `/api/restaurants/${restaurantId}/categories/${categoryId}`,
  },
  // Menu Items
  MENU_ITEMS: {
    LIST: (restaurantId: string) => `/api/restaurants/${restaurantId}/menu-items`,
    CREATE: (restaurantId: string) => `/api/restaurants/${restaurantId}/menu-items`,
    GET: (restaurantId: string, itemId: string) => `/api/restaurants/${restaurantId}/menu-items/${itemId}`,
    UPDATE: (restaurantId: string, itemId: string) => `/api/restaurants/${restaurantId}/menu-items/${itemId}`,
    DELETE: (restaurantId: string, itemId: string) => `/api/restaurants/${restaurantId}/menu-items/${itemId}`,
    UPLOAD_IMAGE: (restaurantId: string, itemId: string) => `/api/restaurants/${restaurantId}/menu-items/${itemId}/image`,
    DELETE_IMAGE: (restaurantId: string, itemId: string) => `/api/restaurants/${restaurantId}/menu-items/${itemId}/image`,
  },
  // Modifiers
  MODIFIERS: {
    LIST: (restaurantId: string) => `/api/restaurants/${restaurantId}/modifiers`,
    CREATE: (restaurantId: string) => `/api/restaurants/${restaurantId}/modifiers`,
    GET: (restaurantId: string, modifierId: string) => `/api/restaurants/${restaurantId}/modifiers/${modifierId}`,
    UPDATE: (restaurantId: string, modifierId: string) => `/api/restaurants/${restaurantId}/modifiers/${modifierId}`,
    DELETE: (restaurantId: string, modifierId: string) => `/api/restaurants/${restaurantId}/modifiers/${modifierId}`,
    LINK_TO_ITEM: (restaurantId: string, itemId: string) => `/api/restaurants/${restaurantId}/menu-items/${itemId}/modifiers`,
    UNLINK_FROM_ITEM: (restaurantId: string, itemId: string, modifierId: string) => `/api/restaurants/${restaurantId}/menu-items/${itemId}/modifiers/${modifierId}`,
  },
  // Operating Hours
  OPERATING_HOURS: {
    LIST: (restaurantId: string) => `/api/restaurants/${restaurantId}/hours`,
    BULK_UPDATE: (restaurantId: string) => `/api/restaurants/${restaurantId}/hours`,
    DELETE_ALL: (restaurantId: string) => `/api/restaurants/${restaurantId}/hours`,
  },
  // Delivery Zones
  DELIVERY_ZONES: {
    LIST: (restaurantId: string) => `/api/restaurants/${restaurantId}/zones`,
    CREATE: (restaurantId: string) => `/api/restaurants/${restaurantId}/zones`,
    GET: (restaurantId: string, zoneId: string) => `/api/restaurants/${restaurantId}/zones/${zoneId}`,
    UPDATE: (restaurantId: string, zoneId: string) => `/api/restaurants/${restaurantId}/zones/${zoneId}`,
    DELETE: (restaurantId: string, zoneId: string) => `/api/restaurants/${restaurantId}/zones/${zoneId}`,
    SET_BOUNDARY: (restaurantId: string, zoneId: string) => `/api/restaurants/${restaurantId}/zones/${zoneId}/boundary`,
    GET_BOUNDARY: (restaurantId: string, zoneId: string) => `/api/restaurants/${restaurantId}/zones/${zoneId}/map`,
    CHECK_POINT: (restaurantId: string) => `/api/restaurants/${restaurantId}/zones/check`,
  },
  // Calls
  CALLS: {
    LIST: (restaurantId: string, limit?: number) => 
      `/api/calls?restaurant_id=${restaurantId}${limit ? `&limit=${limit}` : ''}`,
    GET: (callId: string, restaurantId: string) => 
      `/api/calls/${callId}?restaurant_id=${restaurantId}`,
  },
} as const;

