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

  const homeColor = homeTeam?.primary_color || "#EF0107";
  const awayColor = awayTeam?.primary_color || "#6CABDD";

  const StatRow = ({
    label,
    valH,
    valA,
    format = (v: any) => v,
  }: {
    label: string;
    valH: number;
    valA: number;
    format?: (v: any) => string | number;
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
            style={{ width: `${pctH}%`, backgroundColor: homeColor }}
            className="h-full transition-all duration-500 ease-out"
          />
          <div
            style={{ width: `${100 - pctH}%`, backgroundColor: awayColor }}
            className="h-full transition-all duration-500 ease-out"
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
            Official Match Statistics
          </h3>
        </div>
        <div className="flex items-center gap-3 text-[10px] font-bold">
          <span style={{ color: homeColor }}>{homeTeam?.short_name || "HOME"}</span>
          <span className="text-gray-500">VS</span>
          <span style={{ color: awayColor }}>{awayTeam?.short_name || "AWAY"}</span>
        </div>
      </div>

      {/* Rows */}
      <div className="space-y-1">
        <StatRow
          label="Expected Goals (xG)"
          valH={statsHome.total_xG}
          valA={statsAway.total_xG}
          format={(v) => Number(v).toFixed(2)}
        />
        <StatRow
          label="Possession %"
          valH={statsHome.possession_pct}
          valA={statsAway.possession_pct}
          format={(v) => `${v}%`}
        />
        <StatRow
          label="Total Shots"
          valH={statsHome.total_shots}
          valA={statsAway.total_shots}
          format={(v) => v}
        />
        <StatRow
          label="Shots on Target"
          valH={statsHome.shots_on_target}
          valA={statsAway.shots_on_target}
          format={(v) => v}
        />
        <StatRow
          label="Corner Kicks"
          valH={statsHome.corners ?? 0}
          valA={statsAway.corners ?? 0}
          format={(v) => v}
        />
        <StatRow
          label="Fouls Committed"
          valH={statsHome.fouls ?? 0}
          valA={statsAway.fouls ?? 0}
          format={(v) => v}
        />
        <StatRow
          label="Yellow Cards"
          valH={statsHome.cards_yellow ?? 0}
          valA={statsAway.cards_yellow ?? 0}
          format={(v) => `${v} 🟨`}
        />
        <StatRow
          label="Red Cards"
          valH={statsHome.cards_red ?? 0}
          valA={statsAway.cards_red ?? 0}
          format={(v) => `${v} 🟥`}
        />
        <StatRow
          label="Pass Accuracy %"
          valH={statsHome.pass_accuracy_pct}
          valA={statsAway.pass_accuracy_pct}
          format={(v) => `${v}%`}
        />
      </div>
    </div>
  );
};
