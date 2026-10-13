import React from "react";
import type { ExplainabilityInsight } from "../types";
import { BrainCircuit, CheckCircle2 } from "lucide-react";

interface TacticalExplainabilityCardProps {
  insight: ExplainabilityInsight | null;
}

export const TacticalExplainabilityCard: React.FC<TacticalExplainabilityCardProps> = ({ insight }) => {
  if (!insight) {
    return (
      <div className="bg-[#1b0826] border border-[#38003c] rounded-2xl p-4 text-white shadow-xl flex items-center justify-center min-h-[140px] text-gray-500 text-xs italic">
        Awaiting pivotal tactical inflection point...
      </div>
    );
  }

  return (
    <div className="bg-[#1b0826] border-2 border-purple-800/80 rounded-2xl p-4 text-white shadow-xl flex flex-col gap-2.5 relative overflow-hidden">
      {/* Decorative gradient corner */}
      <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-bl from-[#00FF87]/10 to-transparent pointer-events-none" />

      {/* Header */}
      <div className="flex items-center justify-between border-b border-[#38003c] pb-2">
        <div className="flex items-center gap-2">
          <BrainCircuit className="w-4 h-4 text-[#04F5FF]" />
          <h3 className="font-black text-xs uppercase tracking-wider text-gray-200">
            Explainable Match Intelligence
          </h3>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-[#00FF87] border border-[#00FF87]/40 font-bold">
          Why It Matters
        </span>
      </div>

      {/* Title & Pattern */}
      <div>
        <h4 className="font-extrabold text-sm text-yellow-300">
          {insight.title}
        </h4>
        <span className="inline-block mt-0.5 text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-purple-900/60 text-[#04F5FF] border border-cyan-800/40">
          Pattern: {insight.pattern_detected}
        </span>
      </div>

      {/* Deep Explanation */}
      <div className="bg-[#100418] border border-purple-950 rounded-xl p-3 text-xs text-gray-300 space-y-2 leading-relaxed">
        <p>
          <strong className="text-white">Why it matters:</strong> {insight.why_it_matters}
        </p>
        <p className="text-gray-400 border-t border-purple-900/40 pt-1.5">
          <strong className="text-gray-300">Tactical Shift:</strong> {insight.tactical_shift_explanation}
        </p>
      </div>

      {/* Contributing Factors */}
      {insight.key_contributing_factors.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-1">
          {insight.key_contributing_factors.map((factor, idx) => (
            <span
              key={idx}
              className="text-[10px] bg-black/40 text-gray-300 border border-white/10 px-2 py-0.5 rounded-full flex items-center gap-1 font-mono"
            >
              <CheckCircle2 className="w-2.5 h-2.5 text-[#00FF87]" />
              {factor}
            </span>
          ))}
        </div>
      )}
    </div>
  );
};
