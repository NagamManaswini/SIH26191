import React, { useEffect, useState } from "react";
import { Bed, HeartPulse, AlertCircle, Save, CheckCircle, AlertTriangle, RefreshCw } from "lucide-react";
import { api } from "../api/apiClient";
import { UserAuth } from "./LoginPage";

interface HospitalCapacityPageProps {
  user: UserAuth;
}

export const HospitalCapacityPage: React.FC<HospitalCapacityPageProps> = ({ user }) => {
  const [capacity, setCapacity] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    total_beds: 0, occupied_beds: 0,
    total_icu: 0, occupied_icu: 0,
    total_emergency_beds: 0, occupied_emergency_beds: 0,
    isolation_beds: 0,
    total_ambulances: 0, available_ambulances: 0,
  });

  const loadCapacity = async () => {
    setLoading(true);
    try {
      const cap = await api.hospitalGetCapacity();
      setCapacity(cap);
      setForm({
        total_beds: cap.total_beds, occupied_beds: cap.occupied_beds,
        total_icu: cap.total_icu, occupied_icu: cap.occupied_icu,
        total_emergency_beds: cap.total_emergency_beds, occupied_emergency_beds: cap.occupied_emergency_beds,
        isolation_beds: cap.isolation_beds || 0,
        total_ambulances: cap.total_ambulances, available_ambulances: cap.available_ambulances,
      });
    } catch (e) {
      setError("Failed to load capacity data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadCapacity(); }, []);

  const handleChange = (field: string, val: number) => {
    setForm(f => ({ ...f, [field]: isNaN(val) ? 0 : Math.max(0, val) }));
    setError(null);
  };

  const validate = () => {
    if (form.occupied_beds > form.total_beds) return `Occupied beds (${form.occupied_beds}) cannot exceed total (${form.total_beds}).`;
    if (form.occupied_icu > form.total_icu) return `Occupied ICU (${form.occupied_icu}) cannot exceed total (${form.total_icu}).`;
    if (form.occupied_emergency_beds > form.total_emergency_beds) return `Occupied emergency (${form.occupied_emergency_beds}) cannot exceed total (${form.total_emergency_beds}).`;
    if (form.available_ambulances > form.total_ambulances) return `Available ambulances (${form.available_ambulances}) cannot exceed total (${form.total_ambulances}).`;
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const validationError = validate();
    if (validationError) { setError(validationError); return; }
    setSaving(true);
    setError(null);
    try {
      const updated = await api.hospitalUpdateCapacity(form);
      setCapacity(updated);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (e: any) {
      setError(e?.message || "Failed to update capacity.");
    } finally {
      setSaving(false);
    }
  };

  const avail = (total: number, occupied: number) => Math.max(0, total - occupied);

  const CapacityRow = ({ label, totalKey, occupiedKey, color }: { label: string; totalKey: string; occupiedKey: string; color: string }) => {
    const total = (form as any)[totalKey];
    const occupied = (form as any)[occupiedKey];
    const available = avail(total, occupied);
    const pct = total > 0 ? Math.round((occupied / total) * 100) : 0;
    const isOver = occupied > total;
    return (
      <div className={`bg-white border rounded-2xl p-5 ${isOver ? "border-red-300" : "border-slate-200"}`}>
        <h3 className="font-black text-sm text-slate-800 mb-4">{label}</h3>
        <div className="grid grid-cols-3 gap-3 mb-3">
          <div>
            <label className="block text-[10px] font-extrabold text-slate-500 uppercase tracking-wider mb-1.5">Total</label>
            <input
              type="number" min="0" value={total}
              onChange={e => handleChange(totalKey, parseInt(e.target.value))}
              className="w-full border border-slate-300 rounded-xl px-3 py-2.5 text-sm font-black text-slate-900 focus:outline-none focus:border-emerald-500 text-center"
            />
          </div>
          <div>
            <label className="block text-[10px] font-extrabold text-slate-500 uppercase tracking-wider mb-1.5">Occupied</label>
            <input
              type="number" min="0" max={total} value={occupied}
              onChange={e => handleChange(occupiedKey, parseInt(e.target.value))}
              className={`w-full border rounded-xl px-3 py-2.5 text-sm font-black text-slate-900 focus:outline-none text-center ${isOver ? "border-red-400 bg-red-50 focus:border-red-500" : "border-slate-300 focus:border-emerald-500"}`}
            />
          </div>
          <div>
            <label className="block text-[10px] font-extrabold text-slate-500 uppercase tracking-wider mb-1.5">Available</label>
            <div className={`flex items-center justify-center rounded-xl px-3 py-2.5 border ${
              available === 0 ? "bg-red-50 border-red-200 text-red-700" :
              available < total * 0.2 ? "bg-amber-50 border-amber-200 text-amber-700" :
              "bg-emerald-50 border-emerald-200 text-emerald-700"
            }`}>
              <span className="text-lg font-black">{available}</span>
            </div>
          </div>
        </div>
        <div className="mt-2">
          <div className="flex justify-between text-[10px] font-bold text-slate-500 mb-1">
            <span>Utilization</span>
            <span className={pct >= 90 ? "text-red-600" : pct >= 70 ? "text-amber-600" : "text-emerald-600"}>{pct}%</span>
          </div>
          <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
            <div className={`h-full rounded-full transition-all ${
              pct >= 90 ? "bg-red-500" : pct >= 70 ? "bg-amber-500" : "bg-emerald-500"
            }`} style={{ width: `${Math.min(100, pct)}%` }}></div>
          </div>
        </div>
        {isOver && (
          <p className="text-[10px] text-red-600 font-bold mt-1.5 flex items-center gap-1">
            <AlertTriangle className="w-3 h-3" /> Occupied cannot exceed total
          </p>
        )}
      </div>
    );
  };

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-8 h-8 border-4 border-emerald-600 border-t-transparent rounded-full animate-spin"></div>
    </div>
  );

  return (
    <div className="p-6 max-w-3xl mx-auto space-y-6 font-sans">
      <div className="flex items-center gap-4 mb-2">
        <div className="w-12 h-12 rounded-2xl bg-emerald-600 flex items-center justify-center shadow-lg">
          <Bed className="w-7 h-7 text-white" />
        </div>
        <div>
          <h1 className="text-xl font-black text-slate-900">Bed Capacity Management</h1>
          <p className="text-xs text-slate-500 font-medium">
            Last updated: {capacity?.updated_at ? new Date(capacity.updated_at).toLocaleString("en-IN") : "—"} by {capacity?.updated_by || "—"}
          </p>
        </div>
        <button onClick={loadCapacity} className="ml-auto p-2 text-slate-500 hover:text-emerald-600 hover:bg-emerald-50 rounded-xl transition-all">
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {saved && (
        <div className="flex items-center gap-2 p-3 bg-emerald-50 border border-emerald-300 rounded-xl text-emerald-800 text-xs font-bold">
          <CheckCircle className="w-4 h-4" /> Capacity updated successfully. Available counts recalculated.
        </div>
      )}
      {error && (
        <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-300 rounded-xl text-red-800 text-xs font-bold">
          <AlertTriangle className="w-4 h-4" /> {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <CapacityRow label="🛏️ General Beds" totalKey="total_beds" occupiedKey="occupied_beds" color="emerald" />
        <CapacityRow label="❤️ ICU Beds" totalKey="total_icu" occupiedKey="occupied_icu" color="blue" />
        <CapacityRow label="🚨 Emergency Beds" totalKey="total_emergency_beds" occupiedKey="occupied_emergency_beds" color="orange" />

        {/* Isolation + Ambulances */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-white border border-slate-200 rounded-2xl p-5">
            <h3 className="font-black text-sm text-slate-800 mb-4">🔵 Isolation Beds</h3>
            <div className="flex gap-3">
              <div className="flex-1">
                <label className="block text-[10px] font-extrabold text-slate-500 uppercase tracking-wider mb-1.5">Total</label>
                <input
                  type="number" min="0" value={form.isolation_beds}
                  onChange={e => handleChange("isolation_beds", parseInt(e.target.value))}
                  className="w-full border border-slate-300 rounded-xl px-3 py-2.5 text-sm font-black text-center focus:outline-none focus:border-emerald-500"
                />
              </div>
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-2xl p-5">
            <h3 className="font-black text-sm text-slate-800 mb-4">🚑 Ambulances</h3>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-[10px] font-extrabold text-slate-500 uppercase tracking-wider mb-1.5">Total</label>
                <input
                  type="number" min="0" value={form.total_ambulances}
                  onChange={e => handleChange("total_ambulances", parseInt(e.target.value))}
                  className="w-full border border-slate-300 rounded-xl px-3 py-2.5 text-sm font-black text-center focus:outline-none focus:border-emerald-500"
                />
              </div>
              <div>
                <label className="block text-[10px] font-extrabold text-slate-500 uppercase tracking-wider mb-1.5">Available</label>
                <input
                  type="number" min="0" max={form.total_ambulances} value={form.available_ambulances}
                  onChange={e => handleChange("available_ambulances", parseInt(e.target.value))}
                  className="w-full border border-slate-300 rounded-xl px-3 py-2.5 text-sm font-black text-center focus:outline-none focus:border-emerald-500"
                />
              </div>
            </div>
          </div>
        </div>

        <button
          type="submit"
          disabled={saving || !!validate()}
          className="w-full flex items-center justify-center gap-2 py-3.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-2xl text-sm font-black transition-all shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Save className="w-4 h-4" />
          {saving ? "Updating Capacity..." : "UPDATE CAPACITY"}
        </button>
      </form>

      <div className="flex items-start gap-2 p-3 bg-blue-50 border border-blue-200 rounded-xl text-blue-800 text-xs font-bold">
        <AlertCircle className="w-4 h-4 mt-0.5 shrink-0 text-blue-600" />
        <p>Available = Total − Occupied (calculated automatically). Occupied can never exceed Total. System will auto-update operational status when beds reach 0.</p>
      </div>
    </div>
  );
};
