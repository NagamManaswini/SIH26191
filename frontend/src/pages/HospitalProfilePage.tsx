import React, { useEffect, useState } from "react";
import { Building2, MapPin, Phone, Stethoscope, Edit3, Save, X, CheckCircle, ShieldCheck } from "lucide-react";
import { api } from "../api/apiClient";
import { UserAuth } from "./LoginPage";

interface HospitalProfilePageProps {
  user: UserAuth;
}

const SPECIALIZATION_OPTIONS = [
  "Trauma", "Emergency Medicine", "General Medicine", "Surgery",
  "Orthopedics", "Cardiology", "Neurology", "Pediatrics",
  "Obstetrics & Gynecology", "ICU", "Burns", "Oncology",
];

export const HospitalProfilePage: React.FC<HospitalProfilePageProps> = ({ user }) => {
  const [hospital, setHospital] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ phone: "", specialization: "" });

  const loadProfile = async () => {
    setLoading(true);
    try {
      const data = await api.hospitalGetMe();
      setHospital(data);
      setForm({ phone: data.phone || "", specialization: data.specialization || "" });
    } catch (e) {
      setError("Failed to load hospital profile.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadProfile(); }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const updated = await api.hospitalUpdateProfile({ phone: form.phone, specialization: form.specialization });
      setHospital(updated);
      setEditing(false);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (e) {
      setError("Failed to save profile. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-8 h-8 border-4 border-emerald-600 border-t-transparent rounded-full animate-spin"></div>
    </div>
  );

  const specs = (hospital?.specialization || "").split(",").map((s: string) => s.trim()).filter(Boolean);

  return (
    <div className="p-6 max-w-3xl mx-auto space-y-6 font-sans">
      <div className="flex items-center gap-4 mb-2">
        <div className="w-12 h-12 rounded-2xl bg-emerald-600 flex items-center justify-center shadow-lg">
          <Building2 className="w-7 h-7 text-white" />
        </div>
        <div>
          <h1 className="text-xl font-black text-slate-900">Hospital Profile</h1>
          <p className="text-xs text-slate-500 font-medium">View and manage your hospital's information</p>
        </div>
        {!editing && (
          <button onClick={() => setEditing(true)} className="ml-auto flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-black transition-all">
            <Edit3 className="w-3.5 h-3.5" /> Edit Profile
          </button>
        )}
      </div>

      {saved && (
        <div className="flex items-center gap-2 p-3 bg-emerald-50 border border-emerald-300 rounded-xl text-emerald-800 text-xs font-bold">
          <CheckCircle className="w-4 h-4" /> Profile updated successfully.
        </div>
      )}
      {error && (
        <div className="p-3 bg-red-50 border border-red-300 rounded-xl text-red-800 text-xs font-bold">{error}</div>
      )}

      <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm">
        {/* Header band */}
        <div className="bg-gradient-to-r from-emerald-700 to-emerald-900 p-6">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-xl font-black text-white">{hospital?.name}</h2>
              <p className="text-emerald-200 text-sm font-bold mt-0.5">{hospital?.type} Hospital</p>
            </div>
            <div className={`px-3 py-1.5 rounded-xl text-xs font-black ${
              hospital?.operational_status === "OPEN" ? "bg-emerald-400 text-emerald-950" :
              hospital?.operational_status === "FULL" ? "bg-red-400 text-red-950" :
              "bg-amber-400 text-amber-950"
            }`}>
              {hospital?.operational_status === "OPEN" ? "🟢" : hospital?.operational_status === "FULL" ? "🔴" : "🟡"} {hospital?.operational_status}
            </div>
          </div>
        </div>

        <div className="p-6 space-y-5">
          {/* Read-only fields */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { label: "Hospital ID", value: hospital?.hospital_id, locked: true },
              { label: "Hospital Type", value: hospital?.type, locked: true },
              { label: "District", value: hospital?.district, locked: true },
              { label: "State", value: hospital?.state, locked: true },
            ].map(({ label, value, locked }) => (
              <div key={label} className={`p-3 rounded-xl border ${locked ? "bg-slate-50 border-slate-200" : "bg-white border-slate-300"}`}>
                <p className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider mb-1">
                  {label} {locked && <span className="text-slate-300">🔒</span>}
                </p>
                <p className="text-sm font-bold text-slate-800">{value || "—"}</p>
              </div>
            ))}
          </div>

          <div className="p-3 rounded-xl border bg-slate-50 border-slate-200">
            <p className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider mb-1">
              Address 🔒
            </p>
            <div className="flex items-center gap-2">
              <MapPin className="w-4 h-4 text-slate-400" />
              <p className="text-sm font-bold text-slate-800">{hospital?.address || "—"}</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="p-3 rounded-xl border bg-slate-50 border-slate-200">
              <p className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider mb-1">Latitude 🔒</p>
              <p className="text-sm font-mono font-bold text-slate-800">{hospital?.latitude?.toFixed(6)}</p>
            </div>
            <div className="p-3 rounded-xl border bg-slate-50 border-slate-200">
              <p className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider mb-1">Longitude 🔒</p>
              <p className="text-sm font-mono font-bold text-slate-800">{hospital?.longitude?.toFixed(6)}</p>
            </div>
          </div>

          {/* Editable fields */}
          {editing ? (
            <form onSubmit={handleSave} className="space-y-4 pt-2 border-t border-slate-200">
              <p className="text-xs font-extrabold text-emerald-700 uppercase tracking-wider">Editable Fields</p>
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">Phone Number</label>
                <input
                  value={form.phone}
                  onChange={e => setForm(f => ({ ...f, phone: e.target.value }))}
                  className="w-full border border-slate-300 rounded-xl px-3 py-2.5 text-sm font-bold text-slate-800 focus:outline-none focus:border-emerald-500"
                  placeholder="+91-XXXXXXXXXX"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">Specializations (comma-separated)</label>
                <input
                  value={form.specialization}
                  onChange={e => setForm(f => ({ ...f, specialization: e.target.value }))}
                  className="w-full border border-slate-300 rounded-xl px-3 py-2.5 text-sm font-bold text-slate-800 focus:outline-none focus:border-emerald-500"
                  placeholder="Trauma, Emergency Medicine, Surgery"
                />
                <p className="text-[10px] text-slate-400 mt-1 font-medium">Options: {SPECIALIZATION_OPTIONS.join(", ")}</p>
              </div>
              <div className="flex gap-3">
                <button type="submit" disabled={saving} className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-black transition-all disabled:opacity-50">
                  <Save className="w-3.5 h-3.5" /> {saving ? "Saving..." : "Save Changes"}
                </button>
                <button type="button" onClick={() => setEditing(false)} className="flex items-center gap-2 px-4 py-2 bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-xl text-xs font-black transition-all">
                  <X className="w-3.5 h-3.5" /> Cancel
                </button>
              </div>
            </form>
          ) : (
            <div className="space-y-4 pt-2 border-t border-slate-200">
              <p className="text-xs font-extrabold text-emerald-700 uppercase tracking-wider">Contact & Specializations</p>
              <div className="flex items-center gap-2 p-3 rounded-xl border border-slate-200 bg-white">
                <Phone className="w-4 h-4 text-slate-400" />
                <span className="text-sm font-bold text-slate-800">{hospital?.phone || "—"}</span>
              </div>
              <div className="p-3 rounded-xl border border-slate-200 bg-white">
                <p className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider mb-2">Specializations</p>
                <div className="flex flex-wrap gap-2">
                  {specs.length > 0 ? specs.map((s: string) => (
                    <span key={s} className="flex items-center gap-1 px-2 py-1 bg-emerald-50 border border-emerald-200 rounded-lg text-xs font-bold text-emerald-800">
                      <CheckCircle className="w-3 h-3" /> {s}
                    </span>
                  )) : <span className="text-xs text-slate-400 font-medium">No specializations listed</span>}
                </div>
              </div>
            </div>
          )}

          {/* Non-editable notice */}
          <div className="flex items-start gap-3 p-3 bg-amber-50 border border-amber-200 rounded-xl">
            <ShieldCheck className="w-4 h-4 text-amber-600 mt-0.5 shrink-0" />
            <p className="text-xs text-amber-800 font-bold">
              Fields marked 🔒 (Hospital ID, official location, type, verification status) can only be changed by system administrators.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
