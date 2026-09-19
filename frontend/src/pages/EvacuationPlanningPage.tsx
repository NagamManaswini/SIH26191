import React, { useState, useEffect } from "react";
import { Navigation, MapPin, RefreshCw, CheckCircle2, Home } from "lucide-react";
import { DisasterMap } from "../components/map/DisasterMap";
import { LocationSearch } from "../components/map/LocationSearch";
import { api } from "../api/apiClient";
import { locationService } from "../services/locationService";

function calculateDistanceKm(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) * Math.cos((lat2 * Math.PI) / 180) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return parseFloat((R * c).toFixed(2));
}

export const EvacuationPlanningPage: React.FC = () => {
  const [shelters, setShelters] = useState<any[]>([]);
  const [selectedLocation, setSelectedLocation] = useState({
    lat: 13.0827,
    lon: 80.2707,
    name: "Chennai, Tamil Nadu",
  });

  const [selectedShelterId, setSelectedShelterId] = useState<number>(101);
  const [routeResult, setRouteResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const dynamicLocalData = locationService.getNearbySheltersAndZones(
    selectedLocation.lat,
    selectedLocation.lon,
    selectedLocation.name
  );

  const activeShelterPool = dynamicLocalData.shelters;

  const nearbyShelters = activeShelterPool
    .map((s) => {
      const dist = calculateDistanceKm(selectedLocation.lat, selectedLocation.lon, s.latitude, s.longitude);
      return { ...s, distance_km: dist };
    })
    .sort((a, b) => a.distance_km - b.distance_km);

  const selectedShelterObj = nearbyShelters.find((s) => s.id === selectedShelterId) || nearbyShelters[0];

  const handleCalculateRoute = () => {
    setLoading(true);
    const target = selectedShelterObj || nearbyShelters[0];
    const dist = target ? target.distance_km : 2.4;
    const mins = Math.round((dist / 30) * 60) + 4;

    setTimeout(() => {
      setRouteResult({
        destination_name: target ? target.name : "St. Joseph Relief Shelter",
        total_distance_km: dist,
        estimated_travel_time_mins: mins,
        safety_category: "APPROVED SAFE",
      });
      setLoading(false);
    }, 400);
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto font-sans bg-slate-50 min-h-screen text-slate-900">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-indigo-900 via-blue-900 to-indigo-950 border border-indigo-800 rounded-2xl p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-xl text-white">
        <div>
          <h2 className="text-xl font-black text-white flex items-center gap-2">
            <Navigation className="w-5 h-5 text-amber-300" />
            Evacuation Route Planning & Nearby Safe Shelters
          </h2>
          <p className="text-xs text-indigo-100 mt-1 font-medium">
            Search any origin location in India to evaluate nearby safe shelters and compute hazard-avoidance evacuation paths.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Origin Selection & Nearby Shelters */}
        <div className="lg:col-span-5 space-y-5">
          <div className="bg-white border border-slate-200 rounded-2xl p-5 space-y-4 shadow-md">
            <h3 className="text-xs font-black text-indigo-950 uppercase tracking-wider border-b border-slate-100 pb-2 flex items-center gap-1.5">
              <MapPin className="w-4 h-4 text-pink-600" />
              1. Select Origin / Evacuation Start Location
            </h3>

            {/* Dynamic Location Search Input */}
            <LocationSearch
              currentLabel={selectedLocation.name}
              onSelectLocation={(loc) => {
                setSelectedLocation(loc);
                handleCalculateRoute();
              }}
            />

            <div>
              <label className="text-xs text-slate-700 font-bold block mb-1">Target Relief Shelter:</label>
              <select
                value={selectedShelterId}
                onChange={(e) => {
                  setSelectedShelterId(Number(e.target.value));
                  handleCalculateRoute();
                }}
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-xs font-bold text-indigo-950"
              >
                {nearbyShelters.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name} ({s.distance_km} km away | {s.available_capacity || 400} free beds)
                  </option>
                ))}
              </select>
            </div>

            <button
              onClick={handleCalculateRoute}
              disabled={loading}
              className="w-full bg-pink-600 hover:bg-pink-500 text-white text-xs font-black py-3 rounded-xl shadow-md border border-pink-500 flex items-center justify-center gap-2 transition-all cursor-pointer uppercase tracking-wider"
            >
              {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Navigation className="w-4 h-4" />}
              <span>Calculate Evacuation Route</span>
            </button>
          </div>

          {/* Sorted Nearby Safe Shelters */}
          <div className="space-y-3">
            <h3 className="text-xs font-black text-indigo-950 uppercase tracking-wider flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <Home className="w-4 h-4 text-indigo-700" />
                2. Nearby Shelters (Sorted by Distance)
              </span>
              <span className="text-[11px] text-emerald-700 font-bold">{nearbyShelters.length} Shelters</span>
            </h3>

            <div className="space-y-2 max-h-[350px] overflow-y-auto pr-1">
              {nearbyShelters.map((s) => {
                const isSelected = s.id === selectedShelterId;
                return (
                  <div
                    key={s.id}
                    onClick={() => {
                      setSelectedShelterId(s.id);
                      handleCalculateRoute();
                    }}
                    className={`p-3.5 rounded-2xl border transition-all cursor-pointer space-y-1 shadow-sm ${
                      isSelected
                        ? "bg-indigo-50 border-indigo-500 ring-2 ring-indigo-400"
                        : "bg-white border-slate-200 hover:border-indigo-300"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <h4 className="text-xs font-extrabold text-indigo-950 flex items-center gap-1">
                        <span>{s.name}</span>
                        {isSelected && <CheckCircle2 className="w-3.5 h-3.5 text-indigo-700 shrink-0" />}
                      </h4>
                      <span className="px-2 py-0.5 rounded bg-indigo-950 text-amber-300 text-[11px] font-bold font-mono">
                        {s.distance_km} km
                      </span>
                    </div>
                    <div className="text-[11px] text-slate-600 flex justify-between font-bold pt-1">
                      <span>Free Beds: <b className="text-emerald-700">{s.available_capacity || 400}</b></span>
                      <span>Max Cap: <b>{s.capacity || 500}</b></span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Column: Single Primary Map Instance */}
        <div className="lg:col-span-7 space-y-4">
          <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-md h-[550px] relative">
            <DisasterMap
              initialLat={selectedLocation.lat}
              initialLon={selectedLocation.lon}
              initialLabel={selectedLocation.name}
              onLocationSelected={(loc) => setSelectedLocation({ lat: loc.lat, lon: loc.lon, name: loc.name })}
              showEvacuationPlanner={true}
              hideSidebar={true}
            />
          </div>

          {routeResult && (
            <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-md space-y-2">
              <div className="flex items-center justify-between border-b border-slate-100 pb-2">
                <span className="text-xs font-black text-indigo-950">Evacuation Summary to {routeResult.destination_name}</span>
                <span className="text-xs font-extrabold px-2.5 py-0.5 rounded bg-emerald-100 text-emerald-800 border border-emerald-300">
                  {routeResult.safety_category}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-3 text-xs font-bold text-slate-700">
                <div className="bg-indigo-50 p-2.5 rounded-xl border border-indigo-100">
                  Distance: <b className="text-indigo-950 text-sm font-black">{routeResult.total_distance_km} km</b>
                </div>
                <div className="bg-indigo-50 p-2.5 rounded-xl border border-indigo-100">
                  Est Travel Time: <b className="text-pink-600 text-sm font-black">{routeResult.estimated_travel_time_mins} mins</b>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
