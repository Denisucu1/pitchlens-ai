import asyncio
from typing import Optional, Dict, Any, List
from collections import deque
from app.data.models import (
    LiveMatchPayload, MatchEvent, PlayerProfile, Language,
    TeamMatchStats, RhythmState, ExplainabilityInsight, AgentLog, PassLink
)
from app.data.synthetic_engine import SyntheticMatchEngine
from app.data.teams_data import get_premier_league_teams
from app.data.league_engine import PremierLeagueMatchweekEngine
from app.pipeline.stage_a_ingest import EventIngestionPipeline
from app.pipeline.stage_b_interpret import MatchInterpretationEngine
from app.pipeline.stage_c_explain import TacticalExplainabilityEngine
from app.pipeline.stage_d_render import BroadcastGraphicOverlayEngine
from app.pipeline.stage_e_personalize import PersonalizationStoryEngine
from app.config import settings

class PitchLensOrchestrator:
    """
    Master Multi-Agent Orchestrator executing the 5-Stage Pipeline:
    Coordinates communication and handoffs between:
    - 🎭 Orchestrator Agent (Task Dispatcher & State Coordinator)
    - ⚔️ Tactical Analyst Agent (Spatial & xG Model Reasoning)
    - 📝 Narrative Engine Agent (Persona & Multi-Language Generation)
    - 📺 Broadcast Graphics Agent (On-Screen Lower-Third Producer)
    - 🙋 Fan Interaction Agent (Context Grounding)
    """

    def __init__(self, home_team_id: str = "arsenal", away_team_id: str = "mancity", match_id: str = "EPL-2026-LIVE"):
        self.match_id = match_id
        self.home_team_id = home_team_id
        self.away_team_id = away_team_id
        
        self.engine = SyntheticMatchEngine(home_team_id=home_team_id, away_team_id=away_team_id, match_id=match_id)
        self.league_engine = PremierLeagueMatchweekEngine()
        
        # 5 Pipeline Stages
        self.stage_a = EventIngestionPipeline()
        self.stage_b = MatchInterpretationEngine(
            home_team_id=self.engine.home_team.id,
            away_team_id=self.engine.away_team.id
        )
        self.stage_c = TacticalExplainabilityEngine()
        self.stage_d = BroadcastGraphicOverlayEngine()
        self.stage_e = PersonalizationStoryEngine()

        # Multi-Agent Coordination Log (sliding window of last 8 handoffs)
        self.agent_logs: deque = deque(maxlen=8)

        # State tracking
        self.focused_player_id: Optional[str] = "ars_07"  # Default: Bukayo Saka
        self.current_language: Language = Language.EN
        self.is_paused: bool = False
        self.playback_speed: float = 1.0
        self.current_payload: Optional[LiveMatchPayload] = None
        self.score_home = 0
        self.score_away = 0
        self.history: List[LiveMatchPayload] = []

    def set_fixture(self, home_id: str, away_id: str):
        """Allows switching to any official Premier League fixture."""
        self.home_team_id = home_id
        self.away_team_id = away_id
        self.engine = SyntheticMatchEngine(home_team_id=home_id, away_team_id=away_id, match_id=f"EPL-{home_id.upper()}-{away_id.upper()}")
        self.stage_b = MatchInterpretationEngine(home_team_id=home_id, away_team_id=away_id)
        self.score_home = 0
        self.score_away = 0
        self.focused_player_id = self.engine.home_team.players[8].id if len(self.engine.home_team.players) > 8 else None
        self.agent_logs.clear()
        self.history.clear()
        return self.tick()

    def reset_match(self) -> LiveMatchPayload:
        """Resets the match to minute 0:00 for the current fixture."""
        self.engine = SyntheticMatchEngine(
            home_team_id=self.home_team_id,
            away_team_id=self.away_team_id,
            match_id=f"EPL-{self.home_team_id.upper()}-{self.away_team_id.upper()}"
        )
        self.stage_b = MatchInterpretationEngine(
            home_team_id=self.home_team_id,
            away_team_id=self.away_team_id
        )
        self.score_home = 0
        self.score_away = 0
        self.agent_logs.clear()
        self.history.clear()
        self.league_engine.init_matchweek()
        return self.tick()

    def set_focused_player(self, player_id: Optional[str]):
        self.focused_player_id = player_id

    def set_language(self, language: Language):
        self.current_language = language

    def get_focused_player(self) -> Optional[PlayerProfile]:
        if not self.focused_player_id:
            return None
        for p in self.engine.home_team.players + self.engine.away_team.players:
            if p.id == self.focused_player_id:
                return p
        return None

    def tick(self) -> LiveMatchPayload:
        """
        Executes one full cycle of the 5-Stage Multi-Agent Match Pipeline.
        """
        # 1. Ingestion (Stage A)
        raw_event = self.engine.generate_next_event()
        event = self.stage_a.process(raw_event)

        # Update scores if goal
        if event.event_type.value == "goal":
            if event.team_id == self.engine.home_team.id:
                self.score_home += 1
            else:
                self.score_away += 1

        time_str = f"{event.minute}:{event.second:02d}"

        # Agent Step 1: Orchestrator
        self.agent_logs.append(AgentLog(
            agent_name="🎭 Orchestrator",
            role="Dispatcher & Coordinator",
            message=f"Ingested {event.event_type.value.upper()} by {event.player.name} at {time_str}. Routing to Tactical & Graphics.",
            timestamp=time_str,
            status="handoff"
        ))

        # 2. Interpretation (Stage B)
        stats_h, stats_a, rhythm = self.stage_b.process_event(event)

        # 3. Explainability (Stage C - Tactical Agent)
        insight = self.stage_c.analyze_event(event, rhythm, stats_h, stats_a)
        if insight:
            self.agent_logs.append(AgentLog(
                agent_name="⚔️ Tactical Agent",
                role="Spatial & Formation Analyst",
                message=f"Detected pattern: '{insight.pattern_detected}'. Control Index: {rhythm.control_vs_chaos_index:.0f}%.",
                timestamp=time_str,
                status="alert"
            ))

        # 4. Render Overlays (Stage D - Graphics Producer Agent)
        focused_player = self.get_focused_player()
        overlay = self.stage_d.generate_overlay(event, rhythm, insight, focused_player)
        if overlay:
            self.agent_logs.append(AgentLog(
                agent_name="📺 Graphics Producer",
                role="Broadcast Overlay Engine",
                message=f"Deployed on-screen {overlay.graphic_type.value}: {overlay.primary_metric}.",
                timestamp=time_str,
                status="success"
            ))

        # 5. Personalize (Stage E - Narrative Engine Agent)
        narrative = self.stage_e.generate_narrative(
            event=event,
            rhythm=rhythm,
            focused_player=focused_player,
            language=self.current_language
        )
        self.agent_logs.append(AgentLog(
            agent_name="📝 Narrative Engine",
            role="Storyteller & Localizer",
            message=f"Synthesized live commentary in [{self.current_language.value.upper()}] for Casual Fan & Analyst.",
            timestamp=time_str,
            status="processing"
        ))

        # Synchronize featured match with the Premier League Matchweek Engine
        self.league_engine.sync_featured_match(
            home_id=self.engine.home_team.id,
            away_id=self.engine.away_team.id,
            score_h=self.score_home,
            score_a=self.score_away,
            minute=event.minute,
            is_finished=self.engine.is_finished
        )

        # Tick concurrent background matches in Matchweek 28
        self.league_engine.tick_background_matches(
            current_minute=event.minute,
            featured_home_id=self.engine.home_team.id,
            featured_away_id=self.engine.away_team.id
        )

        if self.league_engine.latest_goal_alert:
            self.agent_logs.append(AgentLog(
                agent_name="📢 Matchweek Desk",
                role="EPL Goal Alert",
                message=self.league_engine.latest_goal_alert.text,
                timestamp=time_str,
                status="alert"
            ))

        # Build Pass Links for Pass Network Visualizer
        pass_links_list: List[PassLink] = []
        for src_id, targets in self.engine.pass_matrix.items():
            for tgt_id, cnt in targets.items():
                if cnt >= 2:  # Only significant pass connections
                    pass_links_list.append(PassLink(source_player_id=src_id, target_player_id=tgt_id, count=cnt))

        standings = self.league_engine.compute_standings()
        matchweek_matches = self.league_engine.get_matchweek_summaries()

        payload = LiveMatchPayload(
            match_id=self.match_id,
            current_minute=event.minute,
            current_second=event.second,
            score_home=self.score_home,
            score_away=self.score_away,
            is_finished=self.engine.is_finished,
            is_half_time=self.engine.is_half_time,
            latest_event=event,
            stats_home=stats_h,
            stats_away=stats_a,
            rhythm=rhythm,
            active_overlay=overlay,
            latest_insight=insight,
            narrative=narrative,
            focused_player=focused_player,
            agent_logs=list(self.agent_logs),
            pass_links=pass_links_list,
            heatmap_points=self.engine.heatmap_cells,
            timeline_moments=self.engine.timeline_moments,
            home_players=self.engine.home_team.players,
            away_players=self.engine.away_team.players,
            league_standings=standings,
            matchweek_matches=matchweek_matches,
            latest_goal_alert=self.league_engine.latest_goal_alert
        )

        self.current_payload = payload
        self.history.append(payload)
        return payload

    async def generate_studio_recap(self, language: Language = Language.EN) -> Dict[str, Any]:
        """Generates an executive studio recap."""
        stats_h = self.stage_b.stats[self.engine.home_team.id]
        stats_a = self.stage_b.stats[self.engine.away_team.id]

        if language == Language.RO:
            title = f"Raport Oficial de Studio: {self.engine.home_team.name} {self.score_home} - {self.score_away} {self.engine.away_team.name}"
            summary = (
                f"O confruntare tactică spectaculoasă în Premier League. {self.engine.home_team.name} a menținut "
                f"{stats_h.possession_pct}% posesie și un total de {stats_h.total_xG:.2f} xG din {stats_h.total_shots} șuturi. "
                f"În replică, {self.engine.away_team.name} a generat {stats_a.total_xG:.2f} xG bazându-se pe tranziții rapide "
                f"și {stats_a.tackles_won} recuperări decisive."
            )
            key_takeaway = "Eficiența în finalizare și gestionarea pressing-ului în treimea neutră au decis duelul."
        elif language == Language.ES:
            title = f"Informe de Estudio: {self.engine.home_team.name} {self.score_home} - {self.score_away} {self.engine.away_team.name}"
            summary = (
                f"Duelo táctico de alto nivel en la Premier League. {self.engine.home_team.name} dominó la posesión con un "
                f"{stats_h.possession_pct}%, generando {stats_h.total_xG:.2f} xG en {stats_h.total_shots} disparos."
            )
            key_takeaway = "La precisión en el último tercio marcó la diferencia en las transiciones rápidas."
        else:
            title = f"Studio Match Intelligence: {self.engine.home_team.name} {self.score_home} - {self.score_away} {self.engine.away_team.name}"
            summary = (
                f"A high-octane Premier League tactical battle. {self.engine.home_team.name} held {stats_h.possession_pct}% possession "
                f"and produced {stats_h.total_xG:.2f} xG from {stats_h.total_shots} total attempts. "
                f"{self.engine.away_team.name} generated {stats_a.total_xG:.2f} xG through clinical direct counter-attacks "
                f"and {stats_a.tackles_won} won tackles."
            )
            key_takeaway = "Superior spatial dominance and rapid line-breaking distribution in the half-spaces proved decisive."

        return {
            "title": title,
            "score": f"{self.score_home} - {self.score_away}",
            "summary": summary,
            "key_takeaway": key_takeaway,
            "stats": {
                "home_possession": stats_h.possession_pct,
                "away_possession": stats_a.possession_pct,
                "home_xg": stats_h.total_xG,
                "away_xg": stats_a.total_xG,
                "home_shots": stats_h.total_shots,
                "away_shots": stats_a.total_shots,
                "home_passes": stats_h.total_passes,
                "away_passes": stats_a.total_passes
            }
        }
