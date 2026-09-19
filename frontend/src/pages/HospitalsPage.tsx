import React, { useEffect, useState } from "react";
import { api } from "../api/apiClient";
import { UserAuth } from "./LoginPage";
import { Building2, Activity, Edit, RefreshCw, ShieldAlert, Plus, CheckCircle, Clock, Truck, Stethoscope, Search, Layers } from "lucide-react";

interface HospitalsPageProps {
  user: UserAuth | null;
  currentLocation?: { name: string; lat: number; lon: number };
}

export const HospitalsPage: React.FC<HospitalsPageProps> = ({ user, currentLocation }) => {
  const isAdmin = user?.role === "admin" || user?.role === "responder";

  const [hospitals, setHospitals] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedType, setSelectedType] = useState<string>("ALL");
  const [selectedStatus, setSelectedStatus] = useState<string>("ALL");

  // Capacity Edit Modal State
  const [editingHospital, setEditingHospital] = useState<any | null>(null);
  const [editCapForm, setEditCapForm] = useState({
    total_beds: 100,
    occupied_beds: 0,
    total_icu: 20,
    occupied_icu: 0,
    total_emergency_beds: 30,
    occupied_emergency_beds: 0,
    total_ambulances: 5,
    available_ambulances: 5,
    operational_status: "OPEN",
  });
  const [saving, setSaving] = useState<boolean>(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  // Audit Logs State
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [selectedAuditHospital, setSelectedAuditHospital] = useState<any | null>(null);

  const fetchHospitalsData = async () => {
    setLoading(true);
    try {
      const data = await api.getHospitals();
      setHospitals(data || []);
    } catch (e) {
      console.warn("Failed to load hospitals:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHospitalsData();
  }, []);

  const openEditModal = (hospital: any) => {
    const cap = hospital.capacity || {};
    setEditingHospital(hospital);
    setSaveError(null);
    setEditCapForm({
      total_beds: cap.total_beds || 100,
      occupied_beds: cap.occupied_beds || 0,
      total_icu: cap.total_icu || 20,
      occupied_icu: cap.occupied_icu || 0,
      total_emergency_beds: cap.total_emergency_beds || 30,
      occupied_emergency_beds: cap.occupied_emergency_beds || 0,
      total_ambulances: cap.total_ambulances || 5,
      available_ambulances: cap.available_ambulances !== undefined ? cap.available_ambulances : 5,
      operational_status: hospital.operational_status || "OPEN",
    });
  };

  const handleSaveCapacity = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingHospital) return;

    if (editCapForm.occupied_beds > editCapForm.total_beds) {
      setSaveError(`Occupied beds (${editCapForm.occupied_beds}) cannot exceed total beds (${editCapForm.total_beds}).`);
      return;
    }
    if (editCapForm.occupied_icu > editCapForm.total_icu) {
      setSaveError(`Occupied ICU beds (${editCapForm.occupied_icu}) cannot exceed total ICU beds (${editCapForm.total_icu}).`);
      return;
    }
    if (editCapForm.occupied_emergency_beds > editCapForm.total_emergency_beds) {
      setSaveError(`Occupied emergency beds (${editCapForm.occupied_emergency_beds}) cannot exceed total emergency beds (${editCapForm.total_emergency_beds}).`);
      return;
    }

    setSaving(true);
    setSaveError(null);

    try {
      // 1. Update hospital operational status if changed
      if (editCapForm.operational_status !== editingHospital.operational_status) {
        await api.updateHospital(editingHospital.id, {
          operational_status: editCapForm.operational_status,
          emergency_status: editCapForm.operational_status,
          updated_by: user?.name || "Admin",
        });
      }

      // 2. Update hospital capacity
      await api.updateHospitalCapacity(editingHospital.id, {
        total_beds: editCapForm.total_beds,
        occupied_beds: editCapForm.occupied_beds,
        total_icu: editCapForm.total_icu,
        occupied_icu: editCapForm.occupied_icu,
        total_emergency_beds: editCapForm.total_emergency_beds,
        occupied_emergency_beds: editCapForm.occupied_emergency_beds,
        total_ambulances: editCapForm.total_ambulances,
        available_ambulances: editCapForm.available_ambulances,
        updated_by: user?.name || "Admin",
      });

      setEditingHospital(null);
      await fetchHospitalsData();
    } catch (err: any) {
      setSaveError(err.message || "Failed to update hospital capacity.");
    } finally {
      setSaving(false);
    }
  };

  const loadAuditHistory = async (hospital: any) => {
    setSelectedAuditHospital(hospital);
    try {
      const logs = await api.getHospitalUpdates(hospital.id);
      setAuditLogs(logs || []);
    } catch (e) {
      setAuditLogs([]);
    }
  };

  // Filtered Hospitals
  const filteredHospitals = hospitals.filter((h) => {
    const matchesSearch =
      h.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (h.district && h.district.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (h.type && h.type.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesType = selectedType === "ALL" || h.type === selectedType;
    const matchesStatus = selectedStatus === "ALL" || h.operational_status === selectedStatus;

    return matchesSearch && matchesType && matchesStatus;
  });

  // Calculate Overall Utilization Metrics
  let totalBedsSum = 0;
  let occupiedBedsSum = 0;
  let totalIcuSum = 0;
  let occupiedIcuSum = 0;
  let totalEmSum = 0;
  let occupiedEmSum = 0;
  let availableAmbulancesSum = 0;

  let openCount = 0;
  let limitedCount = 0;
  let fullCount = 0;
  let emergencyOnlyCount = 0;

  hospitals.forEach((h) => {
    if (h.operational_status === "OPEN") openCount++;
    else if (h.operational_status === "LIMITED") limitedCount++;
    else if (h.operational_status === "FULL") fullCount++;
    else if (h.operational_status === "EMERGENCY_ONLY") emergencyOnlyCount++;

    const cap = h.capacity;
    if (cap) {
      totalBedsSum += cap.total_beds || 0;
      occupiedBedsSum += cap.occupied_beds || 0;
      totalIcuSum += cap.total_icu || 0;
      occupiedIcuSum += cap.occupied_icu || 0;
      totalEmSum += cap.total_emergency_beds || 0;
      occupiedEmSum += cap.occupied_emergency_beds || 0;
      availableAmbulancesSum += cap.available_ambulances || 0;
    }
  });

  const bedUtilPct = totalBedsSum > 0 ? Math.round((occupiedBedsSum / totalBedsSum) * 100) : 0;
  const icuUtilPct = totalIcuSum > 0 ? Math.round((occupiedIcuSum / totalIcuSum) * 100) : 0;
  const emUtilPct = totalEmSum > 0 ? Math.round((occupiedEmSum / totalEmSum) * 100) : 0;

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6 font-sans text-slate-900">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gradient-to-r from-pink-950 via-slate-900 to-indigo-950 p-6 rounded-3xl text-white shadow-2xl">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Building2 className="w-7 h-7 text-pink-500" />
            <h1 className="text-xl font-extrabold tracking-wide">DYNAMIC HOSPITAL MANAGEMENT & EMERGENCY RESPONSE</h1>
          </div>
          <p className="text-xs text-slate-300">
            Real-time healthcare capacity tracking, bed availability, ICU metrics, and ambulance response coordination.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={fetchHospitalsData}
            className="px-4 py-2 rounded-2xl bg-white/10 hover:bg-white/20 text-white font-bold text-xs flex items-center gap-2 border border-white/20 transition-all cursor-pointer"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin text-pink-400" : ""}`} />
            Refresh Capacity Data
          </button>
        </div>
      </div>

      {/* Hospital Capacity Summary & Utilization Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white border border-slate-200 p-4 rounded-3xl shadow-md space-y-2">
          <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider block">Operational Facilities</span>
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-black text-indigo-950">{hospitals.length} Total</span>
            <span className="text-xs font-bold text-emerald-600">🟢 {openCount} OPEN</span>
          </div>
          <div className="flex gap-2 text-[10px] font-bold text-slate-500 pt-1 border-t border-slate-100">
            <span>🟡 Limited: {limitedCount}</span>
            <span>🔴 Full: {fullCount}</span>
            <span>🟠 Emerg: {emergencyOnlyCount}</span>
          </div>
        </div>

        <div className="bg-white border border-slate-200 p-4 rounded-3xl shadow-md space-y-2">
          <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider block">General Bed Utilization</span>
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-black text-indigo-950">{bedUtilPct}%</span>
            <span className="text-xs font-extrabold text-emerald-700">{totalBedsSum - occupiedBedsSum} Available</span>
          </div>
          <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
            <div className={`h-full ${bedUtilPct > 85 ? "bg-red-500" : bedUtilPct > 70 ? "bg-amber-500" : "bg-emerald-500"}`} style={{ width: `${bedUtilPct}%` }}></div>
          </div>
        </div>

        <div className="bg-white border border-slate-200 p-4 rounded-3xl shadow-md space-y-2">
          <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider block">ICU Capacity Utilization</span>
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-black text-purple-950">{icuUtilPct}%</span>
            <span className="text-xs font-extrabold text-purple-700">{totalIcuSum - occupiedIcuSum} Available</span>
          </div>
          <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
            <div className={`h-full ${icuUtilPct > 85 ? "bg-red-500" : "bg-purple-600"}`} style={{ width: `${icuUtilPct}%` }}></div>
          </div>
        </div>

        <div className="bg-white border border-slate-200 p-4 rounded-3xl shadow-md space-y-2">
          <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider block">Emergency Beds & Ambulances</span>
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-black text-red-700">{totalEmSum - occupiedEmSum} Beds</span>
            <span className="text-xs font-extrabold text-amber-700">🚑 {availableAmbulancesSum} Ambulances</span>
          </div>
          <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
            <div className={`h-full ${emUtilPct > 85 ? "bg-red-600" : "bg-red-500"}`} style={{ width: `${emUtilPct}%` }}></div>
          </div>
        </div>
      </div>

      {/* Search & Filter Toolbar */}
      <div className="bg-white border border-slate-200 p-4 rounded-3xl shadow-sm flex flex-col md:flex-row gap-3 items-center justify-between">
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            type="text"
            placeholder="Search by hospital name, district..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-2xl bg-slate-50 border border-slate-200 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-pink-500"
          />
        </div>

        <div className="flex items-center gap-2 w-full md:w-auto">
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="py-2 px-3 rounded-2xl bg-slate-50 border border-slate-200 text-xs font-extrabold text-slate-700 cursor-pointer"
          >
            <option value="ALL">All Hospital Types</option>
            <option value="Government">Government</option>
            <option value="Private">Private</option>
            <option value="Public Medical College">Public Medical College</option>
            <option value="District Hospital">District Hospital</option>
          </select>

          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="py-2 px-3 rounded-2xl bg-slate-50 border border-slate-200 text-xs font-extrabold text-slate-700 cursor-pointer"
          >
            <option value="ALL">All Operational Statuses</option>
            <option value="OPEN">🟢 OPEN</option>
            <option value="LIMITED">🟡 LIMITED</option>
            <option value="FULL">🔴 FULL</option>
            <option value="EMERGENCY_ONLY">🟠 EMERGENCY ONLY</option>
          </select>
        </div>
      </div>

      {/* Main Hospital Table */}
      <div className="bg-white border border-slate-200 rounded-3xl shadow-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-sans">
            <thead className="bg-slate-900 text-slate-300 font-extrabold uppercase tracking-wider text-[10px]">
              <tr>
                <th className="p-4">Hospital Name & Details</th>
                <th className="p-4">Status</th>
                <th className="p-4">General Beds</th>
                <th className="p-4">ICU Beds</th>
                <th className="p-4">Emergency Beds</th>
                <th className="p-4">Ambulances</th>
                <th className="p-4">Last Updated</th>
                <th className="p-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredHospitals.map((h) => {
                const cap = h.capacity;
                const avBeds = cap ? Math.max(0, cap.total_beds - cap.occupied_beds) : 0;
                const avIcu = cap ? Math.max(0, cap.total_icu - cap.occupied_icu) : 0;
                const avEm = cap ? Math.max(0, cap.total_emergency_beds - cap.occupied_emergency_beds) : 0;

                return (
                  <tr key={h.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="p-4">
                      <div className="font-extrabold text-indigo-950 text-sm">{h.name}</div>
                      <div className="text-[11px] text-slate-500 font-medium">{h.address || `${h.district}, ${h.state}`}</div>
                      <div className="text-[10px] text-pink-700 font-bold mt-0.5">{h.type} • {h.specialization || "General Trauma"}</div>
                    </td>

                    <td className="p-4">
                      <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-black border ${
                        h.operational_status === "OPEN"
                          ? "bg-emerald-50 text-emerald-800 border-emerald-300"
                          : h.operational_status === "LIMITED"
                          ? "bg-amber-50 text-amber-800 border-amber-300"
                          : h.operational_status === "FULL"
                          ? "bg-red-50 text-red-800 border-red-300"
                          : "bg-orange-50 text-orange-800 border-orange-300"
                      }`}>
                        {h.operational_status}
                      </span>
                    </td>

                    <td className="p-4">
                      {cap ? (
                        <div>
                          <span className="font-black text-slate-800">{avBeds} <span className="text-slate-400 font-normal">/ {cap.total_beds}</span></span>
                          <div className="w-20 bg-slate-100 h-1.5 rounded-full mt-1 overflow-hidden">
                            <div className="bg-indigo-600 h-full" style={{ width: `${Math.min(100, (cap.occupied_beds / maxVal(cap.total_beds)) * 100)}%` }}></div>
                          </div>
                        </div>
                      ) : (
                        <span className="text-slate-400 italic">N/A</span>
                      )}
                    </td>

                    <td className="p-4 font-bold">
                      {cap ? <span className="text-purple-700">{avIcu} / {cap.total_icu}</span> : <span className="text-slate-400 italic">N/A</span>}
                    </td>

                    <td className="p-4 font-bold">
                      {cap ? <span className="text-red-700">{avEm} / {cap.total_emergency_beds}</span> : <span className="text-slate-400 italic">N/A</span>}
                    </td>

                    <td className="p-4 font-bold text-amber-800">
                      {cap ? `${cap.available_ambulances} / ${cap.total_ambulances}` : "N/A"}
                    </td>

                    <td className="p-4 text-[11px] text-slate-500 font-medium">
                      {cap?.updated_at ? new Date(cap.updated_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "N/A"}
                      <div className="text-[9px] text-slate-400">By {cap?.updated_by || "Admin"}</div>
                    </td>

                    <td className="p-4 text-right space-x-2">
                      {isAdmin ? (
                        <>
                          <button
                            onClick={() => openEditModal(h)}
                            className="px-3 py-1.5 bg-indigo-950 hover:bg-indigo-900 text-amber-300 font-black rounded-xl text-[11px] shadow cursor-pointer"
                          >
                            Update Capacity
                          </button>
                          <button
                            onClick={() => loadAuditHistory(h)}
                            className="px-2 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl text-[11px] cursor-pointer"
                          >
                            History
                          </button>
                        </>
                      ) : (
                        <span className="text-[10px] font-bold text-slate-400 bg-slate-100 px-2 py-1 rounded">View Only</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Admin Capacity Update Modal */}
      {editingHospital && (
        <div className="fixed inset-0 z-[9999] bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl border border-slate-200 max-w-lg w-full p-6 shadow-2xl space-y-4 font-sans text-slate-900 animate-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between border-b pb-3">
              <div>
                <h3 className="text-base font-extrabold text-indigo-950">Update Hospital Capacity & Status</h3>
                <p className="text-xs text-slate-500">{editingHospital.name}</p>
              </div>
              <button onClick={() => setEditingHospital(null)} className="text-slate-400 hover:text-slate-600 font-black">✕</button>
            </div>

            {saveError && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-2xl text-xs font-bold text-red-800">
                ⚠️ {saveError}
              </div>
            )}

            <form onSubmit={handleSaveCapacity} className="space-y-4 text-xs font-bold">
              <div>
                <label className="block text-[10px] uppercase text-slate-500 font-extrabold mb-1">Operational Status</label>
                <select
                  value={editCapForm.operational_status}
                  onChange={(e) => setEditCapForm({ ...editCapForm, operational_status: e.target.value })}
                  className="w-full p-2.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-800"
                >
                  <option value="OPEN">🟢 OPEN (Full Operations)</option>
                  <option value="LIMITED">🟡 LIMITED (High Demand)</option>
                  <option value="FULL">🔴 FULL (No Available Beds)</option>
                  <option value="EMERGENCY_ONLY">🟠 EMERGENCY ONLY</option>
                  <option value="CLOSED">⚫ CLOSED</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[10px] uppercase text-slate-500 font-extrabold mb-1">Total General Beds</label>
                  <input
                    type="number"
                    min="0"
                    value={editCapForm.total_beds}
                    onChange={(e) => setEditCapForm({ ...editCapForm, total_beds: parseInt(e.target.value) || 0 })}
                    className="w-full p-2.5 rounded-xl bg-slate-50 border border-slate-200"
                  />
                </div>
                <div>
                  <label className="block text-[10px] uppercase text-slate-500 font-extrabold mb-1">Occupied General Beds</label>
                  <input
                    type="number"
                    min="0"
                    value={editCapForm.occupied_beds}
                    onChange={(e) => setEditCapForm({ ...editCapForm, occupied_beds: parseInt(e.target.value) || 0 })}
                    className="w-full p-2.5 rounded-xl bg-slate-50 border border-slate-200"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[10px] uppercase text-slate-500 font-extrabold mb-1">Total ICU Beds</label>
                  <input
                    type="number"
                    min="0"
                    value={editCapForm.total_icu}
                    onChange={(e) => setEditCapForm({ ...editCapForm, total_icu: parseInt(e.target.value) || 0 })}
                    className="w-full p-2.5 rounded-xl bg-slate-50 border border-slate-200"
                  />
                </div>
                <div>
                  <label className="block text-[10px] uppercase text-slate-500 font-extrabold mb-1">Occupied ICU Beds</label>
                  <input
                    type="number"
                    min="0"
                    value={editCapForm.occupied_icu}
                    onChange={(e) => setEditCapForm({ ...editCapForm, occupied_icu: parseInt(e.target.value) || 0 })}
                    className="w-full p-2.5 rounded-xl bg-slate-50 border border-slate-200"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[10px] uppercase text-slate-500 font-extrabold mb-1">Total Emergency Beds</label>
                  <input
                    type="number"
                    min="0"
                    value={editCapForm.total_emergency_beds}
                    onChange={(e) => setEditCapForm({ ...editCapForm, total_emergency_beds: parseInt(e.target.value) || 0 })}
                    className="w-full p-2.5 rounded-xl bg-slate-50 border border-slate-200"
                  />
                </div>
                <div>
                  <label className="block text-[10px] uppercase text-slate-500 font-extrabold mb-1">Occupied Emergency Beds</label>
                  <input
                    type="number"
                    min="0"
                    value={editCapForm.occupied_emergency_beds}
                    onChange={(e) => setEditCapForm({ ...editCapForm, occupied_emergency_beds: parseInt(e.target.value) || 0 })}
                    className="w-full p-2.5 rounded-xl bg-slate-50 border border-slate-200"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[10px] uppercase text-slate-500 font-extrabold mb-1">Total Ambulances</label>
                  <input
                    type="number"
                    min="0"
                    value={editCapForm.total_ambulances}
                    onChange={(e) => setEditCapForm({ ...editCapForm, total_ambulances: parseInt(e.target.value) || 0 })}
                    className="w-full p-2.5 rounded-xl bg-slate-50 border border-slate-200"
                  />
                </div>
                <div>
                  <label className="block text-[10px] uppercase text-slate-500 font-extrabold mb-1">Available Ambulances</label>
                  <input
                    type="number"
                    min="0"
                    value={editCapForm.available_ambulances}
                    onChange={(e) => setEditCapForm({ ...editCapForm, available_ambulances: parseInt(e.target.value) || 0 })}
                    className="w-full p-2.5 rounded-xl bg-slate-50 border border-slate-200"
                  />
                </div>
              </div>

              <div className="pt-2 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setEditingHospital(null)}
                  className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="px-5 py-2 rounded-xl bg-pink-600 hover:bg-pink-700 text-white font-extrabold shadow-lg cursor-pointer"
                >
                  {saving ? "Saving Capacity..." : "Save Audit Update"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

function maxVal(n: number): number {
  return n > 0 ? n : 1;
}
