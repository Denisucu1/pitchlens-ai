import React from "react";
import type { TimelineMoment } from "../types";
import { Clock } from "lucide-react";

interface MatchTimelineBarProps {
  currentMinute: number;
  currentSecond: number;
  moments: TimelineMoment[];
}

export const MatchTimelineBar: React.FC<MatchTimelineBarProps> = ({
  currentMinute,
  currentSecond,
  moments,
}) => {
  // Normalize progress to 0-100% across 90 minutes
  const totalMinutes = 90;
  const progressPct = Math.min(100, Math.max(0, (currentMinute / totalMinutes) * 100));

  return (
    <div className="bg-[#1b0826] border border-[#38003c] rounded-2xl p-3 text-white shadow-xl flex flex-col gap-2">
      {/* Header */}
      <div className="flex items-center justify-between text-xs font-mono">
        <div className="flex items-center gap-1.5 text-gray-300">
          <Clock className="w-3.5 h-3.5 text-[#00FF87]" />
          <span className="font-extrabold uppercase text-[11px] tracking-wider">
            Match Momentum Timeline (90 Min)
          </span>
        </div>
        <div className="text-[11px] font-bold text-yellow-400">
          Min {currentMinute}:{currentSecond.toString().padStart(2, "0")}
        </div>
      </div>

      {/* Progress Track */}
      <div className="relative h-6 bg-[#100418] border border-purple-950 rounded-xl overflow-hidden flex items-center px-1">
        {/* Background Half Indicators */}
        <div className="absolute inset-0 flex justify-between pointer-events-none px-4 text-[9px] font-mono text-gray-600 items-center">
          <span>KICKOFF 1'</span>
          <span className="border-l border-gray-700/60 pl-2">HT 45'</span>
          <span>FT 90'</span>
        </div>

        {/* Live Elapsed Fill */}
        <div
          style={{ width: `${progressPct}%` }}
          className="absolute left-0 top-0 bottom-0 bg-gradient-to-r from-purple-900/60 via-[#00FF87]/20 to-[#00FF87]/40 border-r-2 border-[#00FF87] transition-all duration-700 pointer-events-none"
        />

        {/* Render Timeline Event Markers (e.g. Goals, Cards) */}
        {moments.map((m, idx) => {
          const markerPct = Math.min(98, Math.max(2, (m.minute / totalMinutes) * 100));
          const isCard = m.type === "card";
          const isRed = isCard && m.card === "red";

          return (
            <div
              key={idx}
              style={{ left: `${markerPct}%` }}
              className="absolute -translate-x-1/2 z-20 group cursor-pointer flex flex-col items-center"
            >
              <div
                className={`w-4 h-4 rounded-full border border-black/80 text-[10px] flex items-center justify-center shadow-lg group-hover:scale-125 transition-transform animate-bounce ${
                  isCard
                    ? isRed
                      ? "bg-red-500 text-white"
                      : "bg-yellow-400 text-black"
                    : "bg-yellow-400 text-black"
                }`}
              >
                {isCard ? (isRed ? "🟥" : "🟨") : "⚽"}
              </div>

              {/* Tooltip on hover */}
              <div className="opacity-0 group-hover:opacity-100 transition-opacity absolute bottom-6 bg-black/95 text-white border border-[#00FF87] text-[10px] px-2 py-1 rounded shadow-xl whitespace-nowrap pointer-events-none z-30 font-mono">
                {isCard ? (
                  <>
                    <strong className={isRed ? "text-red-400" : "text-yellow-400"}>
                      {m.minute}' {isRed ? "RED CARD!" : "YELLOW CARD"}
                    </strong>{" "}
                    {m.player} ({m.team})
                  </>
                ) : (
                  <>
                    <strong className="text-[#00FF87]">{m.minute}' GOAL!</strong> {m.player} ({m.team})
                    {m.speed ? ` • ${m.speed} km/h` : ""}
                    {m.xg !== undefined && m.xg !== null ? ` (xG: ${Number(m.xg).toFixed(2)})` : ""}
                  </>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
