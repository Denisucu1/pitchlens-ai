from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.data.models import Language, PersonaMode
from app.agents.orchestrator import PitchLensOrchestrator

router = APIRouter(prefix="/api/match", tags=["Match Intelligence"])

# Shared global orchestrator instance
global_orchestrator = PitchLensOrchestrator()

class FocusPlayerRequest(BaseModel):
    player_id: Optional[str] = None

class LanguageRequest(BaseModel):
    language: Language

class FanQueryRequest(BaseModel):
    question: str
    mode: PersonaMode = PersonaMode.CASUAL_FAN
    language: Language = Language.EN

@router.get("/teams")
async def get_teams():
    """Returns team metadata, rosters, formations, and tactical profiles."""
    return {
        "home_team": global_orchestrator.engine.home_team,
        "away_team": global_orchestrator.engine.away_team
    }

@router.get("/state")
async def get_match_state():
    """Returns the current state of the live simulated match."""
    if not global_orchestrator.current_payload:
        global_orchestrator.tick()
    return global_orchestrator.current_payload

@router.post("/tick")
async def trigger_manual_tick():
    """Advances match simulation by one event cycle."""
    return global_orchestrator.tick()

@router.post("/focus-player")
async def set_focus_player(req: FocusPlayerRequest):
    """Sets focused player for Player-Focused Experience mode."""
    global_orchestrator.set_focused_player(req.player_id)
    return {"status": "ok", "focused_player_id": req.player_id}

@router.post("/language")
async def set_match_language(req: LanguageRequest):
    """Sets language for real-time storytelling."""
    global_orchestrator.set_language(req.language)
    return {"status": "ok", "language": req.language}

@router.get("/recap")
async def get_studio_recap(lang: Language = Query(Language.EN)):
    """Generates an explainable studio recap of the match."""
    return await global_orchestrator.generate_studio_recap(language=lang)

@router.post("/ask")
async def ask_pitchlens_ai(req: FanQueryRequest):
    """
    Fan & Analyst Conversational Q&A:
    Answers natural language questions about the match using real-time match state,
    explainability insights, and tactical rhythm metrics.
    """
    curr = global_orchestrator.current_payload
    if not curr:
        curr = global_orchestrator.tick()
        
    home = global_orchestrator.engine.home_team
    away = global_orchestrator.engine.away_team
    q_lower = req.question.lower()
    
    # Intelligent domain answering using current state
    if "why" in q_lower or "de ce" in q_lower or "por qué" in q_lower:
        if curr.latest_insight:
            ans = f"{curr.latest_insight.title}: {curr.latest_insight.why_it_matters} {curr.latest_insight.tactical_shift_explanation}"
        else:
            ans = (
                f"The balance of the game is shaped by the Control vs Chaos Index ({curr.rhythm.control_vs_chaos_index:.1f}%). "
                f"{curr.rhythm.momentum_team_id} currently holds spatial momentum in the {curr.rhythm.dominant_zone}."
            )
    elif "who" in q_lower or "cine" in q_lower or "quién" in q_lower or "player" in q_lower or "jucator" in q_lower:
        p = curr.focused_player or curr.latest_event.player
        ans = (
            f"Key performer spotlight: {p.name} (#{p.number}, {p.position}). "
            f"Clocked top speed of {p.current_speed_kmh} km/h with {p.distance_covered_meters:.0f}m distance covered."
        )
    elif "stat" in q_lower or "xg" in q_lower or "possession" in q_lower or "posesie" in q_lower:
        ans = (
            f"Match Metrics: {home.name} ({curr.stats_home.possession_pct}% possession, {curr.stats_home.total_xG:.2f} xG, {curr.stats_home.total_shots} shots) vs "
            f"{away.name} ({curr.stats_away.possession_pct}% possession, {curr.stats_away.total_xG:.2f} xG, {curr.stats_away.total_shots} shots). "
            f"Average ball speed: {curr.stats_home.avg_ball_speed_kmh} km/h."
        )
    else:
        ans = (
            f"PitchLens Intelligence: The score is {curr.score_home} - {curr.score_away} at minute {curr.current_minute}:{curr.current_second:02d}. "
            f"Game rhythm is currently rated as '{curr.rhythm.pace_rating}' with pressure at {curr.rhythm.tactical_pressure_index:.1f}%."
        )
        
    return {
        "question": req.question,
        "answer": ans,
        "mode": req.mode,
        "language": req.language,
        "grounded_data": {
            "minute": curr.current_minute,
            "score": f"{curr.score_home}-{curr.score_away}",
            "control_index": curr.rhythm.control_vs_chaos_index,
            "dominant_zone": curr.rhythm.dominant_zone
        }
    }
