import asyncio
from typing import Optional, Dict, Any, List
from app.data.models import (
    LiveMatchPayload, MatchEvent, PlayerProfile, Language,
    TeamMatchStats, RhythmState, ExplainabilityInsight
)
from app.data.synthetic_engine import SyntheticMatchEngine
from app.pipeline.stage_a_ingest import EventIngestionPipeline
from app.pipeline.stage_b_interpret import MatchInterpretationEngine
from app.pipeline.stage_c_explain import TacticalExplainabilityEngine
from app.pipeline.stage_d_render import BroadcastGraphicOverlayEngine
from app.pipeline.stage_e_personalize import PersonalizationStoryEngine
from app.config import settings

class PitchLensOrchestrator:
    """
    Master Orchestration Engine coordinating the 5-Stage Pipeline:
    Stage A (Ingest) -> Stage B (Interpret) -> Stage C (Explain) -> Stage D (Render) -> Stage E (Personalize)
    Maintains shared live match state, active overlays, and focused player tracking.
    """
    def __init__(self, match_id: str = "PL-SYNTH-2026-01"):
        self.match_id = match_id
        self.engine = SyntheticMatchEngine(match_id=match_id)
        
        # 5 Pipeline Stages
        self.stage_a = EventIngestionPipeline()
        self.stage_b = MatchInterpretationEngine(
            home_team_id=self.engine.home_team.id,
            away_team_id=self.engine.away_team.id
        )
        self.stage_c = TacticalExplainabilityEngine()
        self.stage_d = BroadcastGraphicOverlayEngine()
        self.stage_e = PersonalizationStoryEngine()
        
        # State tracking
        self.focused_player_id: Optional[str] = "can_07"  # Default: Bukayo Smith (London Cannons RW)
        self.current_language: Language = Language.EN
        self.is_paused: bool = False
        self.playback_speed: float = 1.0
        self.current_payload: Optional[LiveMatchPayload] = None
        self.score_home = 0
        self.score_away = 0
        self.history: List[LiveMatchPayload] = []

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
        Executes one full cycle of the 5-Stage Match Pipeline.
        """
        # 1. Generate & Ingest (Stage A)
        raw_event = self.engine.generate_next_event()
        event = self.stage_a.process(raw_event)
        
        # Update match scores if goal
        if event.event_type.value == "goal":
            if event.team_id == self.engine.home_team.id:
                self.score_home += 1
            else:
                self.score_away += 1

        # 2. Interpret (Stage B)
        stats_h, stats_a, rhythm = self.stage_b.process_event(event)

        # 3. Explainability (Stage C)
        insight = self.stage_c.analyze_event(event, rhythm, stats_h, stats_a)

        # 4. Render Overlays (Stage D)
        focused_player = self.get_focused_player()
        overlay = self.stage_d.generate_overlay(event, rhythm, insight, focused_player)

        # 5. Personalize (Stage E)
        narrative = self.stage_e.generate_narrative(
            event=event,
            rhythm=rhythm,
            focused_player=focused_player,
            language=self.current_language
        )

        payload = LiveMatchPayload(
            match_id=self.match_id,
            current_minute=event.minute,
            current_second=event.second,
            score_home=self.score_home,
            score_away=self.score_away,
            latest_event=event,
            stats_home=stats_h,
            stats_away=stats_a,
            rhythm=rhythm,
            active_overlay=overlay,
            latest_insight=insight,
            narrative=narrative,
            focused_player=focused_player
        )
        
        self.current_payload = payload
        self.history.append(payload)
        return payload

    async def generate_studio_recap(self, language: Language = Language.EN) -> Dict[str, Any]:
        """
        Generates an automated, explainable post-match / half-time studio recap
        summarizing momentum swings, tactical dominance, and key moments.
        """
        stats_h = self.stage_b.stats[self.engine.home_team.id]
        stats_a = self.stage_b.stats[self.engine.away_team.id]
        
        if language == Language.RO:
            title = f"Rezumat Studio: {self.engine.home_team.name} {self.score_home} - {self.score_away} {self.engine.away_team.name}"
            summary = (
                f"Un meci de mare intensitate în Premier League. {self.engine.home_team.name} a dominat posesia cu "
                f"{stats_h.possession_pct}%, generând un total de {stats_h.total_xG:.2f} xG din {stats_h.total_shots} șuturi. "
                f"În replică, {self.engine.away_team.name} a generat {stats_a.total_xG:.2f} xG bazându-se pe tranziții rapide "
                f"și {stats_a.tackles_won} recuperări defensive."
            )
            key_takeaway = "Eficiența în fața porții și gestionarea momentelor de haos tranzițional au stabilit deznodământul."
        elif language == Language.ES:
            title = f"Resumen de Estudio: {self.engine.home_team.name} {self.score_home} - {self.score_away} {self.engine.away_team.name}"
            summary = (
                f"Duelo táctico de alto calibre. {self.engine.home_team.name} controló la posesión con un {stats_h.possession_pct}%, "
                f"acumulando {stats_h.total_xG:.2f} xG en {stats_h.total_shots} disparos."
            )
            key_takeaway = "La presión en zonas interiores desarticuló las líneas defensivas rivales."
        else:
            title = f"Studio Match Recap: {self.engine.home_team.name} {self.score_home} - {self.score_away} {self.engine.away_team.name}"
            summary = (
                f"A thrilling tactical battle at the highest tempo. {self.engine.home_team.name} maintained "
                f"{stats_h.possession_pct}% possession, generating {stats_h.total_xG:.2f} xG across {stats_h.total_shots} shots. "
                f"{self.engine.away_team.name} responded with lethal direct transitions, recording {stats_a.total_xG:.2f} xG "
                f"and {stats_a.tackles_won} key tackles won."
            )
            key_takeaway = "Superior territorial dominance and high-speed passing unlocked defensive low blocks."

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
