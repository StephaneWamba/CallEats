import { useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { setCredentials, logout as logoutAction, updateTokens } from '@/store/slices/authSlice';
import {
  login as loginAPI,
  registerWithRestaurant as registerWithRestaurantAPI,
  resetPassword as resetPasswordAPI,
  changePassword as changePasswordAPI,
  refreshToken as refreshTokenAPI,
  getCurrentUser as getCurrentUserAPI,
  logout as logoutAPI,
} from '@/api/auth';
import type {
  LoginRequest,
  RegisterWithRestaurantRequest,
  ResetPasswordRequest,
  ChangePasswordRequest,
} from '@/types/auth';
import { ROUTES } from '@/config/routes';

export const useAuth = () => {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const { user, accessToken, refreshToken: refreshTokenValue, isAuthenticated } = useAppSelector(
    (state) => state.auth
  );

  /**
   * Login user
   */
  const login = useCallback(
    async (credentials: LoginRequest) => {
      try {
        // Step 1: Login and get tokens
        const response = await loginAPI(credentials);
        
        // Step 2: Store tokens temporarily in localStorage for the next API call
        localStorage.setItem('access_token', response.access_token);
        localStorage.setItem('refresh_token', response.refresh_token);
        
        // Step 3: Fetch full user info (includes restaurant_id and role)
        const fullUserInfo = await getCurrentUserAPI();
        
        // Step 4: Update Redux store with full user info and tokens
        dispatch(
          setCredentials({
            user: fullUserInfo,
            accessToken: response.access_token,
            refreshToken: response.refresh_token,
          })
        );
        return response;
      } catch (error) {
        // Clean up tokens if login or user fetch fails
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        throw error;
      }
    },
    [dispatch]
  );

  /**
   * Register with restaurant (one-step registration)
   */
  const registerWithRestaurant = useCallback(
    async (data: RegisterWithRestaurantRequest) => {
      try {
        const response = await registerWithRestaurantAPI(data);
        dispatch(
          setCredentials({
            user: {
              user_id: response.user.user_id,
              email: response.user.email,
              restaurant_id: response.restaurant.id,
              role: 'user',
            },
            accessToken: response.session.access_token,
            refreshToken: response.session.refresh_token,
          })
        );
        return response;
      } catch (error) {
        throw error;
      }
    },
    [dispatch]
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
   * Refresh access token
   */
  const refreshAccessToken = useCallback(async () => {
    if (!refreshTokenValue) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await refreshTokenAPI({ refresh_token: refreshTokenValue });
      dispatch(
        updateTokens({
          accessToken: response.access_token,
          refreshToken: response.refresh_token,
        })
      );
      return response;
    } catch (error) {
      // Refresh failed - logout user
      dispatch(logoutAction());
      navigate(ROUTES.LOGIN);
      throw error;
    }
  }, [dispatch, navigate, refreshTokenValue]);

  /**
   * Get current user info
   */
  const getCurrentUser = useCallback(async () => {
    try {
      const userData = await getCurrentUserAPI();
      // Update user in store if needed
      return userData;
    } catch (error) {
      throw error;
    }
  }, []);

  /**
   * Logout user
   */
  const logout = useCallback(async () => {
    try {
      await logoutAPI();
    } catch (error) {
      // Ignore API errors - logout is primarily client-side
    } finally {
      dispatch(logoutAction());
      navigate(ROUTES.LANDING);
    }
  }, [dispatch, navigate]);

  return {
    // State
    user,
    accessToken,
    isAuthenticated,
    // Actions
    login,
    registerWithRestaurant,
    resetPassword,
    changePassword,
    refreshAccessToken,
    getCurrentUser,
    logout,
  };
};

