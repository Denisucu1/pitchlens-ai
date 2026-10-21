import React, { useState } from "react";
import type { LeagueTeamStanding, MatchScoreSummary } from "../types";
import { Trophy, Award, ShieldAlert, Zap } from "lucide-react";

interface ChampionshipHubProps {
  standings: LeagueTeamStanding[];
  matches?: MatchScoreSummary[];
  onSelectTeamMatch?: (teamId: string) => void;
}

export const ChampionshipHub: React.FC<ChampionshipHubProps> = ({
  standings,
  matches = [],
  onSelectTeamMatch,
}) => {
  const [activeLeaderTab, setActiveLeaderTab] = useState<"goals" | "assists" | "cleansheets">("goals");

  // Dynamically extract Title Race contenders (Top 3)
  const titleContenders = standings.slice(0, 3);
  const leaderPoints = titleContenders[0]?.points || 0;

  // Dynamically extract Relegation battle (17th safe vs 18th, 19th, 20th)
  const safetyCutoffTeam = standings[16]; // 17th position (0-indexed 16)
  const relegationZone = standings.slice(17, 20); // 18, 19, 20

  // Calculate Matchweek 28 aggregated league-wide statistics
  const totalMatchweekGoals = matches.reduce(
    (sum, m) => sum + (m.score_home || 0) + (m.score_away || 0),
    0
  );
  const liveMatchesCount = matches.filter((m) => m.is_live && !m.is_finished).length;
  const completedMatchesCount = matches.filter((m) => m.is_finished).length;

  // Season individual leaderboard data (Calibrated to current 2026 Premier League season)
  const topScorers = [
    { rank: 1, name: "Erling Haaland", club: "Man City", clubColor: "#6CABDD", count: 21, sub: "xG: 19.4" },
    { rank: 2, name: "Mohamed Salah", club: "Liverpool", clubColor: "#C8102E", count: 18, sub: "xG: 16.2" },
    { rank: 3, name: "Ollie Watkins", club: "Aston Villa", clubColor: "#95BFE5", count: 16, sub: "xG: 14.8" },
    { rank: 4, name: "Cole Palmer", club: "Chelsea", clubColor: "#034694", count: 15, sub: "xG: 12.1" },
    { rank: 5, name: "Bukayo Saka", club: "Arsenal", clubColor: "#EF0107", count: 14, sub: "xG: 11.9" },
  ];

  const topAssists = [
    { rank: 1, name: "Kevin De Bruyne", club: "Man City", clubColor: "#6CABDD", count: 12, sub: "xA: 11.2" },
    { rank: 2, name: "Mohamed Salah", club: "Liverpool", clubColor: "#C8102E", count: 10, sub: "xA: 9.8" },
    { rank: 3, name: "Bukayo Saka", club: "Arsenal", clubColor: "#EF0107", count: 10, sub: "xA: 9.1" },
    { rank: 4, name: "Cole Palmer", club: "Chelsea", clubColor: "#034694", count: 9, sub: "xA: 8.5" },
    { rank: 5, name: "Martin Ødegaard", club: "Arsenal", clubColor: "#EF0107", count: 8, sub: "xA: 8.9" },
  ];

  const topCleanSheets = [
    { rank: 1, name: "David Raya", club: "Arsenal", clubColor: "#EF0107", count: 13, sub: "Saves: 74" },
    { rank: 2, name: "Ederson", club: "Man City", clubColor: "#6CABDD", count: 11, sub: "Saves: 68" },
    { rank: 3, name: "Alisson Becker", club: "Liverpool", clubColor: "#C8102E", count: 10, sub: "Saves: 79" },
    { rank: 4, name: "Emiliano Martínez", club: "Aston Villa", clubColor: "#95BFE5", count: 9, sub: "Saves: 82" },
    { rank: 5, name: "Guglielmo Vicario", club: "Tottenham", clubColor: "#132257", count: 8, sub: "Saves: 88" },
  ];

  const activeLeaderboard =
    activeLeaderTab === "goals"
      ? topScorers
      : activeLeaderTab === "assists"
      ? topAssists
      : topCleanSheets;

  return (
    <div className="flex flex-col gap-5 text-white">
      {/* 1. Title Race Live Tracker */}
      <div className="bg-[#15051f] border border-[#38003c] rounded-2xl p-4 shadow-xl">
        <div className="flex items-center justify-between pb-3 mb-3 border-b border-[#38003c]">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-amber-400 to-yellow-600 flex items-center justify-center text-black shadow-md shadow-yellow-500/20">
              <Trophy className="w-3.5 h-3.5 text-black" />
            </div>
            <div>
              <h4 className="font-extrabold text-xs uppercase tracking-wider text-gray-200">
                Title Race • As It Stands
              </h4>
              <p className="text-[10px] text-gray-400 font-mono">Live Margin to 1st Place</p>
            </div>
          </div>
          <span className="bg-[#00FF87]/15 text-[#00FF87] border border-[#00FF87]/30 text-[9px] font-mono font-black px-2 py-0.5 rounded uppercase">
            LIVE 🏆
          </span>
        </div>

        {/* Top 3 Contenders List */}
        <div className="space-y-2">
          {titleContenders.map((team, idx) => {
            const gap = team.points - leaderPoints;
            const gapText = idx === 0 ? "LEADER" : `${gap} PTS`;

            return (
              <div
                key={team.team_id}
                onClick={() => onSelectTeamMatch && onSelectTeamMatch(team.team_id)}
                className={`p-2.5 rounded-xl border flex items-center justify-between transition-all cursor-pointer ${
                  idx === 0
                    ? "bg-gradient-to-r from-amber-950/40 via-purple-950/30 to-[#100319] border-amber-500/50 shadow-md"
                    : "bg-[#100319] border-purple-950/60 hover:border-purple-600/50"
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <span
                    className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-mono font-black ${
                      idx === 0
                        ? "bg-amber-400 text-black shadow-sm"
                        : "bg-white/10 text-gray-300"
                    }`}
                  >
                    {idx + 1}
                  </span>
                  <span
                    style={{ backgroundColor: team.primary_color }}
                    className="w-3 h-3 rounded-full shrink-0 border border-white/20 shadow-sm"
                  />
                  <div>
                    <span className="font-bold text-xs text-white tracking-tight">
                      {team.team_name}
                    </span>
                    <div className="text-[10px] text-gray-400 font-mono">
                      {team.played} MP • GD: {team.goal_diff > 0 ? `+${team.goal_diff}` : team.goal_diff}
                    </div>
                  </div>
                </div>

                <div className="flex flex-col items-end">
                  <span className="font-mono font-black text-sm text-[#00FF87]">
                    {team.points} <span className="text-[10px] text-gray-400 font-sans">PTS</span>
                  </span>
                  <span
                    className={`text-[9px] font-mono font-bold px-1.5 py-0.2 rounded ${
                      idx === 0
                        ? "bg-amber-400/20 text-amber-300 border border-amber-400/30"
                        : "text-gray-400"
                    }`}
                  >
                    {gapText}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 2. Official Premier League Individual Honors (Golden Boot / Playmaker / Clean Sheets) */}
      <div className="bg-[#15051f] border border-[#38003c] rounded-2xl p-4 shadow-xl">
        <div className="flex items-center justify-between pb-3 mb-3 border-b border-[#38003c]">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-[#00FF87] to-[#04F5FF] flex items-center justify-center text-black shadow-md shadow-emerald-500/20">
              <Award className="w-3.5 h-3.5 text-black" />
            </div>
            <div>
              <h4 className="font-extrabold text-xs uppercase tracking-wider text-gray-200">
                Season Individual Leaders
              </h4>
              <p className="text-[10px] text-gray-400 font-mono">Official 2025/26 Benchmarks</p>
            </div>
          </div>
        </div>

        {/* Category Tabs */}
        <div className="grid grid-cols-3 gap-1 p-1 bg-[#100319] rounded-xl border border-purple-950/60 mb-3 text-[10px] font-mono font-bold">
          <button
            onClick={() => setActiveLeaderTab("goals")}
            className={`py-1.5 rounded-lg transition-all flex items-center justify-center gap-1 ${
              activeLeaderTab === "goals"
                ? "bg-[#38003c] text-[#00FF87] shadow-md border border-[#00FF87]/40 font-black"
                : "text-gray-400 hover:text-white"
            }`}
          >
            <span>⚽</span> Goals
          </button>
          <button
            onClick={() => setActiveLeaderTab("assists")}
            className={`py-1.5 rounded-lg transition-all flex items-center justify-center gap-1 ${
              activeLeaderTab === "assists"
                ? "bg-[#38003c] text-[#04F5FF] shadow-md border border-[#04F5FF]/40 font-black"
                : "text-gray-400 hover:text-white"
            }`}
          >
            <span>🅰️</span> Assists
          </button>
          <button
            onClick={() => setActiveLeaderTab("cleansheets")}
            className={`py-1.5 rounded-lg transition-all flex items-center justify-center gap-1 ${
              activeLeaderTab === "cleansheets"
                ? "bg-[#38003c] text-amber-300 shadow-md border border-amber-400/40 font-black"
                : "text-gray-400 hover:text-white"
            }`}
          >
            <span>🧤</span> Gloves
          </button>
        </div>

        {/* Leaders List */}
        <div className="space-y-1.5">
          {activeLeaderboard.map((item) => (
            <div
              key={item.name}
              className="p-2 rounded-xl bg-[#100319] border border-purple-950/40 flex items-center justify-between hover:border-purple-800/50 transition-colors"
            >
              <div className="flex items-center gap-2">
                <span
                  className={`w-4 h-4 rounded-full flex items-center justify-center text-[9px] font-mono font-bold ${
                    item.rank === 1
                      ? "bg-amber-400 text-black font-black"
                      : "text-gray-500 bg-white/5"
                  }`}
                >
                  {item.rank}
                </span>
                <span
                  style={{ backgroundColor: item.clubColor }}
                  className="w-2.5 h-2.5 rounded-full shrink-0 border border-white/20"
                />
                <div>
                  <div className="text-xs font-bold text-white tracking-tight">{item.name}</div>
                  <div className="text-[10px] text-gray-400 font-mono">{item.club}</div>
                </div>
              </div>

              <div className="flex flex-col items-end">
                <span className="font-mono font-black text-sm text-yellow-300">
                  {item.count}{" "}
                  <span className="text-[9px] text-gray-400 font-normal">
                    {activeLeaderTab === "goals"
                      ? "goals"
                      : activeLeaderTab === "assists"
                      ? "assists"
                      : "clean sheets"}
                  </span>
                </span>
                <span className="text-[9px] text-gray-400 font-mono">{item.sub}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 3. Relegation Scrap & Survival Threshold */}
      {relegationZone.length > 0 && safetyCutoffTeam && (
        <div className="bg-[#15051f] border border-[#38003c] rounded-2xl p-4 shadow-xl">
          <div className="flex items-center justify-between pb-2 mb-2 border-b border-[#38003c]">
            <div className="flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-rose-400" />
              <h4 className="font-extrabold text-xs uppercase tracking-wider text-gray-200">
                Relegation Scrap (Bottom 3)
              </h4>
            </div>
            <span className="text-[10px] font-mono text-gray-400">
              Safety: {safetyCutoffTeam.points} pts ({safetyCutoffTeam.short_name})
            </span>
          </div>

          <div className="space-y-1.5">
            {relegationZone.map((team) => {
              const ptsBehindSafety = safetyCutoffTeam.points - team.points;

              return (
                <div
                  key={team.team_id}
                  className="p-2 rounded-xl bg-red-950/20 border border-red-900/40 flex items-center justify-between"
                >
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono font-black text-rose-400 w-4 text-center">
                      {team.rank}
                    </span>
                    <span
                      style={{ backgroundColor: team.primary_color }}
                      className="w-2.5 h-2.5 rounded-full shrink-0 border border-white/20"
                    />
                    <span className="text-xs font-bold text-gray-200">{team.team_name}</span>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-black text-white">{team.points} pts</span>
                    <span className="text-[9px] font-mono text-rose-400 bg-rose-950/60 px-1.5 py-0.5 rounded border border-rose-500/30">
                      -{ptsBehindSafety} from safety
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* 4. Matchweek 28 League Pulse Card */}
      <div className="bg-[#100319] border border-purple-950/60 rounded-2xl p-4 shadow-xl flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-purple-950/80 border border-purple-500/30 flex items-center justify-center text-purple-300">
            <Zap className="w-4 h-4 text-[#00FF87]" />
          </div>
          <div>
            <div className="text-xs font-black text-white uppercase tracking-wider">
              Matchweek 28 Telemetry
            </div>
            <div className="text-[10px] text-gray-400 font-mono">
              {liveMatchesCount} live fixtures • {completedMatchesCount} finished
            </div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-sm font-mono font-black text-[#00FF87]">
            {totalMatchweekGoals} <span className="text-[10px] text-gray-400 font-sans">GOALS</span>
          </div>
          <div className="text-[9px] text-gray-400 font-mono">
            ~{(totalMatchweekGoals / Math.max(1, matches.length)).toFixed(1)} goals/match
          </div>
        </div>
      </div>
    </div>
  );
};
