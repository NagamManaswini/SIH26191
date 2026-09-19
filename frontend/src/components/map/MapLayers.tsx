import React from "react";
import { Layers, CloudRain, Flame, Shield, Home, Dog, Navigation, RefreshCw } from "lucide-react";

export interface MapLayerState {
  // Weather Layers
  rainPrecipitation: boolean;
  temperature: boolean;
  windSpeed: boolean;

  // Disaster Layers
  hazardRedZones: boolean;
  safeZones: boolean;

  // Response Layers
  shelters: boolean;
  hospitals: boolean;
  animalShelters: boolean;
  evacuationRoutes: boolean;
  relocationAreas: boolean;
}

interface MapLayersProps {
  layers: MapLayerState;
  onToggleLayer: (layerKey: keyof MapLayerState) => void;
  mapTileStyle: "street" | "dark" | "satellite";
  onChangeTileStyle: (style: "street" | "dark" | "satellite") => void;
}

export const MapLayers: React.FC<MapLayersProps> = ({
  layers,
  onToggleLayer,
  mapTileStyle,
  onChangeTileStyle,
}) => {
  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-4 space-y-4 shadow-lg text-slate-900 font-sans text-xs">
      <div className="flex items-center justify-between border-b border-slate-100 pb-2">
        <h3 className="font-black text-indigo-950 uppercase tracking-wider flex items-center gap-1.5 text-xs">
          <Layers className="w-4 h-4 text-pink-600" />
          Single Map Layer Controls
        </h3>
      </div>

      {/* Tile Style Selector */}
      <div>
        <label className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider block mb-1.5">
          Base Map Style
        </label>
        <div className="grid grid-cols-3 gap-1.5">
          <button
            type="button"
            onClick={() => onChangeTileStyle("street")}
            className={`py-1.5 rounded-xl font-bold transition-all border ${
              mapTileStyle === "street"
                ? "bg-indigo-950 text-amber-300 border-indigo-900 shadow-sm"
                : "bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100"
            }`}
          >
            Street
          </button>
          <button
            type="button"
            onClick={() => onChangeTileStyle("dark")}
            className={`py-1.5 rounded-xl font-bold transition-all border ${
              mapTileStyle === "dark"
                ? "bg-indigo-950 text-amber-300 border-indigo-900 shadow-sm"
                : "bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100"
            }`}
          >
            Dark
          </button>
          <button
            type="button"
            onClick={() => onChangeTileStyle("satellite")}
            className={`py-1.5 rounded-xl font-bold transition-all border ${
              mapTileStyle === "satellite"
                ? "bg-indigo-950 text-amber-300 border-indigo-900 shadow-sm"
                : "bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100"
            }`}
          >
            Satellite
          </button>
        </div>
      </div>

      {/* Layer Category 1: Weather */}
      <div className="space-y-1.5">
        <span className="text-[10px] font-extrabold text-indigo-900 uppercase tracking-wider flex items-center gap-1">
          <CloudRain className="w-3.5 h-3.5 text-blue-600" />
          Weather Layers
        </span>

        <label className="flex items-center justify-between bg-indigo-50/50 p-2 rounded-xl border border-indigo-100 cursor-pointer hover:bg-indigo-50">
          <span className="flex items-center gap-2 font-bold text-slate-800">
            <span className="w-2.5 h-2.5 rounded-full bg-blue-500"></span>
            Rain / Precipitation
          </span>
          <input
            type="checkbox"
            checked={layers.rainPrecipitation}
            onChange={() => onToggleLayer("rainPrecipitation")}
            className="rounded text-blue-600 focus:ring-0 cursor-pointer"
          />
        </label>

        <label className="flex items-center justify-between bg-indigo-50/50 p-2 rounded-xl border border-indigo-100 cursor-pointer hover:bg-indigo-50">
          <span className="flex items-center gap-2 font-bold text-slate-800">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
            Temperature Overlay
          </span>
          <input
            type="checkbox"
            checked={layers.temperature}
            onChange={() => onToggleLayer("temperature")}
            className="rounded text-amber-600 focus:ring-0 cursor-pointer"
          />
        </label>
      </div>

      {/* Layer Category 2: Disaster & Risk */}
      <div className="space-y-1.5">
        <span className="text-[10px] font-extrabold text-indigo-900 uppercase tracking-wider flex items-center gap-1">
          <Flame className="w-3.5 h-3.5 text-red-600" />
          Disaster & Risk Layers
        </span>

        <label className="flex items-center justify-between bg-red-50/50 p-2 rounded-xl border border-red-100 cursor-pointer hover:bg-red-50">
          <span className="flex items-center gap-2 font-bold text-slate-800">
            <span className="w-2.5 h-2.5 rounded bg-red-500"></span>
            Red Hazard Zones
          </span>
          <input
            type="checkbox"
            checked={layers.hazardRedZones}
            onChange={() => onToggleLayer("hazardRedZones")}
            className="rounded text-red-600 focus:ring-0 cursor-pointer"
          />
        </label>

        <label className="flex items-center justify-between bg-emerald-50/50 p-2 rounded-xl border border-emerald-100 cursor-pointer hover:bg-emerald-50">
          <span className="flex items-center gap-2 font-bold text-slate-800">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
            Verified Safe Zones
          </span>
          <input
            type="checkbox"
            checked={layers.safeZones}
            onChange={() => onToggleLayer("safeZones")}
            className="rounded text-emerald-600 focus:ring-0 cursor-pointer"
          />
        </label>
      </div>

      {/* Layer Category 3: Response & Facilities */}
      <div className="space-y-1.5">
        <span className="text-[10px] font-extrabold text-indigo-900 uppercase tracking-wider flex items-center gap-1">
          <Home className="w-3.5 h-3.5 text-emerald-600" />
          Response & Relief Layers
        </span>

        <label className="flex items-center justify-between bg-slate-50 p-2 rounded-xl border border-slate-200 cursor-pointer hover:bg-slate-100">
          <span className="flex items-center gap-2 font-bold text-slate-800">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-600"></span>
            Emergency Shelters
          </span>
          <input
            type="checkbox"
            checked={layers.shelters}
            onChange={() => onToggleLayer("shelters")}
            className="rounded text-emerald-600 focus:ring-0 cursor-pointer"
          />
        </label>

        <label className="flex items-center justify-between bg-pink-50/50 p-2 rounded-xl border border-pink-100 cursor-pointer hover:bg-pink-50">
          <span className="flex items-center gap-2 font-bold text-pink-950">
            <span className="w-2.5 h-2.5 rounded-full bg-pink-600"></span>
            🏥 Hospitals Layer
          </span>
          <input
            type="checkbox"
            checked={layers.hospitals}
            onChange={() => onToggleLayer("hospitals")}
            className="rounded text-pink-600 focus:ring-0 cursor-pointer"
          />
        </label>

        <label className="flex items-center justify-between bg-slate-50 p-2 rounded-xl border border-slate-200 cursor-pointer hover:bg-slate-100">
          <span className="flex items-center gap-2 font-bold text-slate-800">
            <span className="w-2.5 h-2.5 rounded-full bg-pink-600"></span>
            Animal Safe Shelters
          </span>
          <input
            type="checkbox"
            checked={layers.animalShelters}
            onChange={() => onToggleLayer("animalShelters")}
            className="rounded text-pink-600 focus:ring-0 cursor-pointer"
          />
        </label>

        <label className="flex items-center justify-between bg-slate-50 p-2 rounded-xl border border-slate-200 cursor-pointer hover:bg-slate-100">
          <span className="flex items-center gap-2 font-bold text-slate-800">
            <span className="w-3 h-0.5 bg-emerald-500 border border-dashed"></span>
            Evacuation Routes
          </span>
          <input
            type="checkbox"
            checked={layers.evacuationRoutes}
            onChange={() => onToggleLayer("evacuationRoutes")}
            className="rounded text-emerald-600 focus:ring-0 cursor-pointer"
          />
        </label>
      </div>
    </div>
  );
};
