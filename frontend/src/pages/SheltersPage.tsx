import React, { useEffect, useState } from "react";
import { Home, Plus, Phone, MapPin, CheckCircle, AlertTriangle, XCircle, RefreshCw, Users, ShieldCheck } from "lucide-react";
import { api } from "../api/apiClient";

const DEFAULT_SHELTERS = [
  {
    id: 1,
    name: "St. Joseph Higher Secondary School Shelter",
    address: "Meppadi Town, Wayanad District, Kerala - 673577",
    capacity: 650,
    current_occupancy: 120,
    status: "active",
    contact_number: "+91-9447100101",
    latitude: 11.5450,
    longitude: 76.1210,
    medical_facility: true,
    water_supply_days: 7.0,
  },
  {
    id: 2,
    name: "Meppadi Community Hall & Relief Camp",
    address: "Near Main Bus Stand, Meppadi, Wayanad, Kerala - 673577",
    capacity: 500,
    current_occupancy: 85,
    status: "active",
    contact_number: "+91-9447100102",
    latitude: 11.5482,
    longitude: 76.1245,
    medical_facility: false,
    water_supply_days: 5.0,
  },
  {
    id: 3,
    name: "Government Primary Health Center (PHC) Meppadi",
    address: "Hospital Road, Meppadi, Wayanad, Kerala - 673577",
    capacity: 250,
    current_occupancy: 40,
    status: "active",
    contact_number: "+91-9447100103",
    latitude: 11.5510,
    longitude: 76.1260,
    medical_facility: true,
    water_supply_days: 4.0,
  },
  {
    id: 4,
    name: "Wayanad Regional Relief Auditorium",
    address: "Kalpetta Bypass Highway, Kalpetta, Wayanad, Kerala - 673121",
    capacity: 1200,
    current_occupancy: 310,
    status: "active",
    contact_number: "+91-9447100104",
    latitude: 11.6080,
    longitude: 76.0840,
    medical_facility: true,
    water_supply_days: 10.0,
  },
  {
    id: 5,
    name: "Idukki District Emergency Relief Center",
    address: "Collectorate Complex, Painavu, Idukki, Kerala - 685603",
    capacity: 800,
    current_occupancy: 150,
    status: "active",
    contact_number: "+91-9447100201",
    latitude: 9.8496,
    longitude: 76.9804,
    medical_facility: true,
    water_supply_days: 8.0,
  },
  {
    id: 6,
    name: "Mumbai Metropolitan Relief Shelter",
    address: "Bandra Kurla Complex (BKC) Auditorium, Mumbai, Maharashtra - 400051",
    capacity: 2000,
    current_occupancy: 450,
    status: "active",
    contact_number: "+91-9820100301",
    latitude: 19.0600,
    longitude: 72.8600,
    medical_facility: true,
    water_supply_days: 14.0,
  },
];

import { locationService } from "../services/locationService";

interface SheltersPageProps {
  currentLocation?: { name: string; lat: number; lon: number };
}

export const SheltersPage: React.FC<SheltersPageProps> = ({ currentLocation }) => {
  const activeLoc = currentLocation || { name: "Chennai, Tamil Nadu", lat: 13.0827, lon: 80.2707 };
  const [loading, setLoading] = useState(false);

  const getDynamicShelters = (loc: { name: string; lat: number; lon: number }) => {
    return locationService.getNearbySheltersAndZones(loc.lat, loc.lon, loc.name).shelters;
  };

  const [shelters, setShelters] = useState<any[]>(() => getDynamicShelters(activeLoc));
  const [error, setError] = useState<string | null>(null);

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [name, setName] = useState("");
  const [address, setAddress] = useState("");
  const [capacity, setCapacity] = useState(400);
  const [currentOccupancy, setCurrentOccupancy] = useState(50);
  const [contactNumber, setContactNumber] = useState("+91-9447100105");
  const [latitude, setLatitude] = useState(activeLoc.lat);
  const [longitude, setLongitude] = useState(activeLoc.lon);

  useEffect(() => {
    setShelters(getDynamicShelters(activeLoc));
    setLatitude(activeLoc.lat);
    setLongitude(activeLoc.lon);
  }, [activeLoc.name, activeLoc.lat, activeLoc.lon]);

  const handleCreateShelter = async (e: React.FormEvent) => {
    e.preventDefault();
    const newShelter = {
      id: Date.now(),
      name: name || "New Relief Shelter",
      address: address || "Emergency District Relief Zone",
      capacity: Number(capacity),
      current_occupancy: Number(currentOccupancy),
      status: "active",
      contact_number: contactNumber,
      latitude: Number(latitude),
      longitude: Number(longitude),
      medical_facility: true,
      water_supply_days: 7.0,
    };

    setShelters((prev) => [newShelter, ...prev]);

    try {
      await fetch("http://localhost:8001/api/v1/shelters", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newShelter),
      });
    } catch (err) {}

    setIsModalOpen(false);
    setName("");
    setAddress("");
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto font-sans bg-slate-50 min-h-screen text-slate-900">
      {/* Header Bar */}
      <div className="bg-gradient-to-r from-indigo-900 via-blue-900 to-indigo-950 border border-indigo-800 rounded-2xl p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-xl text-white">
        <div>
          <h2 className="text-xl font-black text-white flex items-center gap-2">
            <Home className="w-5 h-5 text-amber-300" />
            Emergency Relief Shelters Directory
          </h2>
          <p className="text-xs text-indigo-100 mt-1 font-medium">
            Real-time carrying capacities, physical street addresses, contact numbers, and GPS location coordinates.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShelters(getDynamicShelters(activeLoc))}
            className="p-2.5 rounded-xl bg-indigo-950 hover:bg-indigo-800 text-amber-300 transition-colors border border-indigo-700 shadow-sm"
            title="Refresh Shelters"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </button>
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 bg-pink-600 hover:bg-pink-500 text-white text-xs font-black px-4 py-2.5 rounded-xl shadow-md border border-pink-500 transition-all cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            <span>Register New Shelter</span>
          </button>
        </div>
      </div>

      {/* Shelters Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {shelters.map((s) => {
          const maxCap = s.capacity || 500;
          const currOcc = s.current_occupancy || 0;
          const availCap = Math.max(0, maxCap - currOcc);
          const pct = Math.round((currOcc / maxCap) * 100);
          const isFull = pct >= 100;

          return (
            <div
              key={s.id}
              className="bg-white border border-slate-200 rounded-2xl p-5 space-y-4 hover:border-indigo-300 transition-all shadow-md flex flex-col justify-between"
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <h3 className="text-base font-extrabold text-indigo-950">{s.name}</h3>
                    <p className="text-xs text-slate-600 flex items-start gap-1.5 mt-1 leading-relaxed font-medium">
                      <MapPin className="w-3.5 h-3.5 text-indigo-600 shrink-0 mt-0.5" />
                      <span>{s.address || "Wayanad Sector Relief Area"}</span>
                    </p>
                  </div>
                  <span
                    className={`text-[10px] font-black px-2.5 py-0.5 rounded border uppercase shrink-0 ${
                      isFull
                        ? "bg-red-100 text-red-800 border-red-300"
                        : "bg-emerald-100 text-emerald-800 border-emerald-300"
                    }`}
                  >
                    {isFull ? "FULL" : "ACTIVE"}
                  </span>
                </div>

                {/* Capacity Metrics Box */}
                <div className="p-3 rounded-xl bg-indigo-50/60 border border-indigo-100 space-y-2">
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-600 font-bold">Available Space:</span>
                    <b className={isFull ? "text-red-700 font-black text-sm" : "text-emerald-700 font-black text-sm"}>
                      {availCap} Beds Free
                    </b>
                  </div>

                  <div className="flex justify-between text-[11px] text-slate-600 font-mono font-bold">
                    <span>Occupancy: {currOcc} / {maxCap}</span>
                    <span>{pct}% Filled</span>
                  </div>

                  <div className="w-full bg-white h-2.5 rounded-full overflow-hidden border border-indigo-100 shadow-inner">
                    <div
                      className={`h-full transition-all ${isFull ? "bg-red-600" : pct > 75 ? "bg-amber-500" : "bg-emerald-600"}`}
                      style={{ width: `${Math.min(100, pct)}%` }}
                    ></div>
                  </div>
                </div>
              </div>

              {/* Contact & Meta */}
              <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-600 font-bold">
                <div className="flex items-center gap-1.5">
                  <Phone className="w-3.5 h-3.5 text-pink-600" />
                  <span className="font-mono text-indigo-950 font-extrabold">{s.contact_number || "+91-9447100101"}</span>
                </div>
                <div className="text-[11px] text-slate-500 font-mono">
                  {s.latitude ? `${Number(s.latitude).toFixed(4)}° N` : "11.5450° N"}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Modal: Create Shelter */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <form onSubmit={handleCreateShelter} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 w-full max-w-md space-y-4 shadow-2xl">
            <h3 className="text-sm font-bold text-slate-100 border-b border-slate-800 pb-2">Register Emergency Relief Shelter</h3>

            <div>
              <label className="text-xs text-slate-300 block mb-1">Shelter Name:</label>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Meppadi Higher Secondary Relief Center"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none"
              />
            </div>

            <div>
              <label className="text-xs text-slate-300 block mb-1">Physical Street Address:</label>
              <input
                type="text"
                required
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                placeholder="e.g. Main Highway Road, Meppadi, Wayanad, Kerala - 673577"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-slate-300 block mb-1">Max Capacity:</label>
                <input
                  type="number"
                  required
                  min="1"
                  value={capacity}
                  onChange={(e) => setCapacity(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none"
                />
              </div>
              <div>
                <label className="text-xs text-slate-300 block mb-1">Current Occupancy:</label>
                <input
                  type="number"
                  required
                  min="0"
                  value={currentOccupancy}
                  onChange={(e) => setCurrentOccupancy(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none"
                />
              </div>
            </div>

            <div>
              <label className="text-xs text-slate-300 block mb-1">Emergency Helpline Phone:</label>
              <input
                type="text"
                value={contactNumber}
                onChange={(e) => setContactNumber(e.target.value)}
                placeholder="+91-9447100101"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none font-mono"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-slate-300 block mb-1">Latitude:</label>
                <input
                  type="number"
                  step="any"
                  value={latitude}
                  onChange={(e) => setLatitude(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none font-mono"
                />
              </div>
              <div>
                <label className="text-xs text-slate-300 block mb-1">Longitude:</label>
                <input
                  type="number"
                  step="any"
                  value={longitude}
                  onChange={(e) => setLongitude(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none font-mono"
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setIsModalOpen(false)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs rounded-xl"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-xl shadow-lg"
              >
                Save Shelter
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
