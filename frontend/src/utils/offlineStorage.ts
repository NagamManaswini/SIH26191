/**
 * LocalStorage / Offline Storage Helper for caching emergency disaster data.
 */

const STORAGE_KEYS = {
  SHELTERS: "disaster_cached_shelters",
  ROUTES: "disaster_cached_routes",
  ALERTS: "disaster_cached_alerts",
  LAST_SYNC: "disaster_last_sync_timestamp",
};

export interface CachedEmergencyInstructions {
  title: string;
  steps: string[];
  hotlines: { name: string; number: string }[];
}

export const offlineStorage = {
  // Save Shelters
  saveShelters: (shelters: any[]) => {
    try {
      localStorage.setItem(STORAGE_KEYS.SHELTERS, JSON.stringify(shelters));
      localStorage.setItem(STORAGE_KEYS.LAST_SYNC, new Date().toISOString());
    } catch (e) {
      console.error("Error caching shelters:", e);
    }
  },

  // Get Cached Shelters
  getCachedShelters: (): any[] => {
    try {
      const data = localStorage.getItem(STORAGE_KEYS.SHELTERS);
      return data ? JSON.parse(data) : [];
    } catch (e) {
      return [];
    }
  },

  // Save Calculated Evacuation Route
  saveEvacuationRoute: (route: any) => {
    try {
      const existing = offlineStorage.getCachedEvacuationRoutes();
      const updated = [route, ...existing.filter((r) => r.id !== route.id)].slice(0, 10);
      localStorage.setItem(STORAGE_KEYS.ROUTES, JSON.stringify(updated));
    } catch (e) {
      console.error("Error caching route:", e);
    }
  },

  // Get Cached Evacuation Routes
  getCachedEvacuationRoutes: (): any[] => {
    try {
      const data = localStorage.getItem(STORAGE_KEYS.ROUTES);
      return data ? JSON.parse(data) : [];
    } catch (e) {
      return [];
    }
  },

  // Get Last Sync Timestamp
  getLastSyncTimestamp: (): string => {
    return localStorage.getItem(STORAGE_KEYS.LAST_SYNC) || new Date().toISOString();
  },

  // Get Default Offline Emergency Instructions
  getEmergencyInstructions: (): CachedEmergencyInstructions => {
    return {
      title: "OFFLINE CITIZEN SURVIVAL & EVACUATION GUIDELINES",
      steps: [
        "1. Stay calm and move immediately towards high elevation if in a Flood Red Zone.",
        "2. Avoid crossing flooded roads or flowing streams. Drownings occur in shallow swift water.",
        "3. Proceed directly to your assigned emergency shelter (e.g. Central High School Relief Shelter).",
        "4. Follow pre-downloaded safe evacuation route detours. Do not attempt direct shortcut through landslide zones.",
        "5. Keep emergency battery radio / mobile tuned for disaster broadcast advisories.",
      ],
      hotlines: [
        { name: "National Disaster Response Force (NDRF)", number: "1078 / 011-24363260" },
        { name: "State Disaster Management Authority", number: "1070" },
        { name: "Police Emergency Helpline", number: "112 / 100" },
        { name: "Fire & Rescue Services", number: "101" },
        { name: "Ambulance Emergency Medical Service", number: "108" },
      ],
    };
  },
};
