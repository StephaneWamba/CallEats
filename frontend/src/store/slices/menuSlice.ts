import { createSlice } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import type {
  CategoryResponse,
  MenuItemResponse,
  ModifierResponse,
} from '@/types/menu';

interface MenuState {
  categories: CategoryResponse[];
  menuItems: MenuItemResponse[];
  modifiers: ModifierResponse[];
  selectedCategoryId: string | null;
}

const initialState: MenuState = {
  categories: [],
  menuItems: [],
  modifiers: [],
  selectedCategoryId: null,
};

const menuSlice = createSlice({
  name: 'menu',
  initialState,
  reducers: {
    // Categories
    setCategories: (state, action: PayloadAction<CategoryResponse[]>) => {
      state.categories = action.payload;
    },
    addCategory: (state, action: PayloadAction<CategoryResponse>) => {
      state.categories.push(action.payload);
    },
    updateCategoryInState: (state, action: PayloadAction<CategoryResponse>) => {
      const index = state.categories.findIndex((c) => c.id === action.payload.id);
      if (index !== -1) {
        state.categories[index] = action.payload;
      }
    },
    removeCategory: (state, action: PayloadAction<string>) => {
      state.categories = state.categories.filter((c) => c.id !== action.payload);
    },

    // Menu Items
    setMenuItems: (state, action: PayloadAction<MenuItemResponse[]>) => {
      state.menuItems = action.payload;
    },
    addMenuItem: (state, action: PayloadAction<MenuItemResponse>) => {
      state.menuItems.push(action.payload);
    },
    updateMenuItemInState: (state, action: PayloadAction<MenuItemResponse>) => {
      const index = state.menuItems.findIndex((i) => i.id === action.payload.id);
      if (index !== -1) {
        state.menuItems[index] = action.payload;
      }
    },
    removeMenuItem: (state, action: PayloadAction<string>) => {
      state.menuItems = state.menuItems.filter((i) => i.id !== action.payload);
    },

    // Modifiers
    setModifiers: (state, action: PayloadAction<ModifierResponse[]>) => {
      state.modifiers = action.payload;
    },
    addModifier: (state, action: PayloadAction<ModifierResponse>) => {
      state.modifiers.push(action.payload);
    },
    updateModifierInState: (state, action: PayloadAction<ModifierResponse>) => {
      const index = state.modifiers.findIndex((m) => m.id === action.payload.id);
      if (index !== -1) {
        state.modifiers[index] = action.payload;
      }
    },
    removeModifier: (state, action: PayloadAction<string>) => {
      state.modifiers = state.modifiers.filter((m) => m.id !== action.payload);
    },

    // UI State
    setSelectedCategory: (state, action: PayloadAction<string | null>) => {
      state.selectedCategoryId = action.payload;
    },

    // Clear All
    clearMenu: (state) => {
      state.categories = [];
      state.menuItems = [];
      state.modifiers = [];
      state.selectedCategoryId = null;
    },
  },
});

export const {
  setCategories,
  addCategory,
  updateCategoryInState,
  removeCategory,
  setMenuItems,
  addMenuItem,
  updateMenuItemInState,
  removeMenuItem,
  setModifiers,
  addModifier,
  updateModifierInState,
  removeModifier,
  setSelectedCategory,
  clearMenu,
} = menuSlice.actions;

export default menuSlice.reducer;

