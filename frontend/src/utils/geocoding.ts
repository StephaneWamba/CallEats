/**
 * Geocoding utilities using Nominatim (OpenStreetMap)
 * Free and open-source geocoding service
 */

export interface GeocodeResult {
  lat: number;
  lng: number;
  display_name: string;
  address?: {
    city?: string;
    state?: string;
    country?: string;
    postcode?: string;
  };
}

/**
 * Geocode an address to coordinates
 */
export const geocodeAddress = async (address: string): Promise<GeocodeResult | null> => {
  try {
    const response = await fetch(
      `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}&limit=1`,
      {
        headers: {
          'User-Agent': 'RestaurantVoiceAssistant/1.0', // Required by Nominatim
        },
      }
    );

    if (!response.ok) {
      return null;
    }

    const data = await response.json();
    if (data && data.length > 0) {
      const result = data[0];
      return {
        lat: parseFloat(result.lat),
        lng: parseFloat(result.lon),
        display_name: result.display_name,
        address: result.address,
      };
    }

    return null;
  } catch (error) {
    console.error('Geocoding error:', error);
    return null;
  }
};

/**
 * Reverse geocode coordinates to an address
 */
export const reverseGeocode = async (lat: number, lng: number): Promise<GeocodeResult | null> => {
  try {
    const response = await fetch(
      `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`,
      {
        headers: {
          'User-Agent': 'RestaurantVoiceAssistant/1.0', // Required by Nominatim
        },
      }
    );

    if (!response.ok) {
      return null;
    }

    const data = await response.json();
    if (data) {
      return {
        lat: parseFloat(data.lat),
        lng: parseFloat(data.lon),
        display_name: data.display_name,
        address: data.address,
      };
    }

    return null;
  } catch (error) {
    console.error('Reverse geocoding error:', error);
    return null;
  }
};

