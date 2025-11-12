import React, { createContext, useContext, useState, useCallback, useEffect, useRef } from 'react';
import type { ReactNode } from 'react';
import type { UserResponse } from '@/types/auth';
import { getCurrentUser, logout as logoutApi } from '@/api/auth';
import { setSentryUser } from '@/config/sentry';

interface AuthContextType {
  user: UserResponse | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (user: UserResponse) => void;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

/**
 * AuthProvider - Manages authentication state using Context API
 * 
 * Features:
 * - Initializes auth state on mount by checking cookies
 * - Provides login/logout functions
 * - Persists user in localStorage (non-sensitive data only)
 * - Integrates with Sentry for error tracking
 */
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<UserResponse | null>(() => {
    // Try to restore user from localStorage on mount
    try {
      const stored = localStorage.getItem('auth_user');
      if (stored) {
        return JSON.parse(stored);
      }
    } catch (_error) {
      // Failed to restore user from localStorage, ignore
    }
    return null;
  });
  const [isLoading, setIsLoading] = useState(true);
  const hasInitialized = useRef(false);

  // Persist user to localStorage when it changes
  useEffect(() => {
    if (user) {
      try {
        localStorage.setItem('auth_user', JSON.stringify(user));
      } catch (_error) {
        // Failed to persist user to localStorage, ignore
      }
    } else {
      try {
        localStorage.removeItem('auth_user');
      } catch (_error) {
        // Failed to remove user from localStorage, ignore
      }
    }
  }, [user]);

  // Initialize auth state on mount
  useEffect(() => {
    if (hasInitialized.current) {
      return;
    }

    const initializeAuth = async () => {
      hasInitialized.current = true;
      setIsLoading(true);

      try {
        // Try to get current user - this will verify cookies
        // If cookies are valid, backend will return user info
        const userData = await getCurrentUser();
        
        // If successful, user is authenticated
        setUser(userData);
        
        // Set user context in Sentry for error tracking
        setSentryUser({
          id: userData.user_id,
          email: userData.email,
        });
      } catch (_error) {
        // Cookies are invalid/expired or user not authenticated
        // Clear auth state
        setUser(null);
        setSentryUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const login = useCallback((userData: UserResponse) => {
    setUser(userData);
    setSentryUser({
      id: userData.user_id,
      email: userData.email,
    });
  }, []);

  const logout = useCallback(async () => {
    try {
      // Call logout API to clear cookies on backend
      await logoutApi();
    } catch (_error) {
      // Even if API call fails, clear local state
    } finally {
      // Always clear local state
      setUser(null);
      setSentryUser(null);
    }
  }, []);

  const refreshUser = useCallback(async () => {
    try {
      const userData = await getCurrentUser();
      setUser(userData);
      setSentryUser({
        id: userData.user_id,
        email: userData.email,
      });
    } catch (_error) {
      // If refresh fails, user is no longer authenticated
      setUser(null);
      setSentryUser(null);
    }
  }, []);

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

