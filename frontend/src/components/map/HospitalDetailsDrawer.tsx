import React from "react";
import { X, Phone, MapPin, Navigation, Activity, Clock, ShieldCheck, Truck, Stethoscope, AlertTriangle } from "lucide-react";

export interface HospitalDetailsData {
  id: number;
  hospital_id: string;
  name: string;
  type: string;
  address?: string;
  latitude: number;
  longitude: number;
  district?: string;
  state?: string;
  phone?: string;
  emergency_status: string;
  operational_status: string;
  specialization?: string;
  data_source?: string;
  distance_km?: number;
  estimated_travel_minutes?: number;
  capacity?: {
    total_beds: number;
    occupied_beds: number;
    available_beds: number;
    total_icu: number;
    occupied_icu: number;
    available_icu: number;
    total_emergency_beds: number;
    occupied_emergency_beds: number;
    available_emergency_beds: number;
    isolation_beds?: number;
    total_ambulances: number;
    available_ambulances: number;
    busy_ambulances?: number;
    updated_at?: string;
    updated_by?: string;
  };
}

interface HospitalDetailsDrawerProps {
  hospital: HospitalDetailsData | null;
  onClose: () => void;
  onSelectRoute?: (hospital: HospitalDetailsData) => void;
}

export const HospitalDetailsDrawer: React.FC<HospitalDetailsDrawerProps> = ({
  hospital,
  onClose,
  onSelectRoute,
}) => {
  if (!hospital) return null;

  const getStatusBadge = (statusStr: string) => {
    switch (statusStr.toUpperCase()) {
      case "OPEN":
        return <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-black bg-emerald-100 text-emerald-800 border border-emerald-300">🟢 OPEN</span>;
      case "LIMITED":
        return <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-black bg-amber-100 text-amber-800 border border-amber-300">🟡 LIMITED</span>;
      case "FULL":
        return <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-black bg-red-100 text-red-800 border border-red-300">🔴 FULL</span>;
      case "EMERGENCY_ONLY":
        return <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-black bg-orange-100 text-orange-800 border border-orange-300">🟠 EMERGENCY ONLY</span>;
      case "CLOSED":
        return <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-black bg-slate-200 text-slate-800 border border-slate-400">⚫ CLOSED</span>;
      default:
        return <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-black bg-slate-100 text-slate-600 border border-slate-300">⚪ UNKNOWN</span>;
    }
  };

  const cap = hospital.capacity;
  const hasCapacity = cap && (cap.total_beds > 0 || cap.total_emergency_beds > 0);

  return (
    <div className="fixed top-20 right-4 z-[9999] w-96 max-w-[calc(100vw-2rem)] bg-white border border-slate-200 rounded-3xl shadow-2xl overflow-hidden font-sans text-slate-900 animate-in fade-in slide-in-from-right duration-200">
      {/* Drawer Header */}
      <div className="p-4 bg-gradient-to-r from-pink-950 via-slate-900 to-indigo-950 text-white flex items-start justify-between">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-xl">🏥</span>
            <span className="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded bg-pink-600 text-white tracking-wider">
              {hospital.type}
            </span>
          </div>
          <h3 className="font-extrabold text-base leading-snug">{hospital.name}</h3>
          <p className="text-xs text-slate-300 flex items-center gap-1">
            <MapPin className="w-3.5 h-3.5 text-pink-400 shrink-0" />
            {hospital.district ? `${hospital.district}, ` : ""}{hospital.state || "India"}
          </p>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded-full hover:bg-white/20 text-slate-300 hover:text-white transition-all cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      <div className="p-4 space-y-4 max-h-[75vh] overflow-y-auto">
        {/* Status & Quick Metrics Row */}
        <div className="flex items-center justify-between bg-slate-50 p-3 rounded-2xl border border-slate-100">
          <div>
            <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider block">Operational Status</span>
            <div className="mt-1">{getStatusBadge(hospital.operational_status)}</div>
          </div>
          {hospital.distance_km !== undefined && (
            <div className="text-right">
              <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider block">Proximity / ETA</span>
              <span className="text-sm font-black text-indigo-950">
                {hospital.distance_km} km ({hospital.estimated_travel_minutes || Math.round((hospital.distance_km / 30) * 60)} min)
              </span>
            </div>
          )}
        </div>

        {/* Capacity Breakdown Section */}
        {hasCapacity ? (
          <div className="space-y-2.5">
            <h4 className="text-xs font-black uppercase text-indigo-950 tracking-wider flex items-center justify-between">
              <span>Dynamic Hospital Capacity</span>
              <span className="text-[10px] font-bold text-slate-400">Source: {hospital.data_source || "Hospital Management System"}</span>
            </h4>

            {/* General Beds Progress */}
            <div className="bg-slate-50 p-3 rounded-2xl border border-slate-100 space-y-1.5">
              <div className="flex justify-between text-xs font-bold">
                <span className="text-slate-700">General Ward Beds</span>
                <span className="text-indigo-950 font-extrabold">
                  {cap.available_beds} Available / {cap.total_beds} Total
                </span>
              </div>
              <div className="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all ${
                    (cap.occupied_beds / maxVal(cap.total_beds)) >= 0.9
                      ? "bg-red-500"
                      : (cap.occupied_beds / maxVal(cap.total_beds)) >= 0.7
                      ? "bg-amber-500"
                      : "bg-emerald-500"
                  }`}
                  style={{ width: `${Math.min(100, (cap.occupied_beds / maxVal(cap.total_beds)) * 100)}%` }}
                ></div>
              </div>
              <div className="flex justify-between text-[10px] font-bold text-slate-400">
                <span>Occupied: {cap.occupied_beds}</span>
                <span>
                  Utilization: {Math.round((cap.occupied_beds / maxVal(cap.total_beds)) * 100)}%
                </span>
              </div>
            </div>

            {/* Emergency & ICU Beds Grid */}
            <div className="grid grid-cols-2 gap-2">
              <div className="bg-red-50/70 p-3 rounded-2xl border border-red-100">
                <span className="text-[10px] font-black uppercase text-red-900 tracking-wider block">🚨 Emergency Beds</span>
                <span className="text-lg font-black text-red-700 block mt-0.5">
                  {cap.available_emergency_beds} <span className="text-xs font-bold text-red-900">/ {cap.total_emergency_beds}</span>
                </span>
                <span className="text-[10px] font-bold text-red-700">Occupied: {cap.occupied_emergency_beds}</span>
              </div>

              <div className="bg-purple-50/70 p-3 rounded-2xl border border-purple-100">
                <span className="text-[10px] font-black uppercase text-purple-900 tracking-wider block">🏥 ICU Beds</span>
                <span className="text-lg font-black text-purple-700 block mt-0.5">
                  {cap.available_icu} <span className="text-xs font-bold text-purple-900">/ {cap.total_icu}</span>
                </span>
                <span className="text-[10px] font-bold text-purple-700">Occupied: {cap.occupied_icu}</span>
              </div>
            </div>

            {/* Ambulances */}
            <div className="bg-amber-50/70 p-2.5 rounded-2xl border border-amber-100 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Truck className="w-4 h-4 text-amber-600" />
                <span className="text-xs font-bold text-slate-800">Ambulances Ready</span>
              </div>
              <span className="text-xs font-extrabold text-amber-900 bg-amber-200/80 px-2.5 py-0.5 rounded-full">
                {cap.available_ambulances} / {cap.total_ambulances} Available
              </span>
            </div>
          </div>
        ) : (
          <div className="bg-amber-50 border border-amber-200 p-4 rounded-2xl text-center space-y-1">
            <AlertTriangle className="w-6 h-6 text-amber-600 mx-auto" />
            <p className="text-xs font-black text-amber-900 uppercase tracking-wider">Capacity Data Unavailable</p>
            <p className="text-[11px] text-amber-700 font-bold">
              Capacity metrics have not yet been synchronized with this hospital facility.
            </p>
          </div>
        )}

        {/* Info & Specialization List */}
        <div className="space-y-2 pt-2 border-t border-slate-100 text-xs font-bold text-slate-700">
          <div className="flex items-center gap-2">
            <Stethoscope className="w-4 h-4 text-pink-600 shrink-0" />
            <span>Specialization: <b>{hospital.specialization || "General Trauma & Emergency"}</b></span>
          </div>
          {hospital.phone && (
            <div className="flex items-center gap-2">
              <Phone className="w-4 h-4 text-emerald-600 shrink-0" />
              <span>Contact: <a href={`tel:${hospital.phone}`} className="text-emerald-700 underline font-black">{hospital.phone}</a></span>
            </div>
          )}
          {cap?.updated_at && (
            <div className="flex items-center gap-2 text-[10px] text-slate-400 font-medium pt-1">
              <Clock className="w-3.5 h-3.5" />
              <span>Last Capacity Update: {new Date(cap.updated_at).toLocaleString()} by {cap.updated_by || "Admin"}</span>
            </div>
          )}
        </div>

        {/* Action Button */}
        {onSelectRoute && (
          <button
            onClick={() => onSelectRoute(hospital)}
            className="w-full mt-2 py-3 rounded-2xl bg-gradient-to-r from-pink-600 to-indigo-700 hover:from-pink-700 hover:to-indigo-800 text-white font-extrabold text-xs shadow-lg shadow-pink-900/20 flex items-center justify-center gap-2 transition-all cursor-pointer"
          >
            <Navigation className="w-4 h-4" />
            <span>Start Medical Emergency Route</span>
          </button>
        )}
      </div>
    </div>
  );
};

function maxVal(val: number): number {
  return val > 0 ? val : 1;
}
