import React from "react";
import type { MatchEvent, PlayerProfile, TeamProfile } from "../types";
import { Zap } from "lucide-react";

interface BroadcastPitchProps {
  latestEvent: MatchEvent | null;
  homeTeam: TeamProfile | null;
  awayTeam: TeamProfile | null;
  focusedPlayer: PlayerProfile | null;
  onSelectPlayer: (player: PlayerProfile) => void;
}

export const BroadcastPitch: React.FC<BroadcastPitchProps> = ({
  latestEvent,
  homeTeam,
  awayTeam,
  focusedPlayer,
  onSelectPlayer,
}) => {
  const ballPos = latestEvent ? latestEvent.location : { x: 50, y: 50 };
  const endPos = latestEvent?.end_location;

  // Pass difficulty color mapping
  const getTrajectoryColor = () => {
    if (!latestEvent) return "#00FF87";
    if (latestEvent.event_type === "goal") return "#00FF87";
    if (latestEvent.event_type === "shot") return "#FF2882";
    const diff = latestEvent.pass_difficulty_rating || 0;
    if (diff > 0.7) return "#FF2882"; // Hard / high risk
    if (diff > 0.4) return "#FFA500"; // Medium
    return "#00FF87"; // Low
  };

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

        {/* Left Penalty Area (Home Team Box) */}
        <rect x="2" y="22" width="16" height="56" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.8" />
        <rect x="2" y="36" width="6" height="28" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.8" />
        <circle cx="11" cy="50" r="0.8" fill="rgba(255,255,255,0.8)" />
        <path d="M 18,40 A 10,10 0 0,1 18,60" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.8" />

        {/* Right Penalty Area (Away Team Box) */}
        <rect x="82" y="22" width="16" height="56" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.8" />
        <rect x="92" y="36" width="6" height="28" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.8" />
        <circle cx="89" cy="50" r="0.8" fill="rgba(255,255,255,0.8)" />
        <path d="M 82,40 A 10,10 0 0,0 82,60" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.8" />

        {/* Goal Mouths */}
        <rect x="0" y="44" width="2" height="12" fill="rgba(255,255,255,0.15)" stroke="white" strokeWidth="0.6" />
        <rect x="98" y="44" width="2" height="12" fill="rgba(255,255,255,0.15)" stroke="white" strokeWidth="0.6" />

        {/* Dynamic Pass / Shot Trajectory Vector */}
        {endPos && (
          <g>
            <line
              x1={ballPos.x}
              y1={ballPos.y}
              x2={endPos.x}
              y2={endPos.y}
              stroke={getTrajectoryColor()}
              strokeWidth="1.2"
              strokeDasharray="2 1.5"
              className="animate-pulse"
            />
            <circle cx={endPos.x} cy={endPos.y} r="1.5" fill={getTrajectoryColor()} opacity="0.8" />
          </g>
        )}
      </svg>

      {/* Render Players - Home Team (London Cannons - Red) */}
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
            className={`absolute cursor-pointer transition-all duration-700 ease-out z-20 group flex flex-col items-center`}
          >
            {/* Focused Player Radar Halo */}
            {isFocused && (
              <span className="absolute -inset-2 rounded-full border-2 border-[#04F5FF] animate-ping opacity-75 pointer-events-none" />
            )}

            {/* Player Pin */}
            <div
              className={`w-6 h-6 rounded-full flex items-center justify-center font-bold text-[10px] text-white shadow-lg border-2 transition-transform duration-200 group-hover:scale-125 ${
                isActor
                  ? "bg-[#EF0107] border-yellow-300 scale-110 shadow-yellow-500/50"
                  : isFocused
                  ? "bg-[#EF0107] border-[#04F5FF] shadow-[#04F5FF]/50"
                  : "bg-[#EF0107] border-white/80"
              }`}
            >
              {p.number}
            </div>

            {/* Name Tooltip */}
            <span className="opacity-0 group-hover:opacity-100 transition-opacity bg-black/80 text-[9px] text-white px-1.5 py-0.5 rounded mt-0.5 pointer-events-none font-semibold whitespace-nowrap shadow">
              {p.name} ({p.position})
            </span>
          </div>
        );
      })}

      {/* Render Players - Away Team (Manchester Titans - Sky Blue) */}
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
            className={`absolute cursor-pointer transition-all duration-700 ease-out z-20 group flex flex-col items-center`}
          >
            {isFocused && (
              <span className="absolute -inset-2 rounded-full border-2 border-[#04F5FF] animate-ping opacity-75 pointer-events-none" />
            )}

            <div
              className={`w-6 h-6 rounded-full flex items-center justify-center font-bold text-[10px] text-[#1C2C5B] shadow-lg border-2 transition-transform duration-200 group-hover:scale-125 ${
                isActor
                  ? "bg-[#6CABDD] border-yellow-300 scale-110 shadow-yellow-500/50"
                  : isFocused
                  ? "bg-[#6CABDD] border-[#04F5FF] shadow-[#04F5FF]/50"
                  : "bg-[#6CABDD] border-white/80"
              }`}
            >
              {p.number}
            </div>

            <span className="opacity-0 group-hover:opacity-100 transition-opacity bg-black/80 text-[9px] text-white px-1.5 py-0.5 rounded mt-0.5 pointer-events-none font-semibold whitespace-nowrap shadow">
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
        <div className="w-4 h-4 rounded-full bg-white border-2 border-black shadow-[0_0_12px_rgba(255,255,255,0.9)] flex items-center justify-center animate-bounce">
          <div className="w-1.5 h-1.5 rounded-full bg-black/80"></div>
        </div>

        {/* Live Speed Badge */}
        {latestEvent?.ball_speed_kmh && (
          <div className="mt-1 bg-black/90 text-[#00FF87] border border-[#00FF87]/40 px-1.5 py-0.5 rounded text-[8px] font-mono font-bold flex items-center gap-0.5 shadow-lg whitespace-nowrap">
            <Zap className="w-2.5 h-2.5 text-yellow-400" />
            <span>{latestEvent.ball_speed_kmh} km/h</span>
          </div>
        )}
      </div>

      {/* Corner Watermark */}
      <div className="absolute bottom-2 right-2 bg-black/60 backdrop-blur px-2 py-0.5 rounded text-[9px] text-gray-300 font-mono pointer-events-none border border-white/10">
        PITCH RADAR 105x68m • LIVE TELEMETRY
      </div>
    </div>
  );
};
