import React, { useEffect, useState, useCallback } from "react";
import { ClipboardList, RefreshCw, CheckCircle, Filter, UserCheck } from "lucide-react";
import { api } from "../api/apiClient";
import { UserAuth } from "./LoginPage";

interface HospitalPatientsPageProps { user: UserAuth; }

const TREATMENT_STATUSES = ["WAITING","ADMITTED","IN_TREATMENT","ICU","DISCHARGED","TRANSFERRED"];
const DISCHARGE_STATUSES = ["ACTIVE","DISCHARGED","TRANSFERRED","DECEASED"];
const PRIORITY_STYLES: Record<string,string> = {
  CRITICAL:"bg-red-100 text-red-800 border-red-300",
  HIGH:"bg-orange-100 text-orange-800 border-orange-300",
  MEDIUM:"bg-amber-100 text-amber-800 border-amber-300",
  LOW:"bg-blue-100 text-blue-800 border-blue-300",
};

export const HospitalPatientsPage: React.FC<HospitalPatientsPageProps> = ({ user }) => {
  const [patients, setPatients] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [updatingId, setUpdatingId] = useState<number|null>(null);
  const [filterStatus, setFilterStatus] = useState("ALL");
  const [error, setError] = useState<string|null>(null);

  const loadPatients = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.hospitalGetPatients();
      setPatients(data || []);
    } catch(e) { setError("Failed to load patients."); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { loadPatients(); }, [loadPatients]);

  const handleUpdate = async (id: number, updates: any) => {
    setUpdatingId(id);
    try {
      await api.hospitalUpdatePatient(id, updates);
      await loadPatients();
    } catch(e) { setError("Failed to update patient status."); }
    finally { setUpdatingId(null); }
  };

  const filtered = filterStatus === "ALL" ? patients : patients.filter(p => p.treatment_status === filterStatus || p.discharge_status === filterStatus);
  const active = patients.filter(p => p.discharge_status === "ACTIVE").length;

  if (loading) return <div className="flex items-center justify-center h-64"><div className="w-8 h-8 border-4 border-emerald-600 border-t-transparent rounded-full animate-spin"></div></div>;

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6 font-sans">
      <div className="flex items-center gap-4">
        <div className="w-12 h-12 rounded-2xl bg-blue-600 flex items-center justify-center shadow-lg">
          <ClipboardList className="w-7 h-7 text-white" />
        </div>
        <div>
          <h1 className="text-xl font-black text-slate-900">Patient Management</h1>
          <p className="text-xs text-slate-500 font-medium">{active} active patients — privacy-conscious records only</p>
        </div>
        <button onClick={loadPatients} className="ml-auto flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-black transition-all">
          <RefreshCw className="w-3.5 h-3.5" /> Refresh
        </button>
      </div>

      {error && <div className="p-3 bg-red-50 border border-red-300 rounded-xl text-red-800 text-xs font-bold">{error}</div>}

      {/* Summary */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label:"Active Patients", count: patients.filter(p=>p.discharge_status==="ACTIVE").length, color:"bg-emerald-50 border-emerald-200 text-emerald-800" },
          { label:"In Treatment", count: patients.filter(p=>p.treatment_status==="IN_TREATMENT"||p.treatment_status==="ICU").length, color:"bg-blue-50 border-blue-200 text-blue-800" },
          { label:"Discharged", count: patients.filter(p=>p.discharge_status==="DISCHARGED").length, color:"bg-slate-50 border-slate-200 text-slate-700" },
        ].map(s=>(
          <div key={s.label} className={`${s.color} border rounded-2xl p-4 text-center`}>
            <p className="text-3xl font-black">{s.count}</p>
            <p className="text-xs font-extrabold uppercase tracking-wider mt-1 opacity-70">{s.label}</p>
          </div>
        ))}
      </div>

      {/* Filter */}
      <div className="flex items-center gap-2 flex-wrap">
        <Filter className="w-4 h-4 text-slate-400" />
        {["ALL","WAITING","ADMITTED","IN_TREATMENT","ICU","DISCHARGED"].map(s=>(
          <button key={s} onClick={()=>setFilterStatus(s)} className={`px-3 py-1.5 rounded-lg text-[10px] font-black transition-all ${filterStatus===s?"bg-slate-900 text-white":"bg-slate-100 text-slate-600 hover:bg-slate-200"}`}>{s}</button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-2xl p-12 text-center">
          <UserCheck className="w-12 h-12 text-emerald-500 mx-auto mb-3"/>
          <p className="text-slate-600 font-bold">No patients found</p>
        </div>
      ) : (
        <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm">
          <table className="w-full">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                {["Patient ID","ER Request","Age Range","Priority","Arrival","Treatment Status","Department","Discharge","Actions"].map(h=>(
                  <th key={h} className="px-4 py-3 text-left text-[10px] font-extrabold text-slate-500 uppercase tracking-wider">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map((p:any)=>(
                <tr key={p.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-4 py-3 text-xs font-black text-slate-800 font-mono">{p.patient_code}</td>
                  <td className="px-4 py-3 text-xs text-slate-600 font-bold">{p.emergency_request_id ? `ER-${p.emergency_request_id}` : "—"}</td>
                  <td className="px-4 py-3 text-xs text-slate-600 font-bold">{p.age_range||"—"}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-black border ${PRIORITY_STYLES[p.medical_priority]||""}`}>{p.medical_priority}</span>
                  </td>
                  <td className="px-4 py-3 text-[10px] text-slate-500 font-bold">{p.arrival_time ? new Date(p.arrival_time).toLocaleTimeString("en-IN") : "—"}</td>
                  <td className="px-4 py-3">
                    <select
                      value={p.treatment_status}
                      disabled={updatingId===p.id || p.discharge_status!=="ACTIVE"}
                      onChange={e=>handleUpdate(p.id,{treatment_status:e.target.value})}
                      className="border border-slate-300 rounded-lg px-2 py-1 text-[10px] font-bold text-slate-700 focus:outline-none focus:border-emerald-500 disabled:opacity-50"
                    >
                      {TREATMENT_STATUSES.map(s=><option key={s} value={s}>{s}</option>)}
                    </select>
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-600 font-bold">{p.assigned_department||"—"}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-black ${
                      p.discharge_status==="ACTIVE"?"bg-emerald-100 text-emerald-800":
                      p.discharge_status==="DISCHARGED"?"bg-slate-100 text-slate-700":
                      "bg-red-100 text-red-800"
                    }`}>{p.discharge_status}</span>
                  </td>
                  <td className="px-4 py-3">
                    {p.discharge_status==="ACTIVE" && (
                      <button
                        disabled={updatingId===p.id}
                        onClick={()=>handleUpdate(p.id,{discharge_status:"DISCHARGED",treatment_status:"DISCHARGED"})}
                        className="px-2 py-1 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-[10px] font-black transition-all disabled:opacity-50"
                      >Discharge</button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="p-3 bg-blue-50 border border-blue-200 rounded-xl text-blue-800 text-xs font-bold flex gap-2">
        <span>🔒</span>
        <p>Patient records follow privacy guidelines. Only anonymized identifiers (patient codes) are displayed. No personal names or full identification data is shown.</p>
      </div>
    </div>
  );
};
