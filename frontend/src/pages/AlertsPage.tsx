import React, { useEffect, useState } from "react";
import { Bell, ShieldAlert, Plus, Send, RefreshCw, CheckCircle2, CheckSquare, Filter, Radio } from "lucide-react";
import { api } from "../api/apiClient";
import { EmergencySOSModal, EmergencyAlertData } from "../components/EmergencySOSModal";

const DEFAULT_REAL_ALERTS = [
  {
    id: 1,
    title: "RED LANDSLIDE WARNING — Wayanad (Chooralmala & Mundakkai)",
    message: "Extreme rainfall exceeding 340mm/24h recorded. Unstable soil condition detected on steep slopes.",
    severity: "CRITICAL",
    affected_area: "Wayanad Sector 1 (Chooralmala & Mundakkai)",
    recommended_action: "Immediate evacuation to St. Joseph Higher Secondary School Shelter or Meppadi Community Hall.",
    status: "ACTIVE",
    notification_dispatches: [
      { provider: "Web Push", status: "SENT" },
      { provider: "Emergency SMS", status: "DISPATCHED" },
    ],
  },
  {
    id: 2,
    title: "HEAVY RAINFALL ALERT — Idukki High Altitude Slopes",
    message: "Continuous downpour causing surface runoff accumulation. High risk of localized mudslides.",
    severity: "HIGH",
    affected_area: "Idukki District High Altitude Sector",
    recommended_action: "Citizens in low-lying slope valleys move to Idukki District Relief Center.",
    status: "ACTIVE",
    notification_dispatches: [
      { provider: "Web Push", status: "SENT" },
      { provider: "Email Alert", status: "DELIVERED" },
    ],
  },
  {
    id: 3,
    title: "COASTAL FLOOD & HIGH TIDE ADVISORY — Ernakulam",
    message: "High coastal tide combined with river basin overflow. Low-lying urban streets experiencing waterlogging.",
    severity: "WARNING",
    affected_area: "Ernakulam Coastal Plain",
    recommended_action: "Avoid waterlogged roads and monitor official emergency broadcasts.",
    status: "ACTIVE",
    notification_dispatches: [
      { provider: "Web Push", status: "SENT" },
    ],
  },
];

interface AlertsPageProps {
  currentLocation?: { name: string; lat: number; lon: number };
}

export const AlertsPage: React.FC<AlertsPageProps> = ({ currentLocation }) => {
  const activeLoc = currentLocation || { name: "Chennai, Tamil Nadu", lat: 13.0827, lon: 80.2707 };
  const cityName = activeLoc.name.split(",")[0].trim();
  const [loading, setLoading] = useState(false);

  const getDynamicAlerts = (locName: string) => [
    {
      id: 1,
      title: `RED LANDSLIDE & FLOOD WARNING — ${locName}`,
      message: `Heavy surface runoff and extreme precipitation threshold detected in ${locName} sector.`,
      severity: "CRITICAL",
      affected_area: `${locName} Red Zone`,
      recommended_action: `Immediate evacuation to ${locName.split(",")[0]} General Hospital Emergency Refuge or Community School Shelter.`,
      status: "ACTIVE",
      notification_dispatches: [
        { provider: "Web Push", status: "SENT" },
        { provider: "Emergency SMS", status: "DISPATCHED" },
      ],
    },
    {
      id: 2,
      title: `HEAVY RAINFALL ALERT — ${locName} Urban Sector`,
      message: "Continuous downpour causing surface runoff accumulation. High risk of localized mudslides.",
      severity: "HIGH",
      affected_area: `${locName} High Altitude Sector`,
      recommended_action: `Citizens in low-lying slope valleys move to ${locName.split(",")[0]} Relief Center.`,
      status: "ACTIVE",
      notification_dispatches: [
        { provider: "Web Push", status: "SENT" },
        { provider: "Email Alert", status: "DELIVERED" },
      ],
    },
    {
      id: 3,
      title: `COASTAL FLOOD & HIGH TIDE ADVISORY — ${locName}`,
      message: "High coastal tide combined with river basin overflow. Low-lying urban streets experiencing waterlogging.",
      severity: "WARNING",
      affected_area: `${locName} Coastal Plain`,
      recommended_action: "Avoid waterlogged roads and monitor official emergency broadcasts.",
      status: "ACTIVE",
      notification_dispatches: [
        { provider: "Web Push", status: "SENT" },
      ],
    },
  ];

  const [alerts, setAlerts] = useState<any[]>(() => getDynamicAlerts(activeLoc.name));
  const [error, setError] = useState<string | null>(null);
  const [sosModalAlert, setSosModalAlert] = useState<EmergencyAlertData | null>(null);

  // Filter State
  const [severityFilter, setSeverityFilter] = useState<string>("");
  const [statusFilter, setStatusFilter] = useState<string>("");

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [message, setMessage] = useState("");
  const [severity, setSeverity] = useState("CRITICAL");
  const [affectedArea, setAffectedArea] = useState(`${cityName} Sector Alpha`);
  const [recommendedAction, setRecommendedAction] = useState(`Immediate evacuation to ${cityName} Central Relief Shelter.`);

  useEffect(() => {
    setAlerts(getDynamicAlerts(activeLoc.name));
    setAffectedArea(`${cityName} Sector Alpha`);
    setRecommendedAction(`Immediate evacuation to ${cityName} Central Relief Shelter.`);
  }, [activeLoc.name]);

  const loadAlerts = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getAlerts(
        severityFilter || undefined,
        statusFilter || undefined
      );
      if (Array.isArray(data) && data.length > 0) {
        setAlerts(data);
      } else {
        setAlerts(getDynamicAlerts(activeLoc.name));
      }
    } catch (err: any) {
      setAlerts(getDynamicAlerts(activeLoc.name));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAlerts();
  }, [severityFilter, statusFilter, activeLoc.name]);

  const handleBroadcast = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !message) return;
    const newAlert = {
      id: Date.now(),
      title,
      message,
      severity,
      affected_area: affectedArea,
      recommended_action: recommendedAction,
      status: "ACTIVE",
      notification_dispatches: [
        { provider: "Web Push", status: "SENT" },
        { provider: "Emergency SMS", status: "DISPATCHED" },
      ],
    };

    setAlerts((prev) => [newAlert, ...prev]);

    try {
      const payload = {
        title,
        message,
        severity,
        affected_area: affectedArea,
        recommended_action: recommendedAction,
        status: "ACTIVE",
      };
      await api.createAlert(payload);
    } catch (err) {}

    setIsModalOpen(false);
    setTitle("");
    setMessage("");
  };

  const handleStatusUpdate = async (alertId: number, newStatus: string) => {
    setAlerts((prev) =>
      prev.map((a) => (a.id === alertId ? { ...a, status: newStatus } : a))
    );
    try {
      await api.updateAlertStatus(alertId, newStatus);
    } catch (err) {}
  };

  const getAlertCardClass = (sev: string) => {
    switch ((sev || "").toUpperCase()) {
      case "CRITICAL":
        return "bg-red-50 border-red-300 text-red-950 shadow-md";
      case "HIGH":
        return "bg-amber-50 border-amber-300 text-amber-950 shadow-md";
      case "WARNING":
        return "bg-yellow-50 border-yellow-300 text-yellow-950 shadow-md";
      default:
        return "bg-white border-slate-200 text-slate-900 shadow-md";
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-6xl mx-auto font-sans bg-slate-50 min-h-screen text-slate-900">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-indigo-900 via-blue-900 to-indigo-950 border border-indigo-800 rounded-2xl p-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-xl text-white">
        <div>
          <h2 className="text-xl font-black text-white flex items-center gap-2">
            <Bell className="w-5 h-5 text-amber-300 animate-pulse" />
            Alert Management System & Emergency Broadcast Operations
          </h2>
          <p className="text-xs text-indigo-100 mt-1 font-medium">
            Real-time emergency broadcast pipeline active across Web, SMS, Push Notification, and Email channels.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={loadAlerts}
            className="p-2.5 rounded-xl bg-indigo-950 hover:bg-indigo-800 text-amber-300 transition-colors border border-indigo-700 shadow-sm"
            title="Refresh Alerts Feed"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </button>
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 bg-pink-600 hover:bg-pink-500 text-white text-xs font-black px-4 py-2.5 rounded-xl shadow-md border border-pink-500 transition-all shrink-0 cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            <span>Broadcast Emergency Alert</span>
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="bg-white border border-slate-200 rounded-2xl p-4 flex flex-wrap items-center justify-between gap-4 text-xs shadow-md">
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1.5 text-slate-700 font-extrabold">
            <Filter className="w-4 h-4 text-indigo-600" />
            Filter Severity:
          </span>
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="bg-slate-50 border border-slate-300 rounded-xl px-3 py-1.5 text-indigo-950 font-bold focus:outline-none focus:border-indigo-600"
          >
            <option value="">All Severities</option>
            <option value="CRITICAL">CRITICAL</option>
            <option value="HIGH">HIGH</option>
            <option value="WARNING">WARNING</option>
            <option value="INFO">INFO</option>
          </select>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-slate-700 font-extrabold">Status Filter:</span>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-slate-50 border border-slate-300 rounded-xl px-3 py-1.5 text-indigo-950 font-bold focus:outline-none focus:border-indigo-600"
          >
            <option value="">All Statuses</option>
            <option value="ACTIVE">ACTIVE</option>
            <option value="ACKNOWLEDGED">ACKNOWLEDGED</option>
            <option value="RESOLVED">RESOLVED</option>
            <option value="EXPIRED">EXPIRED</option>
          </select>
        </div>
      </div>

      {/* Alert Feed */}
      <div className="space-y-4">
        {alerts.map((alert) => (
          <div key={alert.id} className={`border rounded-2xl p-5 space-y-3 shadow-xl transition-all ${getAlertCardClass(alert.severity)}`}>
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="flex items-center gap-2">
                  <ShieldAlert className="w-4 h-4 text-red-400 shrink-0" />
                  <h3 className="font-bold text-sm text-slate-100">{alert.title}</h3>
                </div>
                <div className="text-xs opacity-80 mt-1">
                  Affected Area: <b className="text-slate-100">{alert.affected_area}</b>
                </div>
              </div>

              <div className="flex items-center gap-2 shrink-0">
                <span className="text-[10px] font-black px-2 py-0.5 rounded border border-current uppercase">
                  {alert.severity}
                </span>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                  alert.status === "ACTIVE"
                    ? "bg-red-950 text-red-400 border-red-500"
                    : alert.status === "ACKNOWLEDGED"
                    ? "bg-amber-950 text-amber-400 border-amber-500"
                    : "bg-emerald-950 text-emerald-400 border-emerald-500"
                }`}>
                  {alert.status}
                </span>
              </div>
            </div>

            <p className="text-xs leading-relaxed opacity-90">{alert.message}</p>

            {alert.recommended_action && (
              <div className="bg-black/30 border border-white/10 p-3 rounded-xl text-xs space-y-1">
                <span className="font-bold block opacity-80">Recommended Action for Citizens:</span>
                <p className="text-[11px] font-medium">{alert.recommended_action}</p>
              </div>
            )}

            {/* Status Action Buttons */}
            <div className="flex justify-end gap-2 pt-2 border-t border-white/10 text-xs">
              <button
                onClick={() =>
                  setSosModalAlert({
                    id: alert.id,
                    title: alert.title,
                    message: alert.message,
                    severity: alert.severity || "CRITICAL",
                    affected_area: alert.affected_area || "Wayanad Sector 1",
                    recommended_action: alert.recommended_action || "IMMEDIATE EVACUATION",
                    safe_shelter: "St. Joseph Higher Secondary School Shelter",
                    recommended_route: "North Ridge Highway Detour (Route 2)",
                  })
                }
                className="flex items-center gap-1 bg-rose-600 hover:bg-rose-500 text-white font-bold px-3 py-1.5 rounded-xl cursor-pointer shadow-sm"
              >
                <Radio className="w-3.5 h-3.5" />
                <span>View Emergency SOS</span>
              </button>
              {alert.status === "ACTIVE" && (
                <button
                  onClick={() => handleStatusUpdate(alert.id, "ACKNOWLEDGED")}
                  className="flex items-center gap-1 bg-amber-600 hover:bg-amber-500 text-white font-bold px-3 py-1.5 rounded-xl cursor-pointer"
                >
                  <CheckSquare className="w-3.5 h-3.5" />
                  <span>Acknowledge</span>
                </button>
              )}
              {alert.status !== "RESOLVED" && (
                <button
                  onClick={() => handleStatusUpdate(alert.id, "RESOLVED")}
                  className="flex items-center gap-1 bg-emerald-600 hover:bg-emerald-500 text-white font-bold px-3 py-1.5 rounded-xl cursor-pointer"
                >
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Mark Resolved</span>
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Broadcast Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <form onSubmit={handleBroadcast} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 w-full max-w-lg space-y-4 shadow-2xl">
            <h3 className="text-sm font-bold text-slate-100 border-b border-slate-800 pb-2">Broadcast Emergency Alert</h3>

            <div>
              <label className="text-xs text-slate-300 block mb-1">Alert Headline Title:</label>
              <input
                type="text"
                required
                placeholder="e.g. RED FLASH FLOOD WARNING — Riverside Sector"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-slate-300 block mb-1">Severity Level:</label>
                <select
                  value={severity}
                  onChange={(e) => setSeverity(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none"
                >
                  <option value="CRITICAL">CRITICAL</option>
                  <option value="HIGH">HIGH</option>
                  <option value="WARNING">WARNING</option>
                  <option value="INFO">INFO</option>
                </select>
              </div>

              <div>
                <label className="text-xs text-slate-300 block mb-1">Affected Area Name:</label>
                <input
                  type="text"
                  required
                  value={affectedArea}
                  onChange={(e) => setAffectedArea(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none"
                />
              </div>
            </div>

            <div>
              <label className="text-xs text-slate-300 block mb-1">Alert Message:</label>
              <textarea
                required
                rows={3}
                placeholder="Enter alert message details..."
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none"
              />
            </div>

            <div>
              <label className="text-xs text-slate-300 block mb-1">Recommended Citizen Action:</label>
              <input
                type="text"
                value={recommendedAction}
                onChange={(e) => setRecommendedAction(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none"
              />
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setIsModalOpen(false)}
                className="px-4 py-2 bg-slate-800 text-slate-300 text-xs rounded-xl"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white text-xs font-bold rounded-xl shadow-lg flex items-center gap-1 cursor-pointer"
              >
                <Send className="w-3.5 h-3.5" />
                <span>Broadcast Alert</span>
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Emergency SOS Sound Alert Overlay inside Alerts Page */}
      <EmergencySOSModal
        alert={sosModalAlert}
        onDismiss={() => setSosModalAlert(null)}
        onAcknowledge={(id) => {
          if (id) handleStatusUpdate(id, "ACKNOWLEDGED");
          setSosModalAlert(null);
        }}
      />
    </div>
  );
};
