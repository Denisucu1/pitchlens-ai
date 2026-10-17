import React from "react";
import type { PlayerProfile, TeamProfile } from "../types";
import { X, Flame, Activity, Zap, Footprints, Shield, Target } from "lucide-react";

interface PlayerBroadcastCardProps {
  player: PlayerProfile | null;
  team: TeamProfile | null;
  onClose: () => void;
  onToggleHeatmap: () => void;
  isHeatmapActive: boolean;
}

export const PlayerBroadcastCard: React.FC<PlayerBroadcastCardProps> = ({
  player,
  team,
  onClose,
  onToggleHeatmap,
  isHeatmapActive,
}) => {
  if (!player) return null;

  const teamColor = team?.primary_color || "#EF0107";
  const distKm = (player.distance_covered_meters / 1000).toFixed(2);
  const staminaPct = Math.max(10, Math.min(100, player.stamina));

  return (
    <div className="absolute bottom-4 left-4 z-50 w-72 bg-black/90 backdrop-blur-xl rounded-2xl border-2 border-white/15 shadow-[0_12px_40px_rgba(0,0,0,0.8)] overflow-hidden text-white font-sans animate-in fade-in slide-in-from-bottom-4 duration-300">
      {/* Top Header Strip with Club Brand */}
      <div
        style={{
          background: `linear-gradient(90deg, ${teamColor} 0%, rgba(20,20,30,0.95) 100%)`,
        }}
        className="px-3.5 py-2.5 flex items-center justify-between border-b border-white/10"
      >
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-full bg-black/40 border border-white/30 flex items-center justify-center font-black text-sm text-white">
            {player.number}
          </div>
          <div>
            <div className="text-[10px] tracking-wider uppercase font-mono font-bold text-white/80">
              {team?.short_name || "EPL"} • {player.position}
            </div>
            <div className="text-sm font-black tracking-tight leading-none text-white drop-shadow">
              {player.name}
            </div>
          </div>
        </div>
        <button
          onClick={onClose}
          className="text-white/60 hover:text-white p-1 rounded-lg hover:bg-white/10 transition"
          title="Închide cardul"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Body: Live Match Telemetry */}
      <div className="p-3.5 space-y-3">
        {/* Key Stats Grid */}
        <div className="grid grid-cols-3 gap-2 text-center">
          <div className="bg-white/5 rounded-xl p-2 border border-white/5">
            <div className="flex items-center justify-center text-emerald-400 mb-0.5">
              <Footprints className="w-3.5 h-3.5" />
            </div>
            <div className="text-xs font-black font-mono">{distKm} <span className="text-[9px] font-normal text-gray-400">km</span></div>
            <div className="text-[8px] uppercase tracking-wider text-gray-400">Distanță</div>
          </div>

          <div className="bg-white/5 rounded-xl p-2 border border-white/5">
            <div className="flex items-center justify-center text-yellow-400 mb-0.5">
              <Zap className="w-3.5 h-3.5" />
            </div>
            <div className="text-xs font-black font-mono">{player.current_speed_kmh} <span className="text-[9px] font-normal text-gray-400">km/h</span></div>
            <div className="text-[8px] uppercase tracking-wider text-gray-400">Viteză</div>
          </div>

          <div className="bg-white/5 rounded-xl p-2 border border-white/5">
            <div className="flex items-center justify-center text-[#04F5FF] mb-0.5">
              <Activity className="w-3.5 h-3.5" />
            </div>
            <div className="text-xs font-black font-mono">{player.sprint_count}</div>
            <div className="text-[8px] uppercase tracking-wider text-gray-400">Sprinturi</div>
          </div>
        </div>

        {/* Stamina & Technical Radar Gauges */}
        <div className="space-y-1.5 bg-white/5 p-2.5 rounded-xl border border-white/5 text-[10px]">
          <div>
            <div className="flex justify-between text-gray-300 font-semibold mb-1">
              <span>Nivel Stamina</span>
              <span className="font-mono">{staminaPct}%</span>
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

          <div className="pt-1.5 flex justify-between border-t border-white/5 text-[9px] text-gray-400">
            <span className="flex items-center gap-1">
              <Target className="w-3 h-3 text-amber-400" /> Pase: <strong className="text-white">{player.passing_skill}</strong>
            </span>
            <span className="flex items-center gap-1">
              <Shield className="w-3 h-3 text-purple-400" /> Șut: <strong className="text-white">{player.shooting_skill}</strong>
            </span>
            <span className="flex items-center gap-1">
              <Zap className="w-3 h-3 text-cyan-400" /> Pace: <strong className="text-white">{player.pace}</strong>
            </span>
          </div>
        </div>

        {/* Action: Toggle Heatmap on Pitch */}
        <button
          onClick={onToggleHeatmap}
          className={`w-full py-2 px-3 rounded-xl text-xs font-bold font-mono flex items-center justify-center gap-2 transition-all shadow-md ${
            isHeatmapActive
              ? "bg-amber-500 text-black hover:bg-amber-400"
              : "bg-white/10 hover:bg-white/20 text-amber-400 border border-amber-500/40"
          }`}
        >
          <Flame className="w-3.5 h-3.5" />
          <span>{isHeatmapActive ? "Ascunde Heatmap-ul lui" : `Activează Heatmap: ${player.name}`}</span>
        </button>
      </div>
    </div>
  );
};
