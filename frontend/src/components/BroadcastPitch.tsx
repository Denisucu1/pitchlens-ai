import React, { useState } from "react";
import type { MatchEvent, PlayerProfile, TeamProfile, PitchCoordinates, PassLink } from "../types";
import { Zap, Flame, Share2 } from "lucide-react";

interface BroadcastPitchProps {
  latestEvent: MatchEvent | null;
  homeTeam: TeamProfile | null;
  awayTeam: TeamProfile | null;
  focusedPlayer: PlayerProfile | null;
  onSelectPlayer: (player: PlayerProfile) => void;
  heatmapPoints?: PitchCoordinates[];
  passLinks?: PassLink[];
}

export const BroadcastPitch: React.FC<BroadcastPitchProps> = ({
  latestEvent,
  homeTeam,
  awayTeam,
  focusedPlayer,
  onSelectPlayer,
  heatmapPoints = [],
  passLinks = [],
}) => {
  const [showHeatmap, setShowHeatmap] = useState(false);
  const [showPassNetwork, setShowPassNetwork] = useState(false);

  const ballPos = latestEvent ? latestEvent.location : { x: 50, y: 50 };
  const endPos = latestEvent?.end_location;

  const getTrajectoryColor = () => {
    if (!latestEvent) return "#00FF87";
    if (latestEvent.event_type === "goal") return "#00FF87";
    if (latestEvent.event_type === "shot") return "#FF2882";
    const diff = latestEvent.pass_difficulty_rating || 0;
    if (diff > 0.7) return "#FF2882"; // High risk / line breaking
    if (diff > 0.4) return "#FFA500"; // Medium
    return "#00FF87"; // Standard
  };

  // Helper map to find player coordinates for pass network
  const allPlayers = [...(homeTeam?.players || []), ...(awayTeam?.players || [])];
  const playerMap = new Map(allPlayers.map((p) => [p.id, p]));

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

      {/* Heatmap Overlay (Canvas-like glow effect) */}
      {showHeatmap && (
        <div className="absolute inset-0 pointer-events-none overflow-hidden opacity-75">
          {heatmapPoints.map((pt, idx) => (
            <div
              key={`hm_${idx}`}
              style={{
                left: `${pt.x}%`,
                top: `${pt.y}%`,
                transform: "translate(-50%, -50%)",
              }}
              className="absolute w-12 h-12 rounded-full bg-gradient-to-r from-yellow-400/30 via-red-500/30 to-rose-600/20 blur-md pointer-events-none"
            />
          ))}
        </div>
      )}

      {/* Render Players - Home Team */}
      {homeTeam?.players.map((p) => {
        const isFocused = focusedPlayer?.id === p.id;
        const isActor = latestEvent?.player.id === p.id;
        return (
          <div
            key={p.id}
            onClick={() => onSelectPlayer(p)}
            style={{
              left: `${p.current_coords.x}%`,
              top: `${p.current_coords.y}%`,
              transform: "translate(-50%, -50%)",
            }}
            className="absolute cursor-pointer transition-all duration-700 ease-out z-20 group flex flex-col items-center"
          >
            {isFocused && (
              <span className="absolute -inset-2.5 rounded-full border-2 border-[#04F5FF] animate-ping opacity-75 pointer-events-none" />
            )}

            <div
              style={{ backgroundColor: homeTeam.primary_color }}
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

      {/* Render Players - Away Team */}
      {awayTeam?.players.map((p) => {
        const isFocused = focusedPlayer?.id === p.id;
        const isActor = latestEvent?.player.id === p.id;
        return (
          <div
            key={p.id}
            onClick={() => onSelectPlayer(p)}
            style={{
              left: `${p.current_coords.x}%`,
              top: `${p.current_coords.y}%`,
              transform: "translate(-50%, -50%)",
            }}
            className="absolute cursor-pointer transition-all duration-700 ease-out z-20 group flex flex-col items-center"
          >
            {isFocused && (
              <span className="absolute -inset-2.5 rounded-full border-2 border-[#04F5FF] animate-ping opacity-75 pointer-events-none" />
            )}

            <div
              style={{ backgroundColor: awayTeam.primary_color }}
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
        <div className="w-4 h-4 rounded-full bg-white border-2 border-black shadow-[0_0_14px_rgba(255,255,255,0.9)] flex items-center justify-center animate-bounce">
          <div className="w-1.5 h-1.5 rounded-full bg-black/80"></div>
        </div>

        {latestEvent?.ball_speed_kmh && (
          <div className="mt-1 bg-black/95 text-[#00FF87] border border-[#00FF87]/40 px-1.5 py-0.5 rounded text-[8px] font-mono font-bold flex items-center gap-0.5 shadow-lg whitespace-nowrap">
            <Zap className="w-2.5 h-2.5 text-yellow-400" />
            <span>{latestEvent.ball_speed_kmh} km/h</span>
          </div>
        )}
      </div>

      {/* Floating Spatial Controls Over Pitch */}
      <div className="absolute top-3 right-3 flex items-center gap-1.5 z-40 bg-black/70 backdrop-blur-md p-1 rounded-xl border border-white/10">
        <button
          onClick={() => setShowHeatmap(!showHeatmap)}
          className={`flex items-center gap-1 text-[10px] font-bold px-2 py-1 rounded-lg transition-all ${
            showHeatmap
              ? "bg-amber-500 text-black shadow-md"
              : "text-gray-300 hover:text-white hover:bg-white/10"
          }`}
          title="Toggle Territorial Pressure Heatmap"
        >
          <Flame className="w-3 h-3" />
          <span>Heatmap</span>
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
      <div className="absolute bottom-2 right-2 bg-black/60 backdrop-blur px-2 py-0.5 rounded text-[9px] text-gray-300 font-mono pointer-events-none border border-white/10">
        OPTA CALIBRATED • 105x68m
      </div>
    </div>
  );
};
