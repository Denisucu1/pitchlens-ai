import React from "react";
import type { PersonaMode, Language, LiveMatchPayload } from "../types";
import { Play, Pause, FastForward, Globe, User, BarChart3, Tv, FileText } from "lucide-react";

interface NavbarProps {
  payload: LiveMatchPayload | null;
  persona: PersonaMode;
  setPersona: (p: PersonaMode) => void;
  language: Language;
  setLanguage: (l: Language) => void;
  isPaused: boolean;
  togglePause: () => void;
  speed: number;
  setSpeed: (s: number) => void;
  onOpenRecap: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  payload,
  persona,
  setPersona,
  language,
  setLanguage,
  isPaused,
  togglePause,
  speed,
  setSpeed,
  onOpenRecap,
}) => {
  return (
    <header className="bg-[#1b0826] border-b border-[#38003c] text-white px-4 py-3 flex flex-wrap items-center justify-between gap-4 sticky top-0 z-50 shadow-2xl">
      {/* Brand & Match Headline */}
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-[#00FF87] to-[#04F5FF] flex items-center justify-center font-black text-[#1b0826] text-xl shadow-lg">
          ⚽
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="font-extrabold tracking-wide text-transparent bg-clip-text bg-gradient-to-r from-white via-[#00FF87] to-[#04F5FF]">
              PitchLens AI
            </span>
            <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-[#38003c] text-[#00FF87] border border-[#00FF87]/30">
              Inside the Game
            </span>
          </div>
          <p className="text-xs text-gray-400 font-mono">
            Microsoft & Premier League Hackathon Edition
          </p>
        </div>
      </div>

      {/* Live Match Scoreboard & Clock */}
      {payload && (
        <div className="flex items-center bg-[#100418] border border-[#38003c] rounded-xl px-4 py-1.5 gap-4 shadow-inner">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#EF0107]"></span>
            <span className="font-bold text-sm tracking-wide">London Cannons</span>
          </div>
          <div className="flex items-center gap-2 bg-[#1b0826] px-3 py-0.5 rounded-lg border border-purple-900/50">
            <span className="font-black text-xl text-[#00FF87] font-mono">
              {payload.score_home} - {payload.score_away}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="font-bold text-sm tracking-wide">Manchester Titans</span>
            <span className="w-2.5 h-2.5 rounded-full bg-[#6CABDD]"></span>
          </div>
          <div className="border-l border-gray-700 pl-3 flex items-center gap-1.5 font-mono text-xs text-yellow-400 font-bold">
            <span className="w-2 h-2 rounded-full bg-red-500 animate-ping"></span>
            {payload.current_minute}:{payload.current_second.toString().padStart(2, "0")}
            <span className="text-gray-400 ml-1">({payload.latest_event.period})</span>
          </div>
        </div>
      )}

      {/* Control Actions & Mode Switchers */}
      <div className="flex items-center gap-2 flex-wrap">
        {/* Persona Mode Switcher */}
        <div className="flex items-center bg-[#100418] p-1 rounded-lg border border-[#38003c]">
          <button
            onClick={() => setPersona("casual_fan")}
            className={`flex items-center gap-1 text-xs px-2.5 py-1.5 rounded-md font-semibold transition-all ${
              persona === "casual_fan"
                ? "bg-[#FF2882] text-white shadow-md"
                : "text-gray-400 hover:text-white"
            }`}
            title="Casual Fan Experience"
          >
            <Tv className="w-3.5 h-3.5" />
            <span>Casual Fan</span>
          </button>
          <button
            onClick={() => setPersona("data_analyst")}
            className={`flex items-center gap-1 text-xs px-2.5 py-1.5 rounded-md font-semibold transition-all ${
              persona === "data_analyst"
                ? "bg-[#00FF87] text-[#1b0826] font-bold shadow-md"
                : "text-gray-400 hover:text-white"
            }`}
            title="Data-Hungry Analyst Experience"
          >
            <BarChart3 className="w-3.5 h-3.5" />
            <span>Data Analyst</span>
          </button>
          <button
            onClick={() => setPersona("player_focus")}
            className={`flex items-center gap-1 text-xs px-2.5 py-1.5 rounded-md font-semibold transition-all ${
              persona === "player_focus"
                ? "bg-[#04F5FF] text-[#1b0826] font-bold shadow-md"
                : "text-gray-400 hover:text-white"
            }`}
            title="Player-Focused Tracking Experience"
          >
            <User className="w-3.5 h-3.5" />
            <span>Player Focus</span>
          </button>
        </div>

        {/* Language Switcher */}
        <div className="flex items-center bg-[#100418] p-1 rounded-lg border border-[#38003c] text-xs">
          <Globe className="w-3.5 h-3.5 text-gray-400 ml-1.5 mr-1" />
          {(["en", "ro", "es"] as Language[]).map((l) => (
            <button
              key={l}
              onClick={() => setLanguage(l)}
              className={`px-2 py-1 rounded uppercase font-bold text-[11px] transition-all ${
                language === l
                  ? "bg-purple-700 text-white"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              {l}
            </button>
          ))}
        </div>

        {/* Simulation Controls */}
        <div className="flex items-center gap-1 bg-[#100418] p-1 rounded-lg border border-[#38003c]">
          <button
            onClick={togglePause}
            className="p-1.5 rounded hover:bg-[#38003c] text-white transition-colors"
            title={isPaused ? "Resume Simulation" : "Pause Simulation"}
          >
            {isPaused ? <Play className="w-4 h-4 text-green-400" /> : <Pause className="w-4 h-4 text-yellow-400" />}
          </button>
          <button
            onClick={() => setSpeed(speed === 1 ? 2 : speed === 2 ? 4 : 1)}
            className="flex items-center gap-0.5 px-2 py-1 text-xs font-mono font-bold text-gray-300 hover:text-white hover:bg-[#38003c] rounded"
            title="Change Playback Speed"
          >
            <FastForward className="w-3.5 h-3.5" />
            <span>{speed}x</span>
          </button>
        </div>

        {/* Studio Recap Modal Trigger */}
        <button
          onClick={onOpenRecap}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold bg-[#38003c] text-[#00FF87] border border-[#00FF87]/40 hover:bg-[#520058] transition-all shadow-md"
        >
          <FileText className="w-3.5 h-3.5" />
          <span>Studio Recap</span>
        </button>
      </div>
    </header>
  );
};
