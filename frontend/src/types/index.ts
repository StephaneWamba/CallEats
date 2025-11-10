// Generic API Types
export interface ApiError {
  detail: string | { [key: string]: string[] };
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

// Re-export all types
export * from './auth';
export * from './restaurant';
export * from './menu';
export * from './operating-hours';
export * from './delivery-zones';
export * from './calls';

