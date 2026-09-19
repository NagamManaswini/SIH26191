import React, { useEffect, useState, useCallback } from "react";
import { AlertCircle, CheckCircle, XCircle, Clock, MapPin, Users, Ambulance, RefreshCw, ChevronDown, Filter } from "lucide-react";
import { api } from "../api/apiClient";
import { UserAuth } from "./LoginPage";

interface HospitalEmergencyPageProps {
  user: UserAuth;
}

const PRIORITY_STYLES: Record<string, string> = {
  CRITICAL: "bg-red-100 text-red-800 border-red-300",
  HIGH: "bg-orange-100 text-orange-800 border-orange-300",
  MEDIUM: "bg-amber-100 text-amber-800 border-amber-300",
  LOW: "bg-blue-100 text-blue-800 border-blue-300",
};

const STATUS_STYLES: Record<string, string> = {
  PENDING: "bg-amber-100 text-amber-800",
  ACCEPTED: "bg-emerald-100 text-emerald-800",
  REJECTED: "bg-red-100 text-red-800",
  IN_PROGRESS: "bg-blue-100 text-blue-800",
  COMPLETED: "bg-slate-100 text-slate-700",
};

const STATUS_ICONS: Record<string, React.ReactNode> = {
  PENDING: <Clock className="w-3.5 h-3.5" />,
  ACCEPTED: <CheckCircle className="w-3.5 h-3.5" />,
  REJECTED: <XCircle className="w-3.5 h-3.5" />,
  IN_PROGRESS: <RefreshCw className="w-3.5 h-3.5 animate-spin" />,
  COMPLETED: <CheckCircle className="w-3.5 h-3.5" />,
};

export const HospitalEmergencyPage: React.FC<HospitalEmergencyPageProps> = ({ user }) => {
  const [requests, setRequests] = useState<any[]>([]);
  const [capacity, setCapacity] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [updatingId, setUpdatingId] = useState<number | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>("ALL");
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [reqs, cap] = await Promise.allSettled([
        api.hospitalGetEmergencyRequests(),
        api.hospitalGetCapacity(),
      ]);
      if (reqs.status === "fulfilled") setRequests(reqs.value || []);
      if (cap.status === "fulfilled") setCapacity(cap.value);
    } catch (e) {
      setError("Failed to load emergency requests.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  const handleAction = async (id: number, status: string) => {
    setUpdatingId(id);
    setError(null);
    try {
      await api.hospitalUpdateEmergencyRequest(id, { status });
      await loadData();
    } catch (e) {
      setError("Failed to update request status.");
    } finally {
      setUpdatingId(null);
    }
  };

  const filtered = filterStatus === "ALL" ? requests : requests.filter(r => r.status === filterStatus);
  const pending = requests.filter(r => r.status === "PENDING");
  const accepted = requests.filter(r => r.status === "ACCEPTED");

  const getCapacityWarning = (patientsCount: number) => {
    if (!capacity) return null;
    const avail = capacity.available_emergency_beds;
    if (avail === 0) return { type: "error", msg: `🔴 INSUFFICIENT CAPACITY — No emergency beds available` };
    if (avail < patientsCount) return { type: "warning", msg: `🟡 LIMITED CAPACITY — Only ${avail} emergency beds available for ${patientsCount} patients` };
    return { type: "ok", msg: `🟢 CAPACITY AVAILABLE — ${avail} emergency beds for ${patientsCount} patients` };
  };

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-8 h-8 border-4 border-emerald-600 border-t-transparent rounded-full animate-spin"></div>
    </div>
  );

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6 font-sans">
      <div className="flex items-center gap-4">
        <div className="w-12 h-12 rounded-2xl bg-red-600 flex items-center justify-center shadow-lg">
          <AlertCircle className="w-7 h-7 text-white" />
        </div>
        <div>
          <h1 className="text-xl font-black text-slate-900">Emergency Requests</h1>
          <p className="text-xs text-slate-500 font-medium">Incoming emergency requests from disaster zones</p>
        </div>
        <button onClick={loadData} className="ml-auto flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-black transition-all">
          <RefreshCw className="w-3.5 h-3.5" /> Refresh
        </button>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: "Pending", count: pending.length, color: "bg-amber-50 border-amber-200 text-amber-800" },
          { label: "Accepted", count: accepted.length, color: "bg-emerald-50 border-emerald-200 text-emerald-800" },
          { label: "Total Today", count: requests.length, color: "bg-blue-50 border-blue-200 text-blue-800" },
        ].map(s => (
          <div key={s.label} className={`${s.color} border rounded-2xl p-4 text-center`}>
            <p className="text-3xl font-black">{s.count}</p>
            <p className="text-xs font-extrabold uppercase tracking-wider mt-1 opacity-70">{s.label}</p>
          </div>
        ))}
      </div>

      {error && (
        <div className="p-3 bg-red-50 border border-red-300 rounded-xl text-red-800 text-xs font-bold">{error}</div>
      )}

      {/* Filter */}
      <div className="flex items-center gap-2 flex-wrap">
        <Filter className="w-4 h-4 text-slate-400" />
        {["ALL", "PENDING", "ACCEPTED", "REJECTED", "IN_PROGRESS", "COMPLETED"].map(s => (
          <button
            key={s}
            onClick={() => setFilterStatus(s)}
            className={`px-3 py-1.5 rounded-lg text-[10px] font-black transition-all ${
              filterStatus === s ? "bg-slate-900 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
          >{s}</button>
        ))}
      </div>

      {/* Request cards */}
      {filtered.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-2xl p-12 text-center">
          <CheckCircle className="w-12 h-12 text-emerald-500 mx-auto mb-3" />
          <p className="text-slate-600 font-bold">No {filterStatus !== "ALL" ? filterStatus.toLowerCase() : ""} emergency requests</p>
        </div>
      ) : (
        <div className="space-y-4">
          {filtered.map((req: any) => {
            const warning = req.status === "PENDING" ? getCapacityWarning(req.patients_count) : null;
            return (
              <div key={req.id} className={`bg-white border-2 rounded-2xl overflow-hidden shadow-sm transition-all ${
                req.status === "PENDING" ? "border-amber-300" :
                req.status === "ACCEPTED" ? "border-emerald-300" :
                req.status === "REJECTED" ? "border-red-200" :
                "border-slate-200"
              }`}>
                {/* Request header */}
                <div className={`px-5 py-3 flex items-center justify-between ${
                  req.status === "PENDING" ? "bg-amber-50" : req.status === "ACCEPTED" ? "bg-emerald-50" : "bg-slate-50"
                }`}>
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-black text-slate-700">{req.request_code}</span>
                    <span className={`flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-black border ${PRIORITY_STYLES[req.priority] || "bg-slate-100 text-slate-700 border-slate-300"}`}>
                      {req.priority}
                    </span>
                    <span className={`flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-black ${STATUS_STYLES[req.status] || ""}`}>
                      {STATUS_ICONS[req.status]} {req.status}
                    </span>
                  </div>
                  <span className="text-[10px] text-slate-400 font-bold">
                    {req.created_at ? new Date(req.created_at).toLocaleString("en-IN") : ""}
                  </span>
                </div>

                <div className="p-5">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div>
                      <p className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">Location</p>
                      <p className="text-sm font-bold text-slate-800 flex items-center gap-1 mt-0.5">
                        <MapPin className="w-3.5 h-3.5 text-slate-400" /> {req.location_name}
                      </p>
                    </div>
                    <div>
                      <p className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">Patients</p>
                      <p className="text-sm font-bold text-slate-800 flex items-center gap-1 mt-0.5">
                        <Users className="w-3.5 h-3.5 text-slate-400" /> {req.patients_count}
                      </p>
                    </div>
                    <div>
                      <p className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">Distance</p>
                      <p className="text-sm font-bold text-slate-800 mt-0.5">{req.distance_km?.toFixed(1)} km</p>
                    </div>
                    <div>
                      <p className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">ETA</p>
                      <p className="text-sm font-bold text-slate-800 mt-0.5">~{Math.round(req.estimated_arrival_minutes)} min</p>
                    </div>
                  </div>

                  <div className="mb-4">
                    <p className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">Requirement</p>
                    <p className="text-sm font-bold text-slate-800 mt-0.5">{req.medical_requirement}</p>
                  </div>

                  {/* Capacity warning for pending requests */}
                  {warning && (
                    <div className={`flex items-center gap-2 p-3 rounded-xl border mb-4 text-xs font-bold ${
                      warning.type === "ok" ? "bg-emerald-50 border-emerald-200 text-emerald-800" :
                      warning.type === "warning" ? "bg-amber-50 border-amber-200 text-amber-800" :
                      "bg-red-50 border-red-200 text-red-800"
                    }`}>
                      {warning.msg}
                    </div>
                  )}

                  {/* Actions */}
                  {req.status === "PENDING" && (
                    <div className="flex gap-3">
                      <button
                        disabled={updatingId === req.id}
                        onClick={() => handleAction(req.id, "ACCEPTED")}
                        className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-black transition-all disabled:opacity-50 shadow-md"
                      >
                        <CheckCircle className="w-3.5 h-3.5" /> ACCEPT
                      </button>
                      <button
                        disabled={updatingId === req.id}
                        onClick={() => handleAction(req.id, "REJECTED")}
                        className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-xl text-xs font-black transition-all disabled:opacity-50 shadow-md"
                      >
                        <XCircle className="w-3.5 h-3.5" /> REJECT
                      </button>
                    </div>
                  )}
                  {req.status === "ACCEPTED" && (
                    <button
                      disabled={updatingId === req.id}
                      onClick={() => handleAction(req.id, "IN_PROGRESS")}
                      className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-black transition-all disabled:opacity-50"
                    >
                      <RefreshCw className="w-3.5 h-3.5" /> MARK IN PROGRESS
                    </button>
                  )}
                  {req.status === "IN_PROGRESS" && (
                    <button
                      disabled={updatingId === req.id}
                      onClick={() => handleAction(req.id, "COMPLETED")}
                      className="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-xl text-xs font-black transition-all disabled:opacity-50"
                    >
                      <CheckCircle className="w-3.5 h-3.5" /> MARK COMPLETED
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
