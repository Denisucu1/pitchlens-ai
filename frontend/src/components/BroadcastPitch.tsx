import React, { useState } from "react";
import type { MatchEvent, PlayerProfile, TeamProfile, PitchCoordinates, PassLink } from "../types";
import { Zap, Flame, Share2, ArrowRight, ArrowLeft } from "lucide-react";

interface BroadcastPitchProps {
  latestEvent: MatchEvent | null;
  homeTeam: TeamProfile | null;
  awayTeam: TeamProfile | null;
  homePlayers?: PlayerProfile[];
  awayPlayers?: PlayerProfile[];
  focusedPlayer: PlayerProfile | null;
  onSelectPlayer: (player: PlayerProfile) => void;
  playerHeatmaps?: Record<string, PitchCoordinates[]>;
  passLinks?: PassLink[];
  currentMinute?: number;
  period?: string;
  homeGameState?: string;
  awayGameState?: string;
}

export const BroadcastPitch: React.FC<BroadcastPitchProps> = ({
  latestEvent,
  homeTeam,
  awayTeam,
  homePlayers = [],
  awayPlayers = [],
  focusedPlayer,
  onSelectPlayer,
  playerHeatmaps = {},
  passLinks = [],
  currentMinute = 1,
  period = "1H",
  homeGameState = "balanced",
  awayGameState = "balanced",
}) => {
  const [showPlayerHeatmap, setShowPlayerHeatmap] = useState(false);
  const [showPassNetwork, setShowPassNetwork] = useState(false);

  const ballPos = latestEvent ? latestEvent.location : { x: 50, y: 50 };
  const endPos = latestEvent?.end_location;

  // Determine if it's 2nd Half (Sides switch!)
  const is2H = period === "2H" || latestEvent?.period === "2H" || currentMinute > 45;

  const getTrajectoryColor = () => {
    if (!latestEvent) return "#00FF87";
    if (latestEvent.event_type === "goal") return "#00FF87";
    if (latestEvent.event_type === "shot") return "#FF2882";
    const diff = latestEvent.pass_difficulty_rating || 0;
    if (diff > 0.7) return "#FF2882"; // High risk / line breaking
    if (diff > 0.4) return "#FFA500"; // Medium
    return "#00FF87"; // Standard
  };

  // Dynamic player coordinates from live payload ticks (fallback to initial team squad)
  const currentHomePlayers = homePlayers.length > 0 ? homePlayers : (homeTeam?.players || []);
  const currentAwayPlayers = awayPlayers.length > 0 ? awayPlayers : (awayTeam?.players || []);
  const allPlayers = [...currentHomePlayers, ...currentAwayPlayers];
  const playerMap = new Map(allPlayers.map((p) => [p.id, p]));

  // Active player for individual heatmap
  const activeHeatmapPlayer = focusedPlayer || (showPlayerHeatmap ? latestEvent?.player : null);
  const playerPoints =
    (activeHeatmapPlayer
      ? playerHeatmaps[activeHeatmapPlayer.id] || activeHeatmapPlayer.heatmap
      : []) || [];

  // Half-time side awareness:
  // 1H: Home defends Left (x=0), attacks Right (x=100) -> Left is Home, Right is Away
  // 2H: Home defends Right (x=100), attacks Left (x=0) -> Left is Away, Right is Home
  const leftTeam = is2H ? awayTeam : homeTeam;
  const rightTeam = is2H ? homeTeam : awayTeam;

  return (
    <div className="relative w-full aspect-[105/68] bg-gradient-to-br from-[#0e3b1c] to-[#072410] rounded-2xl overflow-hidden border-2 border-emerald-900/60 shadow-2xl select-none">
      {/* Grass Stripe Texture */}
      <div className="absolute inset-0 opacity-15 bg-[repeating-linear-gradient(90deg,transparent,transparent_40px,rgba(255,255,255,0.06)_40px,rgba(255,255,255,0.06)_80px)] pointer-events-none" />

      {/* SVG Pitch Markings */}
      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
        {/* Outer Boundary */}
        <rect x="2" y="2" width="96" height="96" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.8" />
        {/* Halfway Line */}
        <line x1="50" y1="2" x2="50" y2="98" stroke="rgba(255,255,255,0.4)" strokeWidth="0.8" />
        {/* Center Circle */}
        <circle cx="50" cy="50" r="10" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.8" />
        <circle cx="50" cy="50" r="0.8" fill="rgba(255,255,255,0.8)" />

        {/* Left Penalty Area */}
        <rect x="2" y="22" width="16" height="56" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.8" />
        <rect x="2" y="36" width="6" height="28" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.8" />
        <circle cx="11" cy="50" r="0.8" fill="rgba(255,255,255,0.8)" />
        <path d="M 18,40 A 10,10 0 0,1 18,60" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.8" />

        {/* Right Penalty Area */}
        <rect x="82" y="22" width="16" height="56" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.8" />
        <rect x="92" y="36" width="6" height="28" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.8" />
        <circle cx="89" cy="50" r="0.8" fill="rgba(255,255,255,0.8)" />
        <path d="M 82,40 A 10,10 0 0,0 82,60" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.8" />

        {/* Goal Mouths */}
        <rect x="0" y="44" width="2" height="12" fill="rgba(255,255,255,0.15)" stroke="white" strokeWidth="0.6" />
        <rect x="98" y="44" width="2" height="12" fill="rgba(255,255,255,0.15)" stroke="white" strokeWidth="0.6" />

        {/* Pass Network Overlay Lines */}
        {showPassNetwork &&
          passLinks.map((link, idx) => {
            const p1 = playerMap.get(link.source_player_id);
            const p2 = playerMap.get(link.target_player_id);
            if (!p1 || !p2) return null;
            const strokeWidth = Math.min(2.5, Math.max(0.6, link.count * 0.4));
            return (
              <line
                key={`pl_${idx}`}
                x1={p1.current_coords.x}
                y1={p1.current_coords.y}
                x2={p2.current_coords.x}
                y2={p2.current_coords.y}
                stroke="#04F5FF"
                strokeWidth={strokeWidth}
                strokeOpacity={0.65}
                strokeDasharray="1 0.8"
              />
            );
          })}

        {/* Dynamic Pass / Shot Trajectory Vector */}
        {endPos && (
          <g>
            <line
              x1={ballPos.x}
              y1={ballPos.y}
              x2={endPos.x}
              y2={endPos.y}
              stroke={getTrajectoryColor()}
              strokeWidth="1.3"
              strokeDasharray="2 1.5"
              className="animate-pulse"
            />
            <circle cx={endPos.x} cy={endPos.y} r="1.5" fill={getTrajectoryColor()} opacity="0.8" />
          </g>
        )}
      </svg>

      {/* Half-Time Side-Switch Notification Banner */}
      {is2H && (
        <div className="absolute top-2.5 left-1/2 -translate-x-1/2 bg-black/80 backdrop-blur-md px-3 py-1 rounded-full border border-amber-500/50 text-[10px] font-mono font-bold text-amber-300 shadow-xl flex items-center gap-1.5 z-30 pointer-events-none">
          <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
          <span>🔄 REPRIZA 2 • ECHIPELE AU SCHIMBAT PORȚILE</span>
        </div>
      )}

      {/* Dynamic Tactical State Alerts */}
      {(homeGameState !== "balanced" || awayGameState !== "balanced") && (
        <div className="absolute top-3 left-3 flex flex-col gap-1 z-30 pointer-events-none">
          {homeGameState === "all_out_attack" && (
            <div className="bg-red-950/85 backdrop-blur border border-red-500/70 text-red-200 text-[9px] font-mono font-black px-2 py-0.5 rounded shadow-lg flex items-center gap-1 animate-pulse">
              <span>⚡ {homeTeam?.short_name || "HOME"}: ALL-OUT ATTACK</span>
            </div>
          )}
          {homeGameState === "park_the_bus" && (
            <div className="bg-blue-950/85 backdrop-blur border border-blue-500/70 text-blue-200 text-[9px] font-mono font-black px-2 py-0.5 rounded shadow-lg flex items-center gap-1">
              <span>🛡️ {homeTeam?.short_name || "HOME"}: PARK THE BUS</span>
            </div>
          )}
          {homeGameState === "counter_attack" && (
            <div className="bg-yellow-950/85 backdrop-blur border border-yellow-500/70 text-yellow-200 text-[9px] font-mono font-black px-2 py-0.5 rounded shadow-lg flex items-center gap-1 animate-bounce">
              <span>🚀 {homeTeam?.short_name || "HOME"}: COUNTER-ATTACK!</span>
            </div>
          )}
          {awayGameState === "all_out_attack" && (
            <div className="bg-red-950/85 backdrop-blur border border-red-500/70 text-red-200 text-[9px] font-mono font-black px-2 py-0.5 rounded shadow-lg flex items-center gap-1 animate-pulse">
              <span>⚡ {awayTeam?.short_name || "AWAY"}: ALL-OUT ATTACK</span>
            </div>
          )}
          {awayGameState === "park_the_bus" && (
            <div className="bg-blue-950/85 backdrop-blur border border-blue-500/70 text-blue-200 text-[9px] font-mono font-black px-2 py-0.5 rounded shadow-lg flex items-center gap-1">
              <span>🛡️ {awayTeam?.short_name || "AWAY"}: PARK THE BUS</span>
            </div>
          )}
          {awayGameState === "counter_attack" && (
            <div className="bg-yellow-950/85 backdrop-blur border border-yellow-500/70 text-yellow-200 text-[9px] font-mono font-black px-2 py-0.5 rounded shadow-lg flex items-center gap-1 animate-bounce">
              <span>🚀 {awayTeam?.short_name || "AWAY"}: COUNTER-ATTACK!</span>
            </div>
          )}
        </div>
      )}

      {/* Attack Direction Indicators on Flanks */}
      <div className="absolute bottom-2 left-3 flex items-center gap-1 text-[9px] font-mono font-bold text-gray-400 bg-black/50 px-2 py-0.5 rounded pointer-events-none border border-white/5">
        <span style={{ color: leftTeam?.primary_color || "#EF0107" }}>{leftTeam?.short_name || "HOME"}</span>
        <ArrowRight className="w-2.5 h-2.5 text-gray-300" />
      </div>
      <div className="absolute bottom-2 right-3 flex items-center gap-1 text-[9px] font-mono font-bold text-gray-400 bg-black/50 px-2 py-0.5 rounded pointer-events-none border border-white/5">
        <ArrowLeft className="w-2.5 h-2.5 text-gray-300" />
        <span style={{ color: rightTeam?.primary_color || "#6CABDD" }}>{rightTeam?.short_name || "AWAY"}</span>
      </div>

      {/* Individual Player Heatmap Overlay (High-Precision Opta Clusters) */}
      {showPlayerHeatmap && (
        <div className="absolute inset-0 pointer-events-none overflow-hidden z-10 transition-opacity duration-300">
          {playerPoints.map((pt, idx) => (
            <div
              key={`phm_${idx}`}
              style={{
                left: `${pt.x}%`,
                top: `${pt.y}%`,
                transform: "translate(-50%, -50%)",
                background:
                  "radial-gradient(circle, rgba(255, 35, 0, 0.85) 0%, rgba(255, 140, 0, 0.55) 45%, rgba(255, 230, 0, 0.22) 75%, transparent 100%)",
              }}
              className="absolute w-20 h-20 rounded-full blur-[6px] pointer-events-none"
            />
          ))}

          {/* Active Individual Player Heatmap Legend */}
          <div className="absolute bottom-7 left-3 bg-black/90 backdrop-blur-md px-3 py-1.5 rounded-lg text-[10px] text-gray-200 font-mono border border-amber-500/50 flex items-center gap-2 pointer-events-none shadow-2xl">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse" />
            <div className="flex flex-col">
              <div className="flex items-center gap-1.5">
                <span className="text-amber-400 font-bold">OPTA HEATMAP:</span>
                {activeHeatmapPlayer ? (
                  <>
                    <span className="text-white font-bold underline">
                      {activeHeatmapPlayer.name} (#{activeHeatmapPlayer.number})
                    </span>
                    <span className="text-gray-400">[{activeHeatmapPlayer.position}]</span>
                  </>
                ) : (
                  <span className="text-yellow-300">Click pe un jucător din teren</span>
                )}
              </div>
              <div className="text-[9px] text-gray-400 mt-0.5">
                {playerPoints.length} atingeri înregistrate {is2H ? "• (Repriza a 2-a: teren inversat)" : "• (Repriza 1)"}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Helper notice if player heatmap toggled but no player focused */}
      {showPlayerHeatmap && !activeHeatmapPlayer && (
        <div className="absolute top-12 left-1/2 -translate-x-1/2 bg-black/85 backdrop-blur px-3 py-1.5 rounded-xl border border-amber-500/60 text-amber-300 text-[11px] font-semibold shadow-lg pointer-events-none animate-pulse z-30">
          👆 Apasă pe orice jucător din teren pentru a-i vedea Heatmap-ul individual
        </div>
      )}

      {/* Render Players - Home Team (Live Dynamic Coordinates) */}
      {currentHomePlayers.map((p) => {
        const isFocused = focusedPlayer?.id === p.id;
        const isActor = latestEvent?.player.id === p.id;
        return (
          <div
            key={p.id}
            onClick={() => onSelectPlayer(p)}
            className="absolute cursor-pointer z-20 group flex flex-col items-center"
            style={{
              left: `${p.current_coords.x}%`,
              top: `${p.current_coords.y}%`,
              transform: "translate(-50%, -50%)",
              transition: "left 750ms cubic-bezier(0.25, 0.46, 0.45, 0.94), top 750ms cubic-bezier(0.25, 0.46, 0.45, 0.94)",
            }}
          >
            {isFocused && (
              <span className="absolute -inset-2.5 rounded-full border-2 border-[#04F5FF] animate-ping opacity-75 pointer-events-none" />
            )}

            <div
              style={{ backgroundColor: homeTeam?.primary_color || "#EF0107" }}
              className={`w-6 h-6 rounded-full flex items-center justify-center font-bold text-[10px] text-white shadow-lg border-2 transition-transform duration-200 group-hover:scale-125 ${
                isActor
                  ? "border-yellow-300 scale-110 shadow-yellow-500/50"
                  : isFocused
                  ? "border-[#04F5FF] shadow-[#04F5FF]/50 scale-105"
                  : "border-white/90"
              }`}
            >
              {p.number}
            </div>

            <span className="opacity-0 group-hover:opacity-100 transition-opacity bg-black/90 text-[9px] text-white px-1.5 py-0.5 rounded mt-0.5 pointer-events-none font-semibold whitespace-nowrap shadow-lg">
              {p.name} ({p.position})
            </span>
          </div>
        );
      })}

      {/* Render Players - Away Team (Live Dynamic Coordinates) */}
      {currentAwayPlayers.map((p) => {
        const isFocused = focusedPlayer?.id === p.id;
        const isActor = latestEvent?.player.id === p.id;
        return (
          <div
            key={p.id}
            onClick={() => onSelectPlayer(p)}
            className="absolute cursor-pointer z-20 group flex flex-col items-center"
            style={{
              left: `${p.current_coords.x}%`,
              top: `${p.current_coords.y}%`,
              transform: "translate(-50%, -50%)",
              transition: "left 750ms cubic-bezier(0.25, 0.46, 0.45, 0.94), top 750ms cubic-bezier(0.25, 0.46, 0.45, 0.94)",
            }}
          >
            {isFocused && (
              <span className="absolute -inset-2.5 rounded-full border-2 border-[#04F5FF] animate-ping opacity-75 pointer-events-none" />
            )}

            <div
              style={{ backgroundColor: awayTeam?.primary_color || "#6CABDD" }}
              className={`w-6 h-6 rounded-full flex items-center justify-center font-bold text-[10px] text-white shadow-lg border-2 transition-transform duration-200 group-hover:scale-125 ${
                isActor
                  ? "border-yellow-300 scale-110 shadow-yellow-500/50"
                  : isFocused
                  ? "border-[#04F5FF] shadow-[#04F5FF]/50 scale-105"
                  : "border-white/90"
              }`}
            >
              {p.number}
            </div>

            <span className="opacity-0 group-hover:opacity-100 transition-opacity bg-black/90 text-[9px] text-white px-1.5 py-0.5 rounded mt-0.5 pointer-events-none font-semibold whitespace-nowrap shadow-lg">
              {p.name} ({p.position})
            </span>
          </div>
        );
      })}

      {/* Real-time Ball Indicator */}
      <div
        style={{
          left: `${ballPos.x}%`,
          top: `${ballPos.y}%`,
          transform: "translate(-50%, -50%)",
        }}
        className="absolute z-30 transition-all duration-500 ease-out pointer-events-none flex flex-col items-center"
      >
        <div className="w-4 h-4 rounded-full bg-white border-2 border-black shadow-[0_0_12px_rgba(255,255,255,0.8)] flex items-center justify-center animate-pulse">
          <div className="w-1.5 h-1.5 rounded-full bg-black/80"></div>
        </div>

        {/* Live Shot Speed Badge (Only shown on shots and goals!) */}
        {latestEvent &&
          (latestEvent.event_type === "shot" || latestEvent.event_type === "goal") &&
          (latestEvent.shot_speed_kmh || latestEvent.ball_speed_kmh) && (
            <div className="mt-1 bg-black/95 text-yellow-300 border-2 border-yellow-400 px-2 py-0.5 rounded-lg text-[9px] font-mono font-black flex items-center gap-1 shadow-[0_0_15px_rgba(255,200,0,0.7)] whitespace-nowrap animate-bounce">
              <Zap className="w-3 h-3 text-yellow-400" />
              <span>SHOT SPEED: {latestEvent.shot_speed_kmh || latestEvent.ball_speed_kmh} km/h</span>
            </div>
          )}
      </div>

      {/* Floating Spatial Controls Over Pitch */}
      <div className="absolute top-3 right-3 flex items-center gap-1.5 z-40 bg-black/70 backdrop-blur-md p-1 rounded-xl border border-white/10">
        <button
          onClick={() => setShowPlayerHeatmap(!showPlayerHeatmap)}
          className={`flex items-center gap-1 text-[10px] font-bold px-2 py-1 rounded-lg transition-all ${
            showPlayerHeatmap
              ? "bg-amber-500 text-black shadow-md"
              : "text-gray-300 hover:text-white hover:bg-white/10"
          }`}
          title="Activează heatmap-ul individual pentru jucătorul selectat"
        >
          <Flame className="w-3 h-3" />
          <span>
            {showPlayerHeatmap && activeHeatmapPlayer
              ? `Heatmap: ${activeHeatmapPlayer.name.split(" ").slice(-1)[0]}`
              : "Heatmap Jucător"}
          </span>
        </button>

        <button
          onClick={() => setShowPassNetwork(!showPassNetwork)}
          className={`flex items-center gap-1 text-[10px] font-bold px-2 py-1 rounded-lg transition-all ${
            showPassNetwork
              ? "bg-[#04F5FF] text-black shadow-md"
              : "text-gray-300 hover:text-white hover:bg-white/10"
          }`}
          title="Toggle Passing Network Diagram"
        >
          <Share2 className="w-3 h-3" />
          <span>Pass Network</span>
        </button>
      </div>

      {/* Corner Watermark */}
      <div className="absolute bottom-2 right-24 bg-black/60 backdrop-blur px-2 py-0.5 rounded text-[9px] text-gray-300 font-mono pointer-events-none border border-white/10">
        OPTA CALIBRATED • 105x68m
      </div>
    </div>
  );
};
