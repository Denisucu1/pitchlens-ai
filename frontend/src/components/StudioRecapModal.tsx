import React, { useState, useEffect } from "react";
import type { Language } from "../types";
import { X, Trophy, Sparkles, Loader2 } from "lucide-react";

interface StudioRecapModalProps {
  isOpen: boolean;
  onClose: () => void;
  language: Language;
}

export const StudioRecapModal: React.FC<StudioRecapModalProps> = ({
  isOpen,
  onClose,
  language,
}) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      fetch(`http://localhost:8000/api/match/recap?lang=${language}`)
        .then((res) => res.json())
        .then((d) => {
          setData(d);
          setLoading(false);
        })
        .catch((err) => {
          console.error("Failed to fetch recap", err);
          setLoading(false);
        });
    }
  }, [isOpen, language]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
      <div className="bg-[#1b0826] border-2 border-[#00FF87] rounded-3xl max-w-2xl w-full p-6 text-white shadow-[0_0_50px_rgba(0,255,135,0.2)] relative overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 text-gray-400 hover:text-white p-1 rounded-full bg-black/40 hover:bg-[#38003c]"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Modal Header */}
        <div className="flex items-center gap-3 border-b border-[#38003c] pb-4 mb-4">
          <div className="p-2.5 rounded-xl bg-gradient-to-br from-[#00FF87] to-[#04F5FF] text-[#1b0826]">
            <Trophy className="w-6 h-6" />
          </div>
          <div>
            <span className="text-[10px] font-mono font-bold text-[#00FF87] uppercase tracking-widest">
              AI-Generated Studio Intelligence
            </span>
            <h2 className="text-xl font-black text-white">
              {data ? data.title : "Executive Match Recap"}
            </h2>
          </div>
        </div>

        {loading ? (
          <div className="py-16 flex flex-col items-center justify-center gap-3 text-gray-400">
            <Loader2 className="w-8 h-8 animate-spin text-[#00FF87]" />
            <p className="text-sm font-mono">Synthesizing match intelligence...</p>
          </div>
        ) : data ? (
          <div className="space-y-4">
            <div className="bg-[#100418] border border-purple-900/60 rounded-2xl p-4">
              <span className="text-[11px] font-bold text-[#04F5FF] uppercase font-mono block mb-1">
                Executive Studio Breakdown
              </span>
              <p className="text-sm text-gray-200 leading-relaxed">
                {data.summary}
              </p>
            </div>

            <div className="bg-[#100418] border border-yellow-500/30 rounded-2xl p-4 flex items-start gap-3">
              <Sparkles className="w-5 h-5 text-yellow-400 shrink-0 mt-0.5" />
              <div>
                <span className="text-[11px] font-bold text-yellow-400 uppercase font-mono block">
                  Pivotal Tactical Takeaway
                </span>
                <p className="text-xs text-gray-300 mt-0.5">
                  {data.key_takeaway}
                </p>
              </div>
            </div>

            {/* Quick Stats Grid */}
            <div className="grid grid-cols-4 gap-2 text-center text-xs font-mono">
              <div className="bg-black/40 p-2.5 rounded-xl border border-white/5">
                <span className="text-gray-400 text-[10px] block">HOME xG</span>
                <span className="text-sm font-bold text-[#00FF87]">{data.stats.home_xg.toFixed(2)}</span>
              </div>
              <div className="bg-black/40 p-2.5 rounded-xl border border-white/5">
                <span className="text-gray-400 text-[10px] block">AWAY xG</span>
                <span className="text-sm font-bold text-[#04F5FF]">{data.stats.away_xg.toFixed(2)}</span>
              </div>
              <div className="bg-black/40 p-2.5 rounded-xl border border-white/5">
                <span className="text-gray-400 text-[10px] block">HOME POSS</span>
                <span className="text-sm font-bold text-white">{data.stats.home_possession}%</span>
              </div>
              <div className="bg-black/40 p-2.5 rounded-xl border border-white/5">
                <span className="text-gray-400 text-[10px] block">AWAY POSS</span>
                <span className="text-sm font-bold text-white">{data.stats.away_possession}%</span>
              </div>
            </div>
          </div>
        ) : null}

        <div className="mt-6 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl text-xs font-bold bg-[#00FF87] text-[#1b0826] hover:bg-emerald-400 transition-colors shadow-lg"
          >
            Close Recap
          </button>
        </div>
      </div>
    </div>
  );
};
