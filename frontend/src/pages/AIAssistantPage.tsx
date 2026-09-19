import React, { useState } from "react";
import {
  Bot,
  Send,
  Trash2,
  AlertTriangle,
  Database,
  Sparkles,
  ShieldCheck,
  HelpCircle,
  Loader2,
  Info,
} from "lucide-react";
import { api } from "../api/apiClient";

interface MessageItem {
  id: string;
  sender: "user" | "assistant";
  text: string;
  sources?: string[];
  relatedData?: any;
  timestamp: string;
}

export const AIAssistantPage: React.FC = () => {
  const [messages, setMessages] = useState<MessageItem[]>([
    {
      id: "welcome-1",
      sender: "assistant",
      text: "Hello! I am your AI Disaster Management Assistant. I provide decision support grounded strictly in verified database state, hazard models, shelter capacity, and route calculations. How can I assist disaster operations today?",
      sources: ["SIH26191 Verified Project Knowledge Base"],
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    },
  ]);

  const [inputQuery, setInputQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const suggestedQuestions = [
    "What areas are currently in the Red Zone?",
    "How many people are affected?",
    "Which shelters have available capacity?",
    "Which shelters are overcrowded?",
    "Which evacuation route is recommended?",
    "Why was this area classified as high risk?",
    "What should authorities do during the current situation?",
    "Which vulnerable population groups need priority?",
    "What happens if rainfall increases?",
    "Which areas should be monitored closely?",
  ];

  const handleSendMessage = async (textToSend?: string) => {
    const query = (textToSend || inputQuery).trim();
    if (!query || isLoading) return;

    const userMsg: MessageItem = {
      id: `user-${Date.now()}`,
      sender: "user",
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInputQuery("");
    setIsLoading(true);
    setErrorMsg("");

    try {
      const res = await api.chatWithAssistant(query);

      const assistantMsg: MessageItem = {
        id: `assistant-${Date.now()}`,
        sender: "assistant",
        text: res.answer,
        sources: res.sources || [],
        relatedData: res.related_data || {},
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      setErrorMsg("Failed to communicate with AI Assistant service. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([
      {
        id: `welcome-${Date.now()}`,
        sender: "assistant",
        text: "Chat history cleared. I am ready for your next disaster operational question.",
        sources: ["System Reset"],
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      },
    ]);
    setErrorMsg("");
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto font-sans bg-slate-50 dark:bg-slate-950 min-h-screen text-slate-900 dark:text-slate-100 flex flex-col">
      {/* Header Banner */}
      <div className="bg-indigo-950 text-white rounded-3xl p-6 shadow-xl border border-indigo-900 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-pink-500 to-indigo-600 flex items-center justify-center shadow-lg border border-pink-400">
            <Bot className="w-8 h-8 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="bg-pink-600 text-white text-[10px] font-black px-2.5 py-0.5 rounded tracking-wider uppercase">
                DECISION SUPPORT AI
              </span>
              <span className="text-xs text-indigo-300 font-bold flex items-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> Grounded Database Intelligence
              </span>
            </div>
            <h1 className="text-2xl font-black tracking-tight mt-1 text-white">
              AI Disaster Management Assistant
            </h1>
          </div>
        </div>

        <button
          onClick={handleClearChat}
          className="flex items-center gap-2 px-4 py-2.5 rounded-2xl bg-indigo-900 hover:bg-indigo-800 text-indigo-200 text-xs font-black transition-all cursor-pointer border border-indigo-700"
        >
          <Trash2 className="w-4 h-4 text-pink-400" />
          Clear Conversation
        </button>
      </div>

      {/* Main Chat Interface */}
      <div className="flex-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl shadow-xl flex flex-col overflow-hidden min-h-[500px]">
        {/* Suggested Quick Questions Toolbar */}
        <div className="p-4 bg-slate-100 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-800">
          <span className="text-[11px] font-extrabold text-slate-500 dark:text-slate-400 uppercase tracking-wider block mb-2.5 flex items-center gap-1.5">
            <HelpCircle className="w-3.5 h-3.5 text-indigo-500" /> Suggested Official Operations Inquiries:
          </span>
          <div className="flex flex-wrap gap-2">
            {suggestedQuestions.map((q, idx) => (
              <button
                key={idx}
                onClick={() => handleSendMessage(q)}
                className="px-3 py-1.5 rounded-xl bg-white dark:bg-slate-700 hover:bg-indigo-50 dark:hover:bg-indigo-950 text-indigo-900 dark:text-indigo-200 text-xs font-bold border border-slate-200 dark:border-slate-600 transition-all cursor-pointer shadow-sm text-left"
              >
                {q}
              </button>
            ))}
          </div>
        </div>

        {/* Chat Messages Log */}
        <div className="flex-1 p-6 space-y-6 overflow-y-auto max-h-[550px]">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex items-start gap-3.5 ${
                msg.sender === "user" ? "flex-row-reverse" : "flex-row"
              }`}
            >
              <div
                className={`w-10 h-10 rounded-2xl flex items-center justify-center shrink-0 font-extrabold text-sm ${
                  msg.sender === "user"
                    ? "bg-indigo-600 text-white"
                    : "bg-pink-600 text-white shadow-md"
                }`}
              >
                {msg.sender === "user" ? "YOU" : <Bot className="w-5 h-5" />}
              </div>

              <div
                className={`max-w-2xl rounded-3xl p-5 space-y-3 ${
                  msg.sender === "user"
                    ? "bg-indigo-600 text-white rounded-tr-none shadow-md"
                    : "bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-slate-100 rounded-tl-none border border-slate-200 dark:border-slate-700 shadow-md"
                }`}
              >
                <div className="flex items-center justify-between gap-4 text-[11px] opacity-80 border-b border-black/10 dark:border-white/10 pb-2">
                  <span className="font-extrabold uppercase">
                    {msg.sender === "user" ? "Disaster Official Query" : "AI Decision Support Engine"}
                  </span>
                  <span>{msg.timestamp}</span>
                </div>

                <p className="text-sm font-medium leading-relaxed whitespace-pre-line">{msg.text}</p>

                {/* Sources & Verified Grounded References */}
                {msg.sources && msg.sources.length > 0 && (
                  <div className="pt-2 border-t border-slate-200 dark:border-slate-700/60 flex flex-wrap items-center gap-2">
                    <span className="text-[10px] font-black text-slate-500 dark:text-slate-400 uppercase flex items-center gap-1">
                      <Database className="w-3 h-3 text-indigo-500" /> Grounded Sources:
                    </span>
                    {msg.sources.map((src, idx) => (
                      <span
                        key={idx}
                        className="bg-indigo-100 dark:bg-indigo-950 text-indigo-800 dark:text-indigo-300 text-[10px] font-bold px-2 py-0.5 rounded-lg border border-indigo-200 dark:border-indigo-800"
                      >
                        ✓ {src}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex items-center gap-3 p-4 bg-indigo-50 dark:bg-indigo-950/40 rounded-2xl border border-indigo-200 dark:border-indigo-800/60 text-indigo-900 dark:text-indigo-300 text-xs font-bold animate-pulse w-fit">
              <Loader2 className="w-5 h-5 animate-spin text-pink-600" />
              <span>Querying GIS risk model, shelter capacities, and active alerts...</span>
            </div>
          )}

          {errorMsg && (
            <div className="p-4 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-300 rounded-2xl text-xs font-bold flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}
        </div>

        {/* Input Bar */}
        <div className="p-4 bg-slate-100 dark:bg-slate-800/80 border-t border-slate-200 dark:border-slate-800 space-y-3">
          <div className="flex items-center gap-3">
            <input
              type="text"
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
              placeholder="Ask the AI Assistant about Red Zones, shelter capacity, evacuation routes, or population priority..."
              className="flex-1 px-5 py-3.5 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-2xl text-sm font-semibold text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-pink-500 shadow-inner"
            />
            <button
              onClick={() => handleSendMessage()}
              disabled={isLoading || !inputQuery.trim()}
              className="px-6 py-3.5 bg-pink-600 hover:bg-pink-700 disabled:opacity-50 text-white font-extrabold text-sm rounded-2xl shadow-lg transition-all flex items-center gap-2 cursor-pointer"
            >
              <Send className="w-4 h-4" />
              Send
            </button>
          </div>

          {/* Mandatory Disclaimer */}
          <div className="flex items-center gap-2 text-[11px] text-slate-500 dark:text-slate-400 font-bold px-1">
            <Info className="w-3.5 h-3.5 text-amber-500 shrink-0" />
            <span>
              <b>Disclaimer:</b> AI-generated recommendations are decision-support information and should be verified by authorized disaster-management personnel.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
