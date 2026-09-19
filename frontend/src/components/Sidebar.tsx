import React from "react";
import {
  LayoutDashboard,
  MapPin,
  Flame,
  Home,
  Gauge,
  Navigation,
  RefreshCw,
  Bell,
  Activity,
  ShieldAlert,
  WifiOff,
  User,
  Bot,
  Dog,
  Radio,
  Users,
  Building2,
  HeartPulse,
  Ambulance,
  ClipboardList,
  AlertCircle,
  Stethoscope,
  Settings,
  LogOut,
  FileText,
} from "lucide-react";
import { UserAuth } from "../pages/LoginPage";

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  isOffline?: boolean;
  user: UserAuth | null;
  onLogout: () => void;
}

export const navItems = [
  { id: "overview", label: "Overview Dashboard", icon: LayoutDashboard, roles: ["admin", "responder"] },
  { id: "user-portal", label: "Citizen Safety Portal", icon: User, roles: ["user"] },
  { id: "map", label: "Live Hazard Map", icon: MapPin, roles: ["admin", "user", "responder"] },
  { id: "hospitals", label: "Hospitals & Medical", icon: Building2, roles: ["admin", "user", "responder"] },
  { id: "red-zone", label: "Red Zones", icon: Flame, roles: ["admin", "responder"] },
  { id: "population", label: "Population Metrics", icon: Users, roles: ["admin", "responder"] },
  { id: "shelters", label: "Shelters & Capacity", icon: Home, roles: ["admin", "user", "responder"] },
  { id: "evacuation", label: "Evacuation Planning", icon: Navigation, roles: ["admin", "user", "responder"] },
  { id: "relocation", label: "Relocation Plan", icon: RefreshCw, roles: ["admin", "responder"] },
  { id: "animal-safety", label: "Animal Safety", icon: Dog, roles: ["admin", "user", "responder"] },
  { id: "communication", label: "Communication", icon: Radio, roles: ["admin", "user", "responder"] },
  { id: "ai-assistant", label: "AI Assistant", icon: Bot, roles: ["admin", "user", "responder"] },
  { id: "alerts", label: "Disaster Alerts", icon: Bell, roles: ["admin", "user", "responder"] },
  { id: "offline", label: "Offline Mode", icon: WifiOff, roles: ["admin", "user", "responder"] },
  { id: "health", label: "System Health", icon: Activity, roles: ["admin"] },
  // ── Hospital portal nav items ──────────────────────────────────────────
  { id: "hospital-dashboard", label: "Dashboard", icon: LayoutDashboard, roles: ["hospital"] },
  { id: "hospital-profile", label: "Hospital Profile", icon: Stethoscope, roles: ["hospital"] },
  { id: "hospital-capacity", label: "Bed Capacity", icon: HeartPulse, roles: ["hospital"] },
  { id: "hospital-emergency", label: "Emergency Requests", icon: AlertCircle, roles: ["hospital"] },
  { id: "hospital-patients", label: "Patients", icon: ClipboardList, roles: ["hospital"] },
  { id: "hospital-ambulances", label: "Ambulances", icon: Ambulance, roles: ["hospital"] },
  { id: "hospital-alerts", label: "Alerts", icon: Bell, roles: ["hospital"] },
  { id: "hospital-assignments", label: "Disaster Assignments", icon: FileText, roles: ["hospital"] },
  { id: "map", label: "Map", icon: MapPin, roles: ["hospital"] },
  { id: "communication", label: "Communication", icon: Radio, roles: ["hospital"] },
  { id: "hospital-settings", label: "Settings", icon: Settings, roles: ["hospital"] },
];


export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab, isOffline, user, onLogout }) => {
  const currentRole = user?.role || "admin";
  const visibleNavItems = navItems.filter((item) => item.roles.includes(currentRole));
  const isHospital = currentRole === "hospital";

  const sidebarBg = isHospital ? "bg-emerald-950" : "bg-indigo-950";
  const borderColor = isHospital ? "border-emerald-900" : "border-indigo-900";
  const headerBg = isHospital ? "bg-emerald-600 border-emerald-400" : "bg-pink-600 border-pink-400";
  const activeItemBg = isHospital ? "bg-emerald-800 text-emerald-100 border border-emerald-600" : "bg-indigo-800 text-amber-300 border border-indigo-600";
  const inactiveText = isHospital ? "text-emerald-100 hover:text-white hover:bg-emerald-900/80" : "text-indigo-100 hover:text-white hover:bg-indigo-900/80";
  const iconActiveClass = isHospital ? "text-emerald-200" : "text-amber-300";
  const iconInactiveClass = isHospital ? "text-emerald-400" : "text-indigo-300";

  return (
    <aside className={`w-64 ${sidebarBg} border-r ${borderColor} flex flex-col h-screen sticky top-0 z-30 shrink-0 font-sans shadow-xl text-white`}>
      {/* Brand Header */}
      <div className={`p-5 border-b ${borderColor} flex items-center gap-3`}>
        <div className={`w-10 h-10 rounded-xl ${headerBg} flex items-center justify-center shadow-lg border`}>
          {isHospital ? <HeartPulse className="w-6 h-6 text-white" /> : <ShieldAlert className="w-6 h-6 text-white" />}
        </div>
        <div>
          <h1 className="font-extrabold text-white text-sm tracking-wide">
            {isHospital ? "HOSPITAL PORTAL" : "DISASTER PLATFORM"}
          </h1>
          <p className={`text-xs font-bold ${isHospital ? "text-emerald-300" : "text-amber-300"}`}>
            {isHospital ? (user?.hospitalName || "Hospital Dashboard") : "CWC Warning Portal"}
          </p>
        </div>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        <div className={`px-3 py-2 text-[10px] font-extrabold uppercase tracking-wider ${isHospital ? "text-emerald-300" : "text-indigo-300"}`}>
          {isHospital ? "Hospital Management" : user?.role === "user" ? "Citizen Emergency Menu" : "Control Center Modules"}
        </div>
        {visibleNavItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={`${item.id}-${item.roles.join("")}`}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-3 px-3.5 py-3 rounded-xl text-xs font-extrabold transition-all cursor-pointer ${
                isActive ? `${activeItemBg} shadow-md font-black` : `${inactiveText}`
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? iconActiveClass : iconInactiveClass}`} />
              <span>{item.label}</span>
              {item.id === "offline" && isOffline && (
                <span className="ml-auto bg-amber-400 text-slate-950 text-[9px] font-black px-1.5 py-0.5 rounded uppercase animate-pulse">
                  ACTIVE
                </span>
              )}
              {item.id === "hospital-emergency" && isHospital && (
                <span className="ml-auto bg-red-500 text-white text-[9px] font-black px-1.5 py-0.5 rounded uppercase animate-pulse">
                  LIVE
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Footer — Logout */}
      <div className={`p-4 border-t ${borderColor} ${sidebarBg}`}>
        {isHospital ? (
          <button
            onClick={onLogout}
            className="w-full flex items-center gap-3 px-3.5 py-3 rounded-xl text-xs font-extrabold text-emerald-200 hover:text-white hover:bg-emerald-900 transition-all cursor-pointer"
          >
            <LogOut className="w-4 h-4 text-emerald-400" />
            <span>Logout</span>
          </button>
        ) : (
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${isOffline ? "bg-amber-400 animate-ping" : "bg-emerald-400 animate-pulse"}`}></span>
              <span className="text-indigo-100 font-bold">{isOffline ? "Offline Mode" : "Live Operations Engine"}</span>
            </div>
            <span className={`text-[10px] px-2 py-0.5 rounded font-black border ${
              isOffline ? "bg-amber-400 text-slate-950 border-amber-300" : "bg-emerald-600 text-white border-emerald-400"
            }`}>
              {isOffline ? "CACHED" : "ONLINE"}
            </span>
          </div>
        )}
      </div>
    </aside>
  );
};
