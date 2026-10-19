import React, { useState, useEffect, useRef } from "react";
import type { MatchEvent, PlayerProfile, TeamProfile, PitchCoordinates, PassLink } from "../types";
import { Zap, Flame, Share2, ArrowRight, ArrowLeft } from "lucide-react";
import { BroadcastGoalBanner } from "./BroadcastGoalBanner";
import { stadiumAudio } from "../utils/audioEffects";

interface BroadcastPitchProps {
  latestEvent: MatchEvent | null;
  homeTeam: TeamProfile | null;
  awayTeam: TeamProfile | null;
  homePlayers?: PlayerProfile[];
  awayPlayers?: PlayerProfile[];
  focusedPlayer: PlayerProfile | null;
  onSelectPlayer: (player: PlayerProfile | null) => void;
  playerHeatmaps?: Record<string, PitchCoordinates[]>;
  passLinks?: PassLink[];
  currentMinute?: number;
  period?: string;
  homeGameState?: string;
  awayGameState?: string;
  scoreHome?: number;
  scoreAway?: number;
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
  scoreHome = 0,
  scoreAway = 0,
}) => {
  const [showPlayerHeatmap, setShowPlayerHeatmap] = useState(false);
  const [showPassNetwork, setShowPassNetwork] = useState(false);

  // Smooth real-time ball gliding state (Passer -> Receiver)
  const [ballCoords, setBallCoords] = useState<PitchCoordinates>(
    latestEvent ? latestEvent.location : { x: 50, y: 50 }
  );
  const [isBallGliding, setIsBallGliding] = useState(false);
  const [glideDurationMs, setGlideDurationMs] = useState(1300);
  const lastProcessedEventId = useRef<string | null>(null);

  // Trigger smooth ball travel on each new match event
  useEffect(() => {
    if (!latestEvent) return;
    if (latestEvent.event_id === lastProcessedEventId.current) return;
    lastProcessedEventId.current = latestEvent.event_id;

    const start = latestEvent.location;
    const end = latestEvent.end_location;

    // Audio cues
    stadiumAudio.playKick(latestEvent.ball_speed_kmh || latestEvent.shot_speed_kmh || 52);
    if (latestEvent.event_type === "shot") {
      stadiumAudio.playCrowdRoar(false);
    } else if (latestEvent.event_type === "goal") {
      stadiumAudio.playWhistle(true);
      stadiumAudio.playCrowdRoar(true);
    }

    if (end) {
      // 1. Instantly place ball at passer's foot
      setBallCoords(start);
      setIsBallGliding(false);

      // 2. Determine duration based on event type
      const isShot = latestEvent.event_type === "shot" || latestEvent.event_type === "goal";
      const duration = isShot ? 600 : 1300;
      setGlideDurationMs(duration);

      // 3. Smooth glide to recipient
      const glideTimer = setTimeout(() => {
        setBallCoords(end);
        setIsBallGliding(true);
      }, 35);

      return () => clearTimeout(glideTimer);
    } else {
      setBallCoords(start);
      setIsBallGliding(false);
    }
  }, [latestEvent?.event_id]);

  // Determine if it's 2nd Half (Sides switch!)
  const is2H = period === "2H" || latestEvent?.period === "2H" || currentMinute > 45;

  const getTrajectoryColor = () => {
    if (!latestEvent) return "#00FF87";
    if (latestEvent.event_type === "goal") return "#00FF87";
    if (latestEvent.event_type === "shot") return "#FF2882";
    const diff = latestEvent.pass_difficulty_rating || 0;
    if (diff > 0.7) return "#FF2882";
    if (diff > 0.4) return "#FFA500";
    return "#00FF87";
  };

  // Dynamic player coordinates
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

  const leftTeam = is2H ? awayTeam : homeTeam;
  const rightTeam = is2H ? homeTeam : awayTeam;

  return (
    <div className="relative w-full">
      {/* Crisp 2D Clean Pitch Container */}
      <div className="relative w-full aspect-[105/68] bg-gradient-to-br from-[#0c381a] via-[#092d14] to-[#06210f] rounded-2xl overflow-hidden border border-emerald-800/60 shadow-[0_12px_40px_rgba(0,0,0,0.7)] select-none">
        {/* Subtle Grass Striping Texture */}
        <div className="absolute inset-0 opacity-15 bg-[repeating-linear-gradient(90deg,transparent,transparent_45px,rgba(255,255,255,0.05)_45px,rgba(255,255,255,0.05)_90px)] pointer-events-none" />

        {/* SVG Pitch Markings */}
        <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
          {/* Outer Boundary */}
          <rect x="2" y="2" width="96" height="96" fill="none" stroke="rgba(255,255,255,0.45)" strokeWidth="0.75" />
          {/* Halfway Line */}
          <line x1="50" y1="2" x2="50" y2="98" stroke="rgba(255,255,255,0.45)" strokeWidth="0.75" />
          {/* Center Circle */}
          <circle cx="50" cy="50" r="10" fill="none" stroke="rgba(255,255,255,0.45)" strokeWidth="0.75" />
          <circle cx="50" cy="50" r="0.8" fill="rgba(255,255,255,0.8)" />

          {/* Left Penalty Area */}
          <rect x="2" y="22" width="16" height="56" fill="none" stroke="rgba(255,255,255,0.45)" strokeWidth="0.75" />
          <rect x="2" y="36" width="6" height="28" fill="none" stroke="rgba(255,255,255,0.45)" strokeWidth="0.75" />
          <circle cx="11" cy="50" r="0.8" fill="rgba(255,255,255,0.8)" />
          <path d="M 18,40 A 10,10 0 0,1 18,60" fill="none" stroke="rgba(255,255,255,0.45)" strokeWidth="0.75" />

          {/* Right Penalty Area */}
          <rect x="82" y="22" width="16" height="56" fill="none" stroke="rgba(255,255,255,0.45)" strokeWidth="0.75" />
          <rect x="92" y="36" width="6" height="28" fill="none" stroke="rgba(255,255,255,0.45)" strokeWidth="0.75" />
          <circle cx="89" cy="50" r="0.8" fill="rgba(255,255,255,0.8)" />
          <path d="M 82,40 A 10,10 0 0,0 82,60" fill="none" stroke="rgba(255,255,255,0.45)" strokeWidth="0.75" />

          {/* Goal Mouths */}
          <rect x="0" y="44" width="2" height="12" fill="rgba(255,255,255,0.15)" stroke="white" strokeWidth="0.6" />
          <rect x="98" y="44" width="2" height="12" fill="rgba(255,255,255,0.15)" stroke="white" strokeWidth="0.6" />

          {/* Pass Network Overlay Lines */}
          {showPassNetwork &&
            passLinks.map((link, idx) => {
              const p1 = playerMap.get(link.source_player_id);
              const p2 = playerMap.get(link.target_player_id);
              if (!p1 || !p2) return null;
              const strokeWidth = Math.min(2.2, Math.max(0.6, link.count * 0.4));
              return (
                <line
                  key={`pl_${idx}`}
                  x1={p1.current_coords.x}
                  y1={p1.current_coords.y}
                  x2={p2.current_coords.x}
                  y2={p2.current_coords.y}
                  stroke="#04F5FF"
                  strokeWidth={strokeWidth}
                  strokeOpacity={0.6}
                  strokeDasharray="1.2 0.8"
                />
              );
            })}

          {/* Clean Subtle Trajectory Line */}
          {latestEvent?.end_location && (
            <g>
              <line
                x1={latestEvent.location.x}
                y1={latestEvent.location.y}
                x2={latestEvent.end_location.x}
                y2={latestEvent.end_location.y}
                stroke={getTrajectoryColor()}
                strokeWidth="1.1"
                strokeDasharray="2 1.5"
                strokeOpacity={isBallGliding ? "0.3" : "0.7"}
              />
              <circle cx={latestEvent.end_location.x} cy={latestEvent.end_location.y} r="1.2" fill={getTrajectoryColor()} opacity="0.6" />
            </g>
          )}
        </svg>

        {/* Premier League Clean Broadcast Scorebug (Top-Left) */}
        <div className="absolute top-3 left-3 z-30 flex items-center bg-black/85 backdrop-blur-md rounded-xl border border-white/15 shadow-xl text-white font-sans overflow-hidden">
          {/* Teams and Score */}
          <div className="flex items-center gap-2 px-3 py-1.5 border-r border-white/10">
            <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: homeTeam?.primary_color || "#EF0107" }} />
            <span className="font-bold text-xs">{homeTeam?.short_name || "HOME"}</span>
            <span className="font-mono font-black text-sm text-yellow-300 px-1">{scoreHome}</span>
            <span className="text-gray-400 font-mono text-xs">-</span>
            <span className="font-mono font-black text-sm text-yellow-300 px-1">{scoreAway}</span>
            <span className="font-bold text-xs">{awayTeam?.short_name || "AWAY"}</span>
            <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: awayTeam?.primary_color || "#6CABDD" }} />
          </div>

          {/* Clock & Half */}
          <div className="px-2.5 py-1.5 font-mono text-[11px] font-bold text-gray-300 flex items-center gap-1.5 bg-white/5">
            <span className="text-[#00FF87]">{currentMinute}'</span>
            <span className="text-gray-400 text-[10px]">[{period}]</span>
          </div>

          {/* Tactical Indicator Tag (If in All-Out Attack or Park-The-Bus) */}
          {homeGameState === "all_out_attack" && (
            <span className="px-2 py-1 text-[9px] font-mono font-bold text-red-400 bg-red-950/60 border-l border-white/10 animate-pulse">
              ▲ {homeTeam?.short_name} Asalt
            </span>
          )}
          {awayGameState === "all_out_attack" && (
            <span className="px-2 py-1 text-[9px] font-mono font-bold text-red-400 bg-red-950/60 border-l border-white/10 animate-pulse">
              ▲ {awayTeam?.short_name} Asalt
            </span>
          )}
          {homeGameState === "park_the_bus" && (
            <span className="px-2 py-1 text-[9px] font-mono font-bold text-blue-300 bg-blue-950/60 border-l border-white/10">
              🛡️ {homeTeam?.short_name} Bloc Jos
            </span>
          )}
          {awayGameState === "park_the_bus" && (
            <span className="px-2 py-1 text-[9px] font-mono font-bold text-blue-300 bg-blue-950/60 border-l border-white/10">
              🛡️ {awayTeam?.short_name} Bloc Jos
            </span>
          )}
        </div>

        {/* Clean Controls (Top-Right) */}
        <div className="absolute top-3 right-3 flex items-center gap-1.5 z-30 bg-black/75 backdrop-blur-md p-1 rounded-xl border border-white/15 shadow-xl">
          <button
            onClick={() => setShowPlayerHeatmap(!showPlayerHeatmap)}
            className={`flex items-center gap-1 text-[10px] font-bold px-2.5 py-1 rounded-lg transition-all ${
              showPlayerHeatmap
                ? "bg-amber-500 text-black shadow-md font-black"
                : "text-gray-300 hover:text-white hover:bg-white/10"
            }`}
            title="Afișează zonele de acțiune pentru jucătorul selectat"
          >
            <Flame className="w-3.5 h-3.5" />
            <span>
              {showPlayerHeatmap && activeHeatmapPlayer
                ? activeHeatmapPlayer.name.split(" ").slice(-1)[0]
                : "Heatmap"}
            </span>
          </button>

          <button
            onClick={() => setShowPassNetwork(!showPassNetwork)}
            className={`flex items-center gap-1 text-[10px] font-bold px-2.5 py-1 rounded-lg transition-all ${
              showPassNetwork
                ? "bg-[#04F5FF] text-black shadow-md font-black"
                : "text-gray-300 hover:text-white hover:bg-white/10"
            }`}
            title="Comută diagrama rețelei de pase"
          >
            <Share2 className="w-3.5 h-3.5" />
            <span>Pase</span>
          </button>
        </div>

        {/* Subtle Half-Time Badge */}
        {is2H && (
          <div className="absolute top-3 left-1/2 -translate-x-1/2 bg-black/70 backdrop-blur px-2.5 py-0.5 rounded-full border border-white/10 text-[9px] font-mono font-bold text-gray-300 pointer-events-none">
            🔄 Repriza a 2-a • Porți inversate
          </div>
        )}

        {/* Subtle Attack Direction Pills */}
        <div className="absolute bottom-2 left-3 flex items-center gap-1 text-[9px] font-mono font-semibold text-gray-400 bg-black/60 px-2 py-0.5 rounded pointer-events-none border border-white/5">
          <span style={{ color: leftTeam?.primary_color || "#EF0107" }}>{leftTeam?.short_name || "HOME"}</span>
          <ArrowRight className="w-2.5 h-2.5 text-gray-300" />
        </div>
        <div className="absolute bottom-2 right-3 flex items-center gap-1 text-[9px] font-mono font-semibold text-gray-400 bg-black/60 px-2 py-0.5 rounded pointer-events-none border border-white/5">
          <ArrowLeft className="w-2.5 h-2.5 text-gray-300" />
          <span style={{ color: rightTeam?.primary_color || "#6CABDD" }}>{rightTeam?.short_name || "AWAY"}</span>
        </div>

        {/* Individual Player Heatmap Overlay (Opta Precision Clusters) */}
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
                    "radial-gradient(circle, rgba(255, 35, 0, 0.8) 0%, rgba(255, 140, 0, 0.5) 45%, rgba(255, 230, 0, 0.2) 75%, transparent 100%)",
                }}
                className="absolute w-16 h-16 rounded-full blur-[6px] pointer-events-none"
              />
            ))}
          </div>
        )}

        {/* Render Players - Home Team */}
        {currentHomePlayers.map((p) => {
          const isFocused = focusedPlayer?.id === p.id;
          const isActor = latestEvent?.player.id === p.id;

          return (
            <div
              key={p.id}
              onClick={() => onSelectPlayer(isFocused ? null : p)}
              className="absolute cursor-pointer z-20 group flex flex-col items-center"
              style={{
                left: `${p.current_coords.x}%`,
                top: `${p.current_coords.y}%`,
                transform: "translate(-50%, -50%)",
                transition: "left 950ms cubic-bezier(0.25, 0.46, 0.45, 0.94), top 950ms cubic-bezier(0.25, 0.46, 0.45, 0.94)",
              }}
            >
              {/* Focus Ring */}
              {isFocused && (
                <span className="absolute -inset-2 rounded-full border-2 border-[#04F5FF] animate-pulse opacity-90 pointer-events-none shadow-[0_0_12px_#04F5FF]" />
              )}

              {/* Player Jersey Dot */}
              <div
                style={{ backgroundColor: homeTeam?.primary_color || "#EF0107" }}
                className={`w-6 h-6 rounded-full flex items-center justify-center font-bold text-[10px] text-white shadow-md border-2 transition-transform duration-200 group-hover:scale-125 ${
                  isActor
                    ? "border-yellow-300 scale-110 shadow-yellow-500/50"
                    : isFocused
                    ? "border-[#04F5FF] scale-110"
                    : "border-white/90"
                }`}
              >
                {p.number}
              </div>

              {/* Clean Hover Name Tag */}
              <span className="opacity-0 group-hover:opacity-100 transition-opacity bg-black/95 text-[9px] text-white px-1.5 py-0.5 rounded mt-0.5 pointer-events-none font-semibold whitespace-nowrap shadow-lg border border-white/10 z-30">
                {p.name} ({p.position})
              </span>
            </div>
          );
        })}

        {/* Render Players - Away Team */}
        {currentAwayPlayers.map((p) => {
          const isFocused = focusedPlayer?.id === p.id;
          const isActor = latestEvent?.player.id === p.id;

          return (
            <div
              key={p.id}
              onClick={() => onSelectPlayer(isFocused ? null : p)}
              className="absolute cursor-pointer z-20 group flex flex-col items-center"
              style={{
                left: `${p.current_coords.x}%`,
                top: `${p.current_coords.y}%`,
                transform: "translate(-50%, -50%)",
                transition: "left 950ms cubic-bezier(0.25, 0.46, 0.45, 0.94), top 950ms cubic-bezier(0.25, 0.46, 0.45, 0.94)",
              }}
            >
              {/* Focus Ring */}
              {isFocused && (
                <span className="absolute -inset-2 rounded-full border-2 border-[#04F5FF] animate-pulse opacity-90 pointer-events-none shadow-[0_0_12px_#04F5FF]" />
              )}

              {/* Player Jersey Dot */}
              <div
                style={{ backgroundColor: awayTeam?.primary_color || "#6CABDD" }}
                className={`w-6 h-6 rounded-full flex items-center justify-center font-bold text-[10px] text-white shadow-md border-2 transition-transform duration-200 group-hover:scale-125 ${
                  isActor
                    ? "border-yellow-300 scale-110 shadow-yellow-500/50"
                    : isFocused
                    ? "border-[#04F5FF] scale-110"
                    : "border-white/90"
                }`}
              >
                {p.number}
              </div>

              {/* Clean Hover Name Tag */}
              <span className="opacity-0 group-hover:opacity-100 transition-opacity bg-black/95 text-[9px] text-white px-1.5 py-0.5 rounded mt-0.5 pointer-events-none font-semibold whitespace-nowrap shadow-lg border border-white/10 z-30">
                {p.name} ({p.position})
              </span>
            </div>
          );
        })}

        {/* Real-time Gliding Ball (Smooth Trajectory across the grass) */}
        <div
          style={{
            left: `${ballCoords.x}%`,
            top: `${ballCoords.y}%`,
            transform: "translate(-50%, -50%)",
            transition: isBallGliding
              ? `left ${glideDurationMs}ms cubic-bezier(0.22, 1, 0.36, 1), top ${glideDurationMs}ms cubic-bezier(0.22, 1, 0.36, 1)`
              : "none",
          }}
          className="absolute z-30 pointer-events-none flex flex-col items-center"
        >
          {/* Football */}
          <div
            className={`w-3.5 h-3.5 rounded-full bg-white border-2 border-black flex items-center justify-center transition-all ${
              isBallGliding ? "scale-110 shadow-[0_0_12px_rgba(255,255,255,0.9)]" : "shadow-[0_0_6px_rgba(255,255,255,0.6)]"
            }`}
          >
            <div className="w-1 h-1 rounded-full bg-black/80"></div>
          </div>

          {/* Shot Speed Badge on Shots/Goals */}
          {latestEvent &&
            (latestEvent.event_type === "shot" || latestEvent.event_type === "goal") &&
            (latestEvent.shot_speed_kmh || latestEvent.ball_speed_kmh) && (
              <div className="mt-1 bg-black/95 text-yellow-300 border border-yellow-400/80 px-1.5 py-0.5 rounded text-[8px] font-mono font-black flex items-center gap-1 shadow-lg whitespace-nowrap z-40">
                <Zap className="w-2.5 h-2.5 text-yellow-400" />
                <span>{latestEvent.shot_speed_kmh || latestEvent.ball_speed_kmh} km/h</span>
              </div>
            )}
        </div>

        {/* Subtle Watermark */}
        <div className="absolute bottom-2 right-20 bg-black/50 backdrop-blur px-2 py-0.5 rounded text-[8px] text-gray-400 font-mono pointer-events-none border border-white/5">
          OPTA LIVE • 105x68m
        </div>
      </div>

      {/* Cinematic Goal Alert Banner */}
      <BroadcastGoalBanner
        latestEvent={latestEvent}
        homeTeam={homeTeam}
        awayTeam={awayTeam}
      />
    </div>
  );
};
