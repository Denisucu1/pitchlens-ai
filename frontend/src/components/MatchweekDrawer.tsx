import React from "react";
import type { MatchScoreSummary } from "../types";
import { Radio, Eye } from "lucide-react";

interface MatchweekDrawerProps {
  matches: MatchScoreSummary[];
  activeHomeId: string;
  activeAwayId: string;
  onSelectMatch: (homeId: string, awayId: string) => void;
}

export const MatchweekDrawer: React.FC<MatchweekDrawerProps> = ({
  matches,
  activeHomeId,
  activeAwayId,
  onSelectMatch,
}) => {
  if (!matches || matches.length === 0) return null;

  return (
    <div className="bg-[#12031a] border border-[#38003c] rounded-2xl p-3 shadow-2xl">
      <div className="flex items-center justify-between mb-2.5 px-1">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-red-500 animate-ping" />
          <h4 className="font-extrabold text-xs text-white uppercase tracking-wider font-mono">
            Matchweek 28 • Simultaneous Live Fixtures
          </h4>
        </div>
        <span className="text-[10px] font-mono text-gray-400">
          Click any match to switch broadcast camera
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-2">
        {matches.map((m) => {
          const isFeatured = m.home_team_id === activeHomeId && m.away_team_id === activeAwayId;

          return (
            <div
              key={m.match_id}
              onClick={() => onSelectMatch(m.home_team_id, m.away_team_id)}
              className={`p-2.5 rounded-xl border cursor-pointer transition-all flex flex-col justify-between select-none ${
                isFeatured
                  ? "bg-gradient-to-br from-purple-900/60 to-[#1b0826] border-[#00FF87] shadow-lg shadow-[#00FF87]/10"
                  : "bg-[#180623] border-purple-950/60 hover:border-purple-700/80 hover:bg-[#20082d]"
              }`}
            >
              {/* Top row: Status / Minute */}
              <div className="flex items-center justify-between text-[10px] font-mono mb-1.5">
                <span className={`font-bold flex items-center gap-1 ${
                  isFeatured ? "text-[#00FF87]" : "text-yellow-400"
                }`}>
                  {isFeatured && <Radio className="w-3 h-3 animate-pulse" />}
                  {m.is_finished ? "FT" : `${m.minute}'`}
                </span>
                {isFeatured ? (
                  <span className="bg-[#00FF87] text-black font-black text-[9px] px-1.5 py-0.2 rounded uppercase">
                    ON AIR
                  </span>
                ) : (
                  <span className="text-gray-400 text-[9px] hover:text-[#04F5FF] flex items-center gap-0.5">
                    <Eye className="w-2.5 h-2.5" /> Watch
                  </span>
                )}
              </div>

              {/* Middle row: Home vs Away with score */}
              <div className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className={`font-semibold truncate max-w-[90px] ${
                    isFeatured ? "text-white font-bold" : "text-gray-200"
                  }`}>
                    {m.home_team_name}
                  </span>
                  <span className="font-mono font-black text-sm text-[#00FF87] ml-2">
                    {m.score_home}
                  </span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className={`font-semibold truncate max-w-[90px] ${
                    isFeatured ? "text-white font-bold" : "text-gray-200"
                  }`}>
                    {m.away_team_name}
                  </span>
                  <span className="font-mono font-black text-sm text-[#00FF87] ml-2">
                    {m.score_away}
                  </span>
                </div>
              </div>

              {/* Bottom row: latest event ticker */}
              {m.latest_event_text && (
                <div className="mt-1.5 pt-1 border-t border-white/5 text-[9px] font-mono text-gray-400 truncate">
                  {m.latest_event_text}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
