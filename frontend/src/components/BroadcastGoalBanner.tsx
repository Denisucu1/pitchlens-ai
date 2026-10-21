import React, { useEffect, useState } from "react";
import type { MatchEvent, TeamProfile } from "../types";
import { Zap, CheckCircle2, X } from "lucide-react";

interface BroadcastGoalBannerProps {
  latestEvent: MatchEvent | null;
  homeTeam: TeamProfile | null;
  awayTeam: TeamProfile | null;
}

export const BroadcastGoalBanner: React.FC<BroadcastGoalBannerProps> = ({
  latestEvent,
  homeTeam,
  awayTeam,
}) => {
  const [visible, setVisible] = useState(false);
  const [activeGoalEvent, setActiveGoalEvent] = useState<MatchEvent | null>(null);

  useEffect(() => {
    if (latestEvent && latestEvent.event_type === "goal") {
      setActiveGoalEvent(latestEvent);
      setVisible(true);

      const timer = setTimeout(() => {
        setVisible(false);
      }, 5500);

      return () => clearTimeout(timer);
    }
  }, [latestEvent?.event_id, latestEvent?.event_type]);

  if (!visible || !activeGoalEvent) return null;

  const isHome = activeGoalEvent.team_id === homeTeam?.id;
  const scoringTeam = isHome ? homeTeam : awayTeam;
  const teamColor = scoringTeam?.primary_color || "#EF0107";
  const shotSpeed = activeGoalEvent.shot_speed_kmh || activeGoalEvent.ball_speed_kmh || 98.4;

  return (
    <div className="absolute top-4 left-1/2 -translate-x-1/2 z-50 w-[92%] max-w-md animate-in zoom-in-95 fade-in slide-in-from-top-6 duration-300">
      <div
        style={{
          boxShadow: `0 0 35px ${teamColor}80, 0 10px 40px rgba(0,0,0,0.9)`,
          background: `linear-gradient(135deg, ${teamColor} 0%, #0d0e15 70%)`,
        }}
        className="rounded-2xl p-4 border-2 border-yellow-400 text-white relative overflow-hidden"
      >
        {/* Animated Gold Shimmer Top Line */}
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-yellow-300 via-white to-yellow-300 animate-pulse" />

        {/* Close Button */}
        <button
          onClick={() => setVisible(false)}
          className="absolute top-2.5 right-2.5 text-white/70 hover:text-white p-1 rounded-lg hover:bg-black/30 transition"
        >
          <X className="w-4 h-4" />
        </button>

        <div className="flex items-center gap-3.5">
          {/* Big Goal Badge */}
          <div className="w-14 h-14 rounded-2xl bg-black/60 border-2 border-yellow-400 flex flex-col items-center justify-center shrink-0 shadow-xl">
            <span className="text-2xl animate-bounce">⚽</span>
            <span className="text-[9px] font-black tracking-widest text-yellow-300 font-mono">GOAL!</span>
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 text-xs font-mono font-bold text-yellow-300 uppercase">
              <span>{scoringTeam?.name || "PREMIER LEAGUE"}</span>
              <span>•</span>
              <span>MINUTE {activeGoalEvent.minute}'</span>
            </div>

            <div className="text-xl font-black tracking-tight leading-tight text-white truncate drop-shadow-md">
              {activeGoalEvent.player.name}
            </div>

            <div className="mt-1 flex items-center gap-3 text-[10px] font-mono text-gray-200">
              <span className="flex items-center gap-1 bg-black/50 px-2 py-0.5 rounded border border-white/10">
                <Zap className="w-3 h-3 text-yellow-400" /> Shot Speed: <strong className="text-white">{shotSpeed} km/h</strong>
              </span>
              <span className="flex items-center gap-1 text-emerald-400">
                <CheckCircle2 className="w-3 h-3" /> VAR Confirmed
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
