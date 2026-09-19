import React from "react";
import { WifiOff, AlertTriangle, RefreshCw } from "lucide-react";
import { offlineStorage } from "../utils/offlineStorage";

interface OfflineBannerProps {
  isOffline: boolean;
  onSync?: () => void;
}

export const OfflineBanner: React.FC<OfflineBannerProps> = ({ isOffline, onSync }) => {
  if (!isOffline) return null;

  const lastSyncStr = new Date(offlineStorage.getLastSyncTimestamp()).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div className="bg-amber-950 border-b border-amber-500/50 px-6 py-2.5 flex items-center justify-between text-amber-200 text-xs shadow-xl sticky top-16 z-30 animate-pulse">
      <div className="flex items-center gap-3">
        <WifiOff className="w-4 h-4 text-amber-400 shrink-0" />
        <div>
          <span className="font-bold text-amber-300 uppercase tracking-wide">
            OFFLINE MODE — DISPLAYING CACHED EMERGENCY DATA (Last Synced: {lastSyncStr} IST)
          </span>
          <p className="text-[11px] text-amber-200/80">
            Real-time live weather feeds unavailable. Displaying previously cached shelters & safe evacuation routes. Data may be stale.
          </p>
        </div>
      </div>

      {onSync && (
        <button
          onClick={onSync}
          className="flex items-center gap-1.5 bg-amber-600 hover:bg-amber-500 text-white text-xs font-bold px-3 py-1.5 rounded-lg shadow transition-all shrink-0"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Try Reconnect Sync</span>
        </button>
      )}
    </div>
  );
};
