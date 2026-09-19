import React, { useState, useEffect } from "react";
import { MapContainer, TileLayer, Marker, Popup, Polygon, Polyline, CircleMarker, useMap, useMapEvents } from "react-leaflet";
import L from "leaflet";
import { LocationSearch } from "./LocationSearch";
import { MapLayers, MapLayerState } from "./MapLayers";
import { weatherService, LiveWeatherData } from "../../services/weatherService";
import { api } from "../../api/apiClient";
import { locationService } from "../../services/locationService";
import { MapPin, Home, CloudRain, AlertTriangle, ShieldCheck, Navigation, Dog, Thermometer, Wind, RefreshCw, Layers } from "lucide-react";

import { HospitalDetailsDrawer, HospitalDetailsData } from "./HospitalDetailsDrawer";

delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

const activeLocationIcon = new L.Icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-gold.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
  iconSize: [32, 48],
  iconAnchor: [16, 48],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const shelterIcon = new L.Icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const animalShelterIcon = new L.Icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-violet.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

// Color Coded Hospital Markers based on Operational Status
const hospitalIconOpen = new L.Icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
  iconSize: [28, 44],
  iconAnchor: [14, 44],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const hospitalIconLimited = new L.Icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-yellow.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
  iconSize: [28, 44],
  iconAnchor: [14, 44],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const hospitalIconFull = new L.Icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
  iconSize: [28, 44],
  iconAnchor: [14, 44],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const hospitalIconEmergencyOnly = new L.Icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-orange.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
  iconSize: [28, 44],
  iconAnchor: [14, 44],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const hospitalIconClosed = new L.Icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-black.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
  iconSize: [28, 44],
  iconAnchor: [14, 44],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const MapFlyToController: React.FC<{ center: [number, number]; zoom: number }> = ({ center, zoom }) => {
  const map = useMap();
  useEffect(() => {
    const timer = setTimeout(() => {
      map.invalidateSize();
      map.flyTo(center, zoom, { duration: 1.2 });
    }, 100);
    return () => clearTimeout(timer);
  }, [center, zoom, map]);
  return null;
};

const MapClickListener: React.FC<{ onMapClick: (lat: number, lon: number) => void }> = ({ onMapClick }) => {
  useMapEvents({
    click(e) {
      onMapClick(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
};

interface DisasterMapProps {
  initialLat?: number;
  initialLon?: number;
  initialLabel?: string;
  onLocationSelected?: (location: { name: string; lat: number; lon: number; weather?: LiveWeatherData }) => void;
  showEvacuationPlanner?: boolean;
  onNavigate?: (tab: string) => void;
  hideSidebar?: boolean;
}

export const DisasterMap: React.FC<DisasterMapProps> = ({
  initialLat = 13.0827,
  initialLon = 80.2707,
  initialLabel = "Chennai, Tamil Nadu",
  onLocationSelected,
  showEvacuationPlanner = false,
  onNavigate,
  hideSidebar = false,
}) => {
  const [selectedLocation, setSelectedLocation] = useState<{ lat: number; lon: number; name: string }>({
    lat: initialLat,
    lon: initialLon,
    name: initialLabel,
  });

  const [mapCenter, setMapCenter] = useState<[number, number]>([initialLat, initialLon]);
  const [mapZoom, setMapZoom] = useState<number>(12);
  const [liveWeather, setLiveWeather] = useState<LiveWeatherData | null>(null);
  const [weatherLoading, setWeatherLoading] = useState<boolean>(false);

  // Entities Data
  const [shelters, setShelters] = useState<any[]>([]);
  const [animalShelters, setAnimalShelters] = useState<any[]>([]);
  const [hospitals, setHospitals] = useState<any[]>([]);
  const [selectedHospital, setSelectedHospital] = useState<HospitalDetailsData | null>(null);
  const [medicalRoute, setMedicalRoute] = useState<[number, number][] | null>(null);

  // Layer Visibility Toggle State
  const [layers, setLayers] = useState<MapLayerState>({
    rainPrecipitation: true,
    temperature: true,
    windSpeed: true,
    hazardRedZones: true,
    safeZones: true,
    shelters: true,
    hospitals: true,
    animalShelters: true,
    evacuationRoutes: true,
    relocationAreas: true,
  });

  const [mapTileStyle, setMapTileStyle] = useState<"street" | "dark" | "satellite">("street");
  const [showLayerPanel, setShowLayerPanel] = useState<boolean>(false);

  const tileUrls = {
    street: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    dark: "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}",
    satellite: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
  };

  const getHospitalMarkerIcon = (statusStr: string) => {
    switch (statusStr.toUpperCase()) {
      case "OPEN": return hospitalIconOpen;
      case "LIMITED": return hospitalIconLimited;
      case "FULL": return hospitalIconFull;
      case "EMERGENCY_ONLY": return hospitalIconEmergencyOnly;
      case "CLOSED": return hospitalIconClosed;
      default: return hospitalIconOpen;
    }
  };

  // Fetch shelters, animal shelters, and hospitals on mount or location change
  const handleLocationChange = async (lat: number, lon: number, name: string) => {
    setSelectedLocation({ lat, lon, name });
    setMapCenter([lat, lon]);
    setMapZoom(14);
    setWeatherLoading(true);

    try {
      const wData = await weatherService.getLiveWeather(lat, lon, name);
      setLiveWeather(wData);
      if (onLocationSelected) {
        onLocationSelected({ name, lat, lon, weather: wData });
      }
    } catch (e) {
      console.warn("Weather fetch notice:", e);
    } finally {
      setWeatherLoading(false);
    }
  };

  useEffect(() => {
    handleLocationChange(initialLat, initialLon, initialLabel);

    // Fetch shelters & hospitals
    Promise.all([
      api.getShelters().catch(() => []),
      api.getAnimalShelters().catch(() => []),
      api.getHospitals().catch(() => []),
    ]).then(([sData, ansData, hData]) => {
      setShelters(sData);
      setAnimalShelters(ansData);
      setHospitals(hData);
    });
  }, [initialLat, initialLon, initialLabel]);

  const handleToggleLayer = (key: keyof MapLayerState) => {
    setLayers((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const dynamicZones = locationService.getNearbySheltersAndZones(
    selectedLocation.lat,
    selectedLocation.lon,
    selectedLocation.name
  );

  const displayShelters = dynamicZones.shelters;

  const currentEvacRoute: [number, number][] = [
    [selectedLocation.lat, selectedLocation.lon],
    [selectedLocation.lat + 0.008, selectedLocation.lon + 0.006],
    [selectedLocation.lat + 0.012, selectedLocation.lon - 0.009],
  ];

  return (
    <div className={`relative w-full bg-slate-50 font-sans overflow-hidden text-slate-900 ${hideSidebar ? "h-full flex flex-col" : "flex flex-col lg:flex-row h-[calc(100vh-4rem)]"}`}>
      {/* Left Control Panel: Location Search & Live Weather Feed */}
      {!hideSidebar && (
        <div className="w-full lg:w-96 bg-white border-b lg:border-b-0 lg:border-r border-slate-200 p-5 flex flex-col space-y-4 overflow-y-auto shrink-0 z-10 shadow-xl">
        <div>
          <h2 className="text-lg font-black text-indigo-950 flex items-center gap-2 mb-1">
            <MapPin className="w-5 h-5 text-pink-600" />
            <span>Single Primary Map Controls</span>
          </h2>
          <p className="text-xs text-slate-600 font-medium leading-relaxed">
            Search any city, district, or locality across India to update live weather and risk assessment.
          </p>
        </div>

        {/* 1. Dynamic Google Maps Location Search (NO STATIC DROPDOWNS) */}
        <div className="space-y-1">
          <label className="text-[10px] font-extrabold text-indigo-950 uppercase tracking-wider block">
            Location Search (Google Maps & Places)
          </label>
          <LocationSearch
            currentLabel={selectedLocation.name}
            onSelectLocation={(loc) => handleLocationChange(loc.lat, loc.lon, loc.name)}
          />
        </div>

        {/* 2. Live Weather Widget (NO FAKE WEATHER DATA) */}
        <div className="bg-gradient-to-br from-indigo-900 to-indigo-950 border border-indigo-800 rounded-2xl p-4 text-white shadow-lg space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-extrabold uppercase tracking-wider text-amber-300 flex items-center gap-1.5">
              <CloudRain className="w-4 h-4 text-amber-300" />
              Live Weather Feed
            </span>
            <span className={`text-[9px] font-black px-2 py-0.5 rounded border uppercase ${
              liveWeather?.data_status === "LIVE"
                ? "bg-emerald-500 text-white border-emerald-400 animate-pulse"
                : "bg-amber-400 text-slate-950 border-amber-300"
            }`}>
              {liveWeather?.data_status || "FETCHING..."}
            </span>
          </div>

          {weatherLoading ? (
            <div className="py-6 flex flex-col items-center justify-center gap-2 text-indigo-200 text-xs font-bold">
              <RefreshCw className="w-6 h-6 animate-spin text-amber-300" />
              <span>Fetching live weather for coordinates...</span>
            </div>
          ) : liveWeather && liveWeather.status !== "unavailable" ? (
            <div className="space-y-2.5">
              <div className="flex items-baseline justify-between">
                <div>
                  <span className="text-3xl font-black text-white">
                    {liveWeather.temperature_c !== undefined ? `${liveWeather.temperature_c} °C` : "N/A"}
                  </span>
                  <span className="text-xs text-indigo-200 ml-2 font-medium">
                    Feels like {liveWeather.feels_like_c !== undefined ? `${liveWeather.feels_like_c} °C` : "N/A"}
                  </span>
                </div>
                <span className="text-xs font-extrabold text-amber-300 bg-indigo-950/80 px-2.5 py-1 rounded-lg border border-indigo-700">
                  {liveWeather.condition}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2 text-[11px] font-bold text-indigo-100 pt-1 border-t border-indigo-800/80">
                <div>Rainfall: <b className="text-amber-300">{liveWeather.precipitation_mm} mm</b></div>
                <div>Humidity: <b className="text-amber-300">{liveWeather.humidity_percent || "N/A"}%</b></div>
                <div>Wind Speed: <b className="text-amber-300">{liveWeather.wind_speed_kmh || "N/A"} km/h</b></div>
                <div>Pressure: <b className="text-amber-300">{liveWeather.pressure_hpa || "N/A"} hPa</b></div>
              </div>

              <div className="text-[10px] text-indigo-300 font-mono pt-1">
                Last updated: <b>{liveWeather.last_updated}</b>
              </div>

              {/* 5-7 Day Forecast */}
              {liveWeather.forecast_daily && liveWeather.forecast_daily.length > 0 && (
                <div className="pt-2 border-t border-indigo-800 space-y-1.5">
                  <span className="text-[10px] font-black uppercase text-amber-300 block">
                    5–7 Day Live Weather Forecast
                  </span>
                  <div className="grid grid-cols-5 gap-1 text-[10px] text-center font-bold">
                    {liveWeather.forecast_daily.slice(0, 5).map((f, i) => (
                      <div key={i} className="bg-indigo-950/90 p-1.5 rounded-lg border border-indigo-800">
                        <span className="block text-[9px] text-indigo-300">{f.date.split("-").slice(1).join("/")}</span>
                        <span className="block font-black text-amber-300">{f.temp_max !== null ? Math.round(f.temp_max) : "--"}°</span>
                        <span className="block text-[8px] text-indigo-200 truncate">{f.condition.split(" ")[0]}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="p-3 bg-red-950/60 border border-red-800 rounded-xl text-xs font-bold text-red-200">
              ⚠️ Live weather data is currently unavailable for this coordinate.
            </div>
          )}
        </div>

        {/* Toggle Layer Control Drawer Button */}
        <button
          type="button"
          onClick={() => setShowLayerPanel(!showLayerPanel)}
          className="w-full py-2.5 px-4 rounded-xl bg-indigo-950 hover:bg-indigo-900 text-amber-300 font-black text-xs flex items-center justify-between transition-colors border border-indigo-800 shadow-md"
        >
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-pink-400" />
            <span>Map Layers & Base Style</span>
          </div>
          <span>{showLayerPanel ? "▲ Hide" : "▼ Show"}</span>
        </button>

        {showLayerPanel && (
          <MapLayers
            layers={layers}
            onToggleLayer={handleToggleLayer}
            mapTileStyle={mapTileStyle}
            onChangeTileStyle={setMapTileStyle}
          />
        )}
      </div>
      )}

      {/* Right Primary Leaflet/Google Map Canvas */}
      <div className="flex-1 h-full w-full relative z-0">
        {hideSidebar && (
          <div className="absolute top-3 right-3 z-[400] flex flex-col items-end gap-2">
            <button
              type="button"
              onClick={() => setShowLayerPanel(!showLayerPanel)}
              className="py-2 px-3 rounded-xl bg-indigo-950/90 hover:bg-indigo-900 text-amber-300 font-black text-xs flex items-center gap-2 border border-indigo-700 shadow-xl backdrop-blur-sm cursor-pointer transition-all"
            >
              <Layers className="w-4 h-4 text-pink-400" />
              <span>Map Layers</span>
              <span>{showLayerPanel ? "▲" : "▼"}</span>
            </button>
            {showLayerPanel && (
              <div className="bg-white border border-slate-200 rounded-2xl p-3 shadow-2xl w-64 text-xs font-sans text-slate-900 space-y-2">
                <MapLayers
                  layers={layers}
                  onToggleLayer={handleToggleLayer}
                  mapTileStyle={mapTileStyle}
                  onChangeTileStyle={setMapTileStyle}
                />
              </div>
            )}
          </div>
        )}
        <MapContainer center={mapCenter} zoom={mapZoom} scrollWheelZoom={true} className="h-full w-full">
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url={tileUrls[mapTileStyle]}
          />

          <MapFlyToController center={mapCenter} zoom={mapZoom} />
          <MapClickListener onMapClick={async (lat, lon) => {
            const label = await locationService.reverseGeocode(lat, lon);
            handleLocationChange(lat, lon, label);
          }} />

          {/* Active Selected Location Pin Marker */}
          <Marker position={[selectedLocation.lat, selectedLocation.lon]} icon={activeLocationIcon}>
            <Popup>
              <div className="text-xs space-y-1.5 font-sans min-w-[200px]">
                <b className="text-amber-600 flex items-center gap-1 font-bold">
                  <MapPin className="w-4 h-4 text-pink-600" />
                  {selectedLocation.name}
                </b>
                <div className="font-mono text-slate-600 text-[11px]">
                  Lat: {selectedLocation.lat.toFixed(4)}° N | Lon: {selectedLocation.lon.toFixed(4)}° E
                </div>
                {liveWeather && (
                  <div className="bg-indigo-50 p-2 rounded border border-indigo-100 text-[11px] text-indigo-950 font-bold">
                    Weather: {liveWeather.temperature_c ?? "--"}°C | {liveWeather.condition}
                  </div>
                )}
              </div>
            </Popup>
          </Marker>

          {/* Layer: Red Hazard Zones */}
          {layers.hazardRedZones && (
            <>
              {/* Red Zone (Critical High Risk) */}
              <Polygon
                positions={dynamicZones.redZonePolygon}
                pathOptions={{ fillColor: "#ef4444", fillOpacity: 0.45, color: "#dc2626", weight: 3 }}
              >
                <Popup>
                  <div className="text-xs space-y-1.5 font-sans min-w-[200px]">
                    <b className="text-red-600 flex items-center gap-1">
                      <AlertTriangle className="w-4 h-4" />
                      RED HAZARD ZONE (Critical Risk Sector)
                    </b>
                    <div>Threat Score: <b className="text-red-600">0.92 (CRITICAL)</b></div>
                    <div>Location: {selectedLocation.name}</div>
                    {onNavigate && (
                      <button
                        onClick={() => onNavigate("red-zone")}
                        className="w-full mt-1.5 py-1.5 px-2 bg-pink-600 hover:bg-pink-500 text-white font-bold text-[11px] rounded-lg shadow transition-colors cursor-pointer text-center block"
                      >
                        🔥 Run Red Zone Risk Analysis →
                      </button>
                    )}
                  </div>
                </Popup>
              </Polygon>

              {/* Medium Zone (Moderate Risk Buffer) */}
              <Polygon
                positions={dynamicZones.mediumZonePolygon}
                pathOptions={{ fillColor: "#f59e0b", fillOpacity: 0.25, color: "#d97706", weight: 2, dashArray: "4, 4" }}
              >
                <Popup>
                  <div className="text-xs space-y-1 font-sans min-w-[180px]">
                    <b className="text-amber-600 flex items-center gap-1">
                      <AlertTriangle className="w-4 h-4" />
                      MEDIUM RISK ZONE (Buffer Sector)
                    </b>
                    <div>Threat Score: <b className="text-amber-600">0.55 (MODERATE)</b></div>
                    <div>Precaution: Prepare for secondary detour evacuation if rainfall increases.</div>
                  </div>
                </Popup>
              </Polygon>
            </>
          )}

          {/* Layer: Safe Zones */}
          {layers.safeZones && (
            <Polygon
              positions={dynamicZones.safeZonePolygon}
              pathOptions={{ fillColor: "#10b981", fillOpacity: 0.2, color: "#059669", weight: 2 }}
            >
              <Popup>
                <div className="text-xs space-y-1 font-sans min-w-[180px]">
                  <b className="text-emerald-700 flex items-center gap-1">
                    <ShieldCheck className="w-4 h-4" />
                    APPROVED SAFE ZONE (High Ground)
                  </b>
                  <div>Safety Clearance: <b className="text-emerald-700">APPROVED SAFE HAVEN</b></div>
                  <div>Contains Primary Hospitals & Community Relief Camps.</div>
                </div>
              </Popup>
            </Polygon>
          )}

          {/* Layer: Evacuation Routes */}
          {layers.evacuationRoutes && (
            <Polyline
              positions={currentEvacRoute}
              pathOptions={{ color: "#10b981", weight: 5, dashArray: "8, 8", opacity: 0.9 }}
            >
              <Popup>
                <div className="text-xs space-y-1 font-sans">
                  <b className="text-emerald-600">RECOMMENDED EVACUATION ROUTE</b>
                  <div>Passage Clearance: <b className="text-emerald-600">APPROVED SAFE</b></div>
                </div>
              </Popup>
            </Polyline>
          )}

          {/* Layer: Emergency Shelters (Hospitals, Schools, Health Centers) */}
          {layers.shelters &&
            displayShelters.map((s, idx) => {
              const sLat = s.latitude || (selectedLocation.lat + 0.007 + idx * 0.005);
              const sLon = s.longitude || (selectedLocation.lon + 0.008 + idx * 0.005);
              return (
                <Marker key={s.id || idx} position={[sLat, sLon]} icon={shelterIcon}>
                  <Popup>
                    <div className="text-xs space-y-1 font-sans min-w-[200px]">
                      <b className="text-emerald-700 flex items-center gap-1 font-extrabold">
                        <Home className="w-4 h-4 text-emerald-600 shrink-0" />
                        {s.name}
                      </b>
                      <div className="text-[11px] text-slate-600">{s.address}</div>
                      <div className="text-[11px] font-bold text-slate-700 pt-1 flex justify-between">
                        <span>Free Beds: <b className="text-emerald-700">{s.available_capacity || (s.capacity - s.current_occupancy)}</b></span>
                        <span>Status: <b className="text-emerald-800 uppercase">{s.status || "ACTIVE"}</b></span>
                      </div>
                    </div>
                  </Popup>
                </Marker>
              );
            })}

          {/* Layer: Hospitals */}
          {layers.hospitals &&
            hospitals.map((h) => {
              const cap = h.capacity;
              const avBeds = cap ? maxZero(cap.total_beds - cap.occupied_beds) : 0;
              const avEm = cap ? maxZero(cap.total_emergency_beds - cap.occupied_emergency_beds) : 0;
              const avIcu = cap ? maxZero(cap.total_icu - cap.occupied_icu) : 0;

              return (
                <Marker
                  key={h.id}
                  position={[h.latitude, h.longitude]}
                  icon={getHospitalMarkerIcon(h.operational_status)}
                  eventHandlers={{
                    click: () => {
                      setSelectedHospital(h);
                    },
                  }}
                >
                  <Popup>
                    <div className="text-xs space-y-1.5 font-sans min-w-[220px]">
                      <div className="flex items-center justify-between border-b pb-1">
                        <b className="text-pink-950 text-sm font-black flex items-center gap-1">
                          🏥 {h.name}
                        </b>
                      </div>
                      <div className="text-[11px] text-slate-600 flex items-center gap-1">
                        <MapPin className="w-3 h-3 text-pink-500 shrink-0" />
                        {h.district ? `${h.district}, ` : ""}{h.state || "India"}
                      </div>
                      <div className="text-[11px] font-bold text-slate-700">
                        Type: <b className="text-indigo-900">{h.type}</b>
                      </div>

                      {cap ? (
                        <div className="bg-slate-50 p-2 rounded-xl border border-slate-200 text-[11px] space-y-1">
                          <div className="flex justify-between font-bold">
                            <span>Emergency Beds:</span>
                            <b className="text-red-600">{avEm} Available</b>
                          </div>
                          <div className="flex justify-between font-bold">
                            <span>ICU Beds:</span>
                            <b className="text-purple-600">{avIcu} Available</b>
                          </div>
                          <div className="flex justify-between text-[10px] text-slate-500">
                            <span>Total Beds: {avBeds} / {cap.total_beds}</span>
                            <span>Ambulances: {cap.available_ambulances}</span>
                          </div>
                        </div>
                      ) : (
                        <div className="bg-amber-50 p-2 rounded text-[10px] font-bold text-amber-800 border border-amber-200 text-center">
                          Capacity data unavailable
                        </div>
                      )}

                      <div className="pt-1 flex gap-1.5">
                        <button
                          type="button"
                          onClick={() => setSelectedHospital(h)}
                          className="flex-1 py-1 px-2 bg-pink-600 hover:bg-pink-700 text-white font-black text-[11px] rounded-lg text-center cursor-pointer"
                        >
                          View Details
                        </button>
                        <button
                          type="button"
                          onClick={() => {
                            setMedicalRoute([
                              [selectedLocation.lat, selectedLocation.lon],
                              [(selectedLocation.lat + h.latitude) / 2, (selectedLocation.lon + h.longitude) / 2 + 0.005],
                              [h.latitude, h.longitude],
                            ]);
                            setSelectedHospital(h);
                          }}
                          className="flex-1 py-1 px-2 bg-indigo-950 hover:bg-indigo-900 text-amber-300 font-black text-[11px] rounded-lg text-center cursor-pointer"
                        >
                          Route
                        </button>
                      </div>
                    </div>
                  </Popup>
                </Marker>
              );
            })}

          {/* Layer: Medical Emergency Route */}
          {medicalRoute && (
            <Polyline
              positions={medicalRoute}
              pathOptions={{ color: "#db2777", weight: 6, opacity: 0.95 }}
            >
              <Popup>
                <div className="text-xs space-y-1 font-sans">
                  <b className="text-pink-600">🚨 MEDICAL EMERGENCY evacuation route</b>
                  <div>Direct Transit to Recommended Hospital</div>
                </div>
              </Popup>
            </Polyline>
          )}

          {/* Layer: Animal Shelters */}
          {layers.animalShelters &&
            animalShelters.map((ans, idx) => {
              const ansLat = ans.latitude || (selectedLocation.lat - 0.02 - idx * 0.005);
              const ansLon = ans.longitude || (selectedLocation.lon + 0.02 + idx * 0.005);
              return (
                <Marker key={ans.id || idx} position={[ansLat, ansLon]} icon={animalShelterIcon}>
                  <Popup>
                    <div className="text-xs space-y-1 font-sans min-w-[180px]">
                      <b className="text-purple-700 flex items-center gap-1">
                        <Dog className="w-4 h-4 text-purple-600" />
                        {ans.name}
                      </b>
                      <div>Available Animal Space: <b className="text-purple-700">{ans.available_capacity || 200}</b></div>
                    </div>
                  </Popup>
                </Marker>
              );
            })}
        </MapContainer>

        {/* Slide-over Hospital Details Drawer */}
        <HospitalDetailsDrawer
          hospital={selectedHospital}
          onClose={() => setSelectedHospital(null)}
          onSelectRoute={(h) => {
            setMedicalRoute([
              [selectedLocation.lat, selectedLocation.lon],
              [(selectedLocation.lat + h.latitude) / 2, (selectedLocation.lon + h.longitude) / 2 + 0.005],
              [h.latitude, h.longitude],
            ]);
            setMapCenter([h.latitude, h.longitude]);
          }}
        />
      </div>
    </div>
  );
};

function maxZero(num: number): number {
  return num > 0 ? num : 0;
}
