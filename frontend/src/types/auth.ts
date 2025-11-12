// Auth Types (matching backend models)
export interface RegisterRequest {
  email: string;
  password: string;
  restaurant_id: string;
}

export interface RegisterWithRestaurantRequest {
  email: string;
  password: string;
  restaurant_name: string;
}

export interface RegisterWithRestaurantResponse {
  user: {
    user_id: string;
    email: string;
  };
  restaurant: {
    id: string;
    name: string;
    phone_number: string | null;
    api_key: string;
  };
  // Tokens are in httpOnly cookies, not in response body
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  user: {
    id: string;  // Note: Backend returns 'id', not 'user_id'
    email: string;
  };
  message: string;
  // Tokens are in httpOnly cookies, not in response body
}

export interface ResetPasswordRequest {
  email: string;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

// RefreshTokenRequest is no longer needed - refresh token comes from cookie
// RefreshTokenResponse is no longer needed - tokens are in cookies

export interface UserResponse {
  user_id: string;
  email: string;
  restaurant_id: string;
  role: string;
}

