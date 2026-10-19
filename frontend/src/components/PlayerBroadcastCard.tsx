import React from "react";
import type { PlayerProfile, TeamProfile } from "../types";
import { X, Activity, Zap, Footprints, Shield, Target } from "lucide-react";

interface PlayerBroadcastCardProps {
  player: PlayerProfile | null;
  team: TeamProfile | null;
  onClose: () => void;
}

export const PlayerBroadcastCard: React.FC<PlayerBroadcastCardProps> = ({
  player,
  team,
  onClose,
}) => {
  if (!player) return null;

  const teamColor = team?.primary_color || "#EF0107";
  const distKm = (player.distance_covered_meters / 1000).toFixed(2);
  const staminaPct = Math.max(10, Math.min(100, player.stamina));

  return (
    <div className="w-full bg-gradient-to-r from-[#140620]/95 via-[#0e0317]/95 to-[#160724]/95 backdrop-blur-md rounded-2xl border border-white/15 p-3.5 shadow-xl text-white font-sans transition-all animate-in fade-in duration-300">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        {/* Player Identity */}
        <div className="flex items-center gap-3">
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
              <span className="text-[10px] text-gray-400 font-mono">FOCALIZAT</span>
            </div>
            <div className="text-base font-black tracking-tight text-white leading-tight">
              {player.name}
            </div>
          </div>
        </div>

        {/* Live Match Metrics */}
        <div className="flex items-center gap-3 sm:gap-4 overflow-x-auto py-1">
          {/* Distance */}
          <div className="flex items-center gap-1.5 bg-white/5 px-2.5 py-1.5 rounded-xl border border-white/5 shrink-0">
            <Footprints className="w-3.5 h-3.5 text-emerald-400" />
            <div>
              <div className="text-xs font-mono font-black">{distKm} <span className="text-[9px] text-gray-400 font-normal">km</span></div>
              <div className="text-[8px] uppercase tracking-wider text-gray-400">Distanță</div>
            </div>
          </div>

          {/* Speed */}
          <div className="flex items-center gap-1.5 bg-white/5 px-2.5 py-1.5 rounded-xl border border-white/5 shrink-0">
            <Zap className="w-3.5 h-3.5 text-yellow-400" />
            <div>
              <div className="text-xs font-mono font-black">{player.current_speed_kmh} <span className="text-[9px] text-gray-400 font-normal">km/h</span></div>
              <div className="text-[8px] uppercase tracking-wider text-gray-400">Viteză</div>
            </div>
          </div>

          {/* Sprints */}
          <div className="flex items-center gap-1.5 bg-white/5 px-2.5 py-1.5 rounded-xl border border-white/5 shrink-0">
            <Activity className="w-3.5 h-3.5 text-[#04F5FF]" />
            <div>
              <div className="text-xs font-mono font-black">{player.sprint_count}</div>
              <div className="text-[8px] uppercase tracking-wider text-gray-400">Sprinturi</div>
            </div>
          </div>

          {/* Stamina Gauge */}
          <div className="bg-white/5 px-2.5 py-1.5 rounded-xl border border-white/5 shrink-0 min-w-[70px]">
            <div className="flex justify-between text-[10px] font-mono mb-0.5">
              <span className="text-gray-400">Stamina</span>
              <span className="font-bold">{staminaPct}%</span>
            </div>
            <div className="w-full h-1 bg-black/60 rounded-full overflow-hidden">
              <div
                style={{ width: `${staminaPct}%` }}
                className={`h-full rounded-full transition-all duration-500 ${
                  staminaPct > 60 ? "bg-emerald-400" : staminaPct > 35 ? "bg-yellow-400" : "bg-red-500"
                }`}
              />
            </div>
          </div>

          {/* Ratings */}
          <div className="hidden md:flex items-center gap-2 text-[10px] text-gray-300 font-mono bg-white/5 px-2 py-1.5 rounded-xl border border-white/5">
            <span className="flex items-center gap-1" title="Passing Skill">
              <Target className="w-3 h-3 text-amber-400" /> {player.passing_skill}
            </span>
            <span className="flex items-center gap-1" title="Shooting Skill">
              <Shield className="w-3 h-3 text-purple-400" /> {player.shooting_skill}
            </span>
          </div>

          {/* Dismiss Button */}
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white p-1.5 rounded-xl hover:bg-white/10 transition shrink-0 ml-auto"
            title="Deselectează jucătorul"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
