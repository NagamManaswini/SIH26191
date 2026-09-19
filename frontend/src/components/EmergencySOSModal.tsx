import React, { useEffect, useState } from "react";
import { ShieldAlert, Volume2, VolumeX, AlertTriangle, CheckCircle, Radio } from "lucide-react";
import { sosSoundService } from "../services/sosSoundService";

export interface EmergencyAlertData {
  id?: number;
  title: string;
  message: string;
  severity: "INFO" | "WARNING" | "HIGH" | "CRITICAL";
  affected_area: string;
  recommended_action: string;
  safe_shelter?: string;
  recommended_route?: string;
  timestamp?: string;
}

interface EmergencySOSModalProps {
  alert: EmergencyAlertData | null;
  onDismiss: () => void;
  onAcknowledge?: (id?: number) => void;
}

export const EmergencySOSModal: React.FC<EmergencySOSModalProps> = ({ alert, onDismiss, onAcknowledge }) => {
  const [isAudioAllowed, setIsAudioAllowed] = useState<boolean>(sosSoundService.getIsAudioAllowed());
  const [isMuted, setIsMuted] = useState<boolean>(sosSoundService.getIsMuted());

  useEffect(() => {
    if (alert && alert.severity === "CRITICAL") {
      sosSoundService.startRepeatingSOS();
    } else {
      sosSoundService.stopSOS();
    }

    return () => {
      sosSoundService.stopSOS();
    };
  }, [alert]);

  if (!alert) return null;

  const handleEnableSound = () => {
    const success = sosSoundService.enableAudio();
    setIsAudioAllowed(success);
    if (success) {
      sosSoundService.startRepeatingSOS();
    }
  };

  const handleToggleMute = () => {
    const muted = sosSoundService.toggleMute();
    setIsMuted(muted);
  };

  const handleTestSound = () => {
    sosSoundService.testSound();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fade-in font-sans">
      <div className="relative w-full max-w-2xl bg-white dark:bg-slate-900 rounded-3xl shadow-2xl border-4 border-rose-600 overflow-hidden">
        {/* Flashing Emergency Header */}
        <div className="bg-rose-600 text-white p-5 flex items-center justify-between animate-pulse">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-white/20 flex items-center justify-center">
              <Radio className="w-7 h-7 text-white animate-bounce" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="bg-white text-rose-700 text-[10px] font-black px-2 py-0.5 rounded tracking-wider uppercase">
                  EMERGENCY SOS BROADCAST
                </span>
                <span className="text-xs font-bold text-rose-100">HIGH SEVERITY</span>
              </div>
              <h2 className="text-xl font-black tracking-tight uppercase text-white mt-0.5">
                {alert.title || "CRITICAL LANDSLIDE RISK DETECTED"}
              </h2>
            </div>
          </div>
          <ShieldAlert className="w-10 h-10 text-rose-200 shrink-0" />
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-5 text-slate-800 dark:text-slate-100">
          <div className="p-4 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800/60 rounded-2xl flex items-start gap-3">
            <AlertTriangle className="w-6 h-6 text-rose-600 shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-bold text-rose-950 dark:text-rose-200">{alert.message}</p>
            </div>
          </div>

          {/* Key Emergency Matrix Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-slate-100 dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700">
              <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">Affected Location</span>
              <p className="text-base font-extrabold text-slate-900 dark:text-white mt-1">
                {alert.affected_area || "Village / Zone X (Chooralmala & Mundakkai)"}
              </p>
            </div>

            <div className="p-4 bg-rose-100/70 dark:bg-rose-900/30 rounded-2xl border border-rose-300 dark:border-rose-700">
              <span className="text-[11px] font-bold text-rose-700 dark:text-rose-300 uppercase tracking-wider block">Recommended Action</span>
              <p className="text-base font-black text-rose-700 dark:text-rose-300 mt-1 uppercase">
                {alert.recommended_action || "IMMEDIATE EVACUATION"}
              </p>
            </div>

            <div className="p-4 bg-emerald-50 dark:bg-emerald-950/30 rounded-2xl border border-emerald-200 dark:border-emerald-800">
              <span className="text-[11px] font-bold text-emerald-700 dark:text-emerald-400 uppercase tracking-wider block">Safe Relief Shelter</span>
              <p className="text-base font-extrabold text-emerald-900 dark:text-emerald-200 mt-1">
                {alert.safe_shelter || "St. Joseph Higher Secondary School Shelter (B)"}
              </p>
            </div>

            <div className="p-4 bg-indigo-50 dark:bg-indigo-950/30 rounded-2xl border border-indigo-200 dark:border-indigo-800">
              <span className="text-[11px] font-bold text-indigo-700 dark:text-indigo-400 uppercase tracking-wider block">Recommended Safe Route</span>
              <p className="text-base font-extrabold text-indigo-900 dark:text-indigo-200 mt-1">
                {alert.recommended_route || "North Ridge Highway Detour (Route 2)"}
              </p>
            </div>
          </div>

          {/* Audio Permission & Controls Section */}
          <div className="p-4 bg-slate-50 dark:bg-slate-800/80 rounded-2xl border border-slate-200 dark:border-slate-700 flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              {isMuted ? (
                <VolumeX className="w-5 h-5 text-amber-500" />
              ) : (
                <Volume2 className="w-5 h-5 text-emerald-500 animate-pulse" />
              )}
              <span className="text-xs font-bold text-slate-700 dark:text-slate-300">
                {!isAudioAllowed ? "Audio Blocked by Browser" : isMuted ? "Sound Muted" : "Emergency SOS Audio Playing"}
              </span>
            </div>

            <div className="flex items-center gap-2">
              {!isAudioAllowed ? (
                <button
                  onClick={handleEnableSound}
                  className="px-3 py-1.5 bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-xs font-extrabold shadow-md transition-all"
                >
                  Enable Emergency Audio
                </button>
              ) : (
                <>
                  <button
                    onClick={handleTestSound}
                    className="px-3 py-1.5 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 text-slate-800 dark:text-slate-200 rounded-xl text-xs font-bold transition-all"
                  >
                    Test Audio Tone
                  </button>
                  <button
                    onClick={handleToggleMute}
                    className={`px-3 py-1.5 rounded-xl text-xs font-extrabold transition-all border ${
                      isMuted
                        ? "bg-emerald-600 text-white border-emerald-500"
                        : "bg-amber-100 text-amber-900 border-amber-300 dark:bg-amber-950 dark:text-amber-300"
                    }`}
                  >
                    {isMuted ? "Unmute Alarm" : "Mute Sound"}
                  </button>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Modal Footer Controls */}
        <div className="p-5 bg-slate-100 dark:bg-slate-950 border-t border-slate-200 dark:border-slate-800 flex items-center justify-end gap-3">
          <button
            onClick={() => {
              sosSoundService.stopSOS();
              if (onAcknowledge) onAcknowledge(alert.id);
              onDismiss();
            }}
            className="flex items-center gap-2 px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-sm rounded-xl shadow-md transition-all cursor-pointer"
          >
            <CheckCircle className="w-4 h-4" />
            Acknowledge & Stop SOS Alarm
          </button>
        </div>
      </div>
    </div>
  );
};
