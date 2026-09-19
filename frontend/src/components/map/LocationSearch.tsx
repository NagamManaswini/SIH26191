import React, { useState, useEffect, useRef } from "react";
import { Search, MapPin, Compass, Loader2 } from "lucide-react";
import { locationService, LocationResult } from "../../services/locationService";

interface LocationSearchProps {
  onSelectLocation: (loc: { name: string; lat: number; lon: number }) => void;
  currentLabel?: string;
  placeholder?: string;
}

export const LocationSearch: React.FC<LocationSearchProps> = ({
  onSelectLocation,
  currentLabel,
  placeholder = "Search any location in India (e.g. Chennai, Visakhapatnam, Tirupati, district...)",
}) => {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<LocationResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const wrapperRef = useRef<HTMLDivElement>(null);

  // Handle outside click to dismiss suggestions
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Debounced search fetch
  useEffect(() => {
    if (!query || query.trim().length < 2) {
      setResults([]);
      setIsOpen(false);
      return;
    }

    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const res = await locationService.searchLocation(query);
        setResults(res);
        setIsOpen(true);
      } catch (e) {
        console.error("Location search error:", e);
      } finally {
        setLoading(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [query]);

  const handleSelect = (item: LocationResult) => {
    const displayLabel = item.formatted_address || item.name;
    setQuery(displayLabel);
    setIsOpen(false);
    onSelectLocation({
      name: displayLabel,
      lat: item.latitude,
      lon: item.longitude,
    });
  };

  const handleKeyDown = async (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      if (results.length > 0) {
        handleSelect(results[0]);
      } else if (query.trim().length >= 2) {
        setLoading(true);
        try {
          const res = await locationService.searchLocation(query);
          if (res.length > 0) {
            handleSelect(res[0]);
          }
        } catch (err) {
          console.error("Enter key search error:", err);
        } finally {
          setLoading(false);
        }
      }
    }
  };

  const handleGPS = () => {
    setLoading(true);

    const applyLocation = async (lat: number, lon: number) => {
      try {
        const label = await locationService.reverseGeocode(lat, lon);
        setQuery(label);
        setIsOpen(false);
        onSelectLocation({ name: label, lat, lon });
      } catch (err) {
        console.warn("Reverse geocode failed:", err);
      } finally {
        setLoading(false);
      }
    };

    const tryIPFallback = async (reason: string) => {
      console.warn(`Browser GPS notice (${reason}). Trying IP location estimation...`);
      const ipLoc = await locationService.getIPLocation();
      if (ipLoc) {
        setQuery(ipLoc.name);
        setIsOpen(false);
        onSelectLocation(ipLoc);
        setLoading(false);
      } else {
        setLoading(false);
        alert(`Location Notice (${reason}): Unable to acquire GPS coordinates automatically. Please search your city or click on the map.`);
      }
    };

    if (!("geolocation" in navigator)) {
      tryIPFallback("Geolocation not supported by browser");
      return;
    }

    // 1. First Attempt: High accuracy GPS (6s timeout)
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        applyLocation(pos.coords.latitude, pos.coords.longitude);
      },
      (err1) => {
        console.warn("High accuracy GPS notice:", err1.message, "- Retrying with standard accuracy");
        // 2. Second Attempt: Standard accuracy GPS (10s timeout, cached up to 1 min)
        navigator.geolocation.getCurrentPosition(
          (pos) => {
            applyLocation(pos.coords.latitude, pos.coords.longitude);
          },
          (err2) => {
            tryIPFallback(err2.message || "GPS acquiring timed out");
          },
          { enableHighAccuracy: false, timeout: 10000, maximumAge: 60000 }
        );
      },
      { enableHighAccuracy: true, timeout: 6000, maximumAge: 0 }
    );
  };

  return (
    <div ref={wrapperRef} className="relative w-full font-sans space-y-1.5">
      <div className="relative flex items-center">
        <div className="absolute left-3.5 text-indigo-600 pointer-events-none">
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4 text-indigo-600" />}
        </div>

        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => {
            if (results.length > 0) setIsOpen(true);
          }}
          placeholder={placeholder}
          className="w-full pl-10 pr-24 py-2.5 bg-white border border-indigo-200 rounded-xl text-xs sm:text-sm text-indigo-950 font-bold placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent shadow-sm transition-all"
        />

        <button
          type="button"
          onClick={handleGPS}
          className="absolute right-2 px-2.5 py-1 bg-emerald-100 hover:bg-emerald-200 text-emerald-900 border border-emerald-300 rounded-lg text-xs font-black flex items-center gap-1 transition-colors"
          title="Use My GPS Location"
        >
          <Compass className="w-3.5 h-3.5 text-emerald-700" />
          <span>GPS</span>
        </button>
      </div>

      {/* Autocomplete Dropdown List */}
      {isOpen && results.length > 0 && (
        <div className="absolute left-0 right-0 top-full mt-1 bg-white border border-indigo-200 rounded-xl shadow-2xl z-50 max-h-64 overflow-y-auto divide-y divide-slate-100 animate-in fade-in duration-100">
          <div className="px-3 py-1.5 text-[10px] font-black uppercase tracking-wider text-indigo-900 bg-indigo-50">
            Location Suggestions ({results.length})
          </div>

          {results.map((item, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleSelect(item)}
              className="w-full px-3.5 py-2.5 text-left text-xs hover:bg-indigo-50 flex items-start gap-2.5 transition-colors group cursor-pointer"
            >
              <MapPin className="w-4 h-4 text-pink-600 shrink-0 mt-0.5 group-hover:scale-110 transition-transform" />
              <div>
                <span className="font-extrabold text-indigo-950 block">{item.name}</span>
                <span className="text-[11px] text-slate-500 font-medium block truncate max-w-md">
                  {item.formatted_address}
                </span>
                <span className="text-[10px] text-indigo-600 font-mono font-bold">
                  Lat: {item.latitude.toFixed(4)} | Lon: {item.longitude.toFixed(4)}
                </span>
              </div>
            </button>
          ))}
        </div>
      )}

      {currentLabel && (
        <div className="text-[11px] text-indigo-950 font-bold flex items-center gap-1.5 pt-0.5">
          <span className="text-slate-500">Active Location:</span>
          <span className="text-pink-700 font-extrabold truncate">📍 {currentLabel}</span>
        </div>
      )}
    </div>
  );
};
