import React from "react";
import type { MatchScoreSummary } from "../types";
import { Radio, Eye, CheckCircle2 } from "lucide-react";

interface LiveMatchHubProps {
  matches: MatchScoreSummary[];
  activeHomeId: string;
  activeAwayId: string;
  onSelectMatch: (homeId: string, awayId: string) => void;
}

export const LiveMatchHub: React.FC<LiveMatchHubProps> = ({
  matches,
  activeHomeId,
  activeAwayId,
  onSelectMatch,
}) => {
  const liveMatches = matches.filter((m) => m.is_live !== false && !m.is_finished);
  const completedMatches = matches.filter((m) => m.is_finished || m.is_live === false);

  return (
    <div className="w-full space-y-6">
      {/* Live Concurrent Matches Section */}
      <div className="bg-[#15051f] border border-[#38003c] rounded-2xl p-5 shadow-2xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4 pb-3 border-b border-white/10">
          <div className="flex items-center gap-2.5">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-ping" />
            <h3 className="font-black text-base text-white tracking-wide flex items-center gap-2">
              <span>Matchweek 28 • Live Fixtures Hub</span>
              <span className="bg-red-950/80 text-red-400 text-[10px] font-mono font-bold px-2 py-0.5 rounded border border-red-500/30 uppercase">
                {liveMatches.length} Live Matches Active
              </span>
            </h3>
          </div>
          <span className="text-xs text-gray-400 font-mono">
            Click "Watch Broadcast" on any match to switch camera
          </span>
        </div>

        {/* 4 Live Matches Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {liveMatches.map((m) => {
            const isFeatured = m.home_team_id === activeHomeId && m.away_team_id === activeAwayId;

            return (
              <div
                key={m.match_id}
                onClick={() => onSelectMatch(m.home_team_id, m.away_team_id)}
                className={`p-4 rounded-xl border transition-all cursor-pointer flex flex-col justify-between group ${
                  isFeatured
                    ? "bg-gradient-to-br from-purple-900/60 to-[#1e072b] border-[#00FF87] shadow-xl shadow-[#00FF87]/15 ring-1 ring-[#00FF87]"
                    : "bg-[#180623] border-purple-950/80 hover:border-purple-600/80 hover:bg-[#20082d]"
                }`}
              >
                {/* Status Bar */}
                <div className="flex items-center justify-between text-xs font-mono mb-3">
                  <div className="flex items-center gap-2">
                    <span className="flex items-center gap-1.5 font-bold text-red-400 bg-red-950/80 px-2 py-0.5 rounded border border-red-500/30">
                      <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-ping" />
                      LIVE {m.minute}' ({m.period})
                    </span>
                    {isFeatured && (
                      <span className="bg-[#00FF87] text-black font-black text-[9px] px-2 py-0.5 rounded uppercase flex items-center gap-1">
                        <Radio className="w-3 h-3 animate-pulse" /> ON AIR
                      </span>
                    )}
                  </div>
                  <span className="text-gray-400 text-[11px] group-hover:text-[#04F5FF] transition flex items-center gap-1">
                    <Eye className="w-3 h-3" />
                    {isFeatured ? "Active Broadcast" : "Watch Broadcast"}
                  </span>
                </div>

                {/* Scoreboard Row */}
                <div className="grid grid-cols-12 items-center gap-2 py-2">
                  {/* Home Team */}
                  <div className="col-span-5 text-right font-bold text-sm text-white truncate">
                    {m.home_team_name}
                  </div>

                  {/* Score */}
                  <div className="col-span-2 text-center">
                    <span className="font-mono font-black text-xl text-[#00FF87] bg-black/60 px-2.5 py-1 rounded-lg border border-white/10 shadow-inner">
                      {m.score_home} - {m.score_away}
                    </span>
                  </div>

                  {/* Away Team */}
                  <div className="col-span-5 text-left font-bold text-sm text-white truncate">
                    {m.away_team_name}
                  </div>
                </div>

                {/* Scorers / Latest Action */}
                <div className="mt-3 pt-2 border-t border-white/10 flex items-center justify-between text-[11px] font-mono text-gray-400">
                  <div className="truncate max-w-[280px]">
                    {m.goal_scorers && m.goal_scorers.length > 0 ? (
                      <span className="text-yellow-300">
                        ⚽ {m.goal_scorers.join(", ")}
                      </span>
                    ) : (
                      <span>{m.latest_event_text || "Tactical buildup in midfield"}</span>
                    )}
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelectMatch(m.home_team_id, m.away_team_id);
                    }}
                    className={`text-[10px] px-2.5 py-1 rounded-lg font-bold font-mono transition ${
                      isFeatured
                        ? "bg-[#00FF87] text-black"
                        : "bg-purple-900/60 hover:bg-purple-700 text-white border border-purple-500/30"
                    }`}
                  >
                    {isFeatured ? "On Pitch" : "Switch Camera"}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Completed Results in MW28 */}
      {completedMatches.length > 0 && (
        <div className="bg-[#12031a] border border-[#38003c] rounded-2xl p-4 shadow-xl">
          <div className="flex items-center gap-2 mb-3 px-1 text-xs font-mono font-bold text-gray-300 uppercase tracking-wider">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>Matchweek 28 • Completed Fixtures (Full Time)</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
            {completedMatches.map((m) => (
              <div
                key={m.match_id}
                className="bg-[#170522] border border-white/5 rounded-xl p-2.5 flex flex-col justify-between"
              >
                <div className="flex items-center justify-between text-[10px] font-mono text-gray-400 mb-1">
                  <span className="bg-white/5 px-1.5 py-0.2 rounded font-bold text-emerald-400">FT</span>
                  <span className="truncate max-w-[150px]">{m.goal_scorers?.slice(-1)[0] || ""}</span>
                </div>
                <div className="flex items-center justify-between text-xs font-semibold">
                  <span className="text-gray-200 truncate">{m.home_team_name}</span>
                  <span className="font-mono font-bold text-white ml-2">{m.score_home} - {m.score_away}</span>
                  <span className="text-gray-200 truncate text-right">{m.away_team_name}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
