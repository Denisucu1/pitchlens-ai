import React from "react";
import type { PersonalizedNarrative, PersonaMode, MatchEvent, PlayerProfile } from "../types";
import { Radio, BarChart2, UserCheck, MessageSquare } from "lucide-react";

interface PersonalizedNarrativeFeedProps {
  narrative: PersonalizedNarrative | null;
  persona: PersonaMode;
  latestEvent: MatchEvent | null;
  focusedPlayer?: PlayerProfile | null;
}

export const PersonalizedNarrativeFeed: React.FC<PersonalizedNarrativeFeedProps> = ({
  narrative,
  persona,
  latestEvent,
  focusedPlayer,
}) => {
  if (!narrative) return null;

  const getPersonaBadge = () => {
    switch (persona) {
      case "casual_fan":
        return {
          title: "Casual Fan Commentary Feed",
          icon: <Radio className="w-3.5 h-3.5 text-[#FF2882]" />,
          color: "border-[#FF2882]/40 text-[#FF2882]",
          content: narrative.casual_fan_narrative,
        };
      case "data_analyst":
        return {
          title: "Data-Hungry Analyst Telemetry",
          icon: <BarChart2 className="w-3.5 h-3.5 text-[#00FF87]" />,
          color: "border-[#00FF87]/40 text-[#00FF87]",
          content: narrative.data_analyst_narrative,
        };
      case "player_focus":
        return {
          title: focusedPlayer
            ? `Spotlight: #${focusedPlayer.number} ${focusedPlayer.name}`
            : "Player Spotlight Narrative",
          icon: <UserCheck className="w-3.5 h-3.5 text-[#04F5FF]" />,
          color: "border-[#04F5FF]/40 text-[#04F5FF]",
          content: narrative.player_focus_narrative || narrative.casual_fan_narrative,
        };
    }
  };

  const badge = getPersonaBadge();

  return (
    <div className="bg-[#1b0826] border border-[#38003c] rounded-2xl p-4 text-white shadow-xl flex flex-col gap-3">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[#38003c] pb-2">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-4 h-4 text-purple-400" />
          <h3 className="font-extrabold text-xs uppercase tracking-wider text-gray-200">
            Real-Time AI Narrative Stream
          </h3>
        </div>
        <span
          className={`text-[10px] font-mono px-2 py-0.5 rounded bg-black/40 border font-bold flex items-center gap-1 ${badge.color}`}
        >
          {badge.icon}
          {badge.title}
        </span>
      </div>

      {/* Main Narrative Display */}
      <div className="bg-[#100418] border border-purple-900/50 rounded-xl p-3">
        <div className="flex items-center justify-between text-[10px] font-mono text-gray-500 mb-1.5">
          <span>
            EVENT #{latestEvent?.event_id.replace("evt_", "")} • {narrative.minute}:{narrative.second.toString().padStart(2, "0")}
          </span>
          <span className="uppercase text-yellow-400 font-bold">
            {latestEvent?.event_type}
          </span>
        </div>
        <p className="text-sm font-medium text-gray-100 leading-relaxed">
          {badge.content}
        </p>
      </div>

      {/* Event Details Quick Ribbon */}
      {latestEvent && (
        <div className="flex flex-wrap items-center gap-2 text-[10px] font-mono text-gray-400">
          {latestEvent.ball_speed_kmh && (
            <span className="bg-black/40 border border-white/10 px-2 py-0.5 rounded">
              Ball Speed: <strong className="text-white">{latestEvent.ball_speed_kmh} km/h</strong>
            </span>
          )}
          {latestEvent.pass_difficulty_rating !== null && latestEvent.pass_difficulty_rating !== undefined && (
            <span className="bg-black/40 border border-white/10 px-2 py-0.5 rounded">
              Difficulty: <strong className="text-white">{latestEvent.pass_difficulty_rating.toFixed(2)}</strong>
            </span>
          )}
          {latestEvent.xG !== null && latestEvent.xG !== undefined && (
            <span className="bg-black/40 border border-white/10 px-2 py-0.5 rounded">
              xG: <strong className="text-[#00FF87]">{latestEvent.xG.toFixed(2)}</strong>
            </span>
          )}
          <span className="bg-black/40 border border-white/10 px-2 py-0.5 rounded">
            Actor Speed: <strong className="text-white">{latestEvent.player_speed_kmh} km/h</strong>
          </span>
        </div>
      )}
    </div>
  );
};
