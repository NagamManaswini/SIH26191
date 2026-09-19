import React, { useEffect, useState, useCallback } from "react";
import {
  HeartPulse, Ambulance, AlertCircle, CheckCircle2, XCircle, Clock,
  RefreshCw, MapPin, Building2, TrendingUp, Activity, Bed,
  Users, Stethoscope, ChevronRight, Bell, FileText, Wifi
} from "lucide-react";
import { api } from "../api/apiClient";
import { UserAuth } from "./LoginPage";

interface HospitalDashboardProps {
  user: UserAuth;
  onNavigate: (tab: string) => void;
}

const STATUS_COLORS: Record<string, string> = {
  OPEN: "bg-emerald-500",
  LIMITED: "bg-amber-500",
  FULL: "bg-red-500",
  EMERGENCY_ONLY: "bg-orange-500",
  CLOSED: "bg-slate-500",
};

const STATUS_TEXT: Record<string, string> = {
  OPEN: "🟢 OPEN",
  LIMITED: "🟡 LIMITED",
  FULL: "🔴 FULL",
  EMERGENCY_ONLY: "🟠 EMERGENCY ONLY",
  CLOSED: "⚫ CLOSED",
};

const PRIORITY_COLORS: Record<string, string> = {
  CRITICAL: "text-red-600 bg-red-50 border-red-200",
  HIGH: "text-orange-600 bg-orange-50 border-orange-200",
  MEDIUM: "text-amber-600 bg-amber-50 border-amber-200",
  LOW: "text-blue-600 bg-blue-50 border-blue-200",
};

export const HospitalDashboard: React.FC<HospitalDashboardProps> = ({ user, onNavigate }) => {
  const [hospital, setHospital] = useState<any>(null);
  const [capacity, setCapacity] = useState<any>(null);
  const [analytics, setAnalytics] = useState<any>(null);
  const [emergencyRequests, setEmergencyRequests] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const [updatingRequestId, setUpdatingRequestId] = useState<number | null>(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [hospData, capData, analyticsData, erData, alertData] = await Promise.allSettled([
        api.hospitalGetMe(),
        api.hospitalGetCapacity(),
        api.hospitalGetAnalytics(),
        api.hospitalGetEmergencyRequests(),
        api.hospitalGetAlerts(),
      ]);
      if (hospData.status === "fulfilled") setHospital(hospData.value);
      if (capData.status === "fulfilled") setCapacity(capData.value);
      if (analyticsData.status === "fulfilled") setAnalytics(analyticsData.value);
      if (erData.status === "fulfilled") setEmergencyRequests(erData.value || []);
      if (alertData.status === "fulfilled") setAlerts(alertData.value || []);
      setLastUpdated(new Date());
    } catch (e) {
      console.warn("Dashboard load error:", e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleERAction = async (requestId: number, newStatus: string) => {
    setUpdatingRequestId(requestId);
    try {
      await api.hospitalUpdateEmergencyRequest(requestId, { status: newStatus });
      await loadData();
    } catch (e) {
      console.warn("ER update failed:", e);
    } finally {
      setUpdatingRequestId(null);
    }
  };

  const operationalStatus = hospital?.operational_status || "OPEN";
  const pendingRequests = emergencyRequests.filter(r => r.status === "PENDING");
  const criticalAlerts = alerts.filter(a => a.severity === "CRITICAL" || a.severity === "HIGH");

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full min-h-screen bg-slate-50">
        <div className="flex flex-col items-center gap-4">
          <HeartPulse className="w-12 h-12 text-emerald-600 animate-pulse" />
          <p className="text-slate-600 font-bold text-sm">Loading Hospital Dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 p-6 space-y-6 font-sans">
      {/* ── Header ─────────────────────────────────────────────────────────── */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-emerald-600 flex items-center justify-center shadow-lg border border-emerald-400">
            <HeartPulse className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-slate-900">
              🏥 {hospital?.name || user.hospitalName || "Hospital Dashboard"}
            </h1>
            <div className="flex items-center gap-3 mt-1">
              <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-black text-white ${STATUS_COLORS[operationalStatus] || "bg-slate-500"}`}>
                {STATUS_TEXT[operationalStatus] || operationalStatus}
              </span>
              <span className="text-xs text-slate-500 font-medium">
                Last updated: {lastUpdated.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}
              </span>
            </div>
          </div>
        </div>
        <button
          onClick={loadData}
          className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-black transition-all shadow-md"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Refresh
        </button>
      </div>

      {/* ── Pending Emergency Alert Banner ──────────────────────────────────── */}
      {pendingRequests.length > 0 && (
        <div className="flex items-center gap-3 p-4 bg-red-50 border-2 border-red-300 rounded-2xl animate-pulse">
          <AlertCircle className="w-6 h-6 text-red-600 shrink-0" />
          <div className="flex-1">
            <p className="text-red-800 font-black text-sm">
              🚨 {pendingRequests.length} PENDING EMERGENCY REQUEST{pendingRequests.length > 1 ? "S" : ""} — IMMEDIATE REVIEW REQUIRED
            </p>
          </div>
          <button onClick={() => onNavigate("hospital-emergency")} className="px-3 py-1.5 bg-red-600 text-white rounded-lg text-xs font-black">
            Review Now →
          </button>
        </div>
      )}

      {/* ── Capacity Stats Grid ─────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          {
            label: "Total Beds",
            value: capacity?.total_beds ?? "—",
            sub: `${capacity?.available_beds ?? "—"} Available`,
            icon: Bed,
            pct: capacity ? Math.round((capacity.occupied_beds / Math.max(1, capacity.total_beds)) * 100) : 0,
            color: "emerald",
          },
          {
            label: "ICU Beds",
            value: capacity?.total_icu ?? "—",
            sub: `${capacity?.available_icu ?? "—"} Available`,
            icon: HeartPulse,
            pct: capacity ? Math.round((capacity.occupied_icu / Math.max(1, capacity.total_icu)) * 100) : 0,
            color: "blue",
          },
          {
            label: "Emergency Beds",
            value: capacity?.total_emergency_beds ?? "—",
            sub: `${capacity?.available_emergency_beds ?? "—"} Available`,
            icon: AlertCircle,
            pct: capacity ? Math.round((capacity.occupied_emergency_beds / Math.max(1, capacity.total_emergency_beds)) * 100) : 0,
            color: "orange",
          },
          {
            label: "Ambulances",
            value: capacity?.total_ambulances ?? "—",
            sub: `${capacity?.available_ambulances ?? "—"} Available`,
            icon: Ambulance,
            pct: capacity ? Math.round((capacity.available_ambulances / Math.max(1, capacity.total_ambulances)) * 100) : 0,
            color: "purple",
          },
        ].map((stat) => {
          const Icon = stat.icon;
          const colorMap: Record<string, string> = {
            emerald: "bg-emerald-50 border-emerald-200 text-emerald-700",
            blue: "bg-blue-50 border-blue-200 text-blue-700",
            orange: "bg-orange-50 border-orange-200 text-orange-700",
            purple: "bg-purple-50 border-purple-200 text-purple-700",
          };
          const barMap: Record<string, string> = {
            emerald: "bg-emerald-500",
            blue: "bg-blue-500",
            orange: "bg-orange-500",
            purple: "bg-purple-500",
          };
          return (
            <div key={stat.label} className={`rounded-2xl border p-4 ${colorMap[stat.color]} transition-all hover:shadow-md`}>
              <div className="flex items-center justify-between mb-2">
                <Icon className="w-5 h-5 opacity-70" />
                <span className="text-2xl font-black">{stat.value}</span>
              </div>
              <p className="text-xs font-black mb-0.5">{stat.label}</p>
              <p className="text-[10px] font-bold opacity-70">{stat.sub}</p>
              <div className="mt-2 h-1.5 bg-white/60 rounded-full overflow-hidden">
                <div className={`h-full ${barMap[stat.color]} rounded-full transition-all`} style={{ width: `${stat.pct}%` }}></div>
              </div>
              <p className="text-[10px] opacity-60 mt-0.5 font-bold">{stat.pct}% utilization</p>
            </div>
          );
        })}
      </div>

      {/* ── Main content 2-column ───────────────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left — Emergency Requests */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-black text-slate-800 flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-red-500" /> Emergency Requests
            </h2>
            <button onClick={() => onNavigate("hospital-emergency")} className="text-xs font-bold text-emerald-700 hover:text-emerald-600 flex items-center gap-1">
              View All <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {emergencyRequests.length === 0 ? (
            <div className="bg-white border border-slate-200 rounded-2xl p-8 text-center">
              <CheckCircle2 className="w-10 h-10 text-emerald-500 mx-auto mb-3" />
              <p className="text-slate-600 font-bold text-sm">No pending emergency requests</p>
              <p className="text-slate-400 text-xs mt-1">You will be notified when new requests arrive</p>
            </div>
          ) : (
            <div className="space-y-3">
              {emergencyRequests.slice(0, 4).map((req: any) => (
                <div key={req.id} className="bg-white border border-slate-200 rounded-2xl p-4 hover:border-emerald-300 transition-all shadow-sm">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs font-black text-slate-600">{req.request_code}</span>
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-black border ${PRIORITY_COLORS[req.priority] || "text-slate-600 bg-slate-50 border-slate-200"}`}>
                          {req.priority}
                        </span>
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-black ${
                          req.status === "PENDING" ? "bg-amber-100 text-amber-800" :
                          req.status === "ACCEPTED" ? "bg-emerald-100 text-emerald-800" :
                          req.status === "REJECTED" ? "bg-red-100 text-red-800" :
                          "bg-blue-100 text-blue-800"
                        }`}>{req.status}</span>
                      </div>
                      <p className="text-sm font-bold text-slate-900 truncate">📍 {req.location_name}</p>
                      <p className="text-xs text-slate-600 mt-0.5">
                        <span className="font-bold">{req.patients_count}</span> patients • {req.medical_requirement} •{" "}
                        <span className="font-bold">{req.distance_km?.toFixed(1)} km</span> •{" "}
                        ~{Math.round(req.estimated_arrival_minutes)} min ETA
                      </p>
                    </div>
                    {req.status === "PENDING" && (
                      <div className="flex gap-2 shrink-0">
                        <button
                          disabled={updatingRequestId === req.id}
                          onClick={() => handleERAction(req.id, "ACCEPTED")}
                          className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-black transition-all disabled:opacity-50"
                        >
                          ACCEPT
                        </button>
                        <button
                          disabled={updatingRequestId === req.id}
                          onClick={() => handleERAction(req.id, "REJECTED")}
                          className="px-3 py-1.5 bg-red-600 hover:bg-red-500 text-white rounded-lg text-xs font-black transition-all disabled:opacity-50"
                        >
                          REJECT
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Analytics */}
          {analytics && (
            <div className="bg-white border border-slate-200 rounded-2xl p-5">
              <h3 className="font-black text-sm text-slate-800 mb-4 flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-emerald-600" /> Today's Analytics
              </h3>
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="text-center p-3 bg-slate-50 rounded-xl">
                  <p className="text-2xl font-black text-emerald-700">{analytics.total_emergency_requests_today}</p>
                  <p className="text-xs font-bold text-slate-500 mt-0.5">Total ER Requests</p>
                </div>
                <div className="text-center p-3 bg-slate-50 rounded-xl">
                  <p className="text-2xl font-black text-blue-700">{analytics.active_patients}</p>
                  <p className="text-xs font-bold text-slate-500 mt-0.5">Active Patients</p>
                </div>
              </div>
              <div className="space-y-3">
                {[
                  { label: "Bed Utilization", pct: analytics.bed_utilization_pct, color: "bg-emerald-500" },
                  { label: "ICU Utilization", pct: analytics.icu_utilization_pct, color: "bg-blue-500" },
                  { label: "Emergency Bed Utilization", pct: analytics.emergency_utilization_pct, color: "bg-orange-500" },
                  { label: "Ambulance Availability", pct: analytics.ambulance_availability_pct, color: "bg-purple-500" },
                ].map((m) => (
                  <div key={m.label}>
                    <div className="flex justify-between text-xs font-bold text-slate-600 mb-1">
                      <span>{m.label}</span>
                      <span>{m.pct}%</span>
                    </div>
                    <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                      <div className={`h-full ${m.color} rounded-full transition-all`} style={{ width: `${m.pct}%` }}></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right — Quick Actions + Alerts */}
        <div className="space-y-4">
          {/* Quick Actions */}
          <div className="bg-white border border-slate-200 rounded-2xl p-5">
            <h3 className="font-black text-sm text-slate-800 mb-4">Quick Actions</h3>
            <div className="space-y-2">
              {[
                { label: "Update Capacity", tab: "hospital-capacity", icon: Bed, color: "bg-emerald-600 hover:bg-emerald-500" },
                { label: "Emergency Requests", tab: "hospital-emergency", icon: AlertCircle, color: "bg-red-600 hover:bg-red-500" },
                { label: "Ambulances", tab: "hospital-ambulances", icon: Ambulance, color: "bg-purple-600 hover:bg-purple-500" },
                { label: "Open Map", tab: "map", icon: MapPin, color: "bg-blue-600 hover:bg-blue-500" },
                { label: "Patients", tab: "hospital-patients", icon: Users, color: "bg-amber-600 hover:bg-amber-500" },
                { label: "Hospital Profile", tab: "hospital-profile", icon: Building2, color: "bg-slate-600 hover:bg-slate-500" },
              ].map(({ label, tab, icon: Icon, color }) => (
                <button
                  key={tab}
                  onClick={() => onNavigate(tab)}
                  className={`w-full flex items-center gap-3 px-4 py-3 ${color} text-white rounded-xl text-xs font-black transition-all shadow-sm`}
                >
                  <Icon className="w-4 h-4" />
                  {label}
                  <ChevronRight className="w-3.5 h-3.5 ml-auto" />
                </button>
              ))}
            </div>
          </div>

          {/* Active Alerts */}
          <div className="bg-white border border-slate-200 rounded-2xl p-5">
            <h3 className="font-black text-sm text-slate-800 mb-4 flex items-center gap-2">
              <Bell className="w-4 h-4 text-red-500" /> Active Alerts
              {criticalAlerts.length > 0 && (
                <span className="ml-auto bg-red-500 text-white text-[9px] px-1.5 py-0.5 rounded font-black animate-pulse">
                  {criticalAlerts.length} CRITICAL
                </span>
              )}
            </h3>
            {alerts.length === 0 ? (
              <p className="text-xs text-slate-400 font-bold text-center py-4">No active alerts</p>
            ) : (
              <div className="space-y-2">
                {alerts.slice(0, 4).map((alert: any) => (
                  <div key={alert.id} className={`p-3 rounded-xl border text-xs ${
                    alert.severity === "CRITICAL" ? "bg-red-50 border-red-200" :
                    alert.severity === "HIGH" ? "bg-orange-50 border-orange-200" :
                    alert.severity === "WARNING" ? "bg-amber-50 border-amber-200" :
                    "bg-blue-50 border-blue-200"
                  }`}>
                    <p className="font-black text-slate-800 truncate">{alert.title}</p>
                    <p className="text-slate-500 mt-0.5 text-[10px]">{alert.affected_area}</p>
                  </div>
                ))}
              </div>
            )}
            <button onClick={() => onNavigate("hospital-alerts")} className="mt-3 text-xs font-bold text-emerald-700 hover:text-emerald-600">
              View all alerts →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
