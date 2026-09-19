import React, { useState, useEffect } from "react";
import { ShieldAlert, Navigation, Home, PhoneCall, AlertTriangle, CloudRain, MapPin, ArrowRight, Globe, ChevronDown, Check, Radio } from "lucide-react";
import { api } from "../api/apiClient";
import { weatherService, LiveWeatherData } from "../services/weatherService";
import { LocationSearch } from "../components/map/LocationSearch";
import { translations, LANGUAGES, Language } from "../utils/translations";

interface UserDashboardProps {
  onNavigate: (tab: string) => void;
}

export const UserDashboard: React.FC<UserDashboardProps> = ({ onNavigate }) => {
  const [shelters, setShelters] = useState<any[]>([]);
  const [sosSent, setSosSent] = useState<boolean>(false);

  const [selectedLocation, setSelectedLocation] = useState({
    lat: 13.0827,
    lon: 80.2707,
    name: "Chennai, Tamil Nadu",
  });

  const [liveWeather, setLiveWeather] = useState<LiveWeatherData | null>(null);

  // Language state
  const [language, setLanguage] = useState<Language>(() => {
    const saved = localStorage.getItem("user_portal_lang");
    return (saved as Language) || "en";
  });

  const [isLangDropdownOpen, setIsLangDropdownOpen] = useState<boolean>(false);
  const t = translations[language] || translations.en;

  const handleLanguageChange = (newLang: Language) => {
    setLanguage(newLang);
    localStorage.setItem("user_portal_lang", newLang);
    setIsLangDropdownOpen(false);
  };

  const loadWeatherForLocation = async (lat: number, lon: number, name: string) => {
    setSelectedLocation({ lat, lon, name });
    try {
      const wData = await weatherService.getLiveWeather(lat, lon, name);
      setLiveWeather(wData);
    } catch (e) {
      console.warn("Live weather notice:", e);
    }
  };

  useEffect(() => {
    api.getShelters().then((data) => {
      if (Array.isArray(data)) setShelters(data.slice(0, 3));
    }).catch(() => {});

    loadWeatherForLocation(selectedLocation.lat, selectedLocation.lon, selectedLocation.name);
  }, []);

  const handleTriggerSOS = () => {
    setSosSent(true);
    setTimeout(() => {
      alert(t.sosAlert);
    }, 400);
  };

  const currentLangObj = LANGUAGES.find((l) => l.code === language) || LANGUAGES[0];

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto font-sans bg-slate-50 min-h-screen text-slate-900">
      {/* Dynamic Location Search Banner for Citizens */}
      <div className="bg-white border border-indigo-200 rounded-2xl p-4 shadow-md space-y-2">
        <span className="text-xs font-black text-indigo-950 uppercase tracking-wider block">
          Search Your Location in India (Google Maps & Places)
        </span>
        <LocationSearch
          currentLabel={selectedLocation.name}
          onSelectLocation={(loc) => loadWeatherForLocation(loc.lat, loc.lon, loc.name)}
        />
      </div>

      {/* Top Customization Toolbar: Language Selector */}
      <div className="bg-indigo-900 border border-indigo-800 text-white rounded-2xl p-4 flex flex-col md:flex-row items-center justify-between gap-4 shadow-xl relative z-30">
        <div className="flex items-center gap-3 w-full md:w-auto relative">
          <div className="flex items-center gap-2 text-indigo-100 font-bold text-sm shrink-0">
            <Globe className="w-5 h-5 text-amber-300" />
            <span>{t.languageLabel}:</span>
          </div>

          <div className="relative inline-block text-left w-full sm:w-60">
            <button
              type="button"
              onClick={() => setIsLangDropdownOpen(!isLangDropdownOpen)}
              className="w-full px-4 py-2.5 rounded-xl font-bold text-xs sm:text-sm bg-white hover:bg-indigo-50 text-indigo-950 border border-indigo-200 flex items-center justify-between gap-2 shadow-md transition-all focus:outline-none"
            >
              <div className="flex items-center gap-2">
                <span className="text-base">{currentLangObj.flag}</span>
                <span>{currentLangObj.nativeName} ({currentLangObj.label})</span>
              </div>
              <ChevronDown className={`w-4 h-4 text-indigo-600 transition-transform ${isLangDropdownOpen ? "rotate-180" : ""}`} />
            </button>

            {isLangDropdownOpen && (
              <div className="absolute left-0 mt-2 w-full sm:w-64 bg-white border border-indigo-200 rounded-xl shadow-2xl z-50 py-1.5 overflow-hidden text-slate-900">
                <div className="px-3 py-1.5 text-[11px] font-extrabold uppercase tracking-wider text-indigo-900 bg-indigo-50">
                  Select Portal Language
                </div>
                <div className="flex flex-col max-h-64 overflow-y-auto">
                  {LANGUAGES.map((lang) => {
                    const isSelected = language === lang.code;
                    return (
                      <button
                        key={lang.code}
                        onClick={() => handleLanguageChange(lang.code)}
                        className={`w-full px-4 py-2.5 text-xs sm:text-sm font-semibold flex items-center justify-between text-left transition-colors ${
                          isSelected ? "bg-indigo-50 text-indigo-900 font-extrabold" : "text-slate-700 hover:bg-slate-100"
                        }`}
                      >
                        <div className="flex items-center gap-2.5">
                          <span className="text-base">{lang.flag}</span>
                          <span>{lang.nativeName}</span>
                        </div>
                        {isSelected && <Check className="w-4 h-4 text-indigo-600 shrink-0" />}
                      </button>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Royal Blue CWC Government Banner */}
      <div className="bg-gradient-to-r from-indigo-900 via-blue-900 to-indigo-950 border border-indigo-800 rounded-2xl p-6 shadow-xl relative overflow-hidden text-white">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2 flex-wrap">
              <span className="px-3 py-1 rounded-full bg-amber-400 text-slate-950 font-black text-xs uppercase tracking-wider flex items-center gap-1.5 shadow-md">
                <AlertTriangle className="w-4 h-4 text-slate-950" />
                {t.hazardBulletin}
              </span>
            </div>
            <h1 className="text-2xl md:text-3xl font-black text-white drop-shadow-sm">{t.portalTitle}</h1>
            <p className="text-sm text-indigo-100 mt-2 max-w-2xl leading-relaxed font-medium">
              {t.portalSubtitle}
            </p>
          </div>

          <button
            onClick={handleTriggerSOS}
            className={`px-7 py-4 rounded-xl font-black text-sm flex items-center gap-3 shadow-2xl transition-all shrink-0 uppercase tracking-wider ${
              sosSent
                ? "bg-emerald-600 text-white shadow-emerald-950/50"
                : "bg-pink-600 hover:bg-pink-500 text-white shadow-pink-900/50 animate-bounce"
            }`}
          >
            <ShieldAlert className="w-6 h-6" />
            <span>{sosSent ? t.sosBtnSent : t.sosBtnNormal}</span>
          </button>
        </div>
      </div>

      {/* Quick Action Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div onClick={() => onNavigate("evacuation")} className="bg-white border border-slate-200 hover:border-indigo-500 rounded-2xl p-5 cursor-pointer group transition-all shadow-md">
          <div className="w-12 h-12 rounded-xl bg-indigo-100 text-indigo-800 flex items-center justify-center mb-4">
            <Navigation className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-black text-indigo-950 mb-1 flex items-center gap-2">
            <span>{t.evacuationTitle}</span>
            <ArrowRight className="w-5 h-5 text-indigo-600" />
          </h3>
          <p className="text-xs md:text-sm text-slate-600 leading-relaxed font-medium">{t.evacuationDesc}</p>
        </div>

        <div onClick={() => onNavigate("shelters")} className="bg-white border border-slate-200 hover:border-emerald-500 rounded-2xl p-5 cursor-pointer group transition-all shadow-md">
          <div className="w-12 h-12 rounded-xl bg-emerald-100 text-emerald-800 flex items-center justify-center mb-4">
            <Home className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-black text-indigo-950 mb-1 flex items-center gap-2">
            <span>{t.shelterTitle}</span>
            <ArrowRight className="w-5 h-5 text-emerald-600" />
          </h3>
          <p className="text-xs md:text-sm text-slate-600 leading-relaxed font-medium">{t.shelterDesc}</p>
        </div>

        <div onClick={() => onNavigate("map")} className="bg-white border border-slate-200 hover:border-amber-500 rounded-2xl p-5 cursor-pointer group transition-all shadow-md">
          <div className="w-12 h-12 rounded-xl bg-amber-100 text-amber-800 flex items-center justify-center mb-4">
            <MapPin className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-black text-indigo-950 mb-1 flex items-center gap-2">
            <span>{t.mapTitle}</span>
            <ArrowRight className="w-5 h-5 text-amber-600" />
          </h3>
          <p className="text-xs md:text-sm text-slate-600 leading-relaxed font-medium">{t.mapDesc}</p>
        </div>
      </div>

      {/* Main Content Grid: Nearby Shelters & Live Weather */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <h3 className="text-lg font-black text-indigo-950 flex items-center gap-2">
              <Home className="w-5 h-5 text-indigo-700" />
              <span>{t.nearestSheltersHeader}</span>
            </h3>
            <button onClick={() => onNavigate("shelters")} className="text-xs md:text-sm font-extrabold text-indigo-700 hover:underline">
              {t.viewAllShelters}
            </button>
          </div>

          <div className="space-y-3">
            {shelters.map((shelter, idx) => (
              <div key={shelter.id || idx} className="bg-white border border-slate-200 rounded-xl p-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-sm">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="text-base font-extrabold text-indigo-950">{shelter.name}</h4>
                    <span className="px-2.5 py-0.5 rounded bg-emerald-100 text-emerald-800 border border-emerald-300 text-xs font-bold">
                      {t.shelterActive}
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 flex items-center gap-1 font-medium">
                    <MapPin className="w-4 h-4 text-indigo-500 shrink-0" />
                    <span>{shelter.address || "Sector Emergency Relief Safe Zone"}</span>
                  </p>
                </div>

                <div className="flex items-center gap-4 text-xs shrink-0">
                  <div className="text-right">
                    <div className="text-emerald-700 font-extrabold text-base">
                      {shelter.capacity ? shelter.capacity - (shelter.current_occupancy || 0) : 450} {t.shelterAvailable}
                    </div>
                    <div className="text-xs text-slate-500 font-semibold">{t.shelterMaxCap}: {shelter.capacity || 500}</div>
                  </div>

                  <button onClick={() => onNavigate("evacuation")} className="px-4 py-2.5 rounded-xl bg-pink-600 hover:bg-pink-500 text-white font-extrabold text-xs transition-colors shadow-md">
                    {t.navigateRoute}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Column: 100% Live Weather Data (NO FAKE WEATHER) */}
        <div className="space-y-6">
          <div className="bg-white border border-slate-200 rounded-2xl p-5 space-y-3 shadow-md">
            <div className="flex items-center justify-between">
              <h4 className="text-xs md:text-sm font-extrabold text-indigo-900 uppercase tracking-wider flex items-center gap-2">
                <CloudRain className="w-5 h-5 text-blue-600" />
                <span>{t.weatherHeader}</span>
              </h4>
              <span className={`text-[10px] font-black px-2 py-0.5 rounded border uppercase ${
                liveWeather?.data_status === "LIVE" ? "bg-emerald-100 text-emerald-800 border-emerald-300" : "bg-amber-100 text-amber-800 border-amber-300"
              }`}>
                {liveWeather?.data_status || "FETCHING"}
              </span>
            </div>

            {liveWeather && liveWeather.status !== "unavailable" ? (
              <div className="p-4 rounded-xl bg-indigo-50/60 border border-indigo-100 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-black text-indigo-950">
                    {liveWeather.temperature_c !== undefined ? `${liveWeather.temperature_c} °C` : "N/A"}
                  </span>
                  <span className="px-2.5 py-1 rounded bg-indigo-900 text-amber-300 text-xs font-bold">
                    {liveWeather.condition}
                  </span>
                </div>
                <div className="text-xs text-slate-700 font-bold grid grid-cols-2 gap-1 pt-1">
                  <div>Precipitation: <b>{liveWeather.precipitation_mm} mm</b></div>
                  <div>Humidity: <b>{liveWeather.humidity_percent || "N/A"}%</b></div>
                  <div>Wind: <b>{liveWeather.wind_speed_kmh || "N/A"} km/h</b></div>
                  <div>Pressure: <b>{liveWeather.pressure_hpa || "N/A"} hPa</b></div>
                </div>
                <div className="text-[10px] text-slate-500 font-mono pt-1">
                  Last updated: <b>{liveWeather.last_updated}</b>
                </div>
              </div>
            ) : (
              <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-xs text-red-800 font-bold">
                Live weather data is currently unavailable.
              </div>
            )}
          </div>

          {/* Emergency Helplines */}
          <div className="bg-white border border-slate-200 rounded-2xl p-5 space-y-3 shadow-md">
            <h4 className="text-xs md:text-sm font-extrabold text-indigo-900 uppercase tracking-wider flex items-center gap-2">
              <PhoneCall className="w-5 h-5 text-amber-600" />
              <span>{t.helplineHeader}</span>
            </h4>

            <div className="space-y-2 text-xs">
              <div className="p-3 rounded-xl bg-amber-50 border border-amber-200 flex items-center justify-between">
                <span className="text-slate-900 font-bold">{t.ndrfControl}</span>
                <span className="font-mono text-pink-700 font-black">1078</span>
              </div>

              <div className="p-3 rounded-xl bg-amber-50 border border-amber-200 flex items-center justify-between">
                <span className="text-slate-900 font-bold">{t.districtCollectorate}</span>
                <span className="font-mono text-pink-700 font-black">+91-9447100101</span>
              </div>

              <div className="p-3 rounded-xl bg-amber-50 border border-amber-200 flex items-center justify-between">
                <span className="text-slate-900 font-bold">{t.fireRescue}</span>
                <span className="font-mono text-pink-700 font-black">101</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
