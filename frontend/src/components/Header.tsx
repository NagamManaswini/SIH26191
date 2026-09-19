import React, { useState, useEffect } from "react";
import { Shield, Clock, LogOut, FileText, Download, RefreshCw, Smartphone, Wifi, WifiOff } from "lucide-react";
import { UserAuth } from "../pages/LoginPage";
import { reportService } from "../services/reportService";

interface HeaderProps {
  activeTabLabel: string;
  user: UserAuth | null;
  onLogout: () => void;
  currentLocation?: { name: string; lat: number; lon: number };
}

export const Header: React.FC<HeaderProps> = ({ activeTabLabel, user, onLogout, currentLocation }) => {
  const currentTime = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  const isAdmin = user?.role === "admin";
  const [downloading, setDownloading] = useState(false);
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);
  const [isInstallable, setIsInstallable] = useState(false);
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    const handleBeforeInstall = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setIsInstallable(true);
    };

    window.addEventListener("beforeinstallprompt", handleBeforeInstall);

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
      window.removeEventListener("beforeinstallprompt", handleBeforeInstall);
    };
  }, []);

  const handleInstallPwa = async () => {
    if (!deferredPrompt) {
      alert("To install as an offline App:\n1. Click the 'Install' icon in your browser address bar, or\n2. Open browser menu (⋮) -> 'Install App' / 'Add to Home Screen'.");
      return;
    }
    deferredPrompt.prompt();
    const choiceResult = await deferredPrompt.userChoice;
    if (choiceResult.outcome === "accepted") {
      console.log("[PWA] User accepted the install prompt");
    }
    setDeferredPrompt(null);
    setIsInstallable(false);
  };

  const handleGeneratePdf = async () => {
    if (!isAdmin) {
      alert("Access Denied: Admin privileges required to generate official PDF reports.");
      return;
    }

    setDownloading(true);
    try {
      const blob = await reportService.generatePdfReport(
        {
          location_name: currentLocation?.name || "Chennai, Tamil Nadu",
          latitude: currentLocation?.lat || 13.0827,
          longitude: currentLocation?.lon || 80.2707,
          admin_name: user?.name || "Command Chief Officer",
        },
        user?.role || "admin"
      );
      reportService.downloadBlobAsFile(blob, `Disaster_Management_Report_${Date.now()}.pdf`);
    } catch (err: any) {
      alert("Report Generation Error: " + err.message);
    } finally {
      setDownloading(false);
    }
  };

  return (
    <header className="h-16 bg-indigo-950 backdrop-blur-md border-b border-indigo-900 px-6 flex items-center justify-between sticky top-0 z-20 shrink-0 shadow-lg text-white font-sans">
      <div>
        <h2 className="text-base font-extrabold text-white flex items-center gap-2">
          <span>{activeTabLabel}</span>
          {!isOnline && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-amber-500/20 text-amber-300 border border-amber-500/40 text-[10px] font-bold">
              <WifiOff className="w-3 h-3" /> OFFLINE PWA ACTIVE
            </span>
          )}
        </h2>
      </div>

      <div className="flex items-center gap-3">
        {/* PWA Install Button */}
        <button
          onClick={handleInstallPwa}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl border text-xs font-black shadow-md transition-all cursor-pointer uppercase tracking-wider shrink-0 ${
            isInstallable
              ? "bg-emerald-600 hover:bg-emerald-500 text-white border-emerald-400 animate-pulse"
              : "bg-indigo-900/80 hover:bg-indigo-800 text-indigo-200 border-indigo-700"
          }`}
          title="Install as Offline PWA App on Desktop / Mobile"
        >
          <Smartphone className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">INSTALL PWA</span>
        </button>

        {/* Generate Official PDF Report Button - ADMIN ONLY */}
        {isAdmin && (
          <button
            onClick={handleGeneratePdf}
            disabled={downloading}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-pink-600 hover:bg-pink-500 text-white border border-pink-400 text-xs font-black shadow-md transition-all cursor-pointer uppercase tracking-wider shrink-0"
            title="Generate Official Disaster Analysis PDF Report (Admin Only)"
          >
            {downloading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <FileText className="w-3.5 h-3.5" />}
            <span className="hidden sm:inline">GENERATE PDF REPORT</span>
            <Download className="w-3.5 h-3.5 ml-0.5" />
          </button>
        )}

        {/* Live Clock & Network Status Badge */}
        <div className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-900/90 border border-indigo-700 text-amber-300 text-xs font-mono font-bold">
          {isOnline ? <Wifi className="w-3.5 h-3.5 text-emerald-400" /> : <WifiOff className="w-3.5 h-3.5 text-amber-400" />}
          <Clock className="w-3.5 h-3.5 text-amber-300" />
          <span>{currentTime} IST</span>
        </div>

        {/* User Profile Badge */}
        {user ? (
          <div className="flex items-center gap-3 pl-2 border-l border-indigo-800">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-pink-600 text-white font-black flex items-center justify-center text-xs shadow-md border border-pink-400">
                {user.name.charAt(0)}
              </div>
              <div className="hidden sm:block text-left">
                <div className="text-xs font-extrabold text-white flex items-center gap-1">
                  <span>{user.name}</span>
                  <span
                    className={`px-1.5 py-0.2 rounded text-[9px] font-black uppercase ${
                      user.role === "admin"
                        ? "bg-red-600 text-white border border-red-400"
                        : "bg-emerald-600 text-white border border-emerald-400"
                    }`}
                  >
                    {user.role}
                  </span>
                </div>
                <div className="text-[10px] text-indigo-200">{user.email}</div>
              </div>
            </div>

            <button
              onClick={onLogout}
              title="Logout"
              className="p-2 rounded-lg bg-indigo-900 hover:bg-pink-700 text-indigo-200 hover:text-white border border-indigo-700 transition-colors flex items-center gap-1 text-xs font-bold"
            >
              <LogOut className="w-4 h-4" />
              <span className="hidden xl:inline">Logout</span>
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-pink-950/80 border border-pink-500/60 text-pink-200 text-xs font-extrabold animate-pulse">
            <Shield className="w-3.5 h-3.5 text-pink-400" />
            <span>ACTIVE HAZARD MONITORING</span>
          </div>
        )}
      </div>
    </header>
  );
};

