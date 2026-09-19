import React, { useEffect, useState } from "react";
import {
  MessageSquare,
  Radio,
  Send,
  Plus,
  Filter,
  CheckCircle2,
  AlertTriangle,
  Megaphone,
  Smartphone,
  Mail,
  Building,
  Trash2,
} from "lucide-react";
import { api } from "../api/apiClient";
import { UserAuth } from "./LoginPage";

interface CommunityCommunicationPageProps {
  user?: UserAuth | null;
  currentLocation?: { name: string; lat: number; lon: number };
}

export const CommunityCommunicationPage: React.FC<CommunityCommunicationPageProps> = ({ user, currentLocation }) => {
  const activeLoc = currentLocation || { name: "Chennai, Tamil Nadu", lat: 13.0827, lon: 80.2707 };
  const cityName = activeLoc.name.split(",")[0].trim();
  const isAdmin = !user || user.role === "admin";

  const [messages, setMessages] = useState<any[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>("ALL");
  const [selectedArea, setSelectedArea] = useState<string>("ALL");
  const [showBroadcastModal, setShowBroadcastModal] = useState(false);
  const [showPostModal, setShowPostModal] = useState(false);

  // Broadcast Form State
  const [bTitle, setBTitle] = useState("");
  const [bMessage, setBMessage] = useState("");
  const [bArea, setBArea] = useState(`${cityName} Sector`);

  // Post Message Form State
  const [pCategory, setPCategory] = useState("GENERAL");
  const [pTitle, setPTitle] = useState("");
  const [pMessage, setPMessage] = useState("");
  const [pArea, setPArea] = useState(`${cityName} Sector`);
  const [pSeverity, setPSeverity] = useState("INFO");

  useEffect(() => {
    loadMessages();
  }, [selectedCategory, selectedArea]);

  const loadMessages = async () => {
    const cat = selectedCategory === "ALL" ? undefined : selectedCategory;
    const area = selectedArea === "ALL" ? undefined : selectedArea;
    const msgs = await api.getCommunicationMessages(cat, area);
    setMessages(msgs);
  };

  const handleDeleteMessage = async (id: number) => {
    if (user && user.role !== "admin") {
      alert("Permission denied: Only Admin Command Officers can delete announcements.");
      return;
    }
    await api.deleteCommunicationMessage(id);
    setMessages((prev) => prev.filter((m) => m.id !== id));
  };

  const handleSendBroadcast = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!bTitle || !bMessage) return;
    const res = await api.sendEmergencyBroadcast({
      title: bTitle,
      message: bMessage,
      target_area: bArea,
      category: "EMERGENCY",
      severity: "CRITICAL",
    });
    if (res) {
      setMessages((prev) => [res, ...prev.filter((m) => m.id !== res.id)]);
    }
    setBTitle("");
    setBMessage("");
    setShowBroadcastModal(false);
    loadMessages();
  };

  const handlePostMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!pTitle || !pMessage) return;
    const res = await api.postCommunicationMessage({
      category: pCategory,
      title: pTitle,
      message: pMessage,
      target_area: pArea,
      severity: pSeverity,
      sender_name: user?.name || "Disaster Command Center",
      sender_role: user?.role || "admin",
      is_emergency_broadcast: pSeverity === "CRITICAL",
    });
    if (res) {
      setMessages((prev) => [res, ...prev.filter((m) => m.id !== res.id)]);
    }
    setPTitle("");
    setPMessage("");
    setShowPostModal(false);
    loadMessages();
  };

  const categories = [
    "ALL",
    "GENERAL",
    "EVACUATION",
    "ANIMAL_SAFETY",
    "SHELTER",
    "ROAD_BLOCK",
    "WEATHER",
    "EMERGENCY",
  ];

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto font-sans bg-slate-50 dark:bg-slate-950 min-h-screen text-slate-900 dark:text-slate-100">
      {/* Header Banner */}
      <div className="bg-indigo-950 text-white rounded-3xl p-6 shadow-xl border border-indigo-900 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-pink-500 to-indigo-600 flex items-center justify-center shadow-lg border border-pink-400">
            <Radio className="w-8 h-8 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="bg-pink-600 text-white text-[10px] font-black px-2.5 py-0.5 rounded tracking-wider uppercase">
                COMMUNITY COMMUNICATION CENTER
              </span>
            </div>
            <h1 className="text-2xl font-black tracking-tight mt-1 text-white">
              Official Disaster Announcements & Broadcasts
            </h1>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowPostModal(true)}
            className="flex items-center gap-2 px-4 py-2.5 rounded-2xl bg-indigo-800 hover:bg-indigo-700 text-white text-xs font-black transition-all cursor-pointer border border-indigo-600"
          >
            <Plus className="w-4 h-4 text-pink-400" />
            Post Announcement
          </button>
          <button
            onClick={() => setShowBroadcastModal(true)}
            className="flex items-center gap-2 px-5 py-2.5 rounded-2xl bg-rose-600 hover:bg-rose-700 text-white font-black text-xs shadow-lg transition-all cursor-pointer"
          >
            <Megaphone className="w-4 h-4 animate-bounce" />
            Send Emergency Broadcast
          </button>
        </div>
      </div>

      {/* Notification Abstraction Layer Channels Info */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-5 shadow-md flex flex-wrap items-center justify-between gap-4 text-xs font-extrabold">
        <div className="flex items-center gap-2 text-indigo-950 dark:text-indigo-300">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
          <span>Multi-Channel Notification Abstraction Dispatcher Active:</span>
        </div>

        <div className="flex items-center gap-4 text-slate-700 dark:text-slate-300">
          <span className="flex items-center gap-1.5 bg-slate-100 dark:bg-slate-800 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-700">
            <Smartphone className="w-4 h-4 text-indigo-500" /> SMS Provider (Ready)
          </span>
          <span className="flex items-center gap-1.5 bg-slate-100 dark:bg-slate-800 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-700">
            <Radio className="w-4 h-4 text-pink-500" /> Web/Push Notifications
          </span>
          <span className="flex items-center gap-1.5 bg-slate-100 dark:bg-slate-800 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-700">
            <Mail className="w-4 h-4 text-amber-500" /> Email Gateway
          </span>
          <span className="flex items-center gap-1.5 bg-slate-100 dark:bg-slate-800 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-700">
            <Building className="w-4 h-4 text-emerald-500" /> Government Emergency Net
          </span>
        </div>
      </div>

      {/* Category Filter Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-white dark:bg-slate-900 p-4 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-md">
        <div className="flex flex-wrap gap-2 items-center">
          <span className="text-xs font-black text-slate-500 uppercase tracking-wider flex items-center gap-1 mr-2">
            <Filter className="w-3.5 h-3.5" /> Category:
          </span>
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1.5 rounded-xl text-xs font-black transition-all cursor-pointer ${
                selectedCategory === cat
                  ? "bg-indigo-600 text-white shadow-md"
                  : "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2 text-xs font-extrabold text-slate-600 dark:text-slate-300">
          <span>Target Sector:</span>
          <select
            value={selectedArea}
            onChange={(e) => setSelectedArea(e.target.value)}
            className="p-2 bg-slate-100 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl font-extrabold text-xs"
          >
            <option value="ALL">All Sectors</option>
            <option value="Chooralmala & Mundakkai">Chooralmala & Mundakkai</option>
            <option value="Wayanad Sector 1">Wayanad Sector 1</option>
            <option value="Idukki District">Idukki District</option>
          </select>
        </div>
      </div>

      {/* Feed Messages */}
      <div className="space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`p-6 rounded-3xl border shadow-lg space-y-3 transition-all ${
              msg.severity === "CRITICAL"
                ? "bg-rose-50 dark:bg-rose-950/40 border-rose-300 dark:border-rose-800"
                : msg.severity === "HIGH"
                ? "bg-amber-50 dark:bg-amber-950/30 border-amber-300 dark:border-amber-900"
                : "bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800"
            }`}
          >
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <span
                  className={`text-[10px] font-black px-2.5 py-0.5 rounded tracking-wider uppercase ${
                    msg.severity === "CRITICAL"
                      ? "bg-rose-600 text-white animate-pulse"
                      : msg.severity === "HIGH"
                      ? "bg-amber-500 text-slate-950"
                      : "bg-indigo-600 text-white"
                  }`}
                >
                  {msg.category} • {msg.severity}
                </span>

                {msg.is_emergency_broadcast && (
                  <span className="bg-rose-100 text-rose-700 text-[10px] font-black px-2 py-0.5 rounded uppercase border border-rose-300 flex items-center gap-1">
                    <Megaphone className="w-3 h-3" /> EMERGENCY BROADCAST
                  </span>
                )}
              </div>

              <span className="text-xs font-bold text-slate-500 dark:text-slate-400">
                {new Date(msg.created_at || Date.now()).toLocaleString()}
              </span>
            </div>

            <div>
              <h3 className="text-lg font-black text-slate-900 dark:text-white tracking-tight">{msg.title}</h3>
              <p className="text-sm font-medium text-slate-700 dark:text-slate-300 mt-1 leading-relaxed whitespace-pre-line">
                {msg.message}
              </p>
            </div>

            <div className="flex items-center justify-between text-xs font-bold text-slate-500 dark:text-slate-400 pt-3 border-t border-slate-200 dark:border-slate-800">
              <div>Sender: <b className="text-slate-800 dark:text-slate-200">{msg.sender_name}</b> ({msg.sender_role})</div>
              <div className="flex items-center gap-4">
                <div>Target Area: <b className="text-indigo-600 dark:text-indigo-400">{msg.target_area}</b></div>
                {isAdmin && (
                  <button
                    onClick={() => handleDeleteMessage(msg.id)}
                    className="flex items-center gap-1 bg-rose-600 hover:bg-rose-700 text-white font-black px-3 py-1 rounded-xl text-[11px] shadow transition-colors cursor-pointer"
                    title="Delete announcement (Admin Only)"
                  >
                    <Trash2 className="w-3.5 h-3.5" /> Delete
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Broadcast Modal */}
      {showBroadcastModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
          <div className="w-full max-w-lg bg-white dark:bg-slate-900 rounded-3xl p-6 shadow-2xl border-2 border-rose-600 space-y-4">
            <h3 className="text-base font-black text-rose-600 flex items-center gap-2">
              <Megaphone className="w-5 h-5 text-rose-600" /> Dispatch Emergency Broadcast
            </h3>
            <form onSubmit={handleSendBroadcast} className="space-y-3 text-xs">
              <div>
                <label className="font-bold text-slate-700 dark:text-slate-300 block mb-1">Target Geographic Sector *</label>
                <input
                  type="text"
                  required
                  value={bArea}
                  onChange={(e) => setBArea(e.target.value)}
                  className="w-full p-3 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 font-bold"
                />
              </div>

              <div>
                <label className="font-bold text-slate-700 dark:text-slate-300 block mb-1">Broadcast Title *</label>
                <input
                  type="text"
                  required
                  value={bTitle}
                  onChange={(e) => setBTitle(e.target.value)}
                  placeholder="e.g. MANDATORY EVACUATION ORDER — Sector 1"
                  className="w-full p-3 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 font-bold"
                />
              </div>

              <div>
                <label className="font-bold text-slate-700 dark:text-slate-300 block mb-1">Emergency Message Content *</label>
                <textarea
                  required
                  rows={4}
                  value={bMessage}
                  onChange={(e) => setBMessage(e.target.value)}
                  placeholder="Detailed evacuation route instructions and shelter destinations..."
                  className="w-full p-3 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 font-bold"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setShowBroadcastModal(false)}
                  className="px-4 py-2 bg-slate-200 dark:bg-slate-700 text-slate-800 dark:text-slate-200 rounded-xl font-bold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-rose-600 text-white font-extrabold rounded-xl shadow-md"
                >
                  Broadcast Now
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Post Announcement Modal */}
      {showPostModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
          <div className="w-full max-w-lg bg-white dark:bg-slate-900 rounded-3xl p-6 shadow-2xl border border-slate-200 dark:border-slate-800 space-y-4">
            <h3 className="text-base font-black text-slate-900 dark:text-white">Post Official Announcement</h3>
            <form onSubmit={handlePostMessage} className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-bold text-slate-700 dark:text-slate-300 block mb-1">Category</label>
                  <select
                    value={pCategory}
                    onChange={(e) => setPCategory(e.target.value)}
                    className="w-full p-3 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 font-bold"
                  >
                    <option value="GENERAL">GENERAL</option>
                    <option value="EVACUATION">EVACUATION</option>
                    <option value="ANIMAL_SAFETY">ANIMAL_SAFETY</option>
                    <option value="SHELTER">SHELTER</option>
                    <option value="ROAD_BLOCK">ROAD_BLOCK</option>
                    <option value="WEATHER">WEATHER</option>
                    <option value="EMERGENCY">EMERGENCY</option>
                  </select>
                </div>

                <div>
                  <label className="font-bold text-slate-700 dark:text-slate-300 block mb-1">Severity</label>
                  <select
                    value={pSeverity}
                    onChange={(e) => setPSeverity(e.target.value)}
                    className="w-full p-3 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 font-bold"
                  >
                    <option value="INFO">INFO</option>
                    <option value="WARNING">WARNING</option>
                    <option value="HIGH">HIGH</option>
                    <option value="CRITICAL">CRITICAL</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="font-bold text-slate-700 dark:text-slate-300 block mb-1">Target Area</label>
                <input
                  type="text"
                  value={pArea}
                  onChange={(e) => setPArea(e.target.value)}
                  placeholder="ALL or specific sector name"
                  className="w-full p-3 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 font-bold"
                />
              </div>

              <div>
                <label className="font-bold text-slate-700 dark:text-slate-300 block mb-1">Title *</label>
                <input
                  type="text"
                  required
                  value={pTitle}
                  onChange={(e) => setPTitle(e.target.value)}
                  className="w-full p-3 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 font-bold"
                />
              </div>

              <div>
                <label className="font-bold text-slate-700 dark:text-slate-300 block mb-1">Message Body *</label>
                <textarea
                  required
                  rows={4}
                  value={pMessage}
                  onChange={(e) => setPMessage(e.target.value)}
                  className="w-full p-3 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 font-bold"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setShowPostModal(false)}
                  className="px-4 py-2 bg-slate-200 dark:bg-slate-700 text-slate-800 dark:text-slate-200 rounded-xl font-bold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-indigo-600 text-white font-extrabold rounded-xl"
                >
                  Post Message
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
