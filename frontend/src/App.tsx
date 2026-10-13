import { useState, useEffect, useRef } from "react";
import type {
  LiveMatchPayload,
  PersonaMode,
  Language,
  PlayerProfile,
  TeamProfile,
} from "./types";
import { Navbar } from "./components/Navbar";
import { BroadcastPitch } from "./components/BroadcastPitch";
import { BroadcastOverlayBanner } from "./components/BroadcastOverlayBanner";
import { ControlChaosGauge } from "./components/ControlChaosGauge";
import { TacticalExplainabilityCard } from "./components/TacticalExplainabilityCard";
import { PersonalizedNarrativeFeed } from "./components/PersonalizedNarrativeFeed";
import { StatsPanel } from "./components/StatsPanel";
import { StudioRecapModal } from "./components/StudioRecapModal";
import { FanChatWidget } from "./components/FanChatWidget";

export function App() {
  const [payload, setPayload] = useState<LiveMatchPayload | null>(null);
  const [homeTeam, setHomeTeam] = useState<TeamProfile | null>(null);
  const [awayTeam, setAwayTeam] = useState<TeamProfile | null>(null);
  const [persona, setPersona] = useState<PersonaMode>("casual_fan");
  const [language, setLanguage] = useState<Language>("en");
  const [isPaused, setIsPaused] = useState(false);
  const [speed, setSpeed] = useState(1);
  const [showRecap, setShowRecap] = useState(false);
  const [focusedPlayer, setFocusedPlayer] = useState<PlayerProfile | null>(null);

  const wsRef = useRef<WebSocket | null>(null);

  // Fetch initial teams
  useEffect(() => {
    fetch("http://localhost:8000/api/match/teams")
      .then((res) => res.json())
      .then((data) => {
        setHomeTeam(data.home_team);
        setAwayTeam(data.away_team);
        // Default focus: first winger
        if (data.home_team?.players?.length > 8) {
          setFocusedPlayer(data.home_team.players[8]);
        }
      })
      .catch((err) => console.error("Could not fetch teams", err));
  }, []);

  // Connect WebSocket
  useEffect(() => {
    let reconnectTimeout: any;

    const connectWs = () => {
      const ws = new WebSocket("ws://localhost:8000/ws/live");
      wsRef.current = ws;

      ws.onopen = () => {
        console.log("[WebSocket] Connected to PitchLens AI live feed.");
      };

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === "MATCH_TICK" || msg.type === "INITIAL_STATE") {
            setPayload(msg.data);
            if (msg.data.focused_player) {
              setFocusedPlayer(msg.data.focused_player);
            }
          }
        } catch (e) {
          console.error("Error parsing WebSocket tick", e);
        }
      };

      ws.onclose = () => {
        console.log("[WebSocket] Disconnected. Reconnecting in 2s...");
        reconnectTimeout = setTimeout(connectWs, 2000);
      };

      ws.onerror = (err) => {
        console.error("[WebSocket Error]", err);
        ws.close();
      };
    };

    connectWs();

    return () => {
      clearTimeout(reconnectTimeout);
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  // Control handlers
  const togglePause = () => {
    const next = !isPaused;
    setIsPaused(next);
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: next ? "PAUSE" : "RESUME" }));
    }
  };

  const handleSpeedChange = (newSpeed: number) => {
    setSpeed(newSpeed);
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: "SET_SPEED", speed: newSpeed }));
    }
  };

  const handleSelectPlayer = (p: PlayerProfile) => {
    setFocusedPlayer(p);
    setPersona("player_focus");
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: "SET_PLAYER_FOCUS", player_id: p.id }));
    }
  };

  const handleLanguageChange = (l: Language) => {
    setLanguage(l);
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: "SET_LANGUAGE", language: l }));
    }
  };

  return (
    <div className="min-h-screen bg-[#0c0314] text-white flex flex-col font-sans selection:bg-[#00FF87] selection:text-black">
      {/* Top Bar */}
      <Navbar
        payload={payload}
        persona={persona}
        setPersona={setPersona}
        language={language}
        setLanguage={handleLanguageChange}
        isPaused={isPaused}
        togglePause={togglePause}
        speed={speed}
        setSpeed={handleSpeedChange}
        onOpenRecap={() => setShowRecap(true)}
      />

      {/* Main Studio Console */}
      <main className="flex-1 p-4 md:p-6 max-w-7xl mx-auto w-full grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column (Pitch & Narratives) */}
        <section className="lg:col-span-8 flex flex-col gap-6">
          {/* Live Pitch with Overlay */}
          <div className="relative">
            <BroadcastPitch
              latestEvent={payload?.latest_event || null}
              homeTeam={homeTeam}
              awayTeam={awayTeam}
              focusedPlayer={focusedPlayer}
              onSelectPlayer={handleSelectPlayer}
            />
            {/* On-Screen Graphic Overlay (Stage D) */}
            <BroadcastOverlayBanner overlay={payload?.active_overlay || null} />
          </div>

          {/* Real-time Narrative Stream (Stage E) */}
          <PersonalizedNarrativeFeed
            narrative={payload?.narrative || null}
            persona={persona}
            latestEvent={payload?.latest_event || null}
          />
        </section>

        {/* Right Column (Tactical Intelligence & Stats) */}
        <section className="lg:col-span-4 flex flex-col gap-6">
          {/* Game Rhythm & Control vs Chaos (Stage B) */}
          <ControlChaosGauge rhythm={payload?.rhythm || null} />

          {/* Explainability Engine (Stage C: Why moments matter) */}
          <TacticalExplainabilityCard insight={payload?.latest_insight || null} />

          {/* Aggregated Match Telemetry & Stats (Stage B) */}
          <StatsPanel
            statsHome={payload?.stats_home || null}
            statsAway={payload?.stats_away || null}
            homeTeam={homeTeam}
            awayTeam={awayTeam}
          />
        </section>
      </main>

      {/* Studio Recap Modal */}
      <StudioRecapModal
        isOpen={showRecap}
        onClose={() => setShowRecap(false)}
        language={language}
      />

      {/* Fan AI Conversational Copilot */}
      <FanChatWidget persona={persona} language={language} />
    </div>
  );
}

export default App;
