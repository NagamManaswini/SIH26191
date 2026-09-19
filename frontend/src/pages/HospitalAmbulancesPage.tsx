import React, { useEffect, useState, useCallback } from "react";
import { Ambulance, RefreshCw, Save, CheckCircle, AlertTriangle } from "lucide-react";
import { api } from "../api/apiClient";
import { UserAuth } from "./LoginPage";

interface HospitalAmbulancesPageProps { user: UserAuth; }

export const HospitalAmbulancesPage: React.FC<HospitalAmbulancesPageProps> = ({ user }) => {
  const [capacity, setCapacity] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string|null>(null);
  const [form, setForm] = useState({ total_ambulances: 0, available_ambulances: 0 });

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const cap = await api.hospitalGetCapacity();
      setCapacity(cap);
      setForm({ total_ambulances: cap.total_ambulances, available_ambulances: cap.available_ambulances });
    } catch(e) { setError("Failed to load ambulance data."); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (form.available_ambulances > form.total_ambulances) {
      setError(`Available (${form.available_ambulances}) cannot exceed total (${form.total_ambulances}).`);
      return;
    }
    setSaving(true);
    setError(null);
    try {
      const updated = await api.hospitalUpdateCapacity(form);
      setCapacity(updated);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch(e) { setError("Failed to update ambulance status."); }
    finally { setSaving(false); }
  };

  const available = form.available_ambulances;
  const busy = Math.max(0, form.total_ambulances - form.available_ambulances);
  const outOfService = 0; // Could be tracked separately in future

  if (loading) return <div className="flex items-center justify-center h-64"><div className="w-8 h-8 border-4 border-emerald-600 border-t-transparent rounded-full animate-spin"></div></div>;

  return (
    <div className="p-6 max-w-2xl mx-auto space-y-6 font-sans">
      <div className="flex items-center gap-4">
        <div className="w-12 h-12 rounded-2xl bg-purple-600 flex items-center justify-center shadow-lg">
          <Ambulance className="w-7 h-7 text-white" />
        </div>
        <div>
          <h1 className="text-xl font-black text-slate-900">Ambulance Management</h1>
          <p className="text-xs text-slate-500 font-medium">Manage your hospital fleet status</p>
        </div>
        <button onClick={loadData} className="ml-auto p-2 text-slate-500 hover:text-emerald-600 hover:bg-emerald-50 rounded-xl transition-all">
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {saved && <div className="flex items-center gap-2 p-3 bg-emerald-50 border border-emerald-300 rounded-xl text-emerald-800 text-xs font-bold"><CheckCircle className="w-4 h-4" /> Ambulance status updated successfully.</div>}
      {error && <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-300 rounded-xl text-red-800 text-xs font-bold"><AlertTriangle className="w-4 h-4" /> {error}</div>}

      {/* Status display */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
        <h3 className="font-black text-base text-slate-800 mb-5">Fleet Status</h3>
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="text-center p-4 bg-emerald-50 border border-emerald-200 rounded-2xl">
            <p className="text-4xl font-black text-emerald-700">{available}</p>
            <p className="text-xs font-black text-emerald-600 mt-1">🟢 AVAILABLE</p>
          </div>
          <div className="text-center p-4 bg-amber-50 border border-amber-200 rounded-2xl">
            <p className="text-4xl font-black text-amber-700">{busy}</p>
            <p className="text-xs font-black text-amber-600 mt-1">🟠 BUSY</p>
          </div>
          <div className="text-center p-4 bg-slate-50 border border-slate-200 rounded-2xl">
            <p className="text-4xl font-black text-slate-700">{form.total_ambulances}</p>
            <p className="text-xs font-black text-slate-600 mt-1">TOTAL FLEET</p>
          </div>
        </div>

        {/* Utilization bar */}
        <div>
          <div className="flex justify-between text-xs font-bold text-slate-500 mb-1">
            <span>Availability</span>
            <span className="text-emerald-600">{form.total_ambulances > 0 ? Math.round((available/form.total_ambulances)*100) : 0}% available</span>
          </div>
          <div className="h-3 bg-slate-100 rounded-full overflow-hidden flex gap-0.5">
            {available > 0 && <div className="h-full bg-emerald-500 rounded-full transition-all" style={{width:`${(available/Math.max(1,form.total_ambulances))*100}%`}}></div>}
            {busy > 0 && <div className="h-full bg-amber-500 transition-all" style={{width:`${(busy/Math.max(1,form.total_ambulances))*100}%`}}></div>}
          </div>
        </div>
      </div>

      {/* Update form */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
        <h3 className="font-black text-base text-slate-800 mb-5">Update Status</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1.5">Total Ambulances</label>
              <input
                type="number" min="0" value={form.total_ambulances}
                onChange={e=>setForm(f=>({...f,total_ambulances:Math.max(0,parseInt(e.target.value)||0)}))}
                className="w-full border border-slate-300 rounded-xl px-3 py-2.5 text-lg font-black text-center text-slate-900 focus:outline-none focus:border-emerald-500"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1.5">Available Ambulances</label>
              <input
                type="number" min="0" max={form.total_ambulances} value={form.available_ambulances}
                onChange={e=>setForm(f=>({...f,available_ambulances:Math.max(0,parseInt(e.target.value)||0)}))}
                className="w-full border border-slate-300 rounded-xl px-3 py-2.5 text-lg font-black text-center text-slate-900 focus:outline-none focus:border-emerald-500"
              />
            </div>
          </div>
          <p className="text-xs text-slate-500 font-bold">
            Busy = Total ({form.total_ambulances}) − Available ({form.available_ambulances}) = {Math.max(0,form.total_ambulances-form.available_ambulances)}
          </p>
          <button
            type="submit"
            disabled={saving}
            className="w-full flex items-center justify-center gap-2 py-3 bg-purple-600 hover:bg-purple-500 text-white rounded-xl text-sm font-black transition-all disabled:opacity-50"
          >
            <Save className="w-4 h-4" /> {saving ? "Updating..." : "UPDATE STATUS"}
          </button>
        </form>
      </div>
    </div>
  );
};
