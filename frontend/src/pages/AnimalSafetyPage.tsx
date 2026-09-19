import React, { useEffect, useState } from "react";
import {
  Dog,
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  Plus,
  RefreshCw,
  Home,
  Droplets,
  Utensils,
  MapPin,
} from "lucide-react";
import { api } from "../api/apiClient";
import { LocationSearch } from "../components/map/LocationSearch";
import { UserAuth } from "./LoginPage";

interface AnimalSafetyPageProps {
  user?: UserAuth | null;
}

export const AnimalSafetyPage: React.FC<AnimalSafetyPageProps> = ({ user }) => {
  const isUserRole = user?.role === "user";
  const [animals, setAnimals] = useState<any[]>([]);
  const [animalShelters, setAnimalShelters] = useState<any[]>([]);
  const [rescuePlanResult, setRescuePlanResult] = useState<any | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);

  // Form State
  const [tagId, setTagId] = useState("");
  const [ownerName, setOwnerName] = useState(user?.name || "Resident");
  const [animalType, setAnimalType] = useState("cattle");
  const [animalName, setAnimalName] = useState("");
  const [selectedLoc, setSelectedLoc] = useState({
    name: "Chennai, Tamil Nadu",
    lat: 13.0827,
    lon: 80.2707,
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    const [anData, ansData] = await Promise.all([
      api.getAnimals(),
      api.getAnimalShelters(),
    ]);
    setAnimals(anData);
    setAnimalShelters(ansData);
  };

  const handleCreateAnimal = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!tagId || !animalType) return;

    await api.createAnimal({
      tag_id: tagId,
      owner_name: ownerName,
      animal_type: animalType,
      name: animalName || `${animalType.toUpperCase()} Record`,
      location_name: selectedLoc.name,
      latitude: selectedLoc.lat,
      longitude: selectedLoc.lon,
      emergency_status: "AT_RISK",
    });

    setTagId("");
    setAnimalName("");
    setShowAddModal(false);
    loadData();
  };

  const handleRunRescuePlan = async () => {
    if (isUserRole) {
      alert("Notice: Rescue Optimization Engine trigger is reserved for Disaster Management Responders.");
      return;
    }
    setIsGenerating(true);
    try {
      const plan = await api.runAnimalRescuePlan();
      setRescuePlanResult(plan);
      loadData();
    } catch (e) {
      console.warn("Rescue plan error:", e);
    } finally {
      setIsGenerating(false);
    }
  };

  const atRiskCount = animals.filter((a) => a.emergency_status === "AT_RISK").length;
  const rescuedCount = animals.filter((a) => a.rescue_status === "COMPLETED" || a.rescue_status === "IN_PROGRESS").length;
  const totalAnimalCap = animalShelters.reduce((acc, s) => acc + (s.capacity || 0), 0);
  const totalAnimalAvail = animalShelters.reduce((acc, s) => acc + (s.available_capacity || (s.capacity - s.current_occupancy)), 0);

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto font-sans bg-slate-50 min-h-screen text-slate-900">
      {/* Header Banner */}
      <div className="bg-indigo-950 text-white rounded-3xl p-6 shadow-xl border border-indigo-900 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-pink-600 flex items-center justify-center shadow-lg border border-pink-400">
            <Dog className="w-8 h-8 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="bg-amber-400 text-slate-950 text-[10px] font-black px-2.5 py-0.5 rounded tracking-wider uppercase">
                CITIZEN LIVESTOCK & PET SAFETY PORTAL
              </span>
            </div>
            <h1 className="text-2xl font-black tracking-tight mt-1 text-white">
              Animal Safety & Evacuation Registration
            </h1>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 px-5 py-3 rounded-2xl bg-pink-600 hover:bg-pink-500 text-white font-black text-xs shadow-lg transition-all cursor-pointer border border-pink-400"
          >
            <Plus className="w-4 h-4 text-white" />
            Add Animal / Herd Record
          </button>
          {!isUserRole && (
            <button
              onClick={handleRunRescuePlan}
              disabled={isGenerating}
              className="flex items-center gap-2 px-4 py-3 rounded-2xl bg-indigo-800 hover:bg-indigo-700 disabled:opacity-50 text-white font-black text-xs transition-all cursor-pointer border border-indigo-600"
            >
              <RefreshCw className={`w-4 h-4 ${isGenerating ? "animate-spin" : ""}`} />
              Run Animal Rescue Solver
            </button>
          )}
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white border border-slate-200 p-5 rounded-3xl shadow-md">
          <span className="text-[11px] font-extrabold text-slate-500 uppercase tracking-wider block">Animals at Risk</span>
          <p className="text-2xl font-black text-rose-600 mt-1">{atRiskCount}</p>
          <span className="text-[11px] text-slate-400 font-bold">In Need of Safe Transport</span>
        </div>

        <div className="bg-white border border-slate-200 p-5 rounded-3xl shadow-md">
          <span className="text-[11px] font-extrabold text-slate-500 uppercase tracking-wider block">Relocated to Safe Holding</span>
          <p className="text-2xl font-black text-emerald-600 mt-1">{rescuedCount}</p>
          <span className="text-[11px] text-slate-400 font-bold">Safely Accommodated</span>
        </div>

        <div className="bg-white border border-slate-200 p-5 rounded-3xl shadow-md">
          <span className="text-[11px] font-extrabold text-slate-500 uppercase tracking-wider block">Animal Shelter Capacity</span>
          <p className="text-2xl font-black text-indigo-600 mt-1">{totalAnimalAvail} / {totalAnimalCap}</p>
          <span className="text-[11px] text-slate-400 font-bold">Free Spaces</span>
        </div>

        <div className="bg-white border border-slate-200 p-5 rounded-3xl shadow-md">
          <span className="text-[11px] font-extrabold text-slate-500 uppercase tracking-wider block">Human / Animal Split</span>
          <p className="text-sm font-black text-emerald-600 mt-2 flex items-center gap-1">
            <CheckCircle2 className="w-4 h-4 text-emerald-500" /> SEPARATE FACILITIES
          </p>
          <span className="text-[10px] text-slate-400 font-bold block mt-0.5">Strict Capacity Separation</span>
        </div>
      </div>

      {/* Main Grid: Animal Records & Shelters */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-7 bg-white border border-slate-200 rounded-3xl p-6 shadow-xl space-y-4">
          <h2 className="text-xs font-black text-indigo-950 uppercase tracking-wider flex items-center gap-2">
            <Dog className="w-4 h-4 text-pink-600" />
            My & Community Registered Animals ({animals.length})
          </h2>

          <div className="space-y-3 max-h-[500px] overflow-y-auto pr-1">
            {animals.length === 0 ? (
              <div className="p-8 text-center bg-slate-50 border border-slate-200 rounded-2xl space-y-2">
                <Dog className="w-8 h-8 text-slate-400 mx-auto" />
                <div className="text-xs font-black text-slate-700">No animals registered yet.</div>
                <div className="text-[11px] text-slate-500 font-medium">Click "+ Add Animal / Herd Record" to add livestock or pets.</div>
              </div>
            ) : (
              animals.map((an) => (
                <div key={an.id} className="p-4 rounded-2xl border border-slate-200 bg-slate-50 flex flex-wrap items-center justify-between gap-3 text-xs">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-black text-slate-900 text-sm">{an.name || an.tag_id}</span>
                      <span className="bg-indigo-100 text-indigo-800 font-black px-2 py-0.5 rounded uppercase text-[10px]">
                        {an.animal_type}
                      </span>
                    </div>
                    <div className="text-slate-600 font-bold flex items-center gap-1">
                      <MapPin className="w-3.5 h-3.5 text-pink-600" />
                      <span>Owner: {an.owner_name || "Citizen"} | Location: {an.location_name}</span>
                    </div>
                  </div>

                  <span className={`text-[10px] font-black px-2.5 py-1 rounded-xl uppercase ${
                    an.emergency_status === "AT_RISK" ? "bg-rose-100 text-rose-700 border border-rose-300" : "bg-emerald-100 text-emerald-700 border border-emerald-300"
                  }`}>
                    {an.emergency_status}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="lg:col-span-5 bg-white border border-slate-200 rounded-3xl p-6 shadow-xl space-y-4">
          <h2 className="text-xs font-black text-indigo-950 uppercase tracking-wider flex items-center gap-2">
            <Home className="w-4 h-4 text-indigo-600" />
            Dedicated Animal Safe Facilities ({animalShelters.length})
          </h2>

          <div className="space-y-4">
            {animalShelters.length === 0 ? (
              <div className="p-8 text-center bg-indigo-50/50 border border-indigo-100 rounded-2xl space-y-2">
                <Home className="w-8 h-8 text-indigo-400 mx-auto" />
                <div className="text-xs font-black text-indigo-950">No animal holding facilities registered.</div>
                <div className="text-[11px] text-slate-500 font-medium">Safe holding facilities will appear here when registered.</div>
              </div>
            ) : (
              animalShelters.map((ans) => (
                <div key={ans.id} className="p-4 rounded-2xl border border-indigo-100 bg-indigo-50/40 space-y-3 text-xs">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-black text-indigo-950 text-sm">{ans.name}</h3>
                      <p className="text-[11px] text-slate-500 font-bold">{ans.address || "Sector Animal Safe Holding"}</p>
                    </div>
                    <span className="bg-emerald-600 text-white font-black text-[10px] px-2 py-0.5 rounded">SAFE</span>
                  </div>
                  <div className="flex items-center gap-4 text-[11px] font-bold text-slate-600 pt-1">
                    <span>Capacity: <b>{ans.capacity}</b></span>
                    <span className="text-emerald-700 font-black">Available: {ans.available_capacity || (ans.capacity - ans.current_occupancy)}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Add Animal Modal with Google Location Search */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
          <div className="w-full max-w-lg bg-white rounded-3xl p-6 shadow-2xl border border-slate-200 space-y-4 font-sans text-slate-900">
            <h3 className="text-base font-black text-indigo-950 border-b border-slate-100 pb-2">Register Animal / Herd Record</h3>
            <form onSubmit={handleCreateAnimal} className="space-y-3 text-xs">
              <div>
                <label className="font-extrabold text-slate-700 block mb-1">Tag / ID Number *</label>
                <input
                  type="text"
                  required
                  value={tagId}
                  onChange={(e) => setTagId(e.target.value)}
                  placeholder="e.g. ANIM-CATTLE-501"
                  className="w-full p-2.5 rounded-xl border border-slate-300 bg-slate-50 font-bold focus:outline-none focus:border-indigo-600 text-xs"
                />
              </div>

              <div>
                <label className="font-extrabold text-slate-700 block mb-1">Animal Category *</label>
                <select
                  value={animalType}
                  onChange={(e) => setAnimalType(e.target.value)}
                  className="w-full p-2.5 rounded-xl border border-slate-300 bg-slate-50 font-bold focus:outline-none focus:border-indigo-600 text-xs"
                >
                  <option value="cattle">Cattle</option>
                  <option value="goats">Goats</option>
                  <option value="sheep">Sheep</option>
                  <option value="dogs">Dogs</option>
                  <option value="cats">Cats</option>
                  <option value="poultry">Poultry</option>
                  <option value="other_livestock">Other Livestock</option>
                </select>
              </div>

              <div>
                <label className="font-extrabold text-slate-700 block mb-1">Owner Name</label>
                <input
                  type="text"
                  value={ownerName}
                  onChange={(e) => setOwnerName(e.target.value)}
                  placeholder="Owner or Cooperative name"
                  className="w-full p-2.5 rounded-xl border border-slate-300 bg-slate-50 font-bold focus:outline-none text-xs"
                />
              </div>

              <div>
                <label className="font-extrabold text-slate-700 block mb-1">Herd Name / Label</label>
                <input
                  type="text"
                  value={animalName}
                  onChange={(e) => setAnimalName(e.target.value)}
                  placeholder="e.g. Lakshmi Dairy Herd (10 Cattle)"
                  className="w-full p-2.5 rounded-xl border border-slate-300 bg-slate-50 font-bold focus:outline-none text-xs"
                />
              </div>

              {/* Location Picker Search */}
              <div className="space-y-1">
                <label className="font-extrabold text-slate-700 block">Animal Location (Google Maps Search)</label>
                <LocationSearch
                  currentLabel={selectedLoc.name}
                  onSelectLocation={(loc) => setSelectedLoc(loc)}
                  placeholder="Search animal location in India..."
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 bg-slate-200 text-slate-800 rounded-xl font-bold text-xs"
                >
                  Cancel
                </button>
                <button type="submit" className="px-5 py-2 bg-pink-600 text-white font-black rounded-xl text-xs shadow-md">
                  Save Animal Record
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
