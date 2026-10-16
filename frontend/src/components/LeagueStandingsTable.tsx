import React from "react";
import type { LeagueTeamStanding } from "../types";
import { ArrowUp, ArrowDown, Minus, Trophy, Flame } from "lucide-react";

interface LeagueStandingsTableProps {
  standings: LeagueTeamStanding[];
  currentHomeId?: string;
  currentAwayId?: string;
}

export const LeagueStandingsTable: React.FC<LeagueStandingsTableProps> = ({
  standings,
  currentHomeId,
  currentAwayId,
}) => {
  if (!standings || standings.length === 0) {
    return (
      <div className="bg-[#1b0826] border border-[#38003c] rounded-2xl p-6 text-center text-gray-400 text-xs">
        Loading live Premier League standings...
      </div>
    );
  }

  return (
    <div className="bg-[#15051f] border border-[#38003c] rounded-2xl shadow-2xl overflow-hidden flex flex-col">
      {/* Table Header */}
      <div className="bg-gradient-to-r from-[#220731] via-[#1b0826] to-[#12031a] p-4 border-b border-[#38003c] flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-[#00FF87] to-[#04F5FF] flex items-center justify-center text-black font-black text-sm">
            <Trophy className="w-4 h-4 text-[#1b0826]" />
          </div>
          <div>
            <h3 className="font-black text-sm text-white tracking-wide flex items-center gap-2">
              <span>Premier League Standings</span>
              <span className="bg-[#38003c] text-[#00FF87] text-[10px] font-mono font-bold px-2 py-0.5 rounded border border-[#00FF87]/30">
                LIVE AS IT STANDS
              </span>
            </h3>
            <p className="text-[11px] text-gray-400 font-mono">
              Matchweek 28 • Real-time table updates
            </p>
          </div>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-3 text-[10px] font-mono text-gray-400">
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-blue-500" /> UCL (1-4)
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-amber-500" /> UEL (5)
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-red-500" /> Relegation (18-20)
          </span>
        </div>
      </div>

      {/* Table Content */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs font-sans">
          <thead>
            <tr className="bg-[#100319] text-gray-400 font-mono text-[10px] uppercase border-b border-purple-950/60 select-none">
              <th className="py-2.5 px-3 text-center w-12">#</th>
              <th className="py-2.5 px-3">Club</th>
              <th className="py-2.5 px-2 text-center">P</th>
              <th className="py-2.5 px-2 text-center">W</th>
              <th className="py-2.5 px-2 text-center">D</th>
              <th className="py-2.5 px-2 text-center">L</th>
              <th className="py-2.5 px-2 text-center">GF:GA</th>
              <th className="py-2.5 px-2 text-center">GD</th>
              <th className="py-2.5 px-3 text-center font-bold text-white">PTS</th>
              <th className="py-2.5 px-3 text-center hidden md:table-cell">Form</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-purple-950/40">
            {standings.map((team) => {
              const isHomePlaying = currentHomeId === team.team_id;
              const isAwayPlaying = currentAwayId === team.team_id;
              const isFeatured = isHomePlaying || isAwayPlaying;

              // Rank movement indicator
              let rankDiff = team.previous_rank - team.rank;

              // Border accents for qualification zones
              let zoneBorder = "border-l-4 border-transparent";
              if (team.rank <= 4) {
                zoneBorder = "border-l-4 border-blue-500";
              } else if (team.rank === 5) {
                zoneBorder = "border-l-4 border-amber-500";
              } else if (team.rank >= 18) {
                zoneBorder = "border-l-4 border-red-500";
              }

              return (
                <tr
                  key={team.team_id}
                  className={`transition-colors text-gray-200 ${zoneBorder} ${
                    isFeatured
                      ? "bg-purple-950/40 hover:bg-purple-950/60 font-semibold"
                      : "hover:bg-white/[0.03]"
                  }`}
                >
                  {/* Position & Rank Shift Indicator */}
                  <td className="py-2 px-3 text-center font-mono">
                    <div className="flex items-center justify-center gap-1">
                      <span className="font-bold text-xs">{team.rank}</span>
                      {rankDiff > 0 && (
                        <span title={`Up ${rankDiff} places`}>
                          <ArrowUp className="w-3 h-3 text-emerald-400 stroke-[3] animate-bounce" />
                        </span>
                      )}
                      {rankDiff < 0 && (
                        <span title={`Down ${Math.abs(rankDiff)} places`}>
                          <ArrowDown className="w-3 h-3 text-rose-500 stroke-[3] animate-bounce" />
                        </span>
                      )}
                      {rankDiff === 0 && (
                        <Minus className="w-2.5 h-2.5 text-gray-600" />
                      )}
                    </div>
                  </td>

                  {/* Club Name & Badge */}
                  <td className="py-2 px-3">
                    <div className="flex items-center gap-2.5">
                      <span
                        style={{ backgroundColor: team.primary_color }}
                        className="w-3.5 h-3.5 rounded-full flex-shrink-0 shadow-sm border border-white/20"
                      />
                      <span className="font-bold tracking-tight text-white whitespace-nowrap">
                        {team.team_name}
                      </span>
                      {isFeatured && (
                        <span className="ml-1 px-1.5 py-0.2 text-[9px] font-mono rounded bg-emerald-500/20 text-[#00FF87] border border-[#00FF87]/40 flex items-center gap-0.5 animate-pulse">
                          <Flame className="w-2.5 h-2.5 text-[#00FF87]" />
                          LIVE
                        </span>
                      )}
                    </div>
                  </td>

                  {/* Matches Played */}
                  <td className="py-2 px-2 text-center font-mono text-gray-400">
                    {team.played}
                  </td>

                  {/* Won */}
                  <td className="py-2 px-2 text-center font-mono text-gray-300">
                    {team.won}
                  </td>

                  {/* Drawn */}
                  <td className="py-2 px-2 text-center font-mono text-gray-400">
                    {team.drawn}
                  </td>

                  {/* Lost */}
                  <td className="py-2 px-2 text-center font-mono text-gray-400">
                    {team.lost}
                  </td>

                  {/* Goals For : Goals Against */}
                  <td className="py-2 px-2 text-center font-mono text-gray-400 text-[11px] whitespace-nowrap">
                    {team.goals_for}:{team.goals_against}
                  </td>

                  {/* Goal Difference */}
                  <td className={`py-2 px-2 text-center font-mono font-semibold ${
                    team.goal_diff > 0
                      ? "text-emerald-400"
                      : team.goal_diff < 0
                      ? "text-rose-400"
                      : "text-gray-400"
                  }`}>
                    {team.goal_diff > 0 ? `+${team.goal_diff}` : team.goal_diff}
                  </td>

                  {/* Points */}
                  <td className="py-2 px-3 text-center font-mono font-black text-sm text-[#00FF87]">
                    {team.points}
                  </td>

                  {/* Form (Last 5 matches) */}
                  <td className="py-2 px-3 text-center hidden md:table-cell">
                    <div className="flex items-center justify-center gap-1">
                      {team.form.map((res, i) => (
                        <span
                          key={i}
                          className={`w-4 h-4 rounded text-[9px] font-mono font-bold flex items-center justify-center ${
                            res === "W"
                              ? "bg-emerald-600/80 text-white"
                              : res === "D"
                              ? "bg-amber-600/70 text-white"
                              : "bg-rose-700/80 text-white"
                          }`}
                        >
                          {res}
                        </span>
                      ))}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
