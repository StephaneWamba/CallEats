import { createSlice } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import type { RestaurantResponse } from '@/types/restaurant';

interface RestaurantState {
  restaurant: RestaurantResponse | null;
  stats: {
    total_calls_today: number;
    menu_items_count: number;
    phone_status: 'active' | 'inactive';
    categories_count: number;
  } | null;
}

const initialState: RestaurantState = {
  restaurant: null,
  stats: null,
};

const restaurantSlice = createSlice({
  name: 'restaurant',
  initialState,
  reducers: {
    setRestaurant: (state, action: PayloadAction<RestaurantResponse>) => {
      state.restaurant = action.payload;
    },
    updateRestaurant: (
      state,
      action: PayloadAction<Partial<RestaurantResponse>>
    ) => {
      if (state.restaurant) {
        state.restaurant = { ...state.restaurant, ...action.payload };
      }
    },
    setStats: (
      state,
      action: PayloadAction<{
        total_calls_today: number;
        menu_items_count: number;
        phone_status: 'active' | 'inactive';
        categories_count: number;
      }>
    ) => {
      state.stats = action.payload;
    },
    clearRestaurant: (state) => {
      state.restaurant = null;
      state.stats = null;
    },
  },
});

export const {
  setRestaurant,
  updateRestaurant,
  setStats,
  clearRestaurant,
} = restaurantSlice.actions;
export default restaurantSlice.reducer;

