import React from "react";
import type { RhythmState } from "../types";
import { Flame, Shield, Activity, Compass } from "lucide-react";

interface ControlChaosGaugeProps {
  rhythm: RhythmState | null;
}

export const ControlChaosGauge: React.FC<ControlChaosGaugeProps> = ({ rhythm }) => {
  if (!rhythm) return null;

  const controlVal = rhythm.control_vs_chaos_index;
  const chaosVal = 100 - controlVal;

  return (
    <div className="bg-[#1b0826] border border-[#38003c] rounded-2xl p-4 text-white shadow-xl flex flex-col gap-3">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[#38003c] pb-2">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-[#00FF87]" />
          <h3 className="font-extrabold text-xs uppercase tracking-wider text-gray-200">
            Game Rhythm & Control Index
          </h3>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-950 text-[#00FF87] border border-[#00FF87]/30 font-bold">
          {rhythm.pace_rating} Tempo
        </span>
      </div>

      {/* Dual Bar: Control vs Chaos */}
      <div>
        <div className="flex justify-between text-xs font-mono font-bold mb-1">
          <span className="text-[#00FF87] flex items-center gap-1">
            <Shield className="w-3.5 h-3.5" /> Control: {controlVal.toFixed(0)}%
          </span>
          <span className="text-[#FF2882] flex items-center gap-1">
            Chaos: {chaosVal.toFixed(0)}% <Flame className="w-3.5 h-3.5" />
          </span>
        </div>
        <div className="h-3 w-full bg-[#100418] rounded-full overflow-hidden flex border border-[#38003c] p-0.5">
          <div
            style={{ width: `${controlVal}%` }}
            className="h-full bg-gradient-to-r from-emerald-500 to-[#00FF87] rounded-l-full transition-all duration-700 ease-out"
          />
          <div
            style={{ width: `${chaosVal}%` }}
            className="h-full bg-gradient-to-r from-[#FF2882] to-rose-600 rounded-r-full transition-all duration-700 ease-out"
          />
        </div>
      </div>

      {/* Secondary Metrics Grid */}
      <div className="grid grid-cols-2 gap-2 text-xs">
        <div className="bg-[#100418] border border-purple-900/40 rounded-xl p-2 flex flex-col">
          <span className="text-[10px] uppercase text-gray-400 font-mono">Pitch Pressure</span>
          <div className="flex items-baseline gap-1 mt-0.5">
            <span className="font-extrabold text-sm text-yellow-400 font-mono">
              {rhythm.tactical_pressure_index.toFixed(1)}%
            </span>
            <span className="text-[9px] text-gray-500">intensity</span>
          </div>
        </div>

        <div className="bg-[#100418] border border-purple-900/40 rounded-xl p-2 flex flex-col">
          <span className="text-[10px] uppercase text-gray-400 font-mono">Dominant Zone</span>
          <div className="flex items-center gap-1 mt-0.5 truncate">
            <Compass className="w-3 h-3 text-[#04F5FF] shrink-0" />
            <span className="font-bold text-xs text-white truncate">
              {rhythm.dominant_zone}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
