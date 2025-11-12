import { useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth as useAuthContext } from '@/contexts/AuthContext';
import {
  login as loginAPI,
  registerWithRestaurant as registerWithRestaurantAPI,
  resetPassword as resetPasswordAPI,
  changePassword as changePasswordAPI,
  getCurrentUser as getCurrentUserAPI,
} from '@/api/auth';
import type {
  LoginRequest,
  RegisterWithRestaurantRequest,
  ResetPasswordRequest,
  ChangePasswordRequest,
} from '@/types/auth';
import { ROUTES } from '@/config/routes';

/**
 * Enhanced auth hook that provides authentication actions
 * Uses AuthContext for state management
 */
export const useAuth = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated, login: loginContext, logout: logoutContext, refreshUser } = useAuthContext();

  /**
   * Login user
   */
  const login = useCallback(
    async (credentials: LoginRequest) => {
      try {
        // Login - backend sets httpOnly cookies automatically
        const response = await loginAPI(credentials);
        
        // Fetch full user info (includes restaurant_id and role)
        // Cookies are sent automatically with the request
        const fullUserInfo = await getCurrentUserAPI();
        
        // Update auth context with user info
        loginContext(fullUserInfo);
        
        return response;
      } catch (error) {
        // Cookies are managed by backend - no cleanup needed
        throw error;
      }
    },
    [loginContext]
  );

  /**
   * Register with restaurant (one-step registration)
   */
  const registerWithRestaurant = useCallback(
    async (data: RegisterWithRestaurantRequest) => {
      try {
        // Register - backend sets httpOnly cookies automatically
        const response = await registerWithRestaurantAPI(data);
        
        // Update auth context with user info
        const userData = {
          user_id: response.user.user_id,
          email: response.user.email,
          restaurant_id: response.restaurant.id,
          role: 'user' as const,
        };
        
        loginContext(userData);
        
        return response;
      } catch (error) {
        throw error;
      }
    },
    [loginContext]
  );

  /**
   * Request password reset
   */
  const resetPassword = useCallback(async (data: ResetPasswordRequest) => {
    try {
      return await resetPasswordAPI(data);
    } catch (error) {
      throw error;
    }
  }, []);

  /**
   * Change password
   */
  const changePassword = useCallback(async (data: ChangePasswordRequest) => {
    try {
      return await changePasswordAPI(data);
    } catch (error) {
      throw error;
    }
  }, []);

  /**
   * Get current user info
   */
  const getCurrentUser = useCallback(async () => {
    try {
      const userData = await getCurrentUserAPI();
      // Refresh user in context
      await refreshUser();
      return userData;
    } catch (error) {
      throw error;
    }
  }, [refreshUser]);

  /**
   * Logout user
   */
  const logout = useCallback(async () => {
    await logoutContext();
    navigate(ROUTES.LANDING);
  }, [logoutContext, navigate]);

  return {
    // State
    user,
    isAuthenticated,
    // Actions
    login,
    registerWithRestaurant,
    resetPassword,
    changePassword,
    getCurrentUser,
    logout,
  };
};

