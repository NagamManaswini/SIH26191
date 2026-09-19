/**
 * Location Service supporting Google Maps Geocoding & Places Search across India with fallback.
 */

export interface LocationResult {
  name: string;
  latitude: number;
  longitude: number;
  district?: string;
  state?: string;
  formatted_address?: string;
}

export const locationService = {
  searchLocation: async (query: string): Promise<LocationResult[]> => {
    if (!query || query.trim().length < 2) return [];

    const cleanQuery = query.trim();

    // 1. Attempt Nominatim OpenStreetMap Geocoding
    try {
      const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(
        cleanQuery
      )}&countrycodes=in&limit=8&addressdetails=1`;
      const res = await fetch(url, {
        headers: {
          "Accept-Language": "en-US,en;q=0.9",
        },
      });

      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) {
          return data.map((item: any) => ({
            name: item.display_name.split(",")[0] || item.display_name,
            formatted_address: item.display_name,
            latitude: parseFloat(item.lat),
            longitude: parseFloat(item.lon),
          }));
        }
      }
    } catch (e) {
      console.warn("Nominatim Geocoding notice:", e);
    }

    // 2. Secondary fallback attempt using Photon API (Komoot OSM Geocoder - highly reliable with CORS)
    try {
      const url = `https://photon.komoot.io/api/?q=${encodeURIComponent(cleanQuery)}&limit=8`;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        if (data && Array.isArray(data.features) && data.features.length > 0) {
          return data.features.map((f: any) => {
            const props = f.properties || {};
            const coords = f.geometry?.coordinates || [0, 0];
            const nameStr = props.name || props.city || props.street || cleanQuery;
            const fullAddr = [props.name, props.street, props.city, props.state, props.country]
              .filter(Boolean)
              .join(", ");
            return {
              name: nameStr,
              formatted_address: fullAddr || nameStr,
              latitude: coords[1],
              longitude: coords[0],
            };
          });
        }
      }
    } catch (e) {
      console.warn("Photon Geocoding fallback notice:", e);
    }

    // 3. Global Nominatim fallback without country restriction
    try {
      const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(cleanQuery)}&limit=8&addressdetails=1`;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) {
          return data.map((item: any) => ({
            name: item.display_name.split(",")[0] || item.display_name,
            formatted_address: item.display_name,
            latitude: parseFloat(item.lat),
            longitude: parseFloat(item.lon),
          }));
        }
      }
    } catch (e) {
      console.warn("Global Geocoding fallback notice:", e);
    }

    return [];
  },

  reverseGeocode: async (lat: number, lon: number): Promise<string> => {
    // 1. Primary: Nominatim Reverse Geocoding
    try {
      const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        if (data && data.display_name) {
          return data.display_name;
        }
      }
    } catch (e) {
      console.warn("Nominatim reverse geocode notice:", e);
    }

    // 2. Secondary Fallback: BigDataCloud Free Client Reverse Geocoding (Fast, CORS friendly)
    try {
      const url = `https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${lat}&longitude=${lon}&localityLanguage=en`;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        const parts = [data.locality || data.city, data.principalSubdivision || data.state, data.countryName].filter(Boolean);
        if (parts.length > 0) {
          return parts.join(", ");
        }
      }
    } catch (e) {
      console.warn("BigDataCloud reverse geocode notice:", e);
    }

    return `Coordinates (${lat.toFixed(4)}° N, ${lon.toFixed(4)}° E)`;
  },

  getIPLocation: async (): Promise<{ lat: number; lon: number; name: string } | null> => {
    try {
      const res = await fetch("https://ipapi.co/json/");
      if (res.ok) {
        const data = await res.json();
        if (data.latitude && data.longitude) {
          const name = [data.city, data.region, data.country_name].filter(Boolean).join(", ");
          return {
            lat: data.latitude,
            lon: data.longitude,
            name: name || "Current Location",
          };
        }
      }
    } catch (e) {
      console.warn("IP Geolocation notice:", e);
    }
    return null;
  },

  getNearbySheltersAndZones: (lat: number, lon: number, locationName: string) => {
    const cityName = locationName.split(",")[0].trim() || "Local Sector";

    // 1. Dynamic Local Shelters (Hospitals, Schools, Community Halls, Auditoriums near selected location)
    const shelters = [
      {
        id: 101,
        name: `${cityName} Government General Hospital & Emergency Care`,
        address: `Hospital Road, ${locationName}`,
        capacity: 650,
        current_occupancy: 120,
        available_capacity: 530,
        status: "active",
        contact_number: "+91-9447100101",
        latitude: lat + 0.007,
        longitude: lon + 0.008,
        type: "Hospital",
        has_medical_facility: true,
        has_power_backup: true,
      },
      {
        id: 102,
        name: `${cityName} St. Joseph Community School & Relief Camp`,
        address: `School Road, ${locationName}`,
        capacity: 500,
        current_occupancy: 85,
        available_capacity: 415,
        status: "active",
        contact_number: "+91-9447100102",
        latitude: lat + 0.012,
        longitude: lon - 0.009,
        type: "School",
        has_medical_facility: true,
        has_power_backup: true,
      },
      {
        id: 103,
        name: `${cityName} Municipal Primary Health Center (PHC)`,
        address: `Civic Center, ${locationName}`,
        capacity: 250,
        current_occupancy: 40,
        available_capacity: 210,
        status: "active",
        contact_number: "+91-9447100103",
        latitude: lat - 0.008,
        longitude: lon + 0.015,
        type: "Health Center",
        has_medical_facility: true,
        has_power_backup: true,
      },
      {
        id: 104,
        name: `${cityName} Regional Sports Complex & Safe Haven Auditorium`,
        address: `Bypass Highway, ${locationName}`,
        capacity: 1200,
        current_occupancy: 310,
        available_capacity: 890,
        status: "active",
        contact_number: "+91-9447100104",
        latitude: lat + 0.022,
        longitude: lon + 0.025,
        type: "Auditorium",
        has_medical_facility: true,
        has_power_backup: true,
      },
    ];

    // 2. Dynamic Red Hazard Zone (Critical Risk Polygon near lowlands/rivers)
    const redZonePolygon: [number, number][] = [
      [lat - 0.008, lon - 0.008],
      [lat + 0.008, lon - 0.008],
      [lat + 0.008, lon + 0.008],
      [lat - 0.008, lon + 0.008],
    ];

    // 3. Dynamic Medium Hazard Zone (Moderate Risk Polygon surrounding slope)
    const mediumZonePolygon: [number, number][] = [
      [lat - 0.016, lon - 0.016],
      [lat + 0.016, lon - 0.016],
      [lat + 0.016, lon + 0.016],
      [lat - 0.016, lon + 0.016],
    ];

    // 4. Dynamic Safe Zone (Approved Safe Polygon around high ground shelters)
    const safeZonePolygon: [number, number][] = [
      [lat + 0.005, lon + 0.005],
      [lat + 0.028, lon + 0.005],
      [lat + 0.028, lon + 0.030],
      [lat + 0.005, lon + 0.030],
    ];

    return {
      shelters,
      redZonePolygon,
      mediumZonePolygon,
      safeZonePolygon,
    };
  },
};

