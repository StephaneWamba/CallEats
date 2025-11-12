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
 * Note: Refresh token is read from httpOnly cookie by backend
 */
export const refreshToken = async (): Promise<{ message: string }> => {
  const response = await apiClient.post<{ message: string }>(
    API_ENDPOINTS.AUTH.REFRESH_TOKEN,
    {}  // Empty body - refresh token comes from cookie
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
 * Logout - clears httpOnly cookies on backend
 */
export const logout = async (): Promise<{ message: string }> => {
  const response = await apiClient.post<{ message: string }>(
    API_ENDPOINTS.AUTH.LOGOUT
  );
  return response.data;
};

