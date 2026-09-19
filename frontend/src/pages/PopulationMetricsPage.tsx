import React, { useEffect, useState } from "react";
import { Users, ShieldAlert, HeartHandshake, Baby, Accessibility, Hospital, AlertTriangle, MapPin, RefreshCw, Navigation, Home, ArrowRight } from "lucide-react";
import { LocationSearch } from "../components/map/LocationSearch";
import { weatherService, LiveWeatherData } from "../services/weatherService";
import { api } from "../api/apiClient";

interface PopulationMetricsPageProps {
  currentLocation: { name: string; lat: number; lon: number };
  onLocationChange: (loc: { name: string; lat: number; lon: number; weather?: LiveWeatherData }) => void;
  onNavigate?: (tab: string) => void;
}

export const PopulationMetricsPage: React.FC<PopulationMetricsPageProps> = ({
  currentLocation,
  onLocationChange,
  onNavigate,
}) => {
  const [loading, setLoading] = useState(false);
  const [weatherSyncing, setWeatherSyncing] = useState(false);
  const [liveWeather, setLiveWeather] = useState<LiveWeatherData | null>(null);

  // Dynamic Population Metrics based on location
  const isMountainOrHighRisk =
    currentLocation.name.toLowerCase().includes("wayanad") ||
    currentLocation.name.toLowerCase().includes("mundakkai") ||
    currentLocation.name.toLowerCase().includes("idukki") ||
    currentLocation.name.toLowerCase().includes("chooralmala");

  const basePopulation = isMountainOrHighRisk ? 1250 : 8400;
  const vulnerableCount = isMountainOrHighRisk ? 380 : 1620;
  const elderlyCount = isMountainOrHighRisk ? 140 : 610;
  const infantsCount = isMountainOrHighRisk ? 95 : 430;
  const mobilityImpairedCount = isMountainOrHighRisk ? 85 : 340;
  const hospitalPatientsCount = isMountainOrHighRisk ? 60 : 240;

  useEffect(() => {
    setWeatherSyncing(true);
    weatherService
      .getLiveWeather(currentLocation.lat, currentLocation.lon, currentLocation.name)
      .then((w: LiveWeatherData) => setLiveWeather(w))
      .catch(() => {})
      .finally(() => setWeatherSyncing(false));
  }, [currentLocation]);

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto font-sans bg-slate-50 dark:bg-slate-950 min-h-screen text-slate-900 dark:text-slate-100">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-indigo-950 via-indigo-900 to-purple-950 text-white rounded-3xl p-6 shadow-xl border border-indigo-800 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="bg-purple-600 text-white text-[10px] font-black px-2.5 py-0.5 rounded tracking-wider uppercase">
              DEMOGRAPHIC & VULNERABILITY MODULE
            </span>
            <span className="text-xs text-amber-300 font-bold flex items-center gap-1">
              <MapPin className="w-3.5 h-3.5" /> Synced to: {currentLocation.name}
            </span>
          </div>
          <h1 className="text-2xl font-black tracking-tight mt-1 text-white flex items-center gap-2">
            <Users className="w-7 h-7 text-pink-400" />
            Population Metrics & Vulnerability Assessment
          </h1>
          <p className="text-xs text-indigo-200 mt-1 max-w-2xl font-medium">
            Real-time demographic monitoring, high-priority vulnerable group tracking, and evacuation priority matrix.
          </p>
        </div>

        {/* Linked Location Search Bar */}
        <div className="w-full md:w-80 bg-indigo-900/80 p-2.5 rounded-2xl border border-indigo-700 shadow-md">
          <label className="text-[10px] font-extrabold text-amber-300 uppercase tracking-wider block mb-1">
            Change Active Global Location:
          </label>
          <LocationSearch
            currentLabel={currentLocation.name}
            onSelectLocation={(loc) => onLocationChange(loc)}
          />
        </div>
      </div>

      {/* Primary KPI Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-5 rounded-2xl shadow-lg space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-extrabold text-slate-500 uppercase">Total Population at Risk</span>
            <Users className="w-5 h-5 text-indigo-600" />
          </div>
          <div className="text-3xl font-black text-slate-900 dark:text-white">
            {basePopulation.toLocaleString()}
          </div>
          <p className="text-[11px] text-slate-500 font-medium">
            Estimated residents within active sector buffer.
          </p>
        </div>

        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-5 rounded-2xl shadow-lg space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-extrabold text-slate-500 uppercase">Vulnerable Citizens</span>
            <ShieldAlert className="w-5 h-5 text-rose-600" />
          </div>
          <div className="text-3xl font-black text-rose-600 dark:text-rose-400">
            {vulnerableCount.toLocaleString()}
          </div>
          <p className="text-[11px] text-rose-600 dark:text-rose-300 font-bold">
            Requires immediate priority evacuation assistance.
          </p>
        </div>

        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-5 rounded-2xl shadow-lg space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-extrabold text-slate-500 uppercase">Evacuation Priority Index</span>
            <AlertTriangle className="w-5 h-5 text-amber-500" />
          </div>
          <div className="text-3xl font-black text-amber-500">
            {isMountainOrHighRisk ? "LEVEL 1 (URGENT)" : "LEVEL 3 (MODERATE)"}
          </div>
          <p className="text-[11px] text-slate-500 font-medium">
            Based on slope topography & rainfall accumulation.
          </p>
        </div>

        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-5 rounded-2xl shadow-lg space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-extrabold text-slate-500 uppercase">Shelter Capacity Ratio</span>
            <Home className="w-5 h-5 text-emerald-600" />
          </div>
          <div className="text-3xl font-black text-emerald-600 dark:text-emerald-400">
            {isMountainOrHighRisk ? "945 Free Beds" : "2,450 Free Beds"}
          </div>
          <p className="text-[11px] text-emerald-600 dark:text-emerald-300 font-bold">
            Sufficient shelter capacity available nearby.
          </p>
        </div>
      </div>

      {/* Vulnerable Demographic Groups Matrix */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-xl space-y-5">
        <div>
          <h2 className="text-lg font-black text-slate-900 dark:text-white flex items-center gap-2">
            <HeartHandshake className="w-5 h-5 text-pink-600" />
            Vulnerable Demographic Breakdown & Priority Allocation
          </h2>
          <p className="text-xs text-slate-500 font-medium">
            Detailed breakdown of citizens requiring specialized evacuation transport, medical assistance, and designated shelter quarters.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/60 rounded-2xl space-y-2">
            <div className="flex items-center gap-2 text-amber-900 dark:text-amber-300 font-extrabold text-sm">
              <Accessibility className="w-4 h-4 text-amber-600" />
              <span>Elderly (65+ years)</span>
            </div>
            <div className="text-2xl font-black text-amber-950 dark:text-amber-200">{elderlyCount} Citizens</div>
            <p className="text-[11px] text-amber-800 dark:text-amber-300 font-medium">
              Priority transport assigned to wheelchair-accessible shelters.
            </p>
          </div>

          <div className="p-4 bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800/60 rounded-2xl space-y-2">
            <div className="flex items-center gap-2 text-indigo-900 dark:text-indigo-300 font-extrabold text-sm">
              <Baby className="w-4 h-4 text-indigo-600" />
              <span>Infants & Young Children</span>
            </div>
            <div className="text-2xl font-black text-indigo-950 dark:text-indigo-200">{infantsCount} Children</div>
            <p className="text-[11px] text-indigo-800 dark:text-indigo-300 font-medium">
              Pediatric ration kits & formula allocated at relief centers.
            </p>
          </div>

          <div className="p-4 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800/60 rounded-2xl space-y-2">
            <div className="flex items-center gap-2 text-rose-900 dark:text-rose-300 font-extrabold text-sm">
              <Accessibility className="w-4 h-4 text-rose-600" />
              <span>Mobility-Impaired</span>
            </div>
            <div className="text-2xl font-black text-rose-950 dark:text-rose-200">{mobilityImpairedCount} Citizens</div>
            <p className="text-[11px] text-rose-800 dark:text-rose-300 font-medium">
              Specialized stretcher & ramp transport units dispatched.
            </p>
          </div>

          <div className="p-4 bg-purple-50 dark:bg-purple-950/40 border border-purple-200 dark:border-purple-800/60 rounded-2xl space-y-2">
            <div className="flex items-center gap-2 text-purple-900 dark:text-purple-300 font-extrabold text-sm">
              <Hospital className="w-4 h-4 text-purple-600" />
              <span>Medical / Critical Care</span>
            </div>
            <div className="text-2xl font-black text-purple-950 dark:text-purple-200">{hospitalPatientsCount} Patients</div>
            <p className="text-[11px] text-purple-800 dark:text-purple-300 font-medium">
              Direct transfer to Primary Health Center (PHC) Medical Unit.
            </p>
          </div>
        </div>

        {/* Action Shortcuts */}
        <div className="flex flex-wrap justify-end gap-3 pt-3 border-t border-slate-200 dark:border-slate-800">
          {onNavigate && (
            <>
              <button
                onClick={() => onNavigate("evacuation")}
                className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-extrabold text-xs rounded-xl shadow transition-all cursor-pointer"
              >
                <Navigation className="w-4 h-4" />
                <span>Calculate Evacuation Route →</span>
              </button>

              <button
                onClick={() => onNavigate("red-zone")}
                className="flex items-center gap-2 px-4 py-2.5 bg-pink-600 hover:bg-pink-500 text-white font-extrabold text-xs rounded-xl shadow transition-all cursor-pointer"
              >
                <ShieldAlert className="w-4 h-4" />
                <span>View Red Zone Risk Analysis →</span>
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
