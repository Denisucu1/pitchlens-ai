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
import { PlayerBroadcastCard } from "./components/PlayerBroadcastCard";
import { ControlChaosGauge } from "./components/ControlChaosGauge";
import { TacticalExplainabilityCard } from "./components/TacticalExplainabilityCard";
import { PersonalizedNarrativeFeed } from "./components/PersonalizedNarrativeFeed";
import { StatsPanel } from "./components/StatsPanel";
import { StudioRecapModal } from "./components/StudioRecapModal";
import { FanChatWidget } from "./components/FanChatWidget";
import { MatchTimelineBar } from "./components/MatchTimelineBar";
import { LeagueStandingsTable } from "./components/LeagueStandingsTable";
import { MatchweekDrawer } from "./components/MatchweekDrawer";
import { GoalAlertToast } from "./components/GoalAlertToast";
import { PlayerRatingsTable } from "./components/PlayerRatingsTable";
import { LiveMatchHub } from "./components/LiveMatchHub";
import { ChampionshipHub } from "./components/ChampionshipHub";
import { PlayerFocusSelector } from "./components/PlayerFocusSelector";
import { playNeuralCommentary, stopNeuralCommentary } from "./utils/neuralCommentator";

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
  const [activeTab, setActiveTab] = useState<"broadcast" | "players" | "standings">("broadcast");

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

  // High-Definition Neural Audio Commentary (Microsoft Cognitive Neural Voices)
  useEffect(() => {
    if (!isAudioEnabled || !payload) {
      stopNeuralCommentary();
      return;
    }

    const currentEvent = payload.latest_event;
    if (!currentEvent || currentEvent.event_id === lastSpokenEventId.current) return;

    // Selective commentary: Speak on pivotal moments (Goals, Dangerous Shots, Saves, Interceptions, Tackles)
    const isPivotal =
      currentEvent.event_type === "goal" ||
      (currentEvent.event_type === "shot" && currentEvent.shot_outcome !== "blocked") ||
      currentEvent.event_type === "save" ||
      currentEvent.event_type === "interception" ||
      currentEvent.event_type === "tackle";

    if (!isPivotal) return;

    lastSpokenEventId.current = currentEvent.event_id;

    // Pick narrative based on current persona
    let textToSpeak = payload.narrative.casual_fan_narrative;
    if (persona === "data_analyst") {
      textToSpeak = payload.narrative.data_analyst_narrative;
    } else if (persona === "player_focus" && payload.narrative.player_focus_narrative) {
      textToSpeak = payload.narrative.player_focus_narrative;
    }

    const isGoal = currentEvent.event_type === "goal";
    playNeuralCommentary(textToSpeak, language, isGoal);
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
            const data: LiveMatchPayload = msg.data;
            setPayload(data);
            if (data.focused_player) {
              setFocusedPlayer(data.focused_player);
            } else {
              setFocusedPlayer((prev) => {
                if (!prev) return null;
                const all = [...(data.home_players || []), ...(data.away_players || [])];
                const updated = all.find((p) => p.id === prev.id);
                return updated || prev;
              });
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

  const handleSelectPlayer = (p: PlayerProfile | null) => {
    setFocusedPlayer(p);
    if (p) {
      setPersona("player_focus");
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ action: "SET_PLAYER_FOCUS", player_id: p.id }));
      }
    } else {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ action: "SET_PLAYER_FOCUS", player_id: null }));
      }
    }
  };

  const handlePersonaChange = (newPersona: PersonaMode) => {
    setPersona(newPersona);
    if (newPersona === "player_focus" && !focusedPlayer) {
      // Auto-select key player (e.g. Saka #7 for Arsenal or Haaland #9 for City)
      const squad = payload?.home_players?.length ? payload.home_players : homeTeam?.players || [];
      const star =
        squad.find((p) => p.number === 7 || p.position === "RW" || p.position === "ST") ||
        squad[0];
      if (star) {
        handleSelectPlayer(star);
      }
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
      const res = await fetch("http://localhost:8000/api/match/switch-fixture", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ home_team_id: homeId, away_team_id: awayId }),
      });
      const data = await res.json();
      if (data && data.match_id) {
        setPayload(data);
        if (data.focused_player) {
          setFocusedPlayer(data.focused_player);
        }
      }
      // Refresh teams
      const teamRes = await fetch("http://localhost:8000/api/match/teams");
      const teamData = await teamRes.json();
      setHomeTeam(teamData.home_team);
      setAwayTeam(teamData.away_team);
      setActiveTab("broadcast"); // Focus camera on the newly selected match
    } catch (err) {
      console.error("Failed to switch fixture", err);
    }
  };

  const handleSelectTeamFromHub = (teamId: string) => {
    const match = payload?.matchweek_matches?.find(
      (m) => m.home_team_id === teamId || m.away_team_id === teamId
    );
    if (match) {
      handleSwitchFixture(match.home_team_id, match.away_team_id);
      setActiveTab("broadcast");
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
        setPersona={handlePersonaChange}
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
            {/* Left Column (Player Focus Selector, Pitch, Overlay, Timeline & Player Card) */}
            <section className="lg:col-span-7 flex flex-col gap-4">
              {/* Quick Interactive Player Focus Selector */}
              <PlayerFocusSelector
                homeTeam={homeTeam}
                awayTeam={awayTeam}
                homePlayers={payload?.home_players || homeTeam?.players || []}
                awayPlayers={payload?.away_players || awayTeam?.players || []}
                focusedPlayer={focusedPlayer}
                onSelectPlayer={handleSelectPlayer}
                persona={persona}
                onSetPersona={handlePersonaChange}
              />

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
                  passLinks={payload?.pass_links || []}
                  currentMinute={payload?.current_minute || 1}
                  period={payload?.latest_event?.period || "1H"}
                  homeGameState={payload?.home_game_state || "balanced"}
                  awayGameState={payload?.away_game_state || "balanced"}
                  scoreHome={payload?.score_home || 0}
                  scoreAway={payload?.score_away || 0}
                  controlVsChaosIndex={payload?.rhythm?.control_vs_chaos_index}
                />
              </div>

              {/* Dedicated Player Broadcast Card - Placed cleanly below pitch without covering turf */}
              {focusedPlayer && (
                <PlayerBroadcastCard
                  player={focusedPlayer}
                  team={focusedPlayer.team_id === homeTeam?.id ? homeTeam : awayTeam}
                  onClose={() => handleSelectPlayer(null)}
                />
              )}

              {/* On-Screen Graphic Overlay (Stage D) */}
              {payload?.active_overlay?.is_active && (
                <BroadcastOverlayBanner overlay={payload.active_overlay} />
              )}

              {/* 90-Minute Momentum Timeline Bar */}
              <MatchTimelineBar
                currentMinute={payload?.current_minute || 1}
                currentSecond={payload?.current_second || 0}
                moments={payload?.timeline_moments || []}
              />
            </section>

            {/* Right Column (AI Narrative Feed Side-by-Side with Pitch, plus Tactical Intelligence & Stats) */}
            <section className="lg:col-span-5 flex flex-col gap-4">
              {/* Real-time Narrative Stream (Stage E) - Prominently alongside pitch */}
              <PersonalizedNarrativeFeed
                narrative={payload?.narrative || null}
                persona={persona}
                latestEvent={payload?.latest_event || null}
                focusedPlayer={focusedPlayer}
              />

              {/* Explainability Engine (Stage C: Why moments matter) */}
              <TacticalExplainabilityCard insight={payload?.latest_insight || null} />

              {/* Game Rhythm & Control vs Chaos (Stage B) */}
              <ControlChaosGauge rhythm={payload?.rhythm || null} />

              {/* Aggregated Match Telemetry & Stats (Stage B) */}
              <StatsPanel
                statsHome={payload?.stats_home || null}
                statsAway={payload?.stats_away || null}
                homeTeam={homeTeam}
                awayTeam={awayTeam}
              />
            </section>
          </div>
        ) : activeTab === "players" ? (
          /* Live Player Ratings & Sofascore Stats View */
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <section className="lg:col-span-8">
              <PlayerRatingsTable
                homeTeam={homeTeam}
                awayTeam={awayTeam}
                homePlayers={payload?.home_players || homeTeam?.players || []}
                awayPlayers={payload?.away_players || awayTeam?.players || []}
                selectedPlayerId={focusedPlayer?.id}
                playerHeatmaps={payload?.player_heatmaps || {}}
                onSelectPlayer={(p) => {
                  handleSelectPlayer(p);
                }}
              />
            </section>

            <section className="lg:col-span-4 flex flex-col gap-5">
              {focusedPlayer ? (
                <PlayerBroadcastCard
                  player={focusedPlayer}
                  team={focusedPlayer.team_id === homeTeam?.id ? homeTeam : awayTeam}
                  onClose={() => handleSelectPlayer(null)}
                  variant="vertical"
                  onFocusOnPitch={() => setActiveTab("broadcast")}
                />
              ) : (
                <ControlChaosGauge rhythm={payload?.rhythm || null} />
              )}

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
          /* Live Standings & Hub View (Flashscore Style) */
          <div className="space-y-6">
            {/* Live Matches Hub with All 4 Concurrent Live Games */}
            <LiveMatchHub
              matches={payload?.matchweek_matches || []}
              activeHomeId={homeTeam?.id || "arsenal"}
              activeAwayId={awayTeam?.id || "mancity"}
              onSelectMatch={(hId, aId) => {
                handleSwitchFixture(hId, aId);
                setActiveTab("broadcast");
              }}
            />

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              <section className="lg:col-span-8">
                <LeagueStandingsTable
                  standings={payload?.league_standings || []}
                  currentHomeId={homeTeam?.id}
                  currentAwayId={awayTeam?.id}
                  matches={payload?.matchweek_matches || []}
                  onSelectMatch={(hId, aId) => {
                    handleSwitchFixture(hId, aId);
                    setActiveTab("broadcast");
                  }}
                />
              </section>

              <section className="lg:col-span-4 flex flex-col gap-5">
                {/* Official Premier League Championship Hub (Title Race, Leaders, Relegation) */}
                <ChampionshipHub
                  standings={payload?.league_standings || []}
                  matches={payload?.matchweek_matches || []}
                  onSelectTeamMatch={handleSelectTeamFromHub}
                />
              </section>
            </div>
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
