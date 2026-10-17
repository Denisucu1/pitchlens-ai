import { useState, useEffect, useRef } from "react";
import type {
  LiveMatchPayload,
  PersonaMode,
  Language,
  PlayerProfile,
  TeamProfile,
  ClubSummary,
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
import { AgentBrainMonitor } from "./components/AgentBrainMonitor";
import { MatchTimelineBar } from "./components/MatchTimelineBar";
import { LeagueStandingsTable } from "./components/LeagueStandingsTable";
import { MatchweekDrawer } from "./components/MatchweekDrawer";
import { GoalAlertToast } from "./components/GoalAlertToast";

export function App() {
  const [payload, setPayload] = useState<LiveMatchPayload | null>(null);
  const [homeTeam, setHomeTeam] = useState<TeamProfile | null>(null);
  const [awayTeam, setAwayTeam] = useState<TeamProfile | null>(null);
  const [clubs, setClubs] = useState<ClubSummary[]>([]);
  const [persona, setPersona] = useState<PersonaMode>("casual_fan");
  const [language, setLanguage] = useState<Language>("en");
  const [isPaused, setIsPaused] = useState(false);
  const [speed, setSpeed] = useState(1);
  const [showRecap, setShowRecap] = useState(false);
  const [focusedPlayer, setFocusedPlayer] = useState<PlayerProfile | null>(null);
  const [isAudioEnabled, setIsAudioEnabled] = useState(false);
  const [activeTab, setActiveTab] = useState<"broadcast" | "standings">("broadcast");

  const wsRef = useRef<WebSocket | null>(null);
  const lastSpokenEventId = useRef<string>("");

  // Fetch initial teams and available clubs
  useEffect(() => {
    fetch("http://localhost:8000/api/match/teams")
      .then((res) => res.json())
      .then((data) => {
        setHomeTeam(data.home_team);
        setAwayTeam(data.away_team);
        if (data.home_team?.players?.length > 8) {
          setFocusedPlayer(data.home_team.players[8]);
        }
      })
      .catch((err) => console.error("Could not fetch teams", err));

    fetch("http://localhost:8000/api/match/clubs")
      .then((res) => res.json())
      .then((data) => {
        if (data.clubs) setClubs(data.clubs);
      })
      .catch((err) => console.error("Could not fetch clubs", err));
  }, []);

  // Web Speech Audio Voice Commentary Synthesis (Calibrated TV Commentator Logic)
  useEffect(() => {
    if (!isAudioEnabled || !payload || !window.speechSynthesis) return;

    const currentEvent = payload.latest_event;
    if (currentEvent.event_id === lastSpokenEventId.current) return;

    // Is it a pivotal event (Goal, Shot, Tackle, High-difficulty pass)?
    const isPivotal = currentEvent.event_type === "goal" || currentEvent.event_type === "shot" || currentEvent.event_type === "tackle" || (currentEvent.pass_difficulty_rating && currentEvent.pass_difficulty_rating > 0.45);
    
    // In standard build-up, only commentate occasionally to avoid non-stop chatter
    const isBuildUpComment = (payload.current_second % 8 === 0);

    if (!isPivotal && !isBuildUpComment) return;

    // If commentator is already speaking, do NOT interrupt unless it's a GOAL!
    if (window.speechSynthesis.speaking && currentEvent.event_type !== "goal") {
      return;
    }

    lastSpokenEventId.current = currentEvent.event_id;

    // Pick narrative based on current persona
    let textToSpeak = payload.narrative.casual_fan_narrative;
    if (persona === "data_analyst") {
      textToSpeak = payload.narrative.data_analyst_narrative;
    } else if (persona === "player_focus" && payload.narrative.player_focus_narrative) {
      textToSpeak = payload.narrative.player_focus_narrative;
    }

    // Strip emojis and bracketed technical tags for clean audio speech
    const cleanText = textToSpeak
      .replace(/\[.*?\]/g, "")
      .replace(/[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}⭐⚡🔥🛡️⚽👀🎯]/gu, "")
      .trim();

    if (!cleanText) return;

    if (currentEvent.event_type === "goal") {
      window.speechSynthesis.cancel(); // Interrupt immediately for a goal!
    }

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.0;
    utterance.pitch = currentEvent.event_type === "goal" ? 1.15 : 1.0;

    const targetLangCode = language === "ro" ? "ro-RO" : language === "es" ? "es-ES" : "en-GB";
    utterance.lang = targetLangCode;

    // Select suitable voice if installed in browser
    const voices = window.speechSynthesis.getVoices();
    const matchedVoice = voices.find((v) =>
      language === "ro" ? (v.lang.startsWith("ro") || v.name.toLowerCase().includes("romanian") || v.name.toLowerCase().includes("andrei") || v.name.toLowerCase().includes("maria")) :
      language === "es" ? (v.lang.startsWith("es") || v.name.toLowerCase().includes("spanish")) :
      (v.lang.startsWith("en") || v.name.toLowerCase().includes("english"))
    );

    if (matchedVoice) {
      utterance.voice = matchedVoice;
    }

    window.speechSynthesis.speak(utterance);
  }, [payload, isAudioEnabled, persona, language]);

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

  const handleSwitchFixture = async (homeId: string, awayId: string) => {
    try {
      await fetch("http://localhost:8000/api/match/switch-fixture", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ home_team_id: homeId, away_team_id: awayId }),
      });
      // Refresh teams
      const res = await fetch("http://localhost:8000/api/match/teams");
      const data = await res.json();
      setHomeTeam(data.home_team);
      setAwayTeam(data.away_team);
      setActiveTab("broadcast"); // Focus camera on the newly selected match
    } catch (err) {
      console.error("Failed to switch fixture", err);
    }
  };

  const handleResetMatch = async () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: "RESET" }));
    } else {
      try {
        const res = await fetch("http://localhost:8000/api/match/reset", { method: "POST" });
        const data = await res.json();
        setPayload(data);
      } catch (err) {
        console.error("Failed to reset match", err);
      }
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
        isAudioEnabled={isAudioEnabled}
        toggleAudio={() => setIsAudioEnabled(!isAudioEnabled)}
        clubs={clubs}
        onSwitchFixture={handleSwitchFixture}
        onResetMatch={handleResetMatch}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
      />

      {/* Matchweek 28 Concurrent Fixtures Bar */}
      <div className="max-w-7xl mx-auto w-full px-4 md:px-6 pt-4">
        <MatchweekDrawer
          matches={payload?.matchweek_matches || []}
          activeHomeId={homeTeam?.id || "arsenal"}
          activeAwayId={awayTeam?.id || "mancity"}
          onSelectMatch={handleSwitchFixture}
        />
      </div>

      {/* Main Content Area */}
      <main className="flex-1 p-4 md:p-6 max-w-7xl mx-auto w-full">
        {activeTab === "broadcast" ? (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left Column (Pitch, Timeline & Narratives) */}
            <section className="lg:col-span-8 flex flex-col gap-5">
              {/* Live Pitch with Overlay */}
              <div className="relative">
                <BroadcastPitch
                  latestEvent={payload?.latest_event || null}
                  homeTeam={homeTeam}
                  awayTeam={awayTeam}
                  homePlayers={payload?.home_players}
                  awayPlayers={payload?.away_players}
                  focusedPlayer={focusedPlayer}
                  onSelectPlayer={handleSelectPlayer}
                  playerHeatmaps={payload?.player_heatmaps || {}}
                  passLinks={payload?.pass_links || []}
                  currentMinute={payload?.current_minute || 1}
                  period={payload?.latest_event?.period || "1H"}
                />
                {/* On-Screen Graphic Overlay (Stage D) */}
                <BroadcastOverlayBanner overlay={payload?.active_overlay || null} />
              </div>

              {/* 90-Minute Momentum Timeline Bar */}
              <MatchTimelineBar
                currentMinute={payload?.current_minute || 1}
                currentSecond={payload?.current_second || 0}
                moments={payload?.timeline_moments || []}
              />

              {/* Real-time Narrative Stream (Stage E) */}
              <PersonalizedNarrativeFeed
                narrative={payload?.narrative || null}
                persona={persona}
                latestEvent={payload?.latest_event || null}
              />

              {/* Agent Brain Activity Monitor (Multi-Agent Orchestration) */}
              <AgentBrainMonitor logs={payload?.agent_logs || []} />
            </section>

            {/* Right Column (Tactical Intelligence & Stats) */}
            <section className="lg:col-span-4 flex flex-col gap-5">
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
          </div>
        ) : (
          /* Live Standings View (Flashscore Style) */
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <section className="lg:col-span-8">
              <LeagueStandingsTable
                standings={payload?.league_standings || []}
                currentHomeId={homeTeam?.id}
                currentAwayId={awayTeam?.id}
              />
            </section>

            <section className="lg:col-span-4 flex flex-col gap-5">
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
          </div>
        )}
      </main>

      {/* Floating Premier League Goal Alert Toast */}
      <GoalAlertToast alert={payload?.latest_goal_alert} />

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
