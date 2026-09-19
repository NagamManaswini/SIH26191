import React from "react";
import { DisasterMap } from "../components/map/DisasterMap";
import { LiveWeatherData } from "../services/weatherService";

interface LiveHazardMapProps {
  currentLocation?: { name: string; lat: number; lon: number };
  onLocationChange?: (loc: { name: string; lat: number; lon: number; weather?: LiveWeatherData }) => void;
  onNavigate?: (tab: string) => void;
}

export const LiveHazardMap: React.FC<LiveHazardMapProps> = ({
  currentLocation,
  onLocationChange,
  onNavigate,
}) => {
  const initialLat = currentLocation?.lat || 13.0827;
  const initialLon = currentLocation?.lon || 80.2707;
  const initialLabel = currentLocation?.name || "Chennai, Tamil Nadu";

  return (
    <div className="w-full h-full min-h-[calc(100vh-4rem)]">
      <DisasterMap
        initialLat={initialLat}
        initialLon={initialLon}
        initialLabel={initialLabel}
        onLocationSelected={(loc) => {
          if (onLocationChange) {
            onLocationChange(loc);
          }
        }}
        onNavigate={onNavigate}
      />
    </div>
  );
};
