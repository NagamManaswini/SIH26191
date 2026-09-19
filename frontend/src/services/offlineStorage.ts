/**
 * Offline Storage Service using localStorage / IndexedDB fallback.
 * 
 * Provides local synchronization, offline shelter caching, evacuation instructions,
 * emergency contacts, animal rescue records, and queued changes.
 */

export interface CachedEmergencyBundle {
  lastSyncTime: string;
  shelters: any[];
  routes: any[];
  hazards: any[];
  alerts: any[];
  animals: any[];
  contacts: any[];
}

const STORAGE_KEY = "disaster_offline_emergency_bundle";
const QUEUE_KEY = "disaster_offline_sync_queue";

export class OfflineStorageService {
  /** Saves emergency dataset bundle to local storage */
  public static saveEmergencyBundle(data: Partial<CachedEmergencyBundle>) {
    try {
      const existing = this.getEmergencyBundle() || {
        lastSyncTime: new Date().toISOString(),
        shelters: [],
        routes: [],
        hazards: [],
        alerts: [],
        animals: [],
        contacts: [
          { name: "District Emergency Operations Center (DEOC)", phone: "1077 / 04936-204151" },
          { name: "State Emergency Operations Center (SEOC)", phone: "1070" },
          { name: "Police Control Room", phone: "112" },
          { name: "Fire & Rescue Services", phone: "101" },
          { name: "Medical Emergency Ambulance", phone: "108" },
          { name: "Veterinary Emergency Cell", phone: "+91-9447200200" },
        ],
      };

      const updatedBundle: CachedEmergencyBundle = {
        ...existing,
        ...data,
        lastSyncTime: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + " IST",
      };

      localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedBundle));
      return updatedBundle;
    } catch (e) {
      console.warn("[Offline Storage] Save bundle error:", e);
      return null;
    }
  }

  /** Gets cached emergency dataset bundle */
  public static getEmergencyBundle(): CachedEmergencyBundle | null {
    try {
      const item = localStorage.getItem(STORAGE_KEY);
      return item ? JSON.parse(item) : null;
    } catch (e) {
      console.warn("[Offline Storage] Get bundle error:", e);
      return null;
    }
  }

  /** Queue a local action while offline */
  public static queueOfflineAction(actionType: string, payload: any) {
    try {
      const queue = this.getSyncQueue();
      queue.push({
        id: Date.now(),
        type: actionType,
        payload,
        timestamp: new Date().toISOString(),
      });
      localStorage.setItem(QUEUE_KEY, JSON.stringify(queue));
    } catch (e) {
      console.warn("[Offline Storage] Queue action error:", e);
    }
  }

  public static getSyncQueue(): any[] {
    try {
      const item = localStorage.getItem(QUEUE_KEY);
      return item ? JSON.parse(item) : [];
    } catch (e) {
      return [];
    }
  }

  public static clearSyncQueue() {
    localStorage.removeItem(QUEUE_KEY);
  }
}
