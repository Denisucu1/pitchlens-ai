import React, { useState } from "react";
import type { PersonaMode, Language } from "../types";
import { MessageSquareText, Send, Bot, Sparkles, ChevronDown } from "lucide-react";

interface FanChatWidgetProps {
  persona: PersonaMode;
  language: Language;
}

interface ChatMessage {
  id: string;
  sender: "user" | "ai";
  text: string;
}

export const FanChatWidget: React.FC<FanChatWidgetProps> = ({ persona, language }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "m_1",
      sender: "ai",
      text: "👋 Welcome to PitchLens AI Copilot! Ask me anything about tactical patterns, player sprint telemetry, or why moments matter.",
    },
  ]);

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg: ChatMessage = {
      id: `u_${Date.now()}`,
      sender: "user",
      text: input,
    };
    setMessages((prev) => [...prev, userMsg]);
    const query = input;
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/api/match/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: query,
          mode: persona,
          language: language,
        }),
      });
      const data = await res.json();
      const aiMsg: ChatMessage = {
        id: `ai_${Date.now()}`,
        sender: "ai",
        text: data.answer,
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: `ai_${Date.now()}`,
          sender: "ai",
          text: "Tactical data stream momentarily unavailable. Please retry in a moment.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
      {/* Expanded Chat Box */}
      {isOpen && (
        <div className="w-80 md:w-96 h-[440px] bg-[#1b0826] border-2 border-[#00FF87] rounded-3xl shadow-[0_10px_35px_rgba(0,0,0,0.9)] flex flex-col overflow-hidden mb-3 animate-in fade-in slide-in-from-bottom-5 duration-200">
          {/* Header */}
          <div className="bg-[#100418] border-b border-[#38003c] p-3.5 flex items-center justify-between text-white">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-[#00FF87] text-[#1b0826] flex items-center justify-center font-bold text-sm">
                <Bot className="w-4 h-4" />
              </div>
              <div>
                <h4 className="font-extrabold text-xs">PitchLens AI Companion</h4>
                <span className="text-[9px] text-[#00FF87] font-mono flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#00FF87] animate-pulse" />
                  Grounded on live match feed
                </span>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-gray-400 hover:text-white p-1 rounded-full hover:bg-white/10"
            >
              <ChevronDown className="w-4 h-4" />
            </button>
          </div>

          {/* Messages Feed */}
          <div className="flex-1 overflow-y-auto p-3 space-y-2.5 text-xs">
            {messages.map((m) => (
              <div
                key={m.id}
                className={`flex ${m.sender === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-3 py-2 leading-relaxed ${
                    m.sender === "user"
                      ? "bg-[#FF2882] text-white rounded-br-sm"
                      : "bg-[#100418] border border-purple-900/60 text-gray-200 rounded-bl-sm"
                  }`}
                >
                  {m.text}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-[#100418] border border-purple-900/60 text-gray-400 rounded-2xl px-3 py-2 text-[11px] font-mono flex items-center gap-1.5">
                  <Sparkles className="w-3 h-3 text-[#00FF87] animate-spin" />
                  Consulting match intelligence...
                </div>
              </div>
            )}
          </div>

          {/* Quick Prompts */}
          <div className="px-3 py-1.5 bg-[#100418]/60 border-t border-purple-950 flex gap-1.5 overflow-x-auto text-[10px] text-gray-300">
            <button
              onClick={() => {
                setInput("Why does this moment matter?");
              }}
              className="px-2 py-0.5 rounded-full bg-purple-900/40 hover:bg-purple-800 border border-purple-800 whitespace-nowrap"
            >
              Why it matters?
            </button>
            <button
              onClick={() => {
                setInput("Who is the top performer right now?");
              }}
              className="px-2 py-0.5 rounded-full bg-purple-900/40 hover:bg-purple-800 border border-purple-800 whitespace-nowrap"
            >
              Top performer?
            </button>
          </div>

          {/* Input Form */}
          <form onSubmit={handleSend} className="p-2.5 bg-[#100418] border-t border-[#38003c] flex items-center gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask anything about the match..."
              className="flex-1 bg-black/40 border border-purple-900/60 rounded-xl px-3 py-2 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-[#00FF87]"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="p-2 rounded-xl bg-[#00FF87] text-[#1b0826] hover:bg-emerald-400 disabled:opacity-50 transition-colors shrink-0"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      )}

      {/* Floating Pill Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 bg-gradient-to-r from-[#00FF87] to-[#04F5FF] text-[#1b0826] font-black px-4 py-3 rounded-full shadow-[0_8px_25px_rgba(0,255,135,0.4)] hover:scale-105 active:scale-95 transition-all text-xs tracking-wide"
      >
        <MessageSquareText className="w-4 h-4" />
        <span>Ask PitchLens AI</span>
      </button>
    </div>
  );
};
