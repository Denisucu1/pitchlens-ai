from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from enum import Enum

# --- ENUMS ---
class EventType(str, Enum):
    PASS = "pass"
    SHOT = "shot"
    TACKLE = "tackle"
    INTERCEPTION = "interception"
    PRESSURE = "pressure"
    CARRY = "carry"
    RECOVERY = "recovery"
    FOUL = "foul"
    CARD = "card"
    GOAL = "goal"
    OFFSIDE = "offside"
    CORNER = "corner"
    FREE_KICK = "free_kick"
    SUBSTITUTION = "substitution"
    SAVE = "save"

class PassOutcome(str, Enum):
    COMPLETE = "complete"
    INCOMPLETE = "incomplete"
    INTERCEPTED = "intercepted"
    OUT_OF_BOUNDS = "out_of_bounds"

class ShotOutcome(str, Enum):
    GOAL = "goal"
    SAVED = "saved"
    BLOCKED = "blocked"
    OFF_TARGET = "off_target"
    POST = "post"

class PersonaMode(str, Enum):
    CASUAL_FAN = "casual_fan"
    DATA_ANALYST = "data_analyst"
    PLAYER_FOCUS = "player_focus"

class Language(str, Enum):
    EN = "en"
    RO = "ro"
    ES = "es"

# --- CORE SCHEMAS ---
class PitchCoordinates(BaseModel):
    x: float = Field(..., ge=0.0, le=100.0, description="Normalized X coordinate (0-100m)")
    y: float = Field(..., ge=0.0, le=100.0, description="Normalized Y coordinate (0-100m)")

class PlayerProfile(BaseModel):
    id: str
    name: str
    number: int
    position: str  # GK, CB, LB, RB, CM, CDM, CAM, LW, RW, ST
    team_id: str
    pace: int = 75
    stamina: int = 80
    passing_skill: int = 75
    shooting_skill: int = 70
    
    # Real-time tracking telemetry
    current_speed_kmh: float = 0.0
    distance_covered_meters: float = 0.0
    sprint_count: int = 0
    current_coords: PitchCoordinates = Field(default_factory=lambda: PitchCoordinates(x=50.0, y=50.0))

class TeamProfile(BaseModel):
    id: str
    name: str
    short_name: str
    primary_color: str
    secondary_color: str
    formation: str  # e.g., "4-3-3", "4-2-3-1"
    manager: str
    tactical_style: str
    players: List[PlayerProfile] = []

# --- SYNTHETIC EVENT SCHEMA (STAGE A) ---
class MatchEvent(BaseModel):
    event_id: str
    match_id: str
    minute: int
    second: int
    period: Literal["1H", "2H", "ET"] = "1H"
    team_id: str
    player: PlayerProfile
    recipient: Optional[PlayerProfile] = None
    event_type: EventType
    
    # Spatial Tracking
    location: PitchCoordinates
    end_location: Optional[PitchCoordinates] = None
    
    # Speed Metrics (Hackathon Required)
    ball_speed_kmh: Optional[float] = None
    shot_speed_kmh: Optional[float] = None
    player_speed_kmh: float = 0.0
    
    # Pass Quality Metrics (Hackathon Required)
    pass_distance_m: Optional[float] = None
    pass_difficulty_rating: Optional[float] = Field(None, ge=0.0, le=1.0)
    pass_outcome: Optional[PassOutcome] = None
    
    # Expected Metrics
    xG: Optional[float] = Field(None, ge=0.0, le=1.0)
    xA: Optional[float] = Field(None, ge=0.0, le=1.0)
    shot_outcome: Optional[ShotOutcome] = None
    
    # Tactical context
    under_pressure: bool = False
    pressure_intensity: float = Field(0.0, ge=0.0, le=100.0)
    possession_chain_id: str = "chain_0"

# --- AGGREGATED MATCH STATE & INTERPRETATION (STAGE B) ---
class TeamMatchStats(BaseModel):
    team_id: str
    possession_pct: float = 50.0
    total_passes: int = 0
    successful_passes: int = 0
    pass_accuracy_pct: float = 0.0
    average_pass_difficulty: float = 0.0
    total_shots: int = 0
    shots_on_target: int = 0
    goals: int = 0
    total_xG: float = 0.0
    tackles_won: int = 0
    pressures_applied: int = 0
    fouls: int = 0
    cards_yellow: int = 0
    cards_red: int = 0
    avg_ball_speed_kmh: float = 0.0
    distance_covered_km: float = 0.0

class RhythmState(BaseModel):
    control_vs_chaos_index: float = Field(50.0, ge=0.0, le=100.0)
    tactical_pressure_index: float = Field(50.0, ge=0.0, le=100.0)
    momentum_team_id: str = ""
    dominant_zone: str = "Center Midfield"
    pace_rating: str = "Medium"

# --- EXPLAINABILITY & TACTICAL INSIGHT (STAGE C) ---
class ExplainabilityInsight(BaseModel):
    insight_id: str
    minute: int
    second: int
    title: str
    why_it_matters: str
    tactical_shift_explanation: str
    pattern_detected: str
    key_contributing_factors: List[str] = []
    confidence_score: float = 0.95

# --- ON-SCREEN BROADCAST GRAPHICS (STAGE D) ---
class GraphicType(str, Enum):
    LOWER_THIRD = "lower_third"
    TACTICAL_RADAR = "tactical_radar"
    SHOT_MAP_CARD = "shot_map_card"
    SPEED_PASS_BADGE = "speed_pass_badge"
    MOMENTUM_GAUGE = "momentum_gauge"
    PLAYER_SPOTLIGHT = "player_spotlight"

class BroadcastOverlay(BaseModel):
    graphic_id: str
    graphic_type: GraphicType
    display_title: str
    primary_metric: str
    secondary_metric: Optional[str] = None
    detail_text: str
    duration_seconds: int = 6
    is_active: bool = True
    accent_color: str = "#38003C"

# --- AUDIENCE PERSONALIZATION & NARRATIVE (STAGE E) ---
class PersonalizedNarrative(BaseModel):
    minute: int
    second: int
    casual_fan_narrative: str
    data_analyst_narrative: str
    player_focus_narrative: Optional[str] = None
    language: Language = Language.EN

# --- MULTI-AGENT ORCHESTRATION LOG SCHEMA ---
class AgentLog(BaseModel):
    agent_name: str  # Orchestrator, Tactical, Narrative, Graphics, Fan
    role: str
    message: str
    timestamp: str
    status: Literal["processing", "handoff", "success", "alert"] = "processing"

class PassLink(BaseModel):
    source_player_id: str
    target_player_id: str
    count: int

# --- COMPLETE LIVE PAYLOAD EMITTED ON EVERY EVENT TICK ---
class LiveMatchPayload(BaseModel):
    match_id: str
    current_minute: int
    current_second: int
    score_home: int
    score_away: int
    latest_event: MatchEvent
    stats_home: TeamMatchStats
    stats_away: TeamMatchStats
    rhythm: RhythmState
    active_overlay: Optional[BroadcastOverlay] = None
    latest_insight: Optional[ExplainabilityInsight] = None
    narrative: PersonalizedNarrative
    focused_player: Optional[PlayerProfile] = None
    agent_logs: List[AgentLog] = []
    pass_links: List[PassLink] = []
    heatmap_points: List[PitchCoordinates] = []
    timeline_moments: List[Dict[str, Any]] = []
