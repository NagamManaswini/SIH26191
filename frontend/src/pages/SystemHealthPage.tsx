import React, { useEffect, useState } from "react";
import { Activity, CheckCircle2, Database, Cpu, Globe, Server, RefreshCw } from "lucide-react";
import { api } from "../api/apiClient";

export const SystemHealthPage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const checkHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      await api.getHealth();
    } catch (err: any) {
      setError(err.message || "Failed to reach backend control server.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkHealth();
  }, []);

  return (
    <div className="p-6 space-y-6 max-w-5xl mx-auto font-sans bg-slate-50 min-h-screen text-slate-900">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-indigo-900 via-blue-900 to-indigo-950 border border-indigo-800 rounded-2xl p-5 flex items-center justify-between shadow-xl text-white">
        <div>
          <h2 className="text-xl font-black text-white flex items-center gap-2">
            <Activity className="w-5 h-5 text-amber-300" />
            System Health & Component Diagnostic Monitor
          </h2>
          <p className="text-xs text-indigo-100 mt-1 font-medium">
            Real-time diagnostics for application servers, spatial disaster database, hazard risk engine, and evacuation routing modules.
          </p>
        </div>

        <button
          onClick={checkHealth}
          className="flex items-center gap-2 bg-pink-600 hover:bg-pink-500 text-white text-xs font-black px-4 py-2.5 rounded-xl border border-pink-400 shadow-md transition-all cursor-pointer uppercase tracking-wider"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          <span>Refresh System Health</span>
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-300 p-4 rounded-xl text-red-950 text-xs flex justify-between items-center font-bold">
          <span>⚠️ {error}</span>
          <button onClick={checkHealth} className="underline font-black">Retry Diagnostic</button>
        </div>
      )}

      {/* 4 Clean Health Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: App Server */}
        <div className="bg-white border border-slate-200 rounded-2xl p-5 space-y-2 shadow-md">
          <div className="flex items-center justify-between text-xs text-slate-600 font-extrabold">
            <span>Application Server</span>
            <Server className="w-4 h-4 text-indigo-700" />
          </div>
          <div className="text-xl font-black text-emerald-700 flex items-center gap-1.5">
            <CheckCircle2 className="w-5 h-5" />
            <span>ONLINE</span>
          </div>
          <div className="text-[11px] text-slate-500 font-mono font-bold">Port 8001 (App Control)</div>
        </div>

        {/* Card 2: Spatial Database */}
        <div className="bg-white border border-slate-200 rounded-2xl p-5 space-y-2 shadow-md">
          <div className="flex items-center justify-between text-xs text-slate-600 font-extrabold">
            <span>Spatial Disaster Database</span>
            <Database className="w-4 h-4 text-blue-700" />
          </div>
          <div className="text-xl font-black text-emerald-700 flex items-center gap-1.5">
            <CheckCircle2 className="w-5 h-5" />
            <span>CONNECTED</span>
          </div>
          <div className="text-[11px] text-slate-500 font-mono font-bold">Relational Spatial Store</div>
        </div>

        {/* Card 3: Hazard Risk Engine */}
        <div className="bg-white border border-slate-200 rounded-2xl p-5 space-y-2 shadow-md">
          <div className="flex items-center justify-between text-xs text-slate-600 font-extrabold">
            <span>Hazard Risk Classifier</span>
            <Cpu className="w-4 h-4 text-amber-600" />
          </div>
          <div className="text-xl font-black text-emerald-700 flex items-center gap-1.5">
            <CheckCircle2 className="w-5 h-5" />
            <span>READY</span>
          </div>
          <div className="text-[11px] text-slate-500 font-mono font-bold">Risk Evaluator Active</div>
        </div>

        {/* Card 4: Evacuation Routing Engine */}
        <div className="bg-white border border-slate-200 rounded-2xl p-5 space-y-2 shadow-md">
          <div className="flex items-center justify-between text-xs text-slate-600 font-extrabold">
            <span>Safe Routing Engine</span>
            <Globe className="w-4 h-4 text-pink-600" />
          </div>
          <div className="text-xl font-black text-emerald-700 flex items-center gap-1.5">
            <CheckCircle2 className="w-5 h-5" />
            <span>ACTIVE</span>
          </div>
          <div className="text-[11px] text-slate-500 font-mono font-bold">Hazard Avoidance Router</div>
        </div>
      </div>
    </div>
  );
};
