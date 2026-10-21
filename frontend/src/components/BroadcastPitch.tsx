import React, { useState, useEffect, useRef } from "react";
import type { MatchEvent, PlayerProfile, TeamProfile, PitchCoordinates, PassLink } from "../types";
import { Zap, Share2, ArrowRight, ArrowLeft, ShieldAlert, Shield } from "lucide-react";
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
  passLinks?: PassLink[];
  currentMinute?: number;
  period?: string;
  homeGameState?: string;
  awayGameState?: string;
  scoreHome?: number;
  scoreAway?: number;
  controlVsChaosIndex?: number;
}

export const BroadcastPitch: React.FC<BroadcastPitchProps> = ({
  latestEvent,
  homeTeam,
  awayTeam,
  homePlayers = [],
  awayPlayers = [],
  focusedPlayer,
  onSelectPlayer,
  passLinks = [],
  currentMinute = 1,
  period = "1H",
  homeGameState = "balanced",
  awayGameState = "balanced",
  scoreHome = 0,
  scoreAway = 0,
  controlVsChaosIndex,
}) => {
  const [showPassNetwork, setShowPassNetwork] = useState(false);

  // Smooth real-time ball gliding state (Passer -> Receiver)
  const [ballCoords, setBallCoords] = useState<PitchCoordinates>(
    latestEvent ? latestEvent.location : { x: 50, y: 50 }
  );
  const [isBallGliding, setIsBallGliding] = useState(false);
  const [glideDurationMs, setGlideDurationMs] = useState(1500);
  const lastProcessedEventId = useRef<string | null>(null);

  // Trigger smooth ball travel on each new match event
  useEffect(() => {
    if (!latestEvent) return;
    if (latestEvent.event_id === lastProcessedEventId.current) return;
    lastProcessedEventId.current = latestEvent.event_id;

    const start = latestEvent.location;
    const end = latestEvent.end_location;

    // Audio cues
    if (latestEvent.event_type === "tackle") {
      stadiumAudio.playTackle();
    } else if (latestEvent.pass_outcome === "intercepted" || latestEvent.event_type === "interception") {
      stadiumAudio.playInterception();
    } else {
      stadiumAudio.playKick(latestEvent.ball_speed_kmh || latestEvent.shot_speed_kmh || 52);
    }

    if (latestEvent.event_type === "shot") {
      stadiumAudio.playCrowdRoar(false);
    } else if (latestEvent.event_type === "goal") {
      stadiumAudio.playWhistle(true);
      stadiumAudio.playCrowdRoar(true);
    }

    if (end && (start.x !== end.x || start.y !== end.y)) {
      // 1. Place ball at passer's foot without transition
      setBallCoords(start);
      setIsBallGliding(false);

      // 2. Determine duration based on event type
      const isShot = latestEvent.event_type === "shot" || latestEvent.event_type === "goal";
      const duration = isShot ? 750 : 1500;
      setGlideDurationMs(duration);

      // 3. Smooth glide to recipient's exact arrival point
      const glideTimer = setTimeout(() => {
        setBallCoords(end);
        setIsBallGliding(true);
      }, 40);

      return () => clearTimeout(glideTimer);
    } else {
      setBallCoords(start);
      setIsBallGliding(false);
    }
  }, [latestEvent?.event_id]);

  // Determine if it's 2nd Half (Sides switch!)
  const is2H = period === "2H" || latestEvent?.period === "2H" || currentMinute > 45;

  const isInterception =
    latestEvent?.pass_outcome === "intercepted" ||
    latestEvent?.event_type === "interception";

  const isTackle = latestEvent?.event_type === "tackle";
  const isCorner = latestEvent?.event_type === "corner" || latestEvent?.set_piece_type === "corner";
  const isPenalty = latestEvent?.event_type === "penalty" || latestEvent?.set_piece_type === "penalty";
  const isFreeKick = latestEvent?.event_type === "free_kick" || latestEvent?.set_piece_type === "free_kick";
  const isFoul = latestEvent?.event_type === "foul";
  const isCard = latestEvent?.event_type === "card";
  const isRedCard = isCard && latestEvent?.card_type === "red";
  const isYellowCard = isCard && !isRedCard;

  const getTrajectoryColor = () => {
    if (!latestEvent) return "#00FF87";
    if (isRedCard) return "#EF4444";
    if (isYellowCard) return "#EAB308";
    if (isFoul) return "#F59E0B";
    if (isPenalty) return "#FF2882";      // Electric Magenta / Penalty
    if (isCorner) return "#04F5FF";       // Radiant Cyan / Corner Cross
    if (isFreeKick) return "#FFA500";     // Gold / Direct Free Kick
    if (isInterception) return "#FF8800"; // Electric Amber / Turnover
    if (latestEvent.event_type === "goal") return "#00FF87";
    if (latestEvent.event_type === "shot") return "#FF2882";
    const diff = latestEvent.pass_difficulty_rating || 0;
    if (diff > 0.7) return "#FF2882";
    if (diff > 0.4) return "#FFA500";
    return "#00FF87";
  };

  // Trajectory distance & validity check
  const trajDistance = latestEvent?.end_location
    ? Math.hypot(
        latestEvent.end_location.x - latestEvent.location.x,
        latestEvent.end_location.y - latestEvent.location.y
      )
    : 0;

  const isBallFlightEvent =
    Boolean(latestEvent?.end_location) &&
    (isCorner || isPenalty || isFreeKick || (
      trajDistance >= 3.0 &&
      (isInterception ||
        !["duel", "tackle", "foul", "yellow_card", "red_card"].includes(
          latestEvent?.event_type || ""
        ))
    ));

  // Dynamic player coordinates
  const currentHomePlayers = homePlayers.length > 0 ? homePlayers : (homeTeam?.players || []);
  const currentAwayPlayers = awayPlayers.length > 0 ? awayPlayers : (awayTeam?.players || []);
  const allPlayers = [...currentHomePlayers, ...currentAwayPlayers];
  const playerMap = new Map(allPlayers.map((p) => [p.id, p]));

  const leftTeam = is2H ? awayTeam : homeTeam;
  const rightTeam = is2H ? homeTeam : awayTeam;

  // Active Possession Identification
  const possessingTeamId = latestEvent?.team_id || (homeTeam ? homeTeam.id : "");
  const isLeftPossessing = leftTeam?.id === possessingTeamId;
  const isRightPossessing = rightTeam?.id === possessingTeamId;

  // Track possession flips for animated Turnover Alert Ribbon
  const prevPossessingTeamRef = useRef<string | null>(null);
  const [turnoverAlert, setTurnoverAlert] = useState<{
    teamName: string;
    teamColor: string;
    type: string;
  } | null>(null);

  useEffect(() => {
    if (!possessingTeamId) return;
    if (prevPossessingTeamRef.current && prevPossessingTeamRef.current !== possessingTeamId) {
      const winner = possessingTeamId === homeTeam?.id ? homeTeam : awayTeam;
      const turnType = isInterception
        ? "INTERCEPTION"
        : isTackle
        ? "TACKLE WON"
        : "TURNOVER";
      setTurnoverAlert({
        teamName: winner?.short_name || "TEAM",
        teamColor: winner?.primary_color || "#00FF87",
        type: turnType,
      });
      const timer = setTimeout(() => setTurnoverAlert(null), 2400);
      return () => clearTimeout(timer);
    }
    prevPossessingTeamRef.current = possessingTeamId;
  }, [possessingTeamId, isInterception, isTackle]);

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

          {/* Defined Arrowheads & Trajectory Glow */}
          <defs>
            <filter id="ballTrailGlow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="0.6" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
            <filter id="interceptionGlow" x="-25%" y="-25%" width="150%" height="150%">
              <feGaussianBlur stdDeviation="0.9" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* High-Visibility Ball Trajectory & Arrival Beacon (Passes & Shots & Interceptions) */}
          {isBallFlightEvent && latestEvent?.end_location && (
            <g>
              {/* Soft Ambient Glow under trajectory */}
              <line
                x1={latestEvent.location.x}
                y1={latestEvent.location.y}
                x2={latestEvent.end_location.x}
                y2={latestEvent.end_location.y}
                stroke={getTrajectoryColor()}
                strokeWidth={isInterception ? "3.4" : "2.8"}
                strokeOpacity={isInterception ? "0.45" : "0.35"}
                filter={isInterception ? "url(#interceptionGlow)" : "url(#ballTrailGlow)"}
              />

              {/* Main Crisp Trajectory Line (Clean dashed line, no triangles) */}
              <line
                x1={latestEvent.location.x}
                y1={latestEvent.location.y}
                x2={latestEvent.end_location.x}
                y2={latestEvent.end_location.y}
                stroke={getTrajectoryColor()}
                strokeWidth={isInterception ? "1.6" : "1.4"}
                strokeDasharray={isInterception ? "1.8 1.4" : "2.2 1.4"}
                strokeOpacity="0.95"
              />

              {/* Origin Kick Anchor Point */}
              <circle
                cx={latestEvent.location.x}
                cy={latestEvent.location.y}
                r="1.0"
                fill={getTrajectoryColor()}
                opacity="0.8"
              />

              {/* Interception Turnover Ring at landing point */}
              {isInterception && (
                <circle
                  cx={latestEvent.end_location.x}
                  cy={latestEvent.end_location.y}
                  r="2.4"
                  stroke="#FF8800"
                  strokeWidth="0.5"
                  strokeDasharray="0.9 0.7"
                  fill="none"
                  opacity="0.85"
                />
              )}

              {/* Arrival Target Point (Clean discrete dot where ball lands) */}
              <circle
                cx={latestEvent.end_location.x}
                cy={latestEvent.end_location.y}
                r={isInterception ? "1.6" : "1.4"}
                fill={getTrajectoryColor()}
                stroke="#000"
                strokeWidth="0.4"
                opacity="0.95"
              />
            </g>
          )}

          {/* Tactical Tackle / Dispossession Pitch Ring */}
          {isTackle && latestEvent?.location && (
            <g>
              <circle
                cx={latestEvent.location.x}
                cy={latestEvent.location.y}
                r="3.2"
                stroke="#04F5FF"
                strokeWidth="0.6"
                strokeDasharray="1.2 0.8"
                fill="rgba(4, 245, 255, 0.12)"
                opacity="0.9"
              />
              <circle
                cx={latestEvent.location.x}
                cy={latestEvent.location.y}
                r="1.4"
                fill="#04F5FF"
                stroke="#000"
                strokeWidth="0.4"
              />
            </g>
          )}

          {/* Corner Kick Turf Arc & Beacon */}
          {isCorner && latestEvent?.location && (
            <g>
              <circle
                cx={latestEvent.location.x}
                cy={latestEvent.location.y}
                r="7.5"
                stroke="#04F5FF"
                strokeWidth="0.9"
                strokeDasharray="1.5 1.0"
                fill="rgba(4, 245, 255, 0.16)"
                opacity="0.95"
              />
              <circle
                cx={latestEvent.location.x}
                cy={latestEvent.location.y}
                r="3.5"
                stroke="#04F5FF"
                strokeWidth="0.7"
                fill="rgba(4, 245, 255, 0.35)"
              />
              <circle
                cx={latestEvent.location.x}
                cy={latestEvent.location.y}
                r="1.4"
                fill="#FFFFFF"
                stroke="#04F5FF"
                strokeWidth="0.5"
              />
            </g>
          )}

          {/* Penalty Spot Holographic Reticle */}
          {isPenalty && latestEvent?.location && (
            <g>
              <circle
                cx={latestEvent.location.x}
                cy={latestEvent.location.y}
                r="6.0"
                stroke="#FF2882"
                strokeWidth="0.9"
                strokeDasharray="1.5 1.0"
                fill="rgba(255, 40, 130, 0.22)"
                opacity="0.95"
              />
              <circle
                cx={latestEvent.location.x}
                cy={latestEvent.location.y}
                r="3.0"
                stroke="#FFD700"
                strokeWidth="0.7"
                fill="rgba(255, 215, 0, 0.3)"
              />
              <circle
                cx={latestEvent.location.x}
                cy={latestEvent.location.y}
                r="1.3"
                fill="#FFD700"
                stroke="#000000"
                strokeWidth="0.4"
              />
            </g>
          )}

          {/* Foul Referee Stoppage Turf Marker */}
          {isFoul && latestEvent?.location && (
            <g>
              <circle
                cx={latestEvent.location.x}
                cy={latestEvent.location.y}
                r="4.8"
                stroke="#F59E0B"
                strokeWidth="0.8"
                strokeDasharray="1.2 0.8"
                fill="rgba(245, 158, 11, 0.2)"
                opacity="0.95"
              />
              <circle
                cx={latestEvent.location.x}
                cy={latestEvent.location.y}
                r="2.0"
                fill="#F59E0B"
                stroke="#000000"
                strokeWidth="0.4"
              />
            </g>
          )}

          {/* Disciplinary Card Turf Marker */}
          {isCard && latestEvent?.location && (
            <g>
              <circle
                cx={latestEvent.location.x}
                cy={latestEvent.location.y}
                r="5.5"
                stroke={isRedCard ? "#EF4444" : "#EAB308"}
                strokeWidth="0.9"
                strokeDasharray="1.4 0.9"
                fill={isRedCard ? "rgba(239, 68, 68, 0.25)" : "rgba(234, 179, 8, 0.25)"}
                opacity="0.95"
              />
              <circle
                cx={latestEvent.location.x}
                cy={latestEvent.location.y}
                r="2.4"
                fill={isRedCard ? "#EF4444" : "#EAB308"}
                stroke="#000000"
                strokeWidth="0.4"
              />
            </g>
          )}
        </svg>

        {/* Premier League Clean Broadcast Scorebug (Top-Left) */}
        <div className="absolute top-3 left-3 z-30 flex items-center bg-black/85 backdrop-blur-md rounded-xl border border-white/15 shadow-xl text-white font-sans overflow-hidden">
          {/* Teams and Score with Possession Indicators */}
          <div className="flex items-center gap-2 px-3 py-1.5 border-r border-white/10">
            <div className="flex items-center gap-1.5">
              <span
                className={`w-2.5 h-2.5 rounded-full transition-all ${
                  homeTeam?.id === possessingTeamId
                    ? "ring-2 ring-white scale-125 shadow-[0_0_8px_#00FF87]"
                    : "opacity-60"
                }`}
                style={{ backgroundColor: homeTeam?.primary_color || "#EF0107" }}
              />
              <span className={`font-bold text-xs ${homeTeam?.id === possessingTeamId ? "text-white underline decoration-emerald-400 underline-offset-4" : "text-gray-400"}`}>
                {homeTeam?.short_name || "HOME"}
              </span>
              {homeTeam?.id === possessingTeamId && (
                <span className="text-[9px] animate-pulse">⚽</span>
              )}
            </div>
            <span className="font-mono font-black text-sm text-yellow-300 px-1">{scoreHome}</span>
            <span className="text-gray-400 font-mono text-xs">-</span>
            <span className="font-mono font-black text-sm text-yellow-300 px-1">{scoreAway}</span>
            <div className="flex items-center gap-1.5">
              {awayTeam?.id === possessingTeamId && (
                <span className="text-[9px] animate-pulse">⚽</span>
              )}
              <span className={`font-bold text-xs ${awayTeam?.id === possessingTeamId ? "text-white underline decoration-cyan-400 underline-offset-4" : "text-gray-400"}`}>
                {awayTeam?.short_name || "AWAY"}
              </span>
              <span
                className={`w-2.5 h-2.5 rounded-full transition-all ${
                  awayTeam?.id === possessingTeamId
                    ? "ring-2 ring-white scale-125 shadow-[0_0_8px_#04F5FF]"
                    : "opacity-60"
                }`}
                style={{ backgroundColor: awayTeam?.primary_color || "#6CABDD" }}
              />
            </div>
          </div>

          {/* Clock & Half */}
          <div className="px-2.5 py-1.5 font-mono text-[11px] font-bold text-gray-300 flex items-center gap-1.5 bg-white/5">
            <span className="text-[#00FF87]">{currentMinute}'</span>
            <span className="text-gray-400 text-[10px]">[{period}]</span>
          </div>

          {/* Tactical Indicator Tag (If in All-Out Attack or Park-The-Bus) */}
          {homeGameState === "all_out_attack" && (
            <span className="px-2 py-1 text-[9px] font-mono font-bold text-red-400 bg-red-950/60 border-l border-white/10 animate-pulse">
              ▲ {homeTeam?.short_name} Overload
            </span>
          )}
          {awayGameState === "all_out_attack" && (
            <span className="px-2 py-1 text-[9px] font-mono font-bold text-red-400 bg-red-950/60 border-l border-white/10 animate-pulse">
              ▲ {awayTeam?.short_name} Overload
            </span>
          )}
          {homeGameState === "park_the_bus" && (
            <span className="px-2 py-1 text-[9px] font-mono font-bold text-blue-300 bg-blue-950/60 border-l border-white/10">
              🛡️ {homeTeam?.short_name} Low Block
            </span>
          )}
          {awayGameState === "park_the_bus" && (
            <span className="px-2 py-1 text-[9px] font-mono font-bold text-blue-300 bg-blue-950/60 border-l border-white/10">
              🛡️ {awayTeam?.short_name} Low Block
            </span>
          )}
          {controlVsChaosIndex !== undefined && controlVsChaosIndex < 35 && (
            <span className="px-2 py-1 text-[9px] font-mono font-bold text-amber-300 bg-amber-950/80 border-l border-white/10 animate-pulse flex items-center gap-1">
              ⚡ High Chaos Phase
            </span>
          )}
        </div>

        {/* High-Visibility Possession Turnover Alert Ribbon */}
        {turnoverAlert && (
          <div className="absolute top-14 left-1/2 -translate-x-1/2 z-40 flex items-center gap-2 bg-black/92 backdrop-blur-md border-2 border-amber-400 px-4 py-1.5 rounded-full shadow-[0_0_24px_rgba(255,170,0,0.65)] animate-in fade-in slide-in-from-top-2 duration-200 pointer-events-none">
            <Zap className="w-3.5 h-3.5 text-amber-400 animate-bounce" />
            <span className="text-[10px] font-black text-amber-300 font-mono tracking-wider uppercase">
              {turnoverAlert.type} •
            </span>
            <span className="text-[10px] font-bold text-white">
              {turnoverAlert.teamName} GAIN POSSESSION
            </span>
            <span
              className="w-2.5 h-2.5 rounded-full ml-0.5 shadow-[0_0_8px_white]"
              style={{ backgroundColor: turnoverAlert.teamColor }}
            />
          </div>
        )}

        {/* Clean Controls (Top-Right) */}
        <div className="absolute top-3 right-3 flex items-center gap-1.5 z-30 bg-black/75 backdrop-blur-md p-1 rounded-xl border border-white/15 shadow-xl">
          <button
            onClick={() => setShowPassNetwork(!showPassNetwork)}
            className={`flex items-center gap-1 text-[10px] font-bold px-2.5 py-1 rounded-lg transition-all ${
              showPassNetwork
                ? "bg-[#04F5FF] text-black shadow-md font-black"
                : "text-gray-300 hover:text-white hover:bg-white/10"
            }`}
            title="Toggle Passing Network diagram"
          >
            <Share2 className="w-3.5 h-3.5" />
            <span>Passes</span>
          </button>
        </div>

        {/* Subtle Half-Time Badge */}
        {is2H && (
          <div className="absolute top-3 left-1/2 -translate-x-1/2 bg-black/70 backdrop-blur px-2.5 py-0.5 rounded-full border border-white/10 text-[9px] font-mono font-bold text-gray-300 pointer-events-none">
            🔄 2nd Half • Sides Swapped
          </div>
        )}

        {/* Live Set Piece / Stoppage TV Indicator Badge */}
        {(isCorner || isPenalty || isFreeKick || isFoul || isCard) && (
          <div className="absolute top-11 left-1/2 -translate-x-1/2 z-30 pointer-events-none animate-in fade-in zoom-in-95 duration-300">
            <div
              className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-black uppercase tracking-wider shadow-2xl border backdrop-blur-md ${
                isCard
                  ? isRedCard
                    ? "bg-red-950/95 border-red-500 text-red-200 shadow-[0_0_22px_rgba(239,68,68,0.95)] animate-pulse"
                    : "bg-yellow-950/95 border-yellow-400 text-yellow-200 shadow-[0_0_22px_rgba(234,179,8,0.95)] animate-pulse"
                  : isPenalty
                  ? "bg-rose-950/95 border-[#FF2882] text-[#FF2882] shadow-[0_0_22px_rgba(255,40,130,0.95)] animate-pulse"
                  : isCorner
                  ? "bg-cyan-950/95 border-[#04F5FF] text-[#04F5FF] shadow-[0_0_22px_rgba(4,245,255,0.9)]"
                  : isFreeKick
                  ? "bg-amber-950/95 border-amber-400 text-amber-300 shadow-[0_0_20px_rgba(251,191,36,0.9)]"
                  : "bg-amber-950/95 border-amber-400 text-amber-300 shadow-[0_0_18px_rgba(245,158,11,0.85)]"
              }`}
            >
              <span>
                {isCard
                  ? isRedCard
                    ? `🟥 RED CARD DISMISSAL • ${latestEvent?.player.name.toUpperCase()}`
                    : `🟨 YELLOW CARD CAUTION • ${latestEvent?.player.name.toUpperCase()}`
                  : isPenalty
                  ? "💥 PENALTY KICK • 11m • xG 0.79"
                  : isCorner
                  ? "🚩 CORNER KICK ROUTINE"
                  : isFreeKick
                  ? "⚡ DIRECT FREE KICK (24m)"
                  : `⚠️ REFEREE FOUL WHISTLE • ${latestEvent?.player.name.toUpperCase()}`}
              </span>
            </div>
          </div>
        )}

        {/* On-Turf Holographic Floating Labels at Event Origin */}
        {latestEvent?.location && (
          <>
            {isCorner && (
              <div
                style={{ left: `${latestEvent.location.x}%`, top: `${latestEvent.location.y}%` }}
                className="absolute pointer-events-none z-30 -translate-x-1/2 -translate-y-9 flex items-center gap-1 bg-black/90 border border-[#04F5FF] text-[#04F5FF] text-[9px] font-black px-2 py-0.5 rounded-full shadow-[0_0_16px_rgba(4,245,255,0.95)] animate-bounce tracking-wide whitespace-nowrap"
              >
                <span>🚩</span>
                <span>CORNER FLAG</span>
              </div>
            )}
            {isPenalty && (
              <div
                style={{ left: `${latestEvent.location.x}%`, top: `${latestEvent.location.y}%` }}
                className="absolute pointer-events-none z-30 -translate-x-1/2 -translate-y-9 flex items-center gap-1 bg-black/95 border-2 border-[#FF2882] text-white text-[9px] font-black px-2.5 py-0.5 rounded-full shadow-[0_0_20px_rgba(255,40,130,0.95)] animate-pulse tracking-wide whitespace-nowrap"
              >
                <span className="text-[#FF2882]">🎯</span>
                <span>11m PENALTY SPOT</span>
              </div>
            )}
            {isFoul && (
              <div
                style={{ left: `${latestEvent.location.x}%`, top: `${latestEvent.location.y}%` }}
                className="absolute pointer-events-none z-30 -translate-x-1/2 -translate-y-9 flex items-center gap-1 bg-black/90 border border-amber-400 text-amber-300 text-[9px] font-black px-2 py-0.5 rounded-full shadow-[0_0_15px_rgba(245,158,11,0.9)] tracking-wide whitespace-nowrap animate-bounce"
              >
                <span>⚠️</span>
                <span>FOUL SPOT</span>
              </div>
            )}
            {isCard && (
              <div
                style={{ left: `${latestEvent.location.x}%`, top: `${latestEvent.location.y}%` }}
                className={`absolute pointer-events-none z-30 -translate-x-1/2 -translate-y-9 flex items-center gap-1 bg-black/95 border-2 text-[9px] font-black px-2.5 py-0.5 rounded-full tracking-wide whitespace-nowrap animate-pulse ${
                  isRedCard
                    ? "border-red-500 text-red-200 shadow-[0_0_20px_rgba(239,68,68,0.95)]"
                    : "border-yellow-400 text-yellow-200 shadow-[0_0_20px_rgba(234,179,8,0.95)]"
                }`}
              >
                <span>{isRedCard ? "🟥" : "🟨"}</span>
                <span>{isRedCard ? "SENT OFF" : "BOOKED"}</span>
              </div>
            )}
          </>
        )}

        {/* Prominent High-Visibility Possession & Attack Direction HUD */}
        <div
          className={`absolute bottom-2.5 left-3 flex items-center gap-2 px-3 py-1.5 rounded-xl pointer-events-none border transition-all duration-300 ${
            isLeftPossessing
              ? "bg-black/90 border-2 shadow-[0_0_20px_rgba(255,255,255,0.25)] scale-105"
              : "bg-black/65 border-white/10 opacity-70"
          }`}
          style={{
            borderColor: isLeftPossessing ? leftTeam?.primary_color || "#EF0107" : "rgba(255,255,255,0.1)",
          }}
        >
          <span
            className="w-2.5 h-2.5 rounded-full shrink-0"
            style={{ backgroundColor: leftTeam?.primary_color || "#EF0107" }}
          />
          <div className="flex flex-col">
            <div className="flex items-center gap-1.5">
              <span className="font-black text-xs text-white font-mono tracking-wide">
                {leftTeam?.short_name || "HOME"}
              </span>
              <ArrowRight
                className={`w-3.5 h-3.5 ${
                  isLeftPossessing ? "text-[#00FF87] animate-pulse" : "text-gray-400"
                }`}
              />
            </div>
            {isLeftPossessing ? (
              <span className="text-[8px] font-black uppercase tracking-wider text-[#00FF87] flex items-center gap-1">
                <span>⚽</span> IN POSSESSION
              </span>
            ) : (
              <span className="text-[8px] font-bold text-gray-400 uppercase tracking-wider flex items-center gap-1">
                <Shield className="w-2.5 h-2.5" /> DEFENDING
              </span>
            )}
          </div>
        </div>

        <div
          className={`absolute bottom-2.5 right-3 flex items-center gap-2 px-3 py-1.5 rounded-xl pointer-events-none border transition-all duration-300 ${
            isRightPossessing
              ? "bg-black/90 border-2 shadow-[0_0_20px_rgba(255,255,255,0.25)] scale-105"
              : "bg-black/65 border-white/10 opacity-70"
          }`}
          style={{
            borderColor: isRightPossessing ? rightTeam?.primary_color || "#6CABDD" : "rgba(255,255,255,0.1)",
          }}
        >
          <div className="flex flex-col items-end">
            <div className="flex items-center gap-1.5">
              <ArrowLeft
                className={`w-3.5 h-3.5 ${
                  isRightPossessing ? "text-[#00FF87] animate-pulse" : "text-gray-400"
                }`}
              />
              <span className="font-black text-xs text-white font-mono tracking-wide">
                {rightTeam?.short_name || "AWAY"}
              </span>
            </div>
            {isRightPossessing ? (
              <span className="text-[8px] font-black uppercase tracking-wider text-[#00FF87] flex items-center gap-1">
                IN POSSESSION <span>⚽</span>
              </span>
            ) : (
              <span className="text-[8px] font-bold text-gray-400 uppercase tracking-wider flex items-center gap-1">
                DEFENDING <Shield className="w-2.5 h-2.5" />
              </span>
            )}
          </div>
          <span
            className="w-2.5 h-2.5 rounded-full shrink-0"
            style={{ backgroundColor: rightTeam?.primary_color || "#6CABDD" }}
          />
        </div>

        {/* Render Players - Home Team */}
        {currentHomePlayers.map((p) => {
          const isFocused = focusedPlayer?.id === p.id;
          const isActor = latestEvent?.player.id === p.id;
          const isTackler = isTackle && isActor;
          const isDispossessed = isTackle && latestEvent?.recipient?.id === p.id;
          const isCornerTaker = isCorner && isActor;
          const isPenaltyTaker = isPenalty && isActor;
          const isCardedPlayer = isCard && isActor;
          const isFoulCommitter = isFoul && isActor;
          const isFouledPlayer = (isFoul || isCard) && latestEvent?.recipient?.id === p.id;
          const isPenaltyGk = isPenalty && p.position === "GK" && latestEvent?.team_id !== p.team_id;

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
              {/* Disciplinary Card Floating 3D Badge */}
              {isCardedPlayer && (
                <div
                  className={`absolute -top-5 flex items-center gap-1 text-[9px] font-black px-2.5 py-0.5 rounded-full pointer-events-none z-40 uppercase tracking-tight shadow-2xl animate-bounce border ${
                    isRedCard
                      ? "bg-red-950/95 border-red-500 text-red-200 shadow-[0_0_20px_rgba(239,68,68,0.95)]"
                      : "bg-yellow-950/95 border-yellow-400 text-yellow-200 shadow-[0_0_20px_rgba(234,179,8,0.95)]"
                  }`}
                >
                  <span>{isRedCard ? "🟥 RED CARD" : "🟨 YELLOW CARD"}</span>
                </div>
              )}

              {/* Penalty Taker Floating Badge */}
              {isPenaltyTaker && !isCardedPlayer && (
                <div className="absolute -top-5 flex items-center gap-1 bg-rose-950/95 border-2 border-[#FF2882] text-rose-200 text-[9px] font-black px-2.5 py-0.5 rounded-full shadow-[0_0_18px_rgba(255,40,130,0.95)] pointer-events-none z-30 uppercase tracking-tight whitespace-nowrap animate-pulse">
                  <span>🎯 Penalty Taker</span>
                </div>
              )}

              {/* Penalty Goalkeeper Floating Badge */}
              {isPenaltyGk && (
                <div className="absolute -top-4.5 flex items-center gap-0.5 bg-amber-950/95 border border-yellow-400 text-yellow-300 text-[8px] font-black px-2 py-0.2 rounded-full shadow-[0_0_12px_rgba(255,215,0,0.85)] pointer-events-none z-30 uppercase tracking-tight whitespace-nowrap">
                  <span>🧤 GK</span>
                </div>
              )}

              {/* Corner Taker Floating Badge */}
              {isCornerTaker && (
                <div className="absolute -top-4.5 flex items-center gap-0.5 bg-cyan-950/95 border border-[#04F5FF] text-[#04F5FF] text-[8px] font-black px-2 py-0.2 rounded-full shadow-[0_0_16px_rgba(4,245,255,0.95)] pointer-events-none z-30 uppercase tracking-tight whitespace-nowrap animate-pulse">
                  <span>🚩 Corner Taker</span>
                </div>
              )}

              {/* Foul Committer Floating Badge */}
              {isFoulCommitter && !isCardedPlayer && (
                <div className="absolute -top-4.5 flex items-center gap-0.5 bg-amber-950/95 border border-amber-400 text-amber-200 text-[8px] font-black px-1.5 py-0.2 rounded-full shadow-[0_0_12px_rgba(245,158,11,0.9)] pointer-events-none z-30 uppercase tracking-tight whitespace-nowrap">
                  <span>⚠️ Foul</span>
                </div>
              )}

              {/* Fouled Player Floating Badge */}
              {isFouledPlayer && (
                <div className="absolute -top-4.5 flex items-center gap-0.5 bg-emerald-950/95 border border-emerald-400 text-emerald-200 text-[8px] font-black px-1.5 py-0.2 rounded-full shadow-[0_0_12px_rgba(16,185,129,0.85)] pointer-events-none z-30 uppercase tracking-tight whitespace-nowrap">
                  <span>🩹 Fouled</span>
                </div>
              )}

              {/* Tackle Winner Floating Badge */}
              {isTackler && !isCardedPlayer && !isFoulCommitter && (
                <div className="absolute -top-4 flex items-center gap-0.5 bg-black/90 border border-cyan-400 text-cyan-300 text-[8px] font-black px-1.5 py-0.2 rounded-full shadow-[0_0_12px_rgba(4,245,255,0.8)] pointer-events-none z-30 uppercase tracking-tight whitespace-nowrap">
                  <Shield className="w-2.5 h-2.5 text-cyan-400" />
                  <span>Won Tackle</span>
                </div>
              )}

              {/* Focused Player Spotlight Floating Badge */}
              {isFocused && !isTackler && !isCardedPlayer && !isPenaltyTaker && !isCornerTaker && (
                <div className="absolute -top-4.5 flex items-center gap-0.5 bg-black/95 border border-[#04F5FF] text-[#04F5FF] text-[8px] font-black px-1.5 py-0.2 rounded-full shadow-[0_0_14px_rgba(4,245,255,0.95)] pointer-events-none z-30 uppercase tracking-tight whitespace-nowrap animate-pulse">
                  <span className="text-yellow-400">★</span>
                  <span>{p.name.split(" ").pop()}</span>
                </div>
              )}

              {/* Jersey Dot & Rings Container - strictly 24x24 px so all rings are perfect circles */}
              <div className="relative w-6 h-6 flex items-center justify-center">
                {/* Disciplinary Card Halo Ring */}
                {isCardedPlayer && (
                  <>
                    <span className={`absolute -inset-2.5 rounded-full border-2 animate-ping opacity-70 pointer-events-none ${isRedCard ? 'border-red-500' : 'border-yellow-400'}`} />
                    <span className={`absolute -inset-1.5 rounded-full border-2 animate-pulse opacity-95 pointer-events-none ${isRedCard ? 'border-red-500 shadow-[0_0_18px_#EF4444]' : 'border-yellow-400 shadow-[0_0_18px_#EAB308]'}`} />
                  </>
                )}

                {/* Corner Taker Glowing Halo */}
                {isCornerTaker && (
                  <>
                    <span className="absolute -inset-2.5 rounded-full border border-cyan-400/50 animate-ping opacity-60 pointer-events-none" />
                    <span className="absolute -inset-1.5 rounded-full border-2 border-[#04F5FF] animate-pulse opacity-95 pointer-events-none shadow-[0_0_16px_#04F5FF]" />
                  </>
                )}

                {/* Penalty Taker Glowing Halo */}
                {isPenaltyTaker && (
                  <>
                    <span className="absolute -inset-2.5 rounded-full border border-rose-500/50 animate-ping opacity-60 pointer-events-none" />
                    <span className="absolute -inset-1.5 rounded-full border-2 border-[#FF2882] animate-pulse opacity-95 pointer-events-none shadow-[0_0_18px_#FF2882]" />
                  </>
                )}

                {/* Foul Committer Amber Halo */}
                {isFoulCommitter && !isCardedPlayer && (
                  <span className="absolute -inset-1.5 rounded-full border-2 border-amber-400 animate-pulse opacity-90 pointer-events-none shadow-[0_0_14px_#F59E0B]" />
                )}

                {/* Tackle Winner Highlight Ring */}
                {isTackler && !isCardedPlayer && (
                  <>
                    <span className="absolute -inset-2.5 rounded-full border-2 border-cyan-400 animate-ping opacity-60 pointer-events-none" />
                    <span className="absolute -inset-1.5 rounded-full border-2 border-cyan-300 animate-pulse opacity-95 pointer-events-none shadow-[0_0_14px_#04F5FF]" />
                  </>
                )}

                {/* Focus Ring & Halo (Selected Player) - perfectly round, glowing spotlight */}
                {isFocused && !isTackler && !isCardedPlayer && (
                  <>
                    <span className="absolute -inset-2.5 rounded-full border border-[#04F5FF]/50 animate-ping opacity-60 pointer-events-none" />
                    <span className="absolute -inset-1.5 rounded-full border-2 border-[#04F5FF] animate-pulse opacity-95 pointer-events-none shadow-[0_0_14px_#04F5FF]" />
                  </>
                )}

                {/* Dispossessed Player Warning Ring */}
                {isDispossessed && (
                  <span className="absolute -inset-1.5 rounded-full border border-amber-400/80 animate-pulse opacity-75 pointer-events-none" />
                )}

                {/* Player Jersey Dot */}
                <div
                  style={{ backgroundColor: homeTeam?.primary_color || "#EF0107" }}
                  className={`w-6 h-6 rounded-full flex items-center justify-center font-bold text-[10px] text-white shadow-md border-2 transition-transform duration-200 group-hover:scale-125 ${
                    isCardedPlayer
                      ? isRedCard
                        ? "border-red-500 ring-2 ring-red-500/60 scale-125 shadow-[0_0_20px_#EF4444]"
                        : "border-yellow-400 ring-2 ring-yellow-400/60 scale-125 shadow-[0_0_20px_#EAB308]"
                      : isPenaltyTaker
                      ? "border-[#FF2882] ring-2 ring-[#FF2882]/70 scale-125 shadow-[0_0_20px_#FF2882]"
                      : isCornerTaker
                      ? "border-[#04F5FF] ring-2 ring-[#04F5FF]/70 scale-125 shadow-[0_0_20px_#04F5FF]"
                      : isFoulCommitter
                      ? "border-amber-400 ring-2 ring-amber-400/50 scale-110 shadow-[0_0_14px_#F59E0B]"
                      : isFouledPlayer
                      ? "border-emerald-400 scale-95 opacity-90 shadow-[0_0_12px_#10B981]"
                      : isTackler
                      ? "border-cyan-300 ring-2 ring-cyan-400/50 scale-125 shadow-[0_0_20px_#04F5FF]"
                      : isDispossessed
                      ? "border-amber-400 scale-95 opacity-90 shadow-amber-500/40"
                      : isActor
                      ? "border-yellow-300 scale-110 shadow-yellow-500/50"
                      : isFocused
                      ? "border-[#04F5FF] ring-2 ring-[#04F5FF]/60 scale-125 shadow-[0_0_16px_#04F5FF]"
                      : "border-white/90"
                  }`}
                >
                  {p.number}
                </div>
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
          const isTackler = isTackle && isActor;
          const isDispossessed = isTackle && latestEvent?.recipient?.id === p.id;
          const isCornerTaker = isCorner && isActor;
          const isPenaltyTaker = isPenalty && isActor;
          const isCardedPlayer = isCard && isActor;
          const isFoulCommitter = isFoul && isActor;
          const isFouledPlayer = (isFoul || isCard) && latestEvent?.recipient?.id === p.id;
          const isPenaltyGk = isPenalty && p.position === "GK" && latestEvent?.team_id !== p.team_id;

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
              {/* Disciplinary Card Floating 3D Badge */}
              {isCardedPlayer && (
                <div
                  className={`absolute -top-5 flex items-center gap-1 text-[9px] font-black px-2.5 py-0.5 rounded-full pointer-events-none z-40 uppercase tracking-tight shadow-2xl animate-bounce border ${
                    isRedCard
                      ? "bg-red-950/95 border-red-500 text-red-200 shadow-[0_0_20px_rgba(239,68,68,0.95)]"
                      : "bg-yellow-950/95 border-yellow-400 text-yellow-200 shadow-[0_0_20px_rgba(234,179,8,0.95)]"
                  }`}
                >
                  <span>{isRedCard ? "🟥 RED CARD" : "🟨 YELLOW CARD"}</span>
                </div>
              )}

              {/* Penalty Taker Floating Badge */}
              {isPenaltyTaker && !isCardedPlayer && (
                <div className="absolute -top-5 flex items-center gap-1 bg-rose-950/95 border-2 border-[#FF2882] text-rose-200 text-[9px] font-black px-2.5 py-0.5 rounded-full shadow-[0_0_18px_rgba(255,40,130,0.95)] pointer-events-none z-30 uppercase tracking-tight whitespace-nowrap animate-pulse">
                  <span>🎯 Penalty Taker</span>
                </div>
              )}

              {/* Penalty Goalkeeper Floating Badge */}
              {isPenaltyGk && (
                <div className="absolute -top-4.5 flex items-center gap-0.5 bg-amber-950/95 border border-yellow-400 text-yellow-300 text-[8px] font-black px-2 py-0.2 rounded-full shadow-[0_0_12px_rgba(255,215,0,0.85)] pointer-events-none z-30 uppercase tracking-tight whitespace-nowrap">
                  <span>🧤 GK</span>
                </div>
              )}

              {/* Corner Taker Floating Badge */}
              {isCornerTaker && (
                <div className="absolute -top-4.5 flex items-center gap-0.5 bg-cyan-950/95 border border-[#04F5FF] text-[#04F5FF] text-[8px] font-black px-2 py-0.2 rounded-full shadow-[0_0_16px_rgba(4,245,255,0.95)] pointer-events-none z-30 uppercase tracking-tight whitespace-nowrap animate-pulse">
                  <span>🚩 Corner Taker</span>
                </div>
              )}

              {/* Foul Committer Floating Badge */}
              {isFoulCommitter && !isCardedPlayer && (
                <div className="absolute -top-4.5 flex items-center gap-0.5 bg-amber-950/95 border border-amber-400 text-amber-200 text-[8px] font-black px-1.5 py-0.2 rounded-full shadow-[0_0_12px_rgba(245,158,11,0.9)] pointer-events-none z-30 uppercase tracking-tight whitespace-nowrap">
                  <span>⚠️ Foul</span>
                </div>
              )}

              {/* Fouled Player Floating Badge */}
              {isFouledPlayer && (
                <div className="absolute -top-4.5 flex items-center gap-0.5 bg-emerald-950/95 border border-emerald-400 text-emerald-200 text-[8px] font-black px-1.5 py-0.2 rounded-full shadow-[0_0_12px_rgba(16,185,129,0.85)] pointer-events-none z-30 uppercase tracking-tight whitespace-nowrap">
                  <span>🩹 Fouled</span>
                </div>
              )}

              {/* Tackle Winner Floating Badge */}
              {isTackler && !isCardedPlayer && !isFoulCommitter && (
                <div className="absolute -top-4 flex items-center gap-0.5 bg-black/90 border border-cyan-400 text-cyan-300 text-[8px] font-black px-1.5 py-0.2 rounded-full shadow-[0_0_12px_rgba(4,245,255,0.8)] pointer-events-none z-30 uppercase tracking-tight whitespace-nowrap">
                  <Shield className="w-2.5 h-2.5 text-cyan-400" />
                  <span>Won Tackle</span>
                </div>
              )}

              {/* Focused Player Spotlight Floating Badge */}
              {isFocused && !isTackler && !isCardedPlayer && !isPenaltyTaker && !isCornerTaker && (
                <div className="absolute -top-4.5 flex items-center gap-0.5 bg-black/95 border border-[#04F5FF] text-[#04F5FF] text-[8px] font-black px-1.5 py-0.2 rounded-full shadow-[0_0_14px_rgba(4,245,255,0.95)] pointer-events-none z-30 uppercase tracking-tight whitespace-nowrap animate-pulse">
                  <span className="text-yellow-400">★</span>
                  <span>{p.name.split(" ").pop()}</span>
                </div>
              )}

              {/* Jersey Dot & Rings Container - strictly 24x24 px so all rings are perfect circles */}
              <div className="relative w-6 h-6 flex items-center justify-center">
                {/* Disciplinary Card Halo Ring */}
                {isCardedPlayer && (
                  <>
                    <span className={`absolute -inset-2.5 rounded-full border-2 animate-ping opacity-70 pointer-events-none ${isRedCard ? 'border-red-500' : 'border-yellow-400'}`} />
                    <span className={`absolute -inset-1.5 rounded-full border-2 animate-pulse opacity-95 pointer-events-none ${isRedCard ? 'border-red-500 shadow-[0_0_18px_#EF4444]' : 'border-yellow-400 shadow-[0_0_18px_#EAB308]'}`} />
                  </>
                )}

                {/* Corner Taker Glowing Halo */}
                {isCornerTaker && (
                  <>
                    <span className="absolute -inset-2.5 rounded-full border border-cyan-400/50 animate-ping opacity-60 pointer-events-none" />
                    <span className="absolute -inset-1.5 rounded-full border-2 border-[#04F5FF] animate-pulse opacity-95 pointer-events-none shadow-[0_0_16px_#04F5FF]" />
                  </>
                )}

                {/* Penalty Taker Glowing Halo */}
                {isPenaltyTaker && (
                  <>
                    <span className="absolute -inset-2.5 rounded-full border border-rose-500/50 animate-ping opacity-60 pointer-events-none" />
                    <span className="absolute -inset-1.5 rounded-full border-2 border-[#FF2882] animate-pulse opacity-95 pointer-events-none shadow-[0_0_18px_#FF2882]" />
                  </>
                )}

                {/* Foul Committer Amber Halo */}
                {isFoulCommitter && !isCardedPlayer && (
                  <span className="absolute -inset-1.5 rounded-full border-2 border-amber-400 animate-pulse opacity-90 pointer-events-none shadow-[0_0_14px_#F59E0B]" />
                )}

                {/* Tackle Winner Highlight Ring */}
                {isTackler && !isCardedPlayer && (
                  <>
                    <span className="absolute -inset-2.5 rounded-full border-2 border-cyan-400 animate-ping opacity-60 pointer-events-none" />
                    <span className="absolute -inset-1.5 rounded-full border-2 border-cyan-300 animate-pulse opacity-95 pointer-events-none shadow-[0_0_14px_#04F5FF]" />
                  </>
                )}

                {/* Focus Ring & Halo (Selected Player) - perfectly round, glowing spotlight */}
                {isFocused && !isTackler && !isCardedPlayer && (
                  <>
                    <span className="absolute -inset-2.5 rounded-full border border-[#04F5FF]/50 animate-ping opacity-60 pointer-events-none" />
                    <span className="absolute -inset-1.5 rounded-full border-2 border-[#04F5FF] animate-pulse opacity-95 pointer-events-none shadow-[0_0_14px_#04F5FF]" />
                  </>
                )}

                {/* Dispossessed Player Warning Ring */}
                {isDispossessed && (
                  <span className="absolute -inset-1.5 rounded-full border border-amber-400/80 animate-pulse opacity-75 pointer-events-none" />
                )}

                {/* Player Jersey Dot */}
                <div
                  style={{ backgroundColor: awayTeam?.primary_color || "#6CABDD" }}
                  className={`w-6 h-6 rounded-full flex items-center justify-center font-bold text-[10px] text-white shadow-md border-2 transition-transform duration-200 group-hover:scale-125 ${
                    isCardedPlayer
                      ? isRedCard
                        ? "border-red-500 ring-2 ring-red-500/60 scale-125 shadow-[0_0_20px_#EF4444]"
                        : "border-yellow-400 ring-2 ring-yellow-400/60 scale-125 shadow-[0_0_20px_#EAB308]"
                      : isPenaltyTaker
                      ? "border-[#FF2882] ring-2 ring-[#FF2882]/70 scale-125 shadow-[0_0_20px_#FF2882]"
                      : isCornerTaker
                      ? "border-[#04F5FF] ring-2 ring-[#04F5FF]/70 scale-125 shadow-[0_0_20px_#04F5FF]"
                      : isFoulCommitter
                      ? "border-amber-400 ring-2 ring-amber-400/50 scale-110 shadow-[0_0_14px_#F59E0B]"
                      : isFouledPlayer
                      ? "border-emerald-400 scale-95 opacity-90 shadow-[0_0_12px_#10B981]"
                      : isTackler
                      ? "border-cyan-300 ring-2 ring-cyan-400/50 scale-125 shadow-[0_0_20px_#04F5FF]"
                      : isDispossessed
                      ? "border-amber-400 scale-95 opacity-90 shadow-amber-500/40"
                      : isActor
                      ? "border-yellow-300 scale-110 shadow-yellow-500/50"
                      : isFocused
                      ? "border-[#04F5FF] ring-2 ring-[#04F5FF]/60 scale-125 shadow-[0_0_16px_#04F5FF]"
                      : "border-white/90"
                  }`}
                >
                  {p.number}
                </div>
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
              ? `left ${glideDurationMs}ms cubic-bezier(0.25, 0.46, 0.45, 0.94), top ${glideDurationMs}ms cubic-bezier(0.25, 0.46, 0.45, 0.94)`
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

        {/* Broadcast Turnover / Interception HUD Tag */}
        {isInterception && latestEvent?.end_location && (
          <div
            style={{
              left: `${latestEvent.end_location.x}%`,
              top: `${Math.max(8, latestEvent.end_location.y - 4.5)}%`,
              transform: "translate(-50%, -100%)",
            }}
            className="absolute z-40 pointer-events-none flex items-center gap-1.5 bg-black/90 backdrop-blur-md border border-amber-500/80 px-2.5 py-1 rounded-full shadow-[0_0_16px_rgba(255,136,0,0.5)] animate-in fade-in zoom-in-95 duration-200"
          >
            <ShieldAlert className="w-3 h-3 text-amber-400 animate-pulse" />
            <span className="text-[9px] font-black text-amber-300 uppercase tracking-wider font-mono">
              INTERCEPTED
            </span>
            {latestEvent.recipient && (
              <span className="text-[9px] font-bold text-white border-l border-white/20 pl-1.5">
                {latestEvent.recipient.name.split(" ").pop()}
              </span>
            )}
          </div>
        )}

        {/* Broadcast Tackle / Dispossession HUD Tag */}
        {isTackle && latestEvent?.location && (
          <div
            style={{
              left: `${latestEvent.location.x}%`,
              top: `${Math.max(8, latestEvent.location.y - 4.5)}%`,
              transform: "translate(-50%, -100%)",
            }}
            className="absolute z-40 pointer-events-none flex items-center gap-1.5 bg-black/92 backdrop-blur-md border border-cyan-400/90 px-2.5 py-1 rounded-full shadow-[0_0_18px_rgba(4,245,255,0.6)] animate-in fade-in zoom-in-95 duration-200"
          >
            <Shield className="w-3 h-3 text-[#04F5FF] animate-pulse" />
            <span className="text-[9px] font-black text-[#04F5FF] uppercase tracking-wider font-mono">
              TACKLE WON
            </span>
            {latestEvent.player && (
              <span className="text-[9px] font-bold text-white border-l border-white/20 pl-1.5">
                {latestEvent.player.name.split(" ").pop()}
              </span>
            )}
            {latestEvent.recipient && (
              <span className="text-[8px] font-mono text-gray-400">
                vs {latestEvent.recipient.name.split(" ").pop()}
              </span>
            )}
          </div>
        )}

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
