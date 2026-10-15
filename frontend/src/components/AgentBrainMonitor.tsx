import React from "react";
import type { AgentLog } from "../types";
import { Network, Cpu, ArrowRight, ShieldAlert, CheckCircle, RefreshCw } from "lucide-react";

interface AgentBrainMonitorProps {
  logs: AgentLog[];
}

export const AgentBrainMonitor: React.FC<AgentBrainMonitorProps> = ({ logs }) => {
  const getStatusBadge = (status: AgentLog["status"]) => {
    switch (status) {
      case "handoff":
        return (
          <span className="flex items-center gap-1 text-[9px] font-mono text-cyan-400 bg-cyan-950/60 border border-cyan-800/50 px-1.5 py-0.5 rounded">
            <ArrowRight className="w-2.5 h-2.5" /> HANDOFF
          </span>
        );
      case "alert":
        return (
          <span className="flex items-center gap-1 text-[9px] font-mono text-yellow-400 bg-yellow-950/60 border border-yellow-800/50 px-1.5 py-0.5 rounded">
            <ShieldAlert className="w-2.5 h-2.5" /> TACTICAL
          </span>
        );
      case "success":
        return (
          <span className="flex items-center gap-1 text-[9px] font-mono text-[#00FF87] bg-emerald-950/60 border border-emerald-800/50 px-1.5 py-0.5 rounded">
            <CheckCircle className="w-2.5 h-2.5" /> DEPLOYED
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1 text-[9px] font-mono text-purple-400 bg-purple-950/60 border border-purple-800/50 px-1.5 py-0.5 rounded">
            <RefreshCw className="w-2.5 h-2.5 animate-spin" /> ACTIVE
          </span>
        );
    }
  };

  return (
    <div className="bg-[#1b0826] border-2 border-[#00FF87]/50 rounded-2xl p-4 text-white shadow-2xl flex flex-col gap-3 relative overflow-hidden">
      {/* Glow Accent */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-[#00FF87]/15 to-transparent pointer-events-none" />

      {/* Header */}
      <div className="flex items-center justify-between border-b border-[#38003c] pb-2.5">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-[#00FF87]/10 text-[#00FF87]">
            <Network className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-extrabold text-xs uppercase tracking-wider text-gray-200">
              Agent Brain Activity Monitor
            </h3>
            <span className="text-[10px] text-gray-400 font-mono">
              Semantic Kernel 1.45 Multi-Agent Orchestration
            </span>
          </div>
        </div>
        <span className="text-[9px] font-mono font-bold px-2 py-0.5 rounded bg-emerald-950 text-[#00FF87] border border-[#00FF87]/40 flex items-center gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-[#00FF87] animate-ping" />
          5 AGENTS LIVE
        </span>
      </div>

      {/* Agent Topology Flow Bar */}
      <div className="bg-[#100418] border border-purple-950 rounded-xl p-2.5 grid grid-cols-4 gap-1 text-center text-[10px] font-mono">
        <div className="p-1 rounded bg-black/40 border border-purple-900/50">
          <span className="block font-bold text-cyan-300">🎭 Orchestrator</span>
          <span className="text-[8px] text-gray-500">Event Ingest</span>
        </div>
        <div className="p-1 rounded bg-black/40 border border-purple-900/50">
          <span className="block font-bold text-yellow-300">⚔️ Tactical</span>
          <span className="text-[8px] text-gray-500">xG & Shape</span>
        </div>
        <div className="p-1 rounded bg-black/40 border border-purple-900/50">
          <span className="block font-bold text-[#FF2882]">📝 Narrative</span>
          <span className="text-[8px] text-gray-500">Multi-Persona</span>
        </div>
        <div className="p-1 rounded bg-black/40 border border-purple-900/50">
          <span className="block font-bold text-[#00FF87]">📺 Graphics</span>
          <span className="text-[8px] text-gray-500">Overlays</span>
        </div>
      </div>

      {/* Live Agent Handoff Stream */}
      <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
        {logs.length === 0 ? (
          <div className="py-6 text-center text-xs text-gray-500 font-mono">
            Synchronizing agent network...
          </div>
        ) : (
          logs.map((log, idx) => (
            <div
              key={idx}
              className="bg-[#100418] border border-purple-900/50 rounded-xl p-2.5 text-xs transition-all hover:border-[#00FF87]/40"
            >
              <div className="flex items-center justify-between gap-2 mb-1">
                <div className="flex items-center gap-1.5">
                  <Cpu className="w-3 h-3 text-[#04F5FF]" />
                  <span className="font-extrabold text-[11px] text-white">
                    {log.agent_name}
                  </span>
                  <span className="text-[9px] text-gray-400">({log.role})</span>
                </div>
                <div className="flex items-center gap-1.5">
                  {getStatusBadge(log.status)}
                  <span className="text-[9px] font-mono text-gray-500">{log.timestamp}</span>
                </div>
              </div>
              <p className="text-gray-300 text-[11px] leading-relaxed pl-4 border-l-2 border-purple-800/60">
                {log.message}
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
