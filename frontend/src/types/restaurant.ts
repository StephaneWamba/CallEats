// Restaurant Types (matching backend models)
export interface RestaurantResponse {
  id: string;
  name: string;
  api_key: string;
  phone_number: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface CreateRestaurantRequest {
  name: string;
  api_key?: string;
  assign_phone?: boolean;
  force_twilio?: boolean;
}

export interface UpdateRestaurantRequest {
  name?: string;
}

export interface RestaurantStatsResponse {
  total_calls_today: number;
  menu_items_count: number;
  phone_status: 'active' | 'inactive';
  categories_count: number;
}

export interface DeleteRestaurantResponse {
  success: boolean;
  message: string;
}

