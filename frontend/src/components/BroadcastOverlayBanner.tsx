import React, { useState, useEffect } from "react";
import type { BroadcastOverlay } from "../types";
import { Sparkles, Activity, ShieldAlert, Award, Compass, ChevronDown, ChevronUp, X } from "lucide-react";

interface BroadcastOverlayBannerProps {
  overlay: BroadcastOverlay | null;
}

export const BroadcastOverlayBanner: React.FC<BroadcastOverlayBannerProps> = ({ overlay }) => {
  const [isMinimized, setIsMinimized] = useState(false);
  const [isDismissed, setIsDismissed] = useState(false);

  // If a new overlay arrives, re-show it
  useEffect(() => {
    setIsDismissed(false);
  }, [overlay?.graphic_id, overlay?.primary_metric]);

  if (!overlay || !overlay.is_active || isDismissed) return null;

  const getIcon = () => {
    switch (overlay.graphic_type) {
      case "lower_third":
        return <Award className="w-3.5 h-3.5 text-yellow-300" />;
      case "speed_pass_badge":
        return <Activity className="w-3.5 h-3.5 text-[#00FF87]" />;
      case "momentum_gauge":
        return <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />;
      case "player_spotlight":
        return <Sparkles className="w-3.5 h-3.5 text-[#04F5FF]" />;
      default:
        return <Compass className="w-3.5 h-3.5 text-purple-300" />;
    }
  };

  // Minimized state: sleek miniature broadcast badge
  if (isMinimized) {
    return (
      <div className="absolute bottom-2 left-2 z-40">
        <button
          onClick={() => setIsMinimized(false)}
          className="bg-[#12031a]/90 backdrop-blur-md border border-[#00FF87]/50 rounded-lg px-2 py-1 text-[10px] text-white flex items-center gap-1.5 hover:bg-[#20082d] transition-all shadow-md group"
          title="Expand Tactical On-Screen Overlay"
        >
          {getIcon()}
          <span className="font-mono text-[#00FF87] font-bold text-[9px]">TACTICAL OVERLAY</span>
          <ChevronUp className="w-3 h-3 text-gray-400 group-hover:text-white" />
        </button>
      </div>
    );
  }

  // Expanded compact state: slim TV lower-third that doesn't obstruct players
  return (
    <div className="absolute bottom-2 left-2 z-40 max-w-[30px] sm:max-w-[300px] transition-all duration-300 select-none">
      <div className="bg-[#12031a]/95 backdrop-blur-md border border-[#00FF87]/70 rounded-xl p-2 shadow-[0_8px_20px_rgba(0,0,0,0.85)] text-white overflow-hidden relative">
        {/* Accent Glow Line */}
        <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-[#00FF87] via-[#04F5FF] to-[#FF2882]" />

        <div className="flex items-start gap-2">
          <div className="p-1 rounded-md bg-black/50 border border-white/10 shrink-0 mt-0.5">
            {getIcon()}
          </div>

          <div className="flex-1 min-w-0">
            {/* Header with Title & Action Controls */}
            <div className="flex items-center justify-between gap-1">
              <span className="text-[9px] font-black uppercase tracking-wider text-[#00FF87] font-mono truncate max-w-[160px]">
                {overlay.display_title.replace(/^TACTICAL NOTE:\s*/i, "")}
              </span>
              <div className="flex items-center gap-0.5">
                <button
                  onClick={() => setIsMinimized(true)}
                  className="p-0.5 text-gray-400 hover:text-white rounded hover:bg-white/10 transition-colors"
                  title="Minimize overlay"
                >
                  <ChevronDown className="w-3 h-3" />
                </button>
                <button
                  onClick={() => setIsDismissed(true)}
                  className="p-0.5 text-gray-400 hover:text-white rounded hover:bg-white/10 transition-colors"
                  title="Hide overlay"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            </div>

            {/* Primary & Secondary Metric */}
            <div className="flex items-baseline gap-1 mt-0.5 flex-wrap">
              <span className="font-bold text-xs text-white leading-tight">
                {overlay.primary_metric}
              </span>
              {overlay.secondary_metric && (
                <span className="text-[9px] text-yellow-300 font-mono font-semibold">
                  • {overlay.secondary_metric}
                </span>
              )}
            </div>

            {/* Compact 1-line detail */}
            <p className="text-[10px] text-gray-300 mt-0.5 line-clamp-1 leading-snug">
              {overlay.detail_text}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
