import React, { useState } from "react";
import { ShieldAlert, User, Lock, ArrowRight, ShieldCheck, PhoneCall, AlertTriangle, Building2, Sparkles } from "lucide-react";

export interface UserAuth {
  email: string;
  name: string;
  role: "admin" | "user" | "responder" | "hospital";
  token: string;
  hospitalId?: number;
  hospitalName?: string;
}

interface LoginPageProps {
  onLogin: (auth: UserAuth) => void;
}

const SAMPLE_CREDENTIALS: Record<string, { email: string; pass: string; title: string }> = {
  admin: { email: "admin@disaster.gov.in", pass: "admin123", title: "Command Chief Officer" },
  user: { email: "citizen@disaster.gov.in", pass: "user123", title: "Wayanad Citizen Resident" },
  responder: { email: "responder@disaster.gov.in", pass: "field123", title: "NDRF Field Ops Captain" },
  hospital: { email: "hospital@ggh.example", pass: "Hospital#2026", title: "Govt General Hospital Officer" },
};

export const LoginPage: React.FC<LoginPageProps> = ({ onLogin }) => {
  const [role, setRole] = useState<"admin" | "user" | "responder" | "hospital">("admin");
  const [email, setEmail] = useState<string>("admin@disaster.gov.in");
  const [password, setPassword] = useState<string>("admin123");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>("");

  const handleRoleSelect = (selectedRole: "admin" | "user" | "responder" | "hospital") => {
    setRole(selectedRole);
    setError("");
    const cred = SAMPLE_CREDENTIALS[selectedRole];
    if (cred) {
      setEmail(cred.email);
      setPassword(cred.pass);
    }
  };

  const handleAutoFill = () => {
    const cred = SAMPLE_CREDENTIALS[role];
    if (cred) {
      setEmail(cred.email);
      setPassword(cred.pass);
      setError("");
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !password.trim()) {
      setError("Please enter your email/username and password.");
      return;
    }

    setIsLoading(true);
    setError("");

    setTimeout(() => {
      setIsLoading(false);
      const nameMap: Record<string, string> = {
        admin: "Command Chief Officer",
        user: "Wayanad Citizen Portal User",
        responder: "NDRF Field Ops Captain",
        hospital: "Government General Hospital",
      };

      onLogin({
        email,
        name: nameMap[role] || email.split("@")[0],
        role,
        token: `jwt-token-${role}-${Date.now()}`,
        hospitalId: role === "hospital" ? 1 : undefined,
        hospitalName: role === "hospital" ? "Government General Hospital" : undefined,
      });
    }, 400);
  };

  const roleConfig = [
    { id: "admin" as const, label: "Admin", icon: ShieldCheck },
    { id: "user" as const, label: "Citizen", icon: User },
    { id: "responder" as const, label: "Field Ops", icon: PhoneCall },
    { id: "hospital" as const, label: "Hospital", icon: Building2 },
  ];

  const currentSample = SAMPLE_CREDENTIALS[role];

  return (
    <div className="min-h-screen w-screen bg-gradient-to-br from-indigo-950 via-blue-900 to-indigo-950 flex items-center justify-center p-4 relative overflow-hidden font-sans">
      <div className="absolute -top-40 -left-40 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl pointer-events-none animate-pulse"></div>
      <div className="absolute -bottom-40 -right-40 w-96 h-96 bg-emerald-400/20 rounded-full blur-3xl pointer-events-none"></div>
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-indigo-800/10 rounded-full blur-3xl pointer-events-none"></div>

      <div className="w-full max-w-md bg-white/95 border border-slate-200 rounded-3xl shadow-2xl p-8 z-10 relative text-slate-900">
        <div className="flex flex-col items-center text-center mb-6">
          <div className="w-14 h-14 rounded-2xl bg-pink-600 flex items-center justify-center shadow-lg border border-pink-400 mb-3">
            <ShieldAlert className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-black tracking-tight text-indigo-950">DISASTER MANAGEMENT SYSTEM</h1>
          <p className="text-xs text-slate-500 font-medium mt-1">Central Warning & Emergency Control System</p>
        </div>

        {/* Role Selector Tabs */}
        <div className="grid grid-cols-4 gap-1.5 bg-slate-100 p-1.5 rounded-xl border border-slate-200 mb-4">
          {roleConfig.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              type="button"
              id={`role-tab-${id}`}
              onClick={() => handleRoleSelect(id)}
              className={`py-2 px-1 rounded-lg text-[10px] font-black transition-all flex flex-col items-center justify-center gap-1 cursor-pointer ${
                role === id
                  ? "bg-indigo-950 text-amber-300 shadow border border-indigo-800"
                  : "text-slate-600 hover:text-indigo-950 hover:bg-slate-200"
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{label}</span>
            </button>
          ))}
        </div>

        <div className="flex items-center justify-between mb-4">
          <span className={`px-3 py-1 rounded-full text-[11px] font-extrabold uppercase tracking-wider ${
            role === "admin" ? "bg-indigo-100 text-indigo-800" :
            role === "user" ? "bg-blue-100 text-blue-800" :
            role === "responder" ? "bg-amber-100 text-amber-800" :
            "bg-emerald-100 text-emerald-800"
          }`}>
            {role === "admin" ? "🛡️ Admin Portal" :
             role === "user" ? "👤 Citizen Portal" :
             role === "responder" ? "📡 Field Operator Portal" :
             "🏥 Hospital Portal"}
          </span>

          <button
            type="button"
            onClick={handleAutoFill}
            className="flex items-center gap-1 text-[11px] text-pink-600 hover:text-pink-700 font-extrabold bg-pink-50 hover:bg-pink-100 px-2.5 py-1 rounded-lg border border-pink-200 cursor-pointer transition-all"
            title="Auto-fill sample credentials for this role"
          >
            <Sparkles className="w-3 h-3" />
            <span>Fill Sample</span>
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-xl bg-red-50 border border-red-300 text-red-950 text-xs flex items-center gap-2 font-bold">
            <AlertTriangle className="w-4 h-4 text-red-600" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1.5">Email / Username</label>
            <div className="relative">
              <User className="w-4 h-4 text-indigo-600 absolute left-3 top-3" />
              <input
                type="text"
                id="login-email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded-xl pl-9 pr-4 py-2.5 text-xs text-indigo-950 font-bold focus:outline-none focus:border-indigo-600 transition-colors"
                placeholder={
                  role === "admin" ? "admin@disaster.gov.in" :
                  role === "responder" ? "responder@disaster.gov.in" :
                  role === "hospital" ? "hospital@ggh.example" :
                  "citizen@disaster.gov.in"
                }
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1.5">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-indigo-600 absolute left-3 top-3" />
              <input
                type="password"
                id="login-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded-xl pl-9 pr-4 py-2.5 text-xs text-indigo-950 font-bold focus:outline-none focus:border-indigo-600 transition-colors"
                placeholder="••••••••"
              />
            </div>
          </div>

          <button
            type="submit"
            id="login-submit"
            disabled={isLoading}
            className="w-full py-3.5 rounded-xl text-xs font-black text-white flex items-center justify-center gap-2 shadow-md transition-all uppercase tracking-wider bg-pink-600 hover:bg-pink-500 border border-pink-400 cursor-pointer"
          >
            {isLoading ? (
              <span>Authenticating Credentials...</span>
            ) : (
              <>
                <span>Sign In to {role === "hospital" ? "Hospital" : role.toUpperCase()} Dashboard</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};



