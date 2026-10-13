import React from "react";
import type { TeamMatchStats, TeamProfile } from "../types";
import { BarChart3 } from "lucide-react";

interface StatsPanelProps {
  statsHome: TeamMatchStats | null;
  statsAway: TeamMatchStats | null;
  homeTeam: TeamProfile | null;
  awayTeam: TeamProfile | null;
}

export const StatsPanel: React.FC<StatsPanelProps> = ({
  statsHome,
  statsAway,
  homeTeam,
  awayTeam,
}) => {
  if (!statsHome || !statsAway) return null;

  const StatRow = ({
    label,
    valH,
    valA,
    format = (v: any) => v,
    invertColor = false,
  }: {
    label: string;
    valH: number;
    valA: number;
    format?: (v: any) => string | number;
    invertColor?: boolean;
  }) => {
    const total = valH + valA;
    const pctH = total > 0 ? (valH / total) * 100 : 50;

    return (
      <div className="flex flex-col gap-1 py-1.5 border-b border-[#38003c]/50 last:border-none">
        <div className="flex justify-between text-xs font-mono">
          <span className="font-bold text-gray-200">{format(valH)}</span>
          <span className="text-[11px] uppercase tracking-wider text-gray-400 font-sans">{label}</span>
          <span className="font-bold text-gray-200">{format(valA)}</span>
        </div>
        <div className="h-1.5 w-full bg-[#100418] rounded-full overflow-hidden flex">
          <div
            style={{ width: `${pctH}%` }}
            className={`h-full ${invertColor ? "bg-cyan-500" : "bg-[#EF0107]"}`}
          />
          <div
            style={{ width: `${100 - pctH}%` }}
            className={`h-full ${invertColor ? "bg-pink-500" : "bg-[#6CABDD]"}`}
          />
        </div>
      </div>
    );
  };

  return (
    <div className="bg-[#1b0826] border border-[#38003c] rounded-2xl p-4 text-white shadow-xl flex flex-col gap-2.5">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[#38003c] pb-2">
        <div className="flex items-center gap-2">
          <BarChart3 className="w-4 h-4 text-[#00FF87]" />
          <h3 className="font-extrabold text-xs uppercase tracking-wider text-gray-200">
            Live Match Telemetry & Stats
          </h3>
        </div>
        <div className="flex items-center gap-3 text-[10px] font-bold">
          <span className="text-[#EF0107]">{homeTeam?.short_name || "CAN"}</span>
          <span className="text-gray-500">VS</span>
          <span className="text-[#6CABDD]">{awayTeam?.short_name || "TIT"}</span>
        </div>
      </div>

      {/* Rows */}
      <div className="space-y-1">
        <StatRow
          label="Possession %"
          valH={statsHome.possession_pct}
          valA={statsAway.possession_pct}
          format={(v) => `${v}%`}
        />
        <StatRow
          label="Expected Goals (xG)"
          valH={statsHome.total_xG}
          valA={statsAway.total_xG}
          format={(v) => Number(v).toFixed(2)}
        />
        <StatRow
          label="Total Shots (On Target)"
          valH={statsHome.total_shots}
          valA={statsAway.total_shots}
          format={(v) => v}
        />
        <StatRow
          label="Pass Accuracy %"
          valH={statsHome.pass_accuracy_pct}
          valA={statsAway.pass_accuracy_pct}
          format={(v) => `${v}%`}
        />
        <StatRow
          label="Avg Pass Difficulty"
          valH={statsHome.average_pass_difficulty}
          valA={statsAway.average_pass_difficulty}
          format={(v) => Number(v).toFixed(2)}
        />
        <StatRow
          label="Tackles Won"
          valH={statsHome.tackles_won}
          valA={statsAway.tackles_won}
        />
        <StatRow
          label="Avg Ball Speed (km/h)"
          valH={statsHome.avg_ball_speed_kmh}
          valA={statsAway.avg_ball_speed_kmh}
          format={(v) => `${Number(v).toFixed(1)} km/h`}
        />
      </div>
    </div>
  );
};
