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
  session: {
    access_token: string;
    refresh_token: string;
    expires_in: number;
    token_type: string;
  };
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  token_type: string;
  user: {
    id: string;  // Note: Backend returns 'id', not 'user_id'
    email: string;
  };
}

export interface ResetPasswordRequest {
  email: string;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface RefreshTokenResponse {
  access_token: string;
  refresh_token?: string;
  expires_in: number;
  token_type: string;
}

export interface UserResponse {
  user_id: string;
  email: string;
  restaurant_id: string;
  role: string;
}

