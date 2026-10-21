from typing import Optional
from app.data.models import (
    MatchEvent, BroadcastOverlay, GraphicType, EventType,
    RhythmState, ExplainabilityInsight, PlayerProfile
)

class BroadcastGraphicOverlayEngine:
    """
    Stage D: Broadcast Overlay Rendering Engine
    Generates clean, machine-readable graphical overlays synchronized with live match events
    for broadcast feeds, studio LED walls, and streaming platform overlays.
    """
    def __init__(self):
        self.graphic_sequence = 0

    def generate_overlay(
        self,
        event: MatchEvent,
        rhythm: RhythmState,
        insight: Optional[ExplainabilityInsight] = None,
        focused_player: Optional[PlayerProfile] = None
    ) -> Optional[BroadcastOverlay]:
        self.graphic_sequence += 1
        
        # 1. Overlay for Goal or High Impact Shot
        if event.event_type == EventType.GOAL:
            return BroadcastOverlay(
                graphic_id=f"gfx_{self.graphic_sequence}",
                graphic_type=GraphicType.LOWER_THIRD,
                display_title="⚡ GOAL BREAKDOWN",
                primary_metric=f"Shot Speed: {event.shot_speed_kmh} km/h",
                secondary_metric=f"xG Value: {event.xG:.2f}" if event.xG else None,
                detail_text=f"{event.player.name} (#{event.player.number}) finds the back of the net!",
                duration_seconds=7,
                accent_color="#00FF87"  # Premier League neon green
            )

        # Set Piece: Penalty Kick
        elif event.event_type == EventType.PENALTY:
            return BroadcastOverlay(
                graphic_id=f"gfx_{self.graphic_sequence}",
                graphic_type=GraphicType.LOWER_THIRD,
                display_title="💥 PENALTY KICK DRAMA",
                primary_metric=f"Conversion xG: {event.xG:.2f}",
                secondary_metric=f"Velocity: {event.shot_speed_kmh} km/h",
                detail_text=f"{event.player.name} steps up 12 yards from goal against the keeper",
                duration_seconds=6,
                accent_color="#FF2882"
            )

        # Set Piece: Corner Kick
        elif event.event_type == EventType.CORNER:
            return BroadcastOverlay(
                graphic_id=f"gfx_{self.graphic_sequence}",
                graphic_type=GraphicType.SPEED_PASS_BADGE,
                display_title="🚩 SET PIECE: CORNER KICK",
                primary_metric="Routine: Near-Post Overload",
                secondary_metric=f"Ball Speed: {event.ball_speed_kmh} km/h",
                detail_text=f"{event.player.name} whips an inswinging ball into the 6-yard box",
                duration_seconds=5,
                accent_color="#04F5FF"
            )

        # Set Piece: Direct Free Kick
        elif event.event_type == EventType.FREE_KICK:
            return BroadcastOverlay(
                graphic_id=f"gfx_{self.graphic_sequence}",
                graphic_type=GraphicType.SPEED_PASS_BADGE,
                display_title="🎯 DIRECT FREE KICK",
                primary_metric="Distance: ~24 meters",
                secondary_metric="Defensive Wall: 4 players",
                detail_text=f"{event.player.name} tests the top corner over the wall",
                duration_seconds=5,
                accent_color="#FFA500"
            )

        # Disciplinary Card Overlay
        elif event.event_type == EventType.CARD:
            is_red = getattr(event, "card_type", "yellow") == "red"
            return BroadcastOverlay(
                graphic_id=f"gfx_{self.graphic_sequence}",
                graphic_type=GraphicType.LOWER_THIRD,
                display_title="🟥 RED CARD DISMISSAL" if is_red else "🟨 YELLOW CARD CAUTION",
                primary_metric=f"Player: {event.player.name} ({event.player.position})",
                secondary_metric="Official Sanction: Card Issued",
                detail_text=f"Referee brandishes a {'red' if is_red else 'yellow'} card for a cynical foul",
                duration_seconds=6,
                accent_color="#EF4444" if is_red else "#EAB308"
            )

        # Foul Stoppage Overlay
        elif event.event_type == EventType.FOUL:
            return BroadcastOverlay(
                graphic_id=f"gfx_{self.graphic_sequence}",
                graphic_type=GraphicType.SPEED_PASS_BADGE,
                display_title="⚠️ REFEREE WHISTLE: FOUL",
                primary_metric=f"Fouled: {event.recipient.name if event.recipient else 'Opponent'}",
                secondary_metric=f"Intensity: {event.pressure_intensity:.0f}%",
                detail_text=f"{event.player.name} commits tactical foul at ({event.location.x:.1f}, {event.location.y:.1f})",
                duration_seconds=4,
                accent_color="#F59E0B"
            )

        # 2. Overlay for High-Speed / High-Difficulty Pass
        elif (
            event.event_type == EventType.PASS and
            event.pass_difficulty_rating is not None and
            event.pass_difficulty_rating >= 0.72
        ):
            return BroadcastOverlay(
                graphic_id=f"gfx_{self.graphic_sequence}",
                graphic_type=GraphicType.SPEED_PASS_BADGE,
                display_title="🎯 KEY PASS TELEMETRY",
                primary_metric=f"Difficulty: {event.pass_difficulty_rating:.2f}/1.0",
                secondary_metric=f"Ball Velocity: {event.ball_speed_kmh} km/h",
                detail_text=f"{event.player.name} finds {event.recipient.name if event.recipient else 'target'} over {event.pass_distance_m}m",
                duration_seconds=5,
                accent_color="#FF2882"  # Vibrant Magenta
            )

        # 3. Tactical Rhythm Alert (Chaos or Control surge)
        elif rhythm.control_vs_chaos_index < 35.0 and event.event_type == EventType.TACKLE:
            return BroadcastOverlay(
                graphic_id=f"gfx_{self.graphic_sequence}",
                graphic_type=GraphicType.MOMENTUM_GAUGE,
                display_title="⚠️ CHAOS TRANSITION PHASE",
                primary_metric=f"Control Index: {rhythm.control_vs_chaos_index:.0f}%",
                secondary_metric=f"Pace: {rhythm.pace_rating}",
                detail_text="Rapid turnovers triggering high-probability counter-attack windows",
                duration_seconds=5,
                accent_color="#FFA500"  # Amber warning
            )

        # 4. Player Focus Mode Overlay
        elif focused_player and event.player.id == focused_player.id:
            return BroadcastOverlay(
                graphic_id=f"gfx_{self.graphic_sequence}",
                graphic_type=GraphicType.PLAYER_SPOTLIGHT,
                display_title=f"⭐ PLAYER RADAR: {focused_player.name.upper()}",
                primary_metric=f"Current Speed: {event.player_speed_kmh} km/h",
                secondary_metric=f"Dist Covered: {focused_player.distance_covered_meters:.0f}m",
                detail_text=f"Position: {focused_player.position} | Sprints: {focused_player.sprint_count}",
                duration_seconds=6,
                accent_color="#00D2BE"  # Teal
            )

        # 5. Insight-backed Tactical Radar
        elif insight:
            return BroadcastOverlay(
                graphic_id=f"gfx_{self.graphic_sequence}",
                graphic_type=GraphicType.TACTICAL_RADAR,
                display_title=f"🧠 TACTICAL NOTE: {insight.title}",
                primary_metric=insight.pattern_detected,
                secondary_metric=f"Confidence: {int(insight.confidence_score * 100)}%",
                detail_text=insight.why_it_matters[:90] + "...",
                duration_seconds=6,
                accent_color="#38003C"  # Premier League royal purple
            )

        return None
