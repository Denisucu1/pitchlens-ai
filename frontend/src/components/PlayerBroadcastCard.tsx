import React, { useState } from "react";
import type { PlayerProfile, TeamProfile } from "../types";
import { X, Activity, Zap, Footprints, Shield, Target, Flame, ArrowRight } from "lucide-react";

interface PlayerBroadcastCardProps {
  player: PlayerProfile | null;
  team: TeamProfile | null;
  onClose: () => void;
  variant?: "horizontal" | "vertical";
  onFocusOnPitch?: () => void;
}

export const PlayerBroadcastCard: React.FC<PlayerBroadcastCardProps> = ({
  player,
  team,
  onClose,
  variant = "horizontal",
  onFocusOnPitch,
}) => {
  const [showHeatmap, setShowHeatmap] = useState(false);
  if (!player) return null;

  const teamColor = team?.primary_color || "#EF0107";
  const distKm = (player.distance_covered_meters / 1000).toFixed(2);
  const staminaPct = Math.max(10, Math.min(100, player.stamina));

  const rating = player.match_rating ?? 6.8;
  const ratingColor =
    rating >= 8.0
      ? "bg-blue-600 text-white"
      : rating >= 7.2
      ? "bg-emerald-600 text-white"
      : rating >= 6.5
      ? "bg-amber-500 text-black"
      : "bg-orange-600 text-white";

  const isAttacker = ["ST", "CF", "RW", "LW"].includes(player.position);
  const isMidfielder = ["CM", "CDM", "CAM", "LM", "RM"].includes(player.position);
  const isDefender = ["CB", "LB", "RB", "RWB", "LWB"].includes(player.position);
  const isGoalkeeper = player.position === "GK";

  // ─────────────────────────────────────────────────────────────────────────────
  // VERTICAL SIDEBAR VARIANT (Tailored for right sidebar column, e.g. Players tab)
  // ─────────────────────────────────────────────────────────────────────────────
  if (variant === "vertical") {
    return (
      <div className="w-full bg-gradient-to-br from-[#140620]/95 via-[#0e0317]/95 to-[#160724]/95 backdrop-blur-md rounded-2xl border border-white/15 p-4 shadow-xl text-white font-sans flex flex-col gap-3 transition-all animate-in fade-in duration-200">
        {/* Header: Number, Name, Position, Close */}
        <div className="flex items-center justify-between pb-2.5 border-b border-white/10">
          <div className="flex items-center gap-2.5 min-w-0">
            <div
              style={{ backgroundColor: teamColor }}
              className="w-9 h-9 rounded-xl flex items-center justify-center font-black text-sm text-white shadow-md border border-white/20 shrink-0"
            >
              {player.number}
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-1.5 flex-wrap">
                <span className="text-[10px] font-mono font-bold uppercase text-emerald-400">
                  {team?.short_name || "EPL"} • {player.position}
                </span>
                <span className="text-gray-500">•</span>
                <span className="text-[9px] text-purple-300 font-mono bg-purple-500/20 px-1 py-0.2 rounded">
                  SPOTLIGHT
                </span>
              </div>
              <div className="text-sm font-black text-white truncate leading-tight mt-0.5">
                {player.name}
              </div>
            </div>
          </div>

          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white p-1.5 rounded-lg hover:bg-white/10 transition shrink-0 ml-1"
            title="Deselect player"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Rating & Stamina Row */}
        <div className="flex items-center justify-between gap-2 bg-white/5 p-2.5 rounded-xl border border-white/10">
          <div className="flex items-center gap-2">
            <div className={`px-2 py-0.5 rounded-md font-mono font-black text-xs ${ratingColor}`}>
              {rating.toFixed(1)}
            </div>
            <div className="flex flex-col">
              <span className="text-[8px] uppercase tracking-wider text-gray-400 font-mono">SOFASCORE RATING</span>
              <span className="text-[10px] font-bold text-white">
                {rating >= 8.0 ? "World Class" : rating >= 7.5 ? "Very Good" : rating >= 7.0 ? "Good" : "Standard"}
              </span>
            </div>
          </div>

          <div className="flex flex-col items-end shrink-0">
            <div className="text-[9px] font-mono text-gray-400 mb-0.5">
              Stamina <strong className="text-white">{staminaPct}%</strong>
            </div>
            <div className="w-16 h-1.5 bg-black/60 rounded-full overflow-hidden">
              <div
                style={{ width: `${staminaPct}%` }}
                className={`h-full rounded-full transition-all duration-500 ${
                  staminaPct > 60 ? "bg-emerald-400" : staminaPct > 35 ? "bg-yellow-400" : "bg-red-500"
                }`}
              />
            </div>
          </div>
        </div>

        {/* 2-Column Grid of Metrics */}
        <div className="grid grid-cols-2 gap-2 text-xs font-mono">
          {/* Role-Specific Metric */}
          <div className="bg-white/5 p-2 rounded-xl border border-white/5 flex items-center gap-2 overflow-hidden">
            {isAttacker ? (
              <>
                <Target className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                <div className="min-w-0">
                  <div className="font-black text-white text-[11px] truncate">
                    {player.goals ?? 0} G • {player.shots_on_target ?? 0}/{player.shots ?? 0}
                  </div>
                  <div className="text-[8px] text-gray-400 uppercase tracking-tight">Goals & Shots</div>
                </div>
              </>
            ) : isMidfielder ? (
              <>
                <Activity className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                <div className="min-w-0">
                  <div className="font-black text-white text-[11px] truncate">
                    {player.passes_completed ?? 0}/{player.passes_total ?? 0}{" "}
                    ({player.passes_total ? Math.round(((player.passes_completed ?? 0) / player.passes_total) * 100) : 0}%)
                  </div>
                  <div className="text-[8px] text-gray-400 uppercase tracking-tight">Pass Accuracy</div>
                </div>
              </>
            ) : isDefender ? (
              <>
                <Shield className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                <div className="min-w-0">
                  <div className="font-black text-white text-[11px] truncate">
                    {player.tackles_won ?? 0} Tkl • {player.recoveries ?? 0} Rec
                  </div>
                  <div className="text-[8px] text-gray-400 uppercase tracking-tight">Tackles & Duels</div>
                </div>
              </>
            ) : (
              <>
                <Shield className="w-3.5 h-3.5 text-yellow-400 shrink-0" />
                <div className="min-w-0">
                  <div className="font-black text-white text-[11px] truncate">{player.saves ?? 0} Saves</div>
                  <div className="text-[8px] text-gray-400 uppercase tracking-tight">Goalkeeping</div>
                </div>
              </>
            )}
          </div>

          {/* Distance */}
          <div className="bg-white/5 p-2 rounded-xl border border-white/5 flex items-center gap-2 overflow-hidden">
            <Footprints className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
            <div className="min-w-0">
              <div className="font-black text-white text-[11px] truncate">{distKm} km</div>
              <div className="text-[8px] text-gray-400 uppercase tracking-tight">Distance</div>
            </div>
          </div>

          {/* Top Speed */}
          <div className="bg-white/5 p-2 rounded-xl border border-white/5 flex items-center gap-2 overflow-hidden">
            <Zap className="w-3.5 h-3.5 text-yellow-400 shrink-0" />
            <div className="min-w-0">
              <div className="font-black text-white text-[11px] truncate">{player.current_speed_kmh} km/h</div>
              <div className="text-[8px] text-gray-400 uppercase tracking-tight">Top Speed</div>
            </div>
          </div>

          {/* Sprints */}
          <div className="bg-white/5 p-2 rounded-xl border border-white/5 flex items-center gap-2 overflow-hidden">
            <Flame className="w-3.5 h-3.5 text-purple-400 shrink-0" />
            <div className="min-w-0">
              <div className="font-black text-white text-[11px] truncate">{player.sprint_count ?? 0} Sprints</div>
              <div className="text-[8px] text-gray-400 uppercase tracking-tight">High Intensity</div>
            </div>
          </div>
        </div>

        {/* Action Buttons (Heatmap & Pitch View) */}
        <div className="flex items-center gap-2 pt-1">
          <button
            onClick={() => setShowHeatmap(!showHeatmap)}
            className={`flex-1 flex items-center justify-center gap-1.5 py-1.5 px-2.5 rounded-xl border text-xs font-mono font-bold transition ${
              showHeatmap
                ? "bg-amber-500 text-black border-amber-400 shadow-md"
                : "bg-white/5 hover:bg-white/10 text-amber-300 border-amber-500/30"
            }`}
          >
            <Flame className="w-3.5 h-3.5" />
            <span>{showHeatmap ? "Hide Heatmap" : "Heatmap"}</span>
          </button>

          {onFocusOnPitch && (
            <button
              onClick={onFocusOnPitch}
              className="flex-1 flex items-center justify-center gap-1 py-1.5 px-2.5 rounded-xl bg-purple-600/30 hover:bg-purple-600/50 text-purple-200 border border-purple-500/40 text-xs font-mono font-bold transition"
            >
              <span>On Pitch</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Scaled Responsive Heatmap for Sidebar */}
        {showHeatmap && (
          <div className="pt-2 border-t border-white/10 animate-in fade-in duration-200">
            <div className="relative w-full aspect-[105/68] bg-gradient-to-br from-[#0c381a] via-[#092d14] to-[#06210f] rounded-xl overflow-hidden border border-emerald-700/60 shadow-inner">
              <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
                <rect x="2" y="2" width="96" height="96" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.8" />
                <line x1="50" y1="2" x2="50" y2="98" stroke="rgba(255,255,255,0.4)" strokeWidth="0.8" />
                <circle cx="50" cy="50" r="9.15" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.8" />
                <rect x="2" y="22" width="16" height="56" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.8" />
                <rect x="82" y="22" width="16" height="56" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.8" />
              </svg>

              <div className="absolute inset-0 pointer-events-none overflow-hidden">
                {(player.heatmap || []).map((pt, idx) => (
                  <div
                    key={`vcard_hp_${idx}`}
                    style={{
                      left: `${pt.x}%`,
                      top: `${pt.y}%`,
                      transform: "translate(-50%, -50%)",
                      background:
                        "radial-gradient(circle, rgba(255, 35, 0, 0.9) 0%, rgba(255, 140, 0, 0.55) 45%, rgba(255, 230, 0, 0.18) 75%, transparent 100%)",
                    }}
                    className="absolute w-10 h-10 rounded-full blur-[5px] pointer-events-none"
                  />
                ))}
              </div>

              <div
                style={{
                  left: `${player.current_coords.x}%`,
                  top: `${player.current_coords.y}%`,
                  transform: "translate(-50%, -50%)",
                }}
                className="absolute z-20 pointer-events-none flex flex-col items-center"
              >
                <div className="w-3 h-3 rounded-full bg-white border-2 border-black flex items-center justify-center shadow animate-pulse">
                  <div className="w-1 h-1 rounded-full bg-red-600" />
                </div>
              </div>
            </div>
            <div className="text-[10px] text-gray-400 font-mono text-center mt-1.5">
              Opta Touches: {(player.heatmap || []).length} recorded
            </div>
          </div>
        )}
      </div>
    );
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // HORIZONTAL BANNER VARIANT (Used below the broadcast pitch)
  // ─────────────────────────────────────────────────────────────────────────────
  return (
    <div className="w-full bg-gradient-to-r from-[#140620]/95 via-[#0e0317]/95 to-[#160724]/95 backdrop-blur-md rounded-2xl border border-white/15 p-3.5 shadow-xl text-white font-sans transition-all animate-in fade-in duration-300">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
        {/* Player Identity */}
        <div className="flex items-center gap-3 shrink-0">
          <div
            style={{ backgroundColor: teamColor }}
            className="w-10 h-10 rounded-xl flex items-center justify-center font-black text-lg text-white shadow-md shrink-0 border border-white/20"
          >
            {player.number}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono font-bold tracking-wider uppercase text-emerald-400">
                {team?.short_name || "EPL"} • {player.position}
              </span>
              <span className="text-gray-500">•</span>
              <span className="text-[10px] text-gray-400 font-mono">SPOTLIGHT</span>
            </div>
            <div className="text-base font-black tracking-tight text-white leading-tight">
              {player.name}
            </div>
          </div>
        </div>

        {/* Live Match Metrics */}
        <div className="flex items-center gap-2 flex-wrap py-1">
          {/* Sofascore Live Rating */}
          <div className="flex items-center gap-1.5 bg-white/5 px-2.5 py-1.5 rounded-xl border border-white/10 shrink-0">
            <div className={`px-2 py-0.5 rounded-md font-mono font-black text-xs ${ratingColor}`}>
              {rating.toFixed(1)}
            </div>
            <div className="text-[8px] uppercase tracking-wider text-gray-400">Rating</div>
          </div>

          {/* Role-Specific Metric */}
          {isAttacker && (
            <div className="flex items-center gap-1.5 bg-white/5 px-2.5 py-1.5 rounded-xl border border-white/5 shrink-0">
              <Target className="w-3.5 h-3.5 text-amber-400" />
              <div>
                <div className="text-xs font-mono font-black">
                  {player.goals ?? 0} <span className="text-[9px] text-gray-400 font-normal">G</span> • {player.shots_on_target ?? 0}/{player.shots ?? 0} <span className="text-[9px] text-gray-400 font-normal">Shots</span>
                </div>
                <div className="text-[8px] uppercase tracking-wider text-gray-400">Goals & Shots</div>
              </div>
            </div>
          )}

          {isMidfielder && (
            <div className="flex items-center gap-1.5 bg-white/5 px-2.5 py-1.5 rounded-xl border border-white/5 shrink-0">
              <Activity className="w-3.5 h-3.5 text-emerald-400" />
              <div>
                <div className="text-xs font-mono font-black">
                  {player.passes_completed ?? 0}/{player.passes_total ?? 0}{" "}
                  <span className="text-[9px] text-gray-400 font-normal">
                    ({player.passes_total ? Math.round(((player.passes_completed ?? 0) / player.passes_total) * 100) : 0}%)
                  </span>
                </div>
                <div className="text-[8px] uppercase tracking-wider text-gray-400">Accurate Passes</div>
              </div>
            </div>
          )}

          {isDefender && (
            <div className="flex items-center gap-1.5 bg-white/5 px-2.5 py-1.5 rounded-xl border border-white/5 shrink-0">
              <Shield className="w-3.5 h-3.5 text-cyan-400" />
              <div>
                <div className="text-xs font-mono font-black">
                  {player.tackles_won ?? 0} <span className="text-[9px] text-gray-400 font-normal">Tkl</span> • {player.recoveries ?? 0} <span className="text-[9px] text-gray-400 font-normal">Rec</span>
                </div>
                <div className="text-[8px] uppercase tracking-wider text-gray-400">Tackles & Duels</div>
              </div>
            </div>
          )}

          {isGoalkeeper && (
            <div className="flex items-center gap-1.5 bg-white/5 px-2.5 py-1.5 rounded-xl border border-white/5 shrink-0">
              <Shield className="w-3.5 h-3.5 text-yellow-400" />
              <div>
                <div className="text-xs font-mono font-black">{player.saves ?? 0}</div>
                <div className="text-[8px] uppercase tracking-wider text-gray-400">Saves</div>
              </div>
            </div>
          )}

          {/* Distance */}
          <div className="flex items-center gap-1.5 bg-white/5 px-2.5 py-1.5 rounded-xl border border-white/5 shrink-0">
            <Footprints className="w-3.5 h-3.5 text-emerald-400" />
            <div>
              <div className="text-xs font-mono font-black">{distKm} <span className="text-[9px] text-gray-400 font-normal">km</span></div>
              <div className="text-[8px] uppercase tracking-wider text-gray-400">Distance</div>
            </div>
          </div>

          {/* Speed */}
          <div className="flex items-center gap-1.5 bg-white/5 px-2.5 py-1.5 rounded-xl border border-white/5 shrink-0">
            <Zap className="w-3.5 h-3.5 text-yellow-400" />
            <div>
              <div className="text-xs font-mono font-black">{player.current_speed_kmh} <span className="text-[9px] text-gray-400 font-normal">km/h</span></div>
              <div className="text-[8px] uppercase tracking-wider text-gray-400">Top Speed</div>
            </div>
          </div>

          {/* Stamina Gauge */}
          <div className="bg-white/5 px-3 py-1.5 rounded-xl border border-white/5 shrink-0 min-w-[95px]">
            <div className="flex justify-between items-center gap-2 text-[10px] font-mono mb-1">
              <span className="text-gray-400">Stamina</span>
              <span className="font-bold text-white">{staminaPct}%</span>
            </div>
            <div className="w-full h-1.5 bg-black/60 rounded-full overflow-hidden">
              <div
                style={{ width: `${staminaPct}%` }}
                className={`h-full rounded-full transition-all duration-500 ${
                  staminaPct > 60 ? "bg-emerald-400" : staminaPct > 35 ? "bg-yellow-400" : "bg-red-500"
                }`}
              />
            </div>
          </div>

          {/* Heatmap Toggle Button */}
          <button
            onClick={() => setShowHeatmap(!showHeatmap)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl border text-xs font-mono font-bold transition shrink-0 ${
              showHeatmap
                ? "bg-amber-500 text-black border-amber-400 shadow-md"
                : "bg-white/5 hover:bg-white/10 text-amber-300 border-amber-500/30"
            }`}
            title="View player Opta action heatmap"
          >
            <Flame className="w-3.5 h-3.5" />
            <span>Heatmap</span>
          </button>

          {/* Dismiss Button */}
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white p-1.5 rounded-xl hover:bg-white/10 transition shrink-0 ml-auto"
            title="Deselect player"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Expandable Individual Player Heatmap */}
      {showHeatmap && (
        <div className="mt-3 pt-3 border-t border-white/10 flex flex-col md:flex-row items-center gap-4 animate-in fade-in duration-200">
          <div className="relative w-full md:w-80 aspect-[105/68] bg-gradient-to-br from-[#0c381a] via-[#092d14] to-[#06210f] rounded-xl overflow-hidden border border-emerald-700/60 shadow-inner shrink-0">
            {/* SVG Pitch Markings */}
            <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
              <rect x="2" y="2" width="96" height="96" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.8" />
              <line x1="50" y1="2" x2="50" y2="98" stroke="rgba(255,255,255,0.4)" strokeWidth="0.8" />
              <circle cx="50" cy="50" r="9.15" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.8" />
              <rect x="2" y="22" width="16" height="56" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.8" />
              <rect x="82" y="22" width="16" height="56" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.8" />
            </svg>

            {/* Heatmap Touchpoints */}
            <div className="absolute inset-0 pointer-events-none overflow-hidden">
              {(player.heatmap || []).map((pt, idx) => (
                <div
                  key={`card_hp_${idx}`}
                  style={{
                    left: `${pt.x}%`,
                    top: `${pt.y}%`,
                    transform: "translate(-50%, -50%)",
                    background:
                      "radial-gradient(circle, rgba(255, 35, 0, 0.9) 0%, rgba(255, 140, 0, 0.55) 45%, rgba(255, 230, 0, 0.18) 75%, transparent 100%)",
                  }}
                  className="absolute w-12 h-12 rounded-full blur-[6px] pointer-events-none"
                />
              ))}
            </div>

            {/* Current Position Marker */}
            <div
              style={{
                left: `${player.current_coords.x}%`,
                top: `${player.current_coords.y}%`,
                transform: "translate(-50%, -50%)",
              }}
              className="absolute z-20 pointer-events-none flex flex-col items-center"
            >
              <div className="w-3.5 h-3.5 rounded-full bg-white border-2 border-black flex items-center justify-center shadow animate-pulse">
                <div className="w-1 h-1 rounded-full bg-red-600" />
              </div>
            </div>
          </div>

          {/* Territory Breakdown */}
          <div className="flex-1 w-full flex flex-col gap-2 bg-white/5 p-3 rounded-xl border border-white/5 text-xs font-mono">
            <div className="flex items-center justify-between text-gray-300">
              <span className="flex items-center gap-1.5 text-amber-400 font-bold">
                <Flame className="w-3.5 h-3.5" />
                Opta Action Territory
              </span>
              <span className="text-[11px] text-gray-400">
                {(player.heatmap || []).length} Recorded Touches
              </span>
            </div>
            <p className="text-[11px] text-gray-400 font-sans leading-relaxed">
              Touch density mapped from Opta tracking data across all phases of play.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
