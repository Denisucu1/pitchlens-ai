import React, { useState } from "react";
import type { PlayerProfile, TeamProfile, PersonaMode } from "../types";
import { UserCheck, X, Sparkles } from "lucide-react";

interface PlayerFocusSelectorProps {
  homeTeam: TeamProfile | null;
  awayTeam: TeamProfile | null;
  homePlayers: PlayerProfile[];
  awayPlayers: PlayerProfile[];
  focusedPlayer: PlayerProfile | null;
  onSelectPlayer: (player: PlayerProfile | null) => void;
  persona: PersonaMode;
  onSetPersona?: (mode: PersonaMode) => void;
}

export const PlayerFocusSelector: React.FC<PlayerFocusSelectorProps> = ({
  homeTeam,
  awayTeam,
  homePlayers,
  awayPlayers,
  focusedPlayer,
  onSelectPlayer,
  persona,
  onSetPersona,
}) => {
  // Team selection tab (defaults to home team or the focused player's team)
  const [selectedTeamId, setSelectedTeamId] = useState<string>(
    focusedPlayer?.team_id || homeTeam?.id || "arsenal"
  );

  // If focused player changes team, sync tab to keep player visible
  React.useEffect(() => {
    if (focusedPlayer?.team_id) {
      setSelectedTeamId(focusedPlayer.team_id);
    }
  }, [focusedPlayer?.id, focusedPlayer?.team_id]);

  const activePlayers =
    selectedTeamId === homeTeam?.id
      ? homePlayers.length > 0
        ? homePlayers
        : homeTeam?.players || []
      : awayPlayers.length > 0
      ? awayPlayers
      : awayTeam?.players || [];

  const activeTeam = selectedTeamId === homeTeam?.id ? homeTeam : awayTeam;

  const handlePlayerClick = (p: PlayerProfile) => {
    if (focusedPlayer?.id === p.id) {
      onSelectPlayer(null);
    } else {
      onSelectPlayer(p);
      if (persona !== "player_focus" && onSetPersona) {
        onSetPersona("player_focus");
      }
    }
  };

  const isPlayerFocusActive = persona === "player_focus" || Boolean(focusedPlayer);

  return (
    <div
      className={`rounded-2xl transition-all duration-300 p-3 shadow-xl backdrop-blur-md ${
        isPlayerFocusActive
          ? "bg-gradient-to-r from-[#140620] via-[#0d1f2d] to-[#140620] border-2 border-[#04F5FF]/70 shadow-[0_0_20px_rgba(4,245,255,0.2)]"
          : "bg-[#1b0826] border border-[#38003c]"
      }`}
    >
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2.5 border-b border-white/10">
        <div className="flex items-center gap-2 min-w-0">
          <div
            className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 ${
              isPlayerFocusActive
                ? "bg-[#04F5FF]/20 text-[#04F5FF] border border-[#04F5FF]/50 shadow-[0_0_10px_#04F5FF]"
                : "bg-purple-900/40 text-purple-300 border border-purple-800"
            }`}
          >
            {isPlayerFocusActive ? (
              <Sparkles className="w-4 h-4 animate-pulse text-[#04F5FF]" />
            ) : (
              <UserCheck className="w-4 h-4" />
            )}
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <span className="font-black text-xs uppercase tracking-wider text-white">
                Player Spotlight Switcher
              </span>
              {focusedPlayer ? (
                <span className="text-[10px] font-mono px-2 py-0.2 rounded-full bg-[#04F5FF]/20 text-[#04F5FF] border border-[#04F5FF]/60 font-bold flex items-center gap-1 animate-pulse">
                  <span>★ ACTIVE</span>
                </span>
              ) : (
                <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-white/5 text-gray-400">
                  CLICK TO FOCUS
                </span>
              )}
            </div>
            <div className="text-[11px] text-gray-400 truncate mt-0.5">
              {focusedPlayer ? (
                <span>
                  Tracking <strong className="text-white">#{focusedPlayer.number} {focusedPlayer.name}</strong> ({focusedPlayer.position}) • Sofascore: <strong className="text-[#00FF87]">★ {focusedPlayer.match_rating?.toFixed(1) ?? "7.0"}</strong> • Top Speed: {focusedPlayer.current_speed_kmh} km/h
                </span>
              ) : (
                <span>Select any player to lock camera spotlight, live Opta telemetry & on-pitch halo</span>
              )}
            </div>
          </div>
        </div>

        {/* Team Tabs & Clear Focus Button */}
        <div className="flex items-center gap-2 shrink-0 self-end sm:self-auto">
          {/* Team Switcher Tabs */}
          <div className="flex items-center bg-black/40 p-1 rounded-xl border border-white/10">
            <button
              onClick={() => setSelectedTeamId(homeTeam?.id || "arsenal")}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-bold transition-all ${
                selectedTeamId === homeTeam?.id
                  ? "bg-[#EF0107] text-white shadow-md"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              <span className="w-2 h-2 rounded-full bg-white" />
              <span>{homeTeam?.short_name || "ARS"}</span>
              <span className="text-[10px] opacity-75">({homePlayers.length || 11})</span>
            </button>
            <button
              onClick={() => setSelectedTeamId(awayTeam?.id || "mancity")}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-bold transition-all ${
                selectedTeamId === awayTeam?.id
                  ? "bg-[#6CABDD] text-white shadow-md"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              <span className="w-2 h-2 rounded-full bg-white" />
              <span>{awayTeam?.short_name || "MCI"}</span>
              <span className="text-[10px] opacity-75">({awayPlayers.length || 11})</span>
            </button>
          </div>

          {/* Reset / Clear Focus Button */}
          {focusedPlayer && (
            <button
              onClick={() => onSelectPlayer(null)}
              className="flex items-center gap-1 text-[11px] font-bold px-2.5 py-1 rounded-xl bg-white/10 hover:bg-white/20 text-gray-300 hover:text-white border border-white/15 transition shadow-sm"
              title="Clear spotlight and return to full tactical view"
            >
              <X className="w-3.5 h-3.5 text-rose-400" />
              <span>Clear Focus</span>
            </button>
          )}
        </div>
      </div>

      {/* Players Horizontal Chips Ribbon */}
      <div className="flex items-center gap-1.5 overflow-x-auto pt-2.5 pb-1 no-scrollbar">
        {activePlayers.map((p) => {
          const isFocused = focusedPlayer?.id === p.id;
          const rating = p.match_rating ?? 6.8;
          const teamColor = activeTeam?.primary_color || "#EF0107";

          return (
            <button
              key={p.id}
              onClick={() => handlePlayerClick(p)}
              className={`group flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl text-xs font-sans font-semibold transition-all shrink-0 cursor-pointer ${
                isFocused
                  ? "bg-gradient-to-r from-cyan-950 via-[#04F5FF]/30 to-cyan-950 border-2 border-[#04F5FF] text-white shadow-[0_0_14px_rgba(4,245,255,0.8)] scale-105 ring-2 ring-[#04F5FF]/40"
                  : "bg-white/5 hover:bg-white/10 border border-white/10 text-gray-300 hover:text-white hover:border-white/25"
              }`}
              title={`Click to focus on #${p.number} ${p.name} (${p.position})`}
            >
              {/* Jersey Number Circle */}
              <span
                style={{ backgroundColor: isFocused ? "#04F5FF" : teamColor }}
                className={`w-5 h-5 rounded-full flex items-center justify-center font-black text-[10px] shrink-0 transition-transform ${
                  isFocused ? "text-black shadow-[0_0_8px_#04F5FF]" : "text-white shadow"
                }`}
              >
                {p.number}
              </span>

              {/* Short Player Name */}
              <span className={`truncate max-w-[85px] font-bold ${isFocused ? "text-white font-black" : "text-gray-200"}`}>
                {p.name.split(" ").pop()}
              </span>

              {/* Position Pill */}
              <span
                className={`text-[9px] font-mono px-1 py-0.2 rounded font-bold uppercase ${
                  isFocused
                    ? "bg-[#04F5FF]/30 text-cyan-200"
                    : "bg-black/40 text-gray-400 group-hover:text-gray-200"
                }`}
              >
                {p.position}
              </span>

              {/* Live Sofascore Rating Badge */}
              <span
                className={`text-[9px] font-mono font-black px-1 py-0.2 rounded flex items-center gap-0.5 ${
                  isFocused
                    ? "bg-[#00FF87] text-black"
                    : rating >= 7.5
                    ? "text-[#00FF87] bg-emerald-950/60"
                    : "text-yellow-400 bg-yellow-950/40"
                }`}
              >
                {rating.toFixed(1)}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
};
