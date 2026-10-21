import React, { useState } from "react";
import type { PlayerProfile, TeamProfile, PitchCoordinates } from "../types";
import { Star, Search, Flame, X, ArrowRight, Eye } from "lucide-react";

interface PlayerRatingsTableProps {
  homeTeam: TeamProfile | null;
  awayTeam: TeamProfile | null;
  homePlayers: PlayerProfile[];
  awayPlayers: PlayerProfile[];
  selectedPlayerId?: string | null;
  onSelectPlayer: (player: PlayerProfile) => void;
  playerHeatmaps?: Record<string, PitchCoordinates[]>;
}

const PlayerHeatmapModal: React.FC<{
  player: PlayerProfile;
  teamName: string;
  teamColor: string;
  points: PitchCoordinates[];
  onClose: () => void;
  onFocus: () => void;
}> = ({ player, teamName, teamColor, points, onClose, onFocus }) => {
  const total = Math.max(1, points.length);
  const defThird = points.filter((p) => p.x < 33.3).length;
  const midThird = points.filter((p) => p.x >= 33.3 && p.x <= 66.6).length;
  const attThird = points.filter((p) => p.x > 66.6).length;

  const defPct = Math.round((defThird / total) * 100);
  const midPct = Math.round((midThird / total) * 100);
  const attPct = Math.round((attThird / total) * 100);

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 animate-in fade-in duration-200">
      <div className="bg-[#12041d] border border-purple-500/30 rounded-2xl p-5 shadow-2xl max-w-lg w-full flex flex-col gap-4 text-white font-sans">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div
              style={{ backgroundColor: teamColor }}
              className="w-10 h-10 rounded-xl flex items-center justify-center font-black text-lg text-white shadow-md border border-white/20"
            >
              {player.number}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-[10px] font-bold text-amber-400 uppercase">
                  {teamName} • {player.position}
                </span>
                <span className="bg-amber-500/20 text-amber-300 border border-amber-500/30 text-[9px] font-mono px-1.5 py-0.2 rounded flex items-center gap-1 font-bold">
                  <Flame className="w-2.5 h-2.5 text-amber-400" /> OPTA HEATMAP
                </span>
              </div>
              <h3 className="font-black text-lg text-white leading-tight">
                {player.name}
              </h3>
            </div>
          </div>

          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white p-1.5 rounded-xl hover:bg-white/10 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* 105x68 Pitch Canvas with Heatmap Clusters */}
        <div className="relative w-full aspect-[105/68] bg-gradient-to-br from-[#0c381a] via-[#092d14] to-[#06210f] rounded-xl overflow-hidden border border-emerald-700/60 shadow-inner">
          <div className="absolute inset-0 opacity-15 bg-[repeating-linear-gradient(90deg,transparent,transparent_40px,rgba(255,255,255,0.05)_40px,rgba(255,255,255,0.05)_80px)] pointer-events-none" />

          {/* SVG Pitch Markings */}
          <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
            <rect x="2" y="2" width="96" height="96" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.8" />
            <line x1="50" y1="2" x2="50" y2="98" stroke="rgba(255,255,255,0.4)" strokeWidth="0.8" />
            <circle cx="50" cy="50" r="9.15" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.8" />
            <circle cx="50" cy="50" r="0.8" fill="rgba(255,255,255,0.7)" />

            <rect x="2" y="22" width="16" height="56" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.8" />
            <rect x="2" y="36" width="6" height="28" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.8" />

            <rect x="82" y="22" width="16" height="56" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.8" />
            <rect x="92" y="36" width="6" height="28" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.8" />
          </svg>

          {/* Direction Marker */}
          <div className="absolute top-2 left-3 bg-black/60 px-2 py-0.5 rounded text-[9px] font-mono font-bold text-gray-300 flex items-center gap-1 border border-white/5">
            <span>Attacking</span>
            <ArrowRight className="w-2.5 h-2.5 text-[#00FF87]" />
          </div>

          {/* Heatmap Overlay Points */}
          <div className="absolute inset-0 pointer-events-none overflow-hidden">
            {points.map((pt, idx) => (
              <div
                key={`modal_hp_${idx}`}
                style={{
                  left: `${pt.x}%`,
                  top: `${pt.y}%`,
                  transform: "translate(-50%, -50%)",
                  background:
                    "radial-gradient(circle, rgba(255, 35, 0, 0.9) 0%, rgba(255, 140, 0, 0.55) 45%, rgba(255, 230, 0, 0.18) 75%, transparent 100%)",
                }}
                className="absolute w-14 h-14 rounded-full blur-[6px] pointer-events-none"
              />
            ))}
          </div>

          {/* Live Position Marker */}
          <div
            style={{
              left: `${player.current_coords.x}%`,
              top: `${player.current_coords.y}%`,
              transform: "translate(-50%, -50%)",
            }}
            className="absolute z-20 pointer-events-none flex flex-col items-center"
          >
            <div className="w-4 h-4 rounded-full bg-white border-2 border-black flex items-center justify-center shadow-lg animate-pulse">
              <div className="w-1.5 h-1.5 rounded-full bg-red-600" />
            </div>
            <span className="text-[8px] bg-black/90 text-white font-mono px-1 rounded shadow">Now</span>
          </div>
        </div>

        {/* Territory Analysis Stats */}
        <div className="bg-white/5 p-3 rounded-xl border border-white/10 flex flex-col gap-2">
          <div className="flex items-center justify-between text-xs font-mono">
            <span className="text-gray-400">Total Recorded Touches</span>
            <span className="font-bold text-amber-400">{points.length} Opta Touchpoints</span>
          </div>

          <div className="space-y-1">
            <div className="flex justify-between text-[10px] font-mono text-gray-400">
              <span>Def 3rd: <strong className="text-white">{defPct}%</strong></span>
              <span>Midfield: <strong className="text-white">{midPct}%</strong></span>
              <span>Att 3rd: <strong className="text-white">{attPct}%</strong></span>
            </div>
            <div className="w-full h-2 bg-black/60 rounded-full overflow-hidden flex">
              <div style={{ width: `${defPct}%` }} className="h-full bg-blue-500" title="Defensive Third" />
              <div style={{ width: `${midPct}%` }} className="h-full bg-amber-400" title="Midfield Third" />
              <div style={{ width: `${attPct}%` }} className="h-full bg-red-500" title="Final Attacking Third" />
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-end gap-2 pt-1">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-xl text-xs font-mono bg-white/10 hover:bg-white/15 text-gray-300 hover:text-white transition"
          >
            Close
          </button>
          <button
            onClick={() => {
              onFocus();
              onClose();
            }}
            className="px-4 py-1.5 rounded-xl text-xs font-mono font-bold bg-[#00FF87] hover:bg-[#00e077] text-black transition shadow-lg shadow-[#00FF87]/20 flex items-center gap-1.5"
          >
            <Eye className="w-3.5 h-3.5" />
            <span>Focus in Broadcast</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export const PlayerRatingsTable: React.FC<PlayerRatingsTableProps> = ({
  homeTeam,
  awayTeam,
  homePlayers,
  awayPlayers,
  selectedPlayerId,
  onSelectPlayer,
  playerHeatmaps = {},
}) => {
  const [selectedTeamTab, setSelectedTeamTab] = useState<"home" | "away" | "both">("both");
  const [searchQuery, setSearchQuery] = useState("");
  const [filterRole, setFilterRole] = useState<"all" | "FWD" | "MID" | "DEF" | "GK">("all");
  const [inspectingHeatmapPlayer, setInspectingHeatmapPlayer] = useState<PlayerProfile | null>(null);

  const getRatingBadge = (rating: number = 6.8) => {
    let bg = "bg-gray-700 text-gray-200";
    if (rating >= 8.0) bg = "bg-blue-600 text-white font-black shadow-md shadow-blue-500/30";
    else if (rating >= 7.2) bg = "bg-emerald-600 text-white font-black";
    else if (rating >= 6.5) bg = "bg-amber-500 text-black font-bold";
    else bg = "bg-orange-600 text-white font-bold";

    return (
      <span className={`inline-flex items-center justify-center px-2 py-0.5 rounded-md font-mono text-xs ${bg}`}>
        {rating.toFixed(1)}
      </span>
    );
  };

  const getPositionCategory = (pos: string): "GK" | "DEF" | "MID" | "FWD" => {
    if (pos === "GK") return "GK";
    if (["CB", "LB", "RB", "LWB", "RWB"].includes(pos)) return "DEF";
    if (["CM", "CDM", "CAM", "LM", "RM"].includes(pos)) return "MID";
    return "FWD";
  };

  const enrichPlayerList = (players: PlayerProfile[], team: TeamProfile | null, isHome: boolean) => {
    return players.map((p) => ({
      ...p,
      teamName: team?.name || (isHome ? "Gazde" : "Oaspeți"),
      teamShort: team?.short_name || (isHome ? "HOU" : "AWY"),
      teamColor: team?.primary_color || (isHome ? "#EF0107" : "#0047AB"),
      category: getPositionCategory(p.position),
      isHome,
    }));
  };

  const allPlayers = [
    ...enrichPlayerList(homePlayers, homeTeam, true),
    ...enrichPlayerList(awayPlayers, awayTeam, false),
  ];

  const filteredPlayers = allPlayers
    .filter((p) => {
      if (selectedTeamTab === "home" && !p.isHome) return false;
      if (selectedTeamTab === "away" && p.isHome) return false;
      if (filterRole !== "all" && p.category !== filterRole) return false;
      if (
        searchQuery &&
        !p.name.toLowerCase().includes(searchQuery.toLowerCase()) &&
        !p.position.toLowerCase().includes(searchQuery.toLowerCase())
      ) {
        return false;
      }
      return true;
    })
    .sort((a, b) => (b.match_rating ?? 6.8) - (a.match_rating ?? 6.8));

  return (
    <div className="w-full bg-[#0a0212]/90 backdrop-blur-md border border-white/10 rounded-2xl p-4 sm:p-6 shadow-2xl text-white font-sans animate-in fade-in duration-300">
      {/* Header & Controls */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-6 pb-4 border-b border-white/10">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-emerald-400 font-bold uppercase tracking-wider mb-1">
            <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
            Opta & Sofascore Live Calibration
          </div>
          <h2 className="text-xl sm:text-2xl font-black tracking-tight text-white">
            Players & Match Ratings
          </h2>
          <p className="text-xs text-gray-400 mt-0.5">
            Role-specific telemetry: Strikers (goals/shots), Midfielders (passes/recoveries), Defenders (duels/tackles) and Goalkeepers.
          </p>
        </div>

        {/* Filter Controls */}
        <div className="flex flex-wrap items-center gap-2.5">
          {/* Team Switcher */}
          <div className="flex items-center bg-white/5 p-1 rounded-xl border border-white/10 text-xs">
            <button
              onClick={() => setSelectedTeamTab("both")}
              className={`px-3 py-1.5 rounded-lg font-medium transition ${
                selectedTeamTab === "both"
                  ? "bg-white/20 text-white font-bold"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              All
            </button>
            <button
              onClick={() => setSelectedTeamTab("home")}
              className={`px-3 py-1.5 rounded-lg font-medium transition flex items-center gap-1.5 ${
                selectedTeamTab === "home"
                  ? "bg-white/20 text-white font-bold"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              <span
                className="w-2 h-2 rounded-full"
                style={{ backgroundColor: homeTeam?.primary_color || "#EF0107" }}
              />
              {homeTeam?.short_name || "Home"}
            </button>
            <button
              onClick={() => setSelectedTeamTab("away")}
              className={`px-3 py-1.5 rounded-lg font-medium transition flex items-center gap-1.5 ${
                selectedTeamTab === "away"
                  ? "bg-white/20 text-white font-bold"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              <span
                className="w-2 h-2 rounded-full"
                style={{ backgroundColor: awayTeam?.primary_color || "#0047AB" }}
              />
              {awayTeam?.short_name || "Away"}
            </button>
          </div>

          {/* Position Filter */}
          <div className="flex items-center bg-white/5 p-1 rounded-xl border border-white/10 text-xs">
            {(["all", "FWD", "MID", "DEF", "GK"] as const).map((role) => (
              <button
                key={role}
                onClick={() => setFilterRole(role)}
                className={`px-2.5 py-1.5 rounded-lg font-medium transition uppercase ${
                  filterRole === role
                    ? "bg-purple-600/60 text-white font-bold"
                    : "text-gray-400 hover:text-white"
                }`}
              >
                {role === "all" ? "All" : role}
              </button>
            ))}
          </div>

          {/* Search box */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search player..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-white/5 border border-white/10 rounded-xl pl-8 pr-3 py-1.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-purple-400 transition w-36 sm:w-44"
            />
          </div>
        </div>
      </div>

      {/* Responsive Table */}
      <div className="overflow-x-auto rounded-xl border border-white/10">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="bg-white/[0.04] text-gray-400 font-mono text-[10px] uppercase tracking-wider border-b border-white/10">
              <th className="py-3 px-3.5">Player</th>
              <th className="py-3 px-2 text-center">Pos</th>
              <th className="py-3 px-2 text-center">Rating</th>
              <th className="py-3 px-3 text-center">Goals / Shots</th>
              <th className="py-3 px-3 text-center">Passes (Accuracy)</th>
              <th className="py-3 px-3 text-center">Tackles / Duels</th>
              <th className="py-3 px-3 text-center">Recoveries</th>
              <th className="py-3 px-3 text-center">Saves</th>
              <th className="py-3 px-3 text-center">Distance</th>
              <th className="py-3 px-3 text-center">Top Speed</th>
              <th className="py-3 px-3 text-center">Heatmap</th>
              <th className="py-3 px-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5 font-sans">
            {filteredPlayers.length === 0 ? (
              <tr>
                <td colSpan={12} className="py-8 text-center text-gray-500 font-mono">
                  No players found matching current filters.
                </td>
              </tr>
            ) : (
              filteredPlayers.map((player) => {
                const isSelected = selectedPlayerId === player.id;
                const distKm = (player.distance_covered_meters / 1000).toFixed(2);
                const passAcc = player.passes_total && player.passes_total > 0
                  ? Math.round(((player.passes_completed ?? 0) / player.passes_total) * 100)
                  : 0;

                return (
                  <tr
                    key={player.id}
                    onClick={() => onSelectPlayer(player)}
                    className={`cursor-pointer transition-colors group ${
                      isSelected
                        ? "bg-purple-950/40 border-l-4 border-l-purple-500"
                        : "hover:bg-white/[0.03]"
                    }`}
                  >
                    {/* Player Info */}
                    <td className="py-3 px-3.5 flex items-center gap-2.5">
                      <div
                        className="w-7 h-7 rounded-lg flex items-center justify-center font-mono font-bold text-xs text-white shrink-0 shadow-sm border border-white/20"
                        style={{ backgroundColor: player.teamColor }}
                      >
                        {player.number}
                      </div>
                      <div>
                        <div className="font-bold text-white text-xs group-hover:text-purple-300 transition flex items-center gap-1.5">
                          {player.name}
                          {isSelected && (
                            <span className="text-[9px] bg-purple-500/20 text-purple-300 font-mono px-1.5 py-0.2 rounded">
                              Spotlight
                            </span>
                          )}
                        </div>
                        <div className="text-[10px] text-gray-400 font-mono">
                          {player.teamShort}
                        </div>
                      </div>
                    </td>

                    {/* Position */}
                    <td className="py-3 px-2 text-center">
                      <span className="font-mono font-bold text-[11px] text-gray-300 px-1.5 py-0.5 rounded bg-white/5 border border-white/5">
                        {player.position}
                      </span>
                    </td>

                    {/* Rating */}
                    <td className="py-3 px-2 text-center">
                      {getRatingBadge(player.match_rating)}
                    </td>

                    {/* Attack (Goals & Shots) */}
                    <td className="py-3 px-3 text-center font-mono">
                      {player.category === "FWD" || (player.shots ?? 0) > 0 ? (
                        <span className="font-bold text-amber-400">
                          {player.goals ?? 0} <span className="text-[10px] text-gray-400 font-normal">G</span> ({player.shots_on_target ?? 0}/{player.shots ?? 0})
                        </span>
                      ) : (
                        <span className="text-gray-500">-</span>
                      )}
                    </td>

                    {/* Midfield (Passes & Accuracy) */}
                    <td className="py-3 px-3 text-center font-mono">
                      {(player.passes_total ?? 0) > 0 ? (
                        <span>
                          <span className="font-bold text-emerald-400">{player.passes_completed ?? 0}</span>
                          <span className="text-gray-500">/{player.passes_total ?? 0} </span>
                          <span className="text-[10px] text-gray-400">({passAcc}%)</span>
                        </span>
                      ) : (
                        <span className="text-gray-500">-</span>
                      )}
                    </td>

                    {/* Defense (Tackles & Duels) */}
                    <td className="py-3 px-3 text-center font-mono">
                      {(player.tackles_won ?? 0) > 0 || (player.duels_won ?? 0) > 0 ? (
                        <span className="font-bold text-cyan-400">
                          {player.tackles_won ?? 0} tkl / {player.duels_won ?? 0} duel
                        </span>
                      ) : (
                        <span className="text-gray-500">-</span>
                      )}
                    </td>

                    {/* Recoveries */}
                    <td className="py-3 px-3 text-center font-mono text-gray-300">
                      {player.recoveries && player.recoveries > 0 ? (
                        <span className="font-bold text-emerald-300">{player.recoveries}</span>
                      ) : (
                        <span className="text-gray-500">0</span>
                      )}
                    </td>

                    {/* Saves */}
                    <td className="py-3 px-3 text-center font-mono">
                      {player.category === "GK" ? (
                        <span className="font-bold text-yellow-400">{player.saves ?? 0}</span>
                      ) : (
                        <span className="text-gray-600">-</span>
                      )}
                    </td>

                    {/* Distance */}
                    <td className="py-3 px-3 text-center font-mono text-gray-300">
                      {distKm} <span className="text-[10px] text-gray-500">km</span>
                    </td>

                    {/* Max Speed */}
                    <td className="py-3 px-3 text-center font-mono text-gray-300">
                      {player.current_speed_kmh} <span className="text-[10px] text-gray-500">km/h</span>
                    </td>

                    {/* Heatmap CTA */}
                    <td className="py-3 px-3 text-center">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setInspectingHeatmapPlayer(player);
                        }}
                        className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-amber-500/15 hover:bg-amber-500/30 text-amber-300 border border-amber-500/30 text-[10px] font-mono font-bold transition shadow-sm"
                        title={`View ${player.name}'s Opta heatmap`}
                      >
                        <Flame className="w-3 h-3 text-amber-400" />
                        <span>Map</span>
                      </button>
                    </td>

                    {/* Focus CTA */}
                    <td className="py-3 px-3 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectPlayer(player);
                        }}
                        className={`px-2.5 py-1 rounded-lg text-[10px] font-mono transition border ${
                          isSelected
                            ? "bg-purple-600 text-white border-purple-400 font-bold"
                            : "bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white border-white/10"
                        }`}
                      >
                        {isSelected ? "Selected" : "Focus"}
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Interactive Individual Player Heatmap Modal */}
      {inspectingHeatmapPlayer && (
        <PlayerHeatmapModal
          player={inspectingHeatmapPlayer}
          teamName={
            inspectingHeatmapPlayer.team_id === homeTeam?.id
              ? homeTeam?.name || "Home"
              : awayTeam?.name || "Away"
          }
          teamColor={
            inspectingHeatmapPlayer.team_id === homeTeam?.id
              ? homeTeam?.primary_color || "#EF0107"
              : awayTeam?.primary_color || "#0047AB"
          }
          points={
            playerHeatmaps[inspectingHeatmapPlayer.id] ||
            inspectingHeatmapPlayer.heatmap ||
            []
          }
          onClose={() => setInspectingHeatmapPlayer(null)}
          onFocus={() => {
            onSelectPlayer(inspectingHeatmapPlayer);
          }}
        />
      )}
    </div>
  );
};
