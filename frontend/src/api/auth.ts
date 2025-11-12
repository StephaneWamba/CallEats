import apiClient from './client';
import { API_ENDPOINTS } from './endpoints';
import type {
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterWithRestaurantRequest,
  RegisterWithRestaurantResponse,
  ResetPasswordRequest,
  ChangePasswordRequest,
  RefreshTokenRequest,
  RefreshTokenResponse,
  UserResponse,
} from '@/types/auth';

/**
 * Login user and get JWT tokens
 */
export const login = async (
  credentials: LoginRequest
): Promise<LoginResponse> => {
  const response = await apiClient.post<LoginResponse>(
    API_ENDPOINTS.AUTH.LOGIN,
    credentials
  );
  return response.data;
};

/**
 * Register a new user (requires existing restaurant_id)
 */
export const register = async (
  data: RegisterRequest
): Promise<{ message: string; user_id: string; email: string }> => {
  const response = await apiClient.post<{
    message: string;
    user_id: string;
    email: string;
  }>(API_ENDPOINTS.AUTH.REGISTER, data);
  return response.data;
};

/**
 * One-step registration: Create restaurant + user, then auto-login
 */
export const registerWithRestaurant = async (
  data: RegisterWithRestaurantRequest
): Promise<RegisterWithRestaurantResponse> => {
  const response = await apiClient.post<RegisterWithRestaurantResponse>(
    API_ENDPOINTS.AUTH.REGISTER_WITH_RESTAURANT,
    data
  );
  return response.data;
};

/**
 * Request password reset email
 */
export const resetPassword = async (
  data: ResetPasswordRequest
): Promise<{ message: string }> => {
  const response = await apiClient.post<{ message: string }>(
    API_ENDPOINTS.AUTH.RESET_PASSWORD,
    data
  );
  return response.data;
};

/**
 * Change authenticated user's password
 */
export const changePassword = async (
  data: ChangePasswordRequest
): Promise<{ message: string }> => {
  const response = await apiClient.post<{ message: string }>(
    API_ENDPOINTS.AUTH.CHANGE_PASSWORD,
    data
  );
  return response.data;
};

/**
 * Refresh expired access token
 */
export const refreshToken = async (
  data: RefreshTokenRequest
): Promise<RefreshTokenResponse> => {
  const response = await apiClient.post<RefreshTokenResponse>(
    API_ENDPOINTS.AUTH.REFRESH_TOKEN,
    data
  );
  return response.data;
};

/**
 * Get current authenticated user info
 */
export const getCurrentUser = async (): Promise<UserResponse> => {
  const response = await apiClient.get<UserResponse>(API_ENDPOINTS.AUTH.ME);
  return response.data;
};

/**
 * Logout (client-side: discard tokens)
 * Note: Backend doesn't invalidate tokens, client just removes them
 */
export const logout = async (): Promise<void> => {
  // Backend logout endpoint exists but doesn't invalidate tokens
  // Client-side logout is handled by removing tokens from localStorage
  try {
    await apiClient.post(API_ENDPOINTS.AUTH.LOGOUT);
  } catch (error) {
    // Ignore errors - logout is primarily client-side
  }
};

