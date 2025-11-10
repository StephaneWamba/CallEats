// Menu Types (matching backend models)
export interface MenuItemResponse {
  id: string;
  restaurant_id: string;
  name: string;
  description: string | null;
  price: number; // Decimal from backend, converted to number
  category_id: string | null;
  category: string | null; // Legacy field
  available: boolean;
  image_url: string | null;
  modifiers?: ModifierResponse[]; // Linked modifiers (returned by GET endpoint)
  created_at: string;
  updated_at: string;
}

export interface CreateMenuItemRequest {
  name: string;
  description?: string | null;
  price: number;
  category_id?: string | null;
  available?: boolean;
}

export interface UpdateMenuItemRequest {
  name?: string;
  description?: string | null;
  price?: number;
  category_id?: string | null;
  available?: boolean;
}

export interface CategoryResponse {
  id: string;
  restaurant_id: string;
  name: string;
  description: string | null;
  display_order: number;
  created_at: string;
  updated_at: string;
}

export interface CreateCategoryRequest {
  name: string;
  description?: string | null;
  display_order?: number;
}

export interface UpdateCategoryRequest {
  name?: string;
  description?: string | null;
  display_order?: number;
}

export interface ModifierResponse {
  id: string;
  restaurant_id: string;
  name: string;
  description: string | null;
  price: number; // Decimal from backend, converted to number
  created_at: string;
  updated_at: string;
}

export interface CreateModifierRequest {
  name: string;
  description?: string | null;
  price: number;
}

export interface UpdateModifierRequest {
  name?: string;
  description?: string | null;
  price?: number;
}

export interface LinkModifierRequest {
  modifier_id: string;
  is_required?: boolean;
  display_order?: number;
}

export interface MenuItemModifierLink {
  id: string;
  menu_item_id: string;
  modifier_id: string;
  modifier: ModifierResponse; // Full modifier details included in response
  is_required: boolean;
  display_order: number;
  created_at: string;
}

