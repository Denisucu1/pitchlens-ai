import React, { useState } from "react";
import type { PersonaMode, Language, LiveMatchPayload, ClubSummary } from "../types";
import { Play, Pause, FastForward, Globe, User, BarChart3, Tv, FileText, Volume2, VolumeX, Shuffle, RotateCcw, Trophy } from "lucide-react";

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
  isAudioEnabled: boolean;
  toggleAudio: () => void;
  clubs: ClubSummary[];
  onSwitchFixture: (homeId: string, awayId: string) => void;
  onResetMatch: () => void;
  activeTab: "broadcast" | "players" | "standings";
  setActiveTab: (t: "broadcast" | "players" | "standings") => void;
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
  isAudioEnabled,
  toggleAudio,
  clubs: _clubs,
  onSwitchFixture,
  onResetMatch,
  activeTab,
  setActiveTab,
}) => {
  const [showFixtureSelector, setShowFixtureSelector] = useState(false);

  const fixtures = [
    { home: "arsenal", away: "mancity", label: "Arsenal vs Man City" },
    { home: "liverpool", away: "chelsea", label: "Liverpool vs Chelsea" },
    { home: "manunited", away: "arsenal", label: "Man United vs Arsenal" },
    { home: "mancity", away: "liverpool", label: "Man City vs Liverpool" },
    { home: "chelsea", away: "manunited", label: "Chelsea vs Man United" },
  ];

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
              Premier League Studio
            </span>
          </div>
          <p className="text-xs text-gray-400 font-mono">
            Microsoft Foundry & Premier League Hackathon Edition
          </p>
        </div>
      </div>

      {/* Main View Switcher: Live Match Studio vs Players vs Standings */}
      <div className="flex items-center bg-[#100418] p-1 rounded-xl border border-[#38003c]">
        <button
          onClick={() => setActiveTab("broadcast")}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
            activeTab === "broadcast"
              ? "bg-[#38003c] text-[#00FF87] border border-[#00FF87]/40 shadow-md"
              : "text-gray-400 hover:text-white"
          }`}
          title="Interactive Pitch, Tactical Radar & AI Commentary"
        >
          <Tv className="w-3.5 h-3.5" />
          <span>Live Match</span>
        </button>

        <button
          onClick={() => setActiveTab("players")}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
            activeTab === "players"
              ? "bg-[#38003c] text-[#00FF87] border border-[#00FF87]/40 shadow-md"
              : "text-gray-400 hover:text-white"
          }`}
          title="Live Sofascore Ratings & Player Statistics (Shots, Passes, Tackles)"
        >
          <User className="w-3.5 h-3.5 text-cyan-400" />
          <span>Players & Ratings</span>
        </button>

        <button
          onClick={() => setActiveTab("standings")}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
            activeTab === "standings"
              ? "bg-[#38003c] text-[#00FF87] border border-[#00FF87]/40 shadow-md"
              : "text-gray-400 hover:text-white"
          }`}
          title="Live Premier League Standings & Matchweek 28 Results"
        >
          <Trophy className="w-3.5 h-3.5 text-yellow-400" />
          <span>Standings & Hub</span>
        </button>
      </div>

      {/* Live Match Scoreboard & Fixture Switcher */}
      {payload && (
        <div className="flex items-center bg-[#100418] border border-[#38003c] rounded-xl px-3 py-1.5 gap-3 shadow-inner relative">
          <div className="flex items-center gap-2">
            <span
              style={{ backgroundColor: payload.latest_event.team_id === "mancity" ? "#6CABDD" : "#EF0107" }}
              className="w-2.5 h-2.5 rounded-full"
            />
            <span className="font-bold text-sm tracking-wide">
              {payload.stats_home.team_id.toUpperCase()}
            </span>
          </div>

          <div className="flex items-center gap-2 bg-[#1b0826] px-3 py-0.5 rounded-lg border border-purple-900/50">
            <span className="font-black text-xl text-[#00FF87] font-mono">
              {payload.score_home} - {payload.score_away}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <span className="font-bold text-sm tracking-wide">
              {payload.stats_away.team_id.toUpperCase()}
            </span>
            <span
              style={{ backgroundColor: "#6CABDD" }}
              className="w-2.5 h-2.5 rounded-full"
            />
          </div>

          <div className="border-l border-gray-700 pl-2.5 flex items-center gap-1.5 font-mono text-xs text-yellow-400 font-bold">
            {payload.is_finished ? (
              <span className="bg-amber-400 text-black px-1.5 py-0.5 rounded text-[10px] font-black uppercase tracking-wider animate-pulse">
                FULL TIME (FT)
              </span>
            ) : payload.is_half_time ? (
              <span className="bg-blue-400 text-black px-1.5 py-0.5 rounded text-[10px] font-black uppercase tracking-wider">
                HALF TIME (HT)
              </span>
            ) : (
              <>
                <span className="w-2 h-2 rounded-full bg-red-500 animate-ping" />
                {payload.current_minute}:{payload.current_second.toString().padStart(2, "0")}
                <span className="text-gray-400 ml-1">({payload.latest_event.period})</span>
              </>
            )}
          </div>

          {/* Fixture Selector Button */}
          <button
            onClick={() => setShowFixtureSelector(!showFixtureSelector)}
            className="ml-1 p-1 rounded-lg bg-[#38003c] hover:bg-purple-800 text-gray-300 hover:text-white transition-all text-xs flex items-center gap-1"
            title="Switch Premier League Fixture"
          >
            <Shuffle className="w-3.5 h-3.5 text-[#04F5FF]" />
          </button>

          {/* Fixture Dropdown Menu */}
          {showFixtureSelector && (
            <div className="absolute top-12 left-0 z-50 bg-[#1b0826] border-2 border-[#00FF87] rounded-2xl shadow-2xl p-2 w-56 flex flex-col gap-1">
              <span className="text-[10px] font-mono font-bold text-gray-400 px-2 py-1 uppercase">
                Select Premier League Match:
              </span>
              {fixtures.map((f, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    onSwitchFixture(f.home, f.away);
                    setShowFixtureSelector(false);
                  }}
                  className="text-left text-xs px-2.5 py-1.5 rounded-lg hover:bg-[#38003c] font-semibold text-gray-200 hover:text-[#00FF87] transition-colors"
                >
                  ⚽ {f.label}
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Control Actions & Mode Switchers */}
      <div className="flex items-center gap-2 flex-wrap">
        {/* Listen Live (Audio Commentary Voice) */}
        <button
          onClick={toggleAudio}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all shadow-md ${
            isAudioEnabled
              ? "bg-[#00FF87] text-[#1b0826] animate-pulse"
              : "bg-[#100418] text-gray-400 hover:text-white border border-[#38003c]"
          }`}
          title="Toggle AI Audio Voice Commentary"
        >
          {isAudioEnabled ? <Volume2 className="w-4 h-4 text-[#1b0826]" /> : <VolumeX className="w-4 h-4" />}
          <span>{isAudioEnabled ? "Audio Live" : "Listen"}</span>
        </button>

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
          <button
            onClick={onResetMatch}
            className={`p-1.5 rounded transition-all flex items-center gap-1 ${
              payload?.is_finished
                ? "bg-amber-500 text-black hover:bg-amber-400 font-bold px-2 animate-bounce shadow-md"
                : "hover:bg-[#38003c] text-gray-300 hover:text-white"
            }`}
            title="Restart Match from 00:00"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            {payload?.is_finished && <span className="text-[10px]">Restart</span>}
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
