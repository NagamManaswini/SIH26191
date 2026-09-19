import React, { useState } from "react";
import { RefreshCw, CheckCircle2, AlertOctagon, Users, Home, MapPin, ArrowRight, ShieldCheck } from "lucide-react";
import { api } from "../api/apiClient";

export const RelocationPlanPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  // Demo Population Groups State
  const [groups, setGroups] = useState([
    {
      location_name: "Red Zone Alpha (Riverside Flood Plain)",
      total_population: 300,
      vulnerable_population: 120,
      latitude: 19.0600,
      longitude: 72.8600,
    },
    {
      location_name: "Red Zone Beta (Steep Landslide Slope)",
      total_population: 250,
      vulnerable_population: 50,
      latitude: 19.1100,
      longitude: 72.9100,
    },
  ]);

  // Form Inputs for Adding New Group
  const [newLocName, setNewLocName] = useState("");
  const [newTotalPop, setNewTotalPop] = useState(100);
  const [newVulnPop, setNewVulnPop] = useState(25);
  const [newLat, setNewLat] = useState(19.0800);
  const [newLon, setNewLon] = useState(72.8800);

  const handleAddGroup = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newLocName) return;
    setGroups([
      ...groups,
      {
        location_name: newLocName,
        total_population: Number(newTotalPop),
        vulnerable_population: Number(newVulnPop),
        latitude: Number(newLat),
        longitude: Number(newLon),
      },
    ]);
    setNewLocName("");
  };

  const handleRunOptimization = async () => {
    setLoading(true);
    setError(null);
    try {
      const payload = {
        population_groups: groups,
        risk_preference: "strict_safety",
        max_distance_km: 50.0,
      };
      const res = await api.planRelocation(payload);
      setResult(res);
    } catch (err: any) {
      setError(err.message || "Relocation optimization failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto font-sans bg-slate-50 min-h-screen text-slate-900">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-900 via-blue-900 to-indigo-950 border border-indigo-800 rounded-2xl p-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-xl text-white">
        <div>
          <h2 className="text-xl font-black text-white flex items-center gap-2">
            <RefreshCw className="w-5 h-5 text-amber-300" />
            Intelligent Multi-Objective Relocation Optimization Engine
          </h2>
          <p className="text-xs text-indigo-100 mt-1 font-medium">
            Assigns vulnerable population groups from hazard red zones to safe emergency relief shelters without exceeding carrying capacity limits.
          </p>
        </div>

        <button
          onClick={handleRunOptimization}
          disabled={loading}
          className="flex items-center gap-2 bg-pink-600 hover:bg-pink-500 text-white text-xs font-black px-5 py-3 rounded-xl shadow-md border border-pink-400 transition-all shrink-0 cursor-pointer uppercase tracking-wider"
        >
          {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <ShieldCheck className="w-4 h-4" />}
          <span>Run Relocation Optimization Solver</span>
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-300 p-4 rounded-xl text-red-950 text-xs font-bold">
          ⚠️ {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Population Groups Input Management */}
        <div className="lg:col-span-5 space-y-4">
          <div className="bg-white border border-slate-200 rounded-2xl p-5 space-y-4 shadow-md">
            <h3 className="text-xs font-black text-indigo-950 uppercase tracking-wider border-b border-slate-100 pb-2">
              Hazard-Affected Population Groups ({groups.length})
            </h3>

            <div className="space-y-3">
              {groups.map((g, idx) => (
                <div key={idx} className="bg-indigo-50/60 p-3 rounded-xl border border-indigo-100 text-xs space-y-1 font-bold">
                  <div className="font-extrabold text-indigo-950 flex items-center justify-between">
                    <span>{g.location_name}</span>
                    <button
                      onClick={() => setGroups(groups.filter((_, i) => i !== idx))}
                      className="text-pink-600 hover:text-pink-700 font-black text-base"
                    >
                      ×
                    </button>
                  </div>
                  <div className="flex justify-between text-slate-600">
                    <span>Total Population: <b className="text-indigo-950 font-black">{g.total_population}</b></span>
                    <span>Vulnerable: <b className="text-pink-600 font-black">{g.vulnerable_population}</b></span>
                  </div>
                </div>
              ))}
            </div>

            {/* Add Group Form */}
            <form onSubmit={handleAddGroup} className="pt-3 border-t border-slate-100 space-y-3">
              <h4 className="text-xs font-black text-indigo-950">Add Red Zone Population Group</h4>
              <input
                type="text"
                required
                placeholder="Group / Hazard Location Name"
                value={newLocName}
                onChange={(e) => setNewLocName(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-xs text-indigo-950 font-bold"
              />
              <div className="grid grid-cols-2 gap-2">
                <input
                  type="number"
                  placeholder="Total Population"
                  value={newTotalPop}
                  onChange={(e) => setNewTotalPop(Number(e.target.value))}
                  className="bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-xs text-indigo-950 font-bold"
                />
                <input
                  type="number"
                  placeholder="Vulnerable Pop"
                  value={newVulnPop}
                  onChange={(e) => setNewVulnPop(Number(e.target.value))}
                  className="bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-xs text-indigo-950 font-bold"
                />
              </div>
              <button
                type="submit"
                className="w-full bg-indigo-950 hover:bg-indigo-900 text-white text-xs font-extrabold py-2.5 rounded-xl border border-indigo-800 shadow-sm"
              >
                + Add Population Group
              </button>
            </form>
          </div>
        </div>

        {/* Right Column: Optimization Results & Transparent Decision Rationale */}
        <div className="lg:col-span-7 space-y-4">
          {result ? (
            <div className="space-y-4">
              {/* Optimization Status Summary Header */}
              <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-md space-y-3">
                <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                  <div>
                    <span className="text-xs text-slate-600 uppercase font-bold">Optimization Status</span>
                    <div className="text-xl font-black text-emerald-700 flex items-center gap-2 mt-0.5">
                      <CheckCircle2 className="w-5 h-5" />
                      {result.status}
                    </div>
                  </div>

                  <div className="text-right">
                    <div className="text-[10px] text-slate-500 uppercase font-bold">Total Evacuated</div>
                    <div className="text-2xl font-black text-indigo-950">{result.total_evacuated} citizens</div>
                  </div>
                </div>

                <p className="text-xs text-slate-700 font-bold">{result.message}</p>
              </div>

              {/* Assignment Cards */}
              <div className="space-y-3">
                <h3 className="text-xs font-black text-indigo-950 uppercase tracking-wider">
                  Assigned Relocation Plan ({result.assignments?.length || 0} Routes)
                </h3>

                {result.assignments?.map((a: any, idx: number) => (
                  <div key={idx} className="bg-white border border-slate-200 rounded-2xl p-5 space-y-3 shadow-md">
                    <div className="flex items-center justify-between font-black text-sm text-indigo-950">
                      <span className="text-pink-600">{a.source_location_name}</span>
                      <ArrowRight className="w-4 h-4 text-indigo-600" />
                      <span className="text-emerald-700">{a.assigned_shelter_name}</span>
                    </div>

                    <div className="grid grid-cols-4 gap-2 text-xs bg-indigo-50/60 p-2.5 rounded-xl border border-indigo-100 font-bold">
                      <div>
                        <span className="text-slate-600 block text-[10px]">Assigned Count</span>
                        <b className="text-indigo-950 font-black">{a.assigned_population_count}</b>
                      </div>
                      <div>
                        <span className="text-slate-600 block text-[10px]">Vulnerable Count</span>
                        <b className="text-pink-600 font-black">{a.vulnerable_assigned_count}</b>
                      </div>
                      <div>
                        <span className="text-slate-600 block text-[10px]">Route Distance</span>
                        <b className="text-indigo-950 font-extrabold">{a.distance_km} km</b>
                      </div>
                      <div>
                        <span className="text-slate-600 block text-[10px]">Shelter Safety</span>
                        <b className="text-emerald-700 font-black">{(a.shelter_safety_score * 100).toFixed(0)}%</b>
                      </div>
                    </div>

                    {/* Decision Rationale */}
                    <div className="bg-slate-50 border border-slate-200 p-3 rounded-xl text-xs text-slate-700">
                      <b className="text-indigo-950 block mb-1 font-black">Transparent Decision Rationale:</b>
                      <p className="text-[11px] text-slate-700 leading-relaxed font-medium">"{a.reason_for_assignment}"</p>
                    </div>
                  </div>
                ))}
              </div>

              {/* Unassigned Populations Overflow */}
              {result.unassigned_populations && result.unassigned_populations.length > 0 && (
                <div className="bg-amber-50 border border-amber-300 rounded-2xl p-5 space-y-2">
                  <h4 className="text-xs font-black text-amber-950 flex items-center gap-1.5">
                    <AlertOctagon className="w-4 h-4 text-amber-600" />
                    Unassigned Capacity Overflow ({result.total_unassigned} citizens)
                  </h4>
                  {result.unassigned_populations.map((u: any, idx: number) => (
                    <div key={idx} className="text-xs text-amber-900 font-bold">
                      • <b>{u.location_name}</b>: {u.unassigned_population} unassigned evacuees — <i>{u.reason}</i>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="bg-white border border-slate-200 rounded-2xl p-12 text-center flex flex-col items-center justify-center gap-3 h-full shadow-md">
              <RefreshCw className="w-10 h-10 text-indigo-600 animate-spin" />
              <h4 className="text-base font-black text-indigo-950">Relocation Solver Ready</h4>
              <p className="text-xs text-slate-600 max-w-sm font-medium">
                Click "Run Relocation Optimization Solver" above to compute optimal shelter assignments with transparent decision rationale.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
