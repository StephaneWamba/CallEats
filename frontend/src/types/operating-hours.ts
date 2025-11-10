// Operating Hours Types
export interface OperatingHourResponse {
  id: string;
  restaurant_id: string;
  day_of_week: string; // "Monday", "Tuesday", etc.
  open_time: string; // HH:MM:SS format
  close_time: string; // HH:MM:SS format
  is_closed: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface OperatingHourRequest {
  day_of_week: string; // "Monday", "Tuesday", etc.
  open_time: string; // HH:MM:SS format
  close_time: string; // HH:MM:SS format
  is_closed?: boolean;
}

export interface BulkUpdateOperatingHoursRequest {
  hours: OperatingHourRequest[];
}

