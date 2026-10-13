import React from "react";
import type { BroadcastOverlay } from "../types";
import { Sparkles, Activity, ShieldAlert, Award, Compass } from "lucide-react";

interface BroadcastOverlayBannerProps {
  overlay: BroadcastOverlay | null;
}

export const BroadcastOverlayBanner: React.FC<BroadcastOverlayBannerProps> = ({ overlay }) => {
  if (!overlay || !overlay.is_active) return null;

  const getIcon = () => {
    switch (overlay.graphic_type) {
      case "lower_third":
        return <Award className="w-5 h-5 text-yellow-300 animate-bounce" />;
      case "speed_pass_badge":
        return <Activity className="w-5 h-5 text-[#00FF87]" />;
      case "momentum_gauge":
        return <ShieldAlert className="w-5 h-5 text-amber-400" />;
      case "player_spotlight":
        return <Sparkles className="w-5 h-5 text-[#04F5FF]" />;
      default:
        return <Compass className="w-5 h-5 text-purple-300" />;
    }
  };

  return (
    <div className="absolute bottom-6 left-6 right-6 md:right-auto md:max-w-md z-40 transition-all duration-300 transform translate-y-0 opacity-100">
      <div className="bg-[#1b0826]/95 backdrop-blur-md border-2 border-[#00FF87] rounded-xl p-3 shadow-[0_10px_25px_rgba(0,0,0,0.8)] text-white overflow-hidden relative">
        {/* Accent Glow Line */}
        <div
          className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-[#00FF87] via-[#04F5FF] to-[#FF2882]"
        />

        <div className="flex items-start gap-3">
          <div className="p-2 rounded-lg bg-black/40 border border-white/10 shrink-0">
            {getIcon()}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between gap-2">
              <span className="text-[11px] font-black uppercase tracking-wider text-[#00FF87] font-mono">
                {overlay.display_title}
              </span>
              <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-white/10 text-gray-300">
                LIVE ON-SCREEN
              </span>
            </div>

            <div className="flex items-baseline gap-2 mt-0.5 flex-wrap">
              <span className="font-extrabold text-sm text-white">
                {overlay.primary_metric}
              </span>
              {overlay.secondary_metric && (
                <span className="text-xs text-yellow-300 font-mono font-semibold">
                  • {overlay.secondary_metric}
                </span>
              )}
            </div>

            <p className="text-xs text-gray-300 mt-1 line-clamp-2 leading-relaxed">
              {overlay.detail_text}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
