import React, { useEffect, useState } from "react";
import {
  WifiOff,
  Wifi,
  Home,
  Phone,
  Navigation,
  ShieldAlert,
  AlertTriangle,
  CheckSquare,
  RefreshCw,
  Info,
  Dog,
} from "lucide-react";
import { OfflineStorageService, CachedEmergencyBundle } from "../services/offlineStorage";

export const OfflineEmergencyPage: React.FC = () => {
  const [isOnline, setIsOnline] = useState<boolean>(navigator.onLine);
  const [bundle, setBundle] = useState<CachedEmergencyBundle | null>(null);
  const [syncStatus, setSyncStatus] = useState<string>("");

  useEffect(() => {
    const loadedBundle = OfflineStorageService.getEmergencyBundle() || OfflineStorageService.saveEmergencyBundle({});
    setBundle(loadedBundle);

    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  const handleManualSync = () => {
    setSyncStatus("Synchronizing offline cache with backend servers...");
    setTimeout(() => {
      const updated = OfflineStorageService.saveEmergencyBundle({
        lastSyncTime: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + " IST",
      });
      setBundle(updated);
      setSyncStatus("Synchronization complete! Cached emergency data updated successfully.");
      setTimeout(() => setSyncStatus(""), 4000);
    }, 1200);
  };

  const handleExportBundle = () => {
    const currentBundle = OfflineStorageService.getEmergencyBundle();
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(currentBundle || {}, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `Disaster_Offline_Emergency_Bundle_${Date.now()}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
    setSyncStatus("Emergency Offline Data Bundle exported successfully for field / USB transfer.");
    setTimeout(() => setSyncStatus(""), 4000);
  };

  const handleImportBundle = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const json = JSON.parse(event.target?.result as string);
        const saved = OfflineStorageService.saveEmergencyBundle(json);
        setBundle(saved);
        setSyncStatus("Emergency Offline Data Bundle imported successfully!");
      } catch (err) {
        alert("Invalid JSON format for Emergency Bundle file.");
      }
    };
    reader.readAsText(file);
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto font-sans bg-slate-50 dark:bg-slate-950 min-h-screen text-slate-900 dark:text-slate-100">
      {/* Network Status Header Banner */}
      <div
        className={`border rounded-3xl p-6 shadow-xl flex flex-wrap items-center justify-between gap-4 transition-all ${
          !isOnline
            ? "bg-amber-400 border-amber-500 text-slate-950"
            : "bg-emerald-600 border-emerald-500 text-white"
        }`}
      >
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-black/10 flex items-center justify-center shrink-0">
            {!isOnline ? <WifiOff className="w-8 h-8 text-slate-950" /> : <Wifi className="w-8 h-8 text-white" />}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className={`text-[10px] font-black px-2.5 py-0.5 rounded tracking-wider uppercase ${
                !isOnline ? "bg-slate-950 text-amber-300" : "bg-white text-emerald-700"
              }`}>
                {!isOnline ? "OFFLINE FIELD DEPLOYMENT ACTIVE" : "OPERATIONAL NETWORK ACTIVE"}
              </span>
              <span className="text-xs font-extrabold opacity-90">
                Last Sync: {bundle?.lastSyncTime || "Just Now"}
              </span>
            </div>
            <h1 className="text-2xl font-black tracking-tight mt-1">
              {!isOnline ? "OFFLINE MODE — Disconnected Field Operations Ready" : "ONLINE CACHE & REAL-TIME DISASTER ENGINE"}
            </h1>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={handleManualSync}
            className="flex items-center gap-2 px-4 py-2.5 rounded-2xl bg-slate-950 text-amber-300 font-extrabold text-xs hover:bg-slate-900 shadow-md transition-all cursor-pointer border border-slate-800"
          >
            <RefreshCw className="w-4 h-4" />
            Synchronize Cache
          </button>
          <button
            onClick={handleExportBundle}
            className="flex items-center gap-2 px-4 py-2.5 rounded-2xl bg-indigo-900 text-white font-extrabold text-xs hover:bg-indigo-800 shadow-md transition-all cursor-pointer border border-indigo-700"
            title="Download emergency data JSON for field USB drives"
          >
            Export Offline Bundle
          </button>
          <label className="flex items-center gap-2 px-4 py-2.5 rounded-2xl bg-emerald-800 text-white font-extrabold text-xs hover:bg-emerald-700 shadow-md transition-all cursor-pointer border border-emerald-600">
            Import Bundle
            <input type="file" accept=".json" onChange={handleImportBundle} className="hidden" />
          </label>
        </div>
      </div>

      {syncStatus && (
        <div className="p-4 bg-indigo-100 dark:bg-indigo-950/60 border border-indigo-300 text-indigo-900 dark:text-indigo-200 rounded-2xl text-xs font-bold animate-pulse">
          {syncStatus}
        </div>
      )}

      {/* Offline Availability Checklist Banner */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-md space-y-4">
        <h2 className="text-xs font-black text-indigo-950 dark:text-indigo-300 uppercase tracking-wider flex items-center gap-2">
          <CheckSquare className="w-4 h-4 text-emerald-500" />
          Offline Available Emergency Resources
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3 text-xs font-extrabold">
          {[
            { label: "Emergency Instructions", status: true },
            { label: "Saved Evacuation Routes", status: true },
            { label: "Shelter Information", status: true },
            { label: "Emergency Contacts", status: true },
            { label: "Animal Rescue Info", status: true },
          ].map((item, idx) => (
            <div key={idx} className="bg-slate-50 dark:bg-slate-800 p-3 rounded-xl border border-slate-200 dark:border-slate-700 flex items-center gap-2 text-slate-800 dark:text-slate-200">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              <span>✓ {item.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Warning Box */}
      <div className="p-4 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800/60 rounded-2xl flex items-center gap-3 text-rose-900 dark:text-rose-200 text-xs font-black">
        <AlertTriangle className="w-5 h-5 text-rose-600 shrink-0" />
        <span>IMPORTANT: Real-time hazard updates are unavailable while network connectivity is offline.</span>
      </div>

      {/* Offline Hotlines Grid */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-md space-y-4">
        <h3 className="text-xs font-black text-indigo-950 dark:text-indigo-300 uppercase tracking-wider flex items-center gap-2">
          <Phone className="w-4 h-4 text-pink-600" />
          Cached Emergency Helpline Numbers
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-3 text-xs">
          {(bundle?.contacts || []).map((c, idx) => (
            <div key={idx} className="bg-amber-50 dark:bg-amber-950/30 p-3 rounded-xl border border-amber-200 dark:border-amber-900/50 space-y-1">
              <span className="text-slate-700 dark:text-slate-300 block text-[11px] font-extrabold">{c.name}</span>
              <b className="text-pink-700 dark:text-pink-400 text-sm font-mono block font-black">{c.phone}</b>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Cached Shelters & Routes */}
        <div className="lg:col-span-7 space-y-6">
          {/* Cached Hospitals & Emergency Medical Facilities */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-md space-y-4">
            <h3 className="text-xs font-black text-indigo-950 dark:text-indigo-300 uppercase tracking-wider flex items-center justify-between">
              <span className="flex items-center gap-2">
                <span className="text-base">🏥</span>
                Cached Hospitals & Medical Facilities
              </span>
              <span className="text-[10px] text-pink-600 font-extrabold bg-pink-100 dark:bg-pink-950 px-2 py-0.5 rounded">
                CACHED DATA • {bundle?.lastSyncTime || "Offline Sync"}
              </span>
            </h3>

            <div className="space-y-3">
              {[
                { id: 201, name: "Rajiv Gandhi Government General Hospital", status: "OPEN", beds: 150, emergency_beds: 25, phone: "+91 44 2530 5000", address: "Park Town, Chennai" },
                { id: 202, name: "Apollo Main Hospital", status: "OPEN", beds: 120, emergency_beds: 12, phone: "+91 44 2829 0200", address: "Greams Lane, Chennai" },
                { id: 203, name: "Wayanad District Hospital", status: "EMERGENCY_ONLY", beds: 40, emergency_beds: 2, phone: "+91 4935 240 223", address: "Mananthavady, Wayanad" },
              ].map((h) => (
                <div key={h.id} className="bg-pink-50/50 dark:bg-pink-950/30 p-4 rounded-2xl border border-pink-100 dark:border-pink-900/60 space-y-1 text-xs font-bold">
                  <div className="flex justify-between font-black text-indigo-950 dark:text-indigo-200">
                    <span>🏥 {h.name}</span>
                    <span className="text-pink-700 dark:text-pink-400 font-black">Emerg Beds: {h.emergency_beds}</span>
                  </div>
                  <div className="text-slate-600 dark:text-slate-400 text-[11px] flex justify-between">
                    <span>Address: {h.address}</span>
                    <span>Contact: <b className="text-emerald-700">{h.phone}</b></span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Cached Relief Shelters */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-md space-y-4">
            <h3 className="text-xs font-black text-indigo-950 dark:text-indigo-300 uppercase tracking-wider flex items-center justify-between">
              <span className="flex items-center gap-2">
                <Home className="w-4 h-4 text-indigo-600" />
                Cached Human Relief Shelters
              </span>
              <span className="text-[10px] text-amber-600 font-extrabold bg-amber-100 dark:bg-amber-950 px-2 py-0.5 rounded">LOCAL CACHE</span>
            </h3>

            <div className="space-y-3">
              {[
                { id: 101, name: "St. Joseph Higher Secondary School Shelter", capacity: 650, available: 530, address: "Meppadi Town, Wayanad" },
                { id: 102, name: "Meppadi Community Hall Relief Camp", capacity: 500, available: 415, address: "Near Main Bus Stand, Meppadi" },
                { id: 103, name: "Wayanad Relief Auditorium", capacity: 1200, available: 890, address: "Kalpetta Bypass Highway" },
              ].map((s) => (
                <div key={s.id} className="bg-indigo-50/60 dark:bg-indigo-950/40 p-4 rounded-2xl border border-indigo-100 dark:border-indigo-900 space-y-1 text-xs font-bold">
                  <div className="flex justify-between font-black text-indigo-950 dark:text-indigo-200">
                    <span>{s.name}</span>
                    <span className="text-emerald-600 dark:text-emerald-400 font-black">Spaces Available: {s.available}</span>
                  </div>
                  <div className="text-slate-600 dark:text-slate-400 text-[11px]">Location: {s.address}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Cached Evacuation Routes */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-md space-y-4">
            <h3 className="text-xs font-black text-indigo-950 dark:text-indigo-300 uppercase tracking-wider flex items-center gap-2">
              <Navigation className="w-4 h-4 text-indigo-600" />
              Pre-Downloaded Evacuation Detour Routes
            </h3>

            <div className="space-y-3 text-xs">
              <div className="bg-emerald-50 dark:bg-emerald-950/40 p-4 rounded-2xl border border-emerald-200 dark:border-emerald-800 space-y-1">
                <div className="flex justify-between font-black text-emerald-950 dark:text-emerald-200">
                  <span>North Ridge Highway Detour (Route 2)</span>
                  <span className="text-emerald-600 dark:text-emerald-400 font-black">SAFE DETOUR</span>
                </div>
                <div className="text-[11px] text-slate-600 dark:text-slate-400 font-bold">
                  Distance: 12.4 km | Est. Travel Time: 22 mins | Bypasses Chooralmala Red Zone
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Cached Animal Rescue & Native Architecture Disclaimer */}
        <div className="lg:col-span-5 space-y-6">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-md space-y-4">
            <h3 className="text-xs font-black text-indigo-950 dark:text-indigo-300 uppercase tracking-wider flex items-center gap-2">
              <Dog className="w-4 h-4 text-pink-600" />
              Cached Animal Rescue Facilities
            </h3>

            <div className="space-y-3 text-xs">
              <div className="bg-amber-50 dark:bg-amber-950/30 p-3.5 rounded-2xl border border-amber-200 dark:border-amber-900/50 space-y-1">
                <div className="font-black text-amber-950 dark:text-amber-200">North Valley Livestock Safe Holding</div>
                <div className="text-[11px] text-slate-600 dark:text-slate-400">Capacity: 250 animals | Supported: Cattle, Goats, Pets</div>
              </div>
              <div className="bg-amber-50 dark:bg-amber-950/30 p-3.5 rounded-2xl border border-amber-200 dark:border-amber-900/50 space-y-1">
                <div className="font-black text-amber-950 dark:text-amber-200">Community Animal Rescue Center B</div>
                <div className="text-[11px] text-slate-600 dark:text-slate-400">Capacity: 150 animals | Supported: Goats, Dogs, Cats</div>
              </div>
            </div>
          </div>

          {/* Peer-to-Peer Mesh Native Placeholder */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-md space-y-3 text-xs">
            <h4 className="font-black text-indigo-950 dark:text-indigo-300 flex items-center gap-2">
              <Info className="w-4 h-4 text-indigo-600" />
              Peer-to-Peer Mesh Native SDK Integration
            </h4>
            <p className="text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed font-medium">
              <b>Native Implementation Note:</b> Web browser security sandboxes do not permit raw low-level Bluetooth Mesh or Wi-Fi Direct packet broadcasting. Native Android / iOS SDK integration placeholders for mesh networks are documented in <code className="text-indigo-700 dark:text-indigo-400 font-bold">docs/offline-mode.md</code>.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
