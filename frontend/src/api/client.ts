import axios, { AxiosError } from 'axios';
import type { AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import * as Sentry from '@sentry/react';
import { API_BASE_URL } from '@/config/env';
import { addApiBreadcrumb } from '@/config/sentry';
import { ROUTES } from '@/config/routes';

// Create axios instance with credentials for httpOnly cookies
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,  // Required for httpOnly cookies
  timeout: 30000, // 30 seconds timeout for all requests
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Cookies are sent automatically by browser
// No manual token management needed!
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Cookies are automatically sent with requests
    // No Authorization header needed - backend reads from cookies
    
    // Add breadcrumb for API call tracking
    if (config.url) {
      addApiBreadcrumb(config.method?.toUpperCase() || 'GET', config.url);
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle errors and token refresh
apiClient.interceptors.response.use(
  (response) => {
    // Add breadcrumb for successful API calls
    if (response.config.url) {
      addApiBreadcrumb(
        response.config.method?.toUpperCase() || 'GET',
        response.config.url,
        response.status,
        false
      );
    }
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Add breadcrumb for failed API calls
    if (originalRequest?.url) {
      addApiBreadcrumb(
        originalRequest.method?.toUpperCase() || 'GET',
        originalRequest.url,
        error.response?.status,
        true
      );
    }

    // Skip token refresh for login, register, refresh, and me endpoints
    // The /api/auth/me endpoint is used by AuthProvider to check auth status
    // We don't want to trigger refresh/redirect on this endpoint
    const skipRefreshUrls = [
      '/api/auth/login', 
      '/api/auth/register', 
      '/api/auth/register-with-restaurant', 
      '/api/auth/refresh',
      '/api/auth/me'  // Don't refresh on auth check - let AuthProvider handle it
    ];
    const isSkipRefresh = skipRefreshUrls.some((url) => originalRequest.url?.includes(url));

    // Handle 401 Unauthorized - Try to refresh token using cookie
    if (error.response?.status === 401 && !originalRequest._retry && !isSkipRefresh) {
      originalRequest._retry = true;

      try {
        // Refresh token - cookies are sent automatically
        // Backend reads refresh_token from cookie and sets new access_token cookie
        await axios.post(`${API_BASE_URL}/api/auth/refresh`, {}, {
          withCredentials: true,  // Ensure cookies are sent
        });

        // Retry original request - new access_token cookie will be sent automatically
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Log refresh failure to Sentry (only if initialized)
        try {
          Sentry.captureException(refreshError, {
            tags: {
              error_type: 'token_refresh_failed',
            },
            extra: {
              original_url: originalRequest.url,
              original_method: originalRequest.method,
            },
          });
        } catch (_sentryError) {
          // Sentry not initialized, ignore
        }

        // Refresh failed - only redirect if not already on login page
        // This prevents infinite redirect loops
        if (window.location.pathname !== ROUTES.LOGIN && window.location.pathname !== ROUTES.SIGNUP) {
          window.location.href = ROUTES.LOGIN;
        }
        return Promise.reject(refreshError);
      }
    }

    // Log server errors (5xx) and unexpected errors to Sentry
    // Skip 401 (handled above) and 403/404 (expected errors)
    const statusCode = error.response?.status;
    try {
      if (statusCode && statusCode >= 500) {
        // Server errors (5xx)
        Sentry.captureException(error, {
          tags: {
            error_type: 'api_server_error',
            status_code: statusCode.toString(),
          },
          extra: {
            url: originalRequest?.url,
            method: originalRequest?.method,
            response_data: error.response?.data,
          },
          level: 'error',
        });
      } else if (!statusCode) {
        // Network errors (no response)
        Sentry.captureException(error, {
          tags: {
            error_type: 'api_network_error',
          },
          extra: {
            url: originalRequest?.url,
            method: originalRequest?.method,
            code: error.code,
          },
          level: 'error',
        });
      }
    } catch (_sentryError) {
      // Sentry not initialized, ignore
    }

    return Promise.reject(error);
  }
);

export default apiClient;

