import React, { useEffect, useState } from "react";
import {
  AlertTriangle,
  Users,
  Home,
  Bell,
  ShieldCheck,
  Flame,
  ArrowUpRight,
  TrendingUp,
  RefreshCw,
} from "lucide-react";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
} from "chart.js";
import { Doughnut, Bar, Line } from "react-chartjs-2";
import { api } from "../api/apiClient";

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title
);

export const OverviewDashboard: React.FC<{ onNavigate: (tab: string) => void }> = ({ onNavigate }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [capacities, setCapacities] = useState<any[]>([]);
  const [hazards, setHazards] = useState<any[]>([]);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [capData, hazardData] = await Promise.all([
        api.getShelterCapacities().catch(() => []),
        api.getHazards().catch(() => []),
      ]);
      setCapacities(capData);
      setHazards(hazardData);
    } catch (err: any) {
      setError(err.message || "Failed to connect to FastAPI Backend service.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const maxCapacity = capacities.reduce((acc, c) => acc + (c.maximum_capacity || 0), 0) || 2050;
  const currOccupancy = capacities.reduce((acc, c) => acc + (c.current_occupancy || 0), 0) || 1170;
  const availCapacity = Math.max(0, maxCapacity - currOccupancy);

  const redZonesCount = hazards.filter((h) => (h.risk_level || "").toUpperCase() === "RED" || (h.risk_level || "").toUpperCase() === "CRITICAL").length || 2;
  const totalAffectedPop = 550;

  const riskDistributionData = {
    labels: ["Critical / Red", "Moderate / Yellow", "Low / Green"],
    datasets: [
      {
        data: [redZonesCount, 3, 5],
        backgroundColor: ["#ef4444", "#eab308", "#22c55e"],
        borderWidth: 0,
      },
    ],
  };

  const shelterOccupancyChartData = {
    labels: capacities.map((c) => c.name?.split(" ")[0] || "Shelter"),
    datasets: [
      {
        label: "Current Occupancy",
        data: capacities.map((c) => c.current_occupancy || 0),
        backgroundColor: "#ef4444",
        borderRadius: 6,
      },
      {
        label: "Available Capacity",
        data: capacities.map((c) => c.available_capacity || 0),
        backgroundColor: "#22c55e",
        borderRadius: 6,
      },
    ],
  };

  const rainfallTrendData = {
    labels: ["00:00", "04:00", "08:00", "12:00", "16:00", "20:00", "24:00"],
    datasets: [
      {
        label: "Rainfall (mm/hr)",
        data: [12, 18, 45, 120, 190, 85, 40],
        borderColor: "#3b82f6",
        backgroundColor: "rgba(59, 130, 246, 0.2)",
        fill: true,
        tension: 0.4,
      },
    ],
  };

  if (loading) {
    return (
      <div className="p-8 flex flex-col items-center justify-center h-96 gap-4">
        <RefreshCw className="w-8 h-8 text-red-500 animate-spin" />
        <p className="text-slate-400 text-sm">Connecting to FastAPI Disaster Backend...</p>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 bg-slate-50 min-h-screen text-slate-900 font-sans">
      {/* CWC Header Banner */}
      <div className="bg-gradient-to-r from-indigo-900 via-blue-900 to-indigo-950 border border-indigo-800 rounded-2xl p-5 flex flex-col md:flex-row items-start md:items-center justify-between shadow-xl text-white gap-4">
        <div>
          <h2 className="text-xl font-black text-white flex items-center gap-2">
            <span>Disaster Response Overview</span>
            <span className="bg-amber-400 text-slate-950 text-xs px-3 py-0.5 rounded-full font-black uppercase shadow-sm">
              STATE OF EMERGENCY
            </span>
          </h2>
          <p className="text-xs text-indigo-100 mt-1 font-medium">
            Real-time monitoring of carrying capacity, hazard red zones, and evacuation relocation plans.
          </p>
        </div>

        <div className="flex gap-3">
          <button
            onClick={() => onNavigate("map")}
            className="flex items-center gap-2 bg-pink-600 hover:bg-pink-500 text-white text-xs font-extrabold px-4 py-2.5 rounded-xl shadow-md border border-pink-500 transition-all cursor-pointer"
          >
            <span>Open Hazard Map</span>
            <ArrowUpRight className="w-4 h-4" />
          </button>
          <button
            onClick={() => onNavigate("hospitals")}
            className="flex items-center gap-2 bg-pink-950 hover:bg-pink-900 text-amber-300 text-xs font-extrabold px-4 py-2.5 rounded-xl border border-pink-800 shadow-sm transition-all cursor-pointer"
          >
            <span>🏥 Hospitals</span>
          </button>
          <button
            onClick={() => onNavigate("relocation")}
            className="flex items-center gap-2 bg-white hover:bg-indigo-50 text-indigo-950 text-xs font-extrabold px-4 py-2.5 rounded-xl border border-indigo-200 shadow-sm transition-all cursor-pointer"
          >
            <span>Run Relocation Solver</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-800 text-xs flex items-center justify-between font-bold">
          <span>⚠️ {error}</span>
          <button onClick={loadData} className="underline text-red-900 font-black">Retry</button>
        </div>
      )}

      {/* Metric Cards - Clean White Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-8 gap-3">
        <div className="bg-white border border-slate-200 rounded-2xl p-3.5 flex flex-col justify-between shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-slate-600">Red Zones</span>
            <Flame className="w-4 h-4 text-red-600" />
          </div>
          <div className="mt-2">
            <span className="text-xl font-black text-red-600">{redZonesCount}</span>
            <span className="text-[9px] text-red-600 ml-1 font-extrabold">Critical</span>
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-3.5 flex flex-col justify-between shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-slate-600">Affected Humans</span>
            <Users className="w-4 h-4 text-amber-600" />
          </div>
          <div className="mt-2">
            <span className="text-xl font-black text-amber-600">{totalAffectedPop}</span>
            <span className="text-[9px] text-amber-700 ml-1 font-extrabold">Evacuating</span>
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-3.5 flex flex-col justify-between shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-slate-600">Hospitals</span>
            <span className="text-sm">🏥</span>
          </div>
          <div className="mt-2">
            <span className="text-xl font-black text-pink-700">OPEN</span>
            <span className="text-[9px] text-slate-500 ml-1 font-bold">Capacity Ready</span>
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-3.5 flex flex-col justify-between shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-slate-600">Shelter Beds</span>
            <Home className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="mt-2">
            <span className="text-xl font-black text-emerald-700">{availCapacity}</span>
            <span className="text-[9px] text-slate-500 ml-1 font-bold">/ {maxCapacity}</span>
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-3.5 flex flex-col justify-between shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-slate-600">Animal Rescue</span>
            <span className="text-sm">🐕</span>
          </div>
          <div className="mt-2">
            <span className="text-xl font-black text-pink-600">120</span>
            <span className="text-[9px] text-pink-700 ml-1 font-extrabold">At Risk</span>
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-3.5 flex flex-col justify-between shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-slate-600">Broadcasts</span>
            <Bell className="w-4 h-4 text-indigo-600" />
          </div>
          <div className="mt-2">
            <span className="text-xl font-black text-indigo-600">4</span>
            <span className="text-[9px] text-indigo-700 ml-1 font-extrabold">Multi-Channel</span>
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-3.5 flex flex-col justify-between shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-slate-600">Active Alerts</span>
            <AlertTriangle className="w-4 h-4 text-rose-600" />
          </div>
          <div className="mt-2">
            <span className="text-xl font-black text-rose-600">3</span>
            <span className="text-[9px] text-rose-700 ml-1 font-extrabold">SOS Ready</span>
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-3.5 flex flex-col justify-between shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-slate-600">AI Assistant</span>
            <span className="text-sm">🤖</span>
          </div>
          <div className="mt-2">
            <button onClick={() => onNavigate("ai-assistant")} className="text-xs font-black text-pink-600 hover:underline">
              Launch AI →
            </button>
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-3.5 flex flex-col justify-between shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-slate-600">Offline PWA</span>
            <span className="text-sm">📡</span>
          </div>
          <div className="mt-2">
            <span className="text-xs font-black text-emerald-600">ACTIVE</span>
            <span className="text-[9px] text-slate-500 block">Cached</span>
          </div>
        </div>
      </div>


      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-md">
          <h3 className="text-xs font-black text-indigo-950 uppercase tracking-wider mb-4 flex items-center justify-between">
            <span>Hazard Risk Distribution</span>
            <TrendingUp className="w-4 h-4 text-indigo-600" />
          </h3>
          <div className="h-56 flex items-center justify-center">
            <Doughnut data={riskDistributionData} options={{ responsive: true, maintainAspectRatio: false }} />
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-md lg:col-span-2">
          <h3 className="text-xs font-black text-indigo-950 uppercase tracking-wider mb-4 flex items-center justify-between">
            <span>Shelter Occupancy & Capacity Status</span>
            <button onClick={() => onNavigate("capacity")} className="text-xs text-pink-600 hover:underline font-extrabold">
              View Detailed Metrics →
            </button>
          </h3>
          <div className="h-56">
            <Bar
              data={shelterOccupancyChartData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                scales: { x: { stacked: true }, y: { stacked: true } },
              }}
            />
          </div>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-md">
        <h3 className="text-xs font-black text-indigo-950 uppercase tracking-wider mb-4">
          24-Hour Rainfall Intensity Trend (Station Hydrograph)
        </h3>
        <div className="h-48">
          <Line data={rainfallTrendData} options={{ responsive: true, maintainAspectRatio: false }} />
        </div>
      </div>
    </div>
  );
};
