import os
from typing import Optional, List
from app.data.models import (
    MatchEvent, EventType, ShotOutcome, RhythmState,
    ExplainabilityInsight, TeamMatchStats
)
from app.config import settings

class TacticalExplainabilityEngine:
    """
    Stage C: Explainability Layer ("Why Moments Matter")
    Analyzes tactical inflection points, control vs chaos transitions,
    and explains the strategic context behind match events.
    """
    def __init__(self):
        self.insight_counter = 0
        self.active_insight: Optional[ExplainabilityInsight] = None

    def analyze_event(
        self,
        event: MatchEvent,
        rhythm: RhythmState,
        stats_home: TeamMatchStats,
        stats_away: TeamMatchStats
    ) -> ExplainabilityInsight:
        """
        Determines if the event is a pivotal tactical moment and produces
        an explainable breakdown of why it matters. Never returns None so
        the broadcast commentary and tactical card are always alive.
        """
        self.insight_counter += 1
        
        # 1. GOAL or HIGH xG MOMENT
        if event.event_type == EventType.GOAL:
            self.active_insight = ExplainabilityInsight(
                insight_id=f"ins_{self.insight_counter}",
                minute=event.minute,
                second=event.second,
                title="GOAL: Defensive Block Breached",
                why_it_matters=(
                    f"A breakthrough {event.shot_speed_kmh or event.ball_speed_kmh or 85} km/h finish from {event.player.name}. "
                    f"Rather than just a finishing error by the defense, this goal was engineered by creating numerical overload "
                    f"in the box, producing a high-value xG chance of {event.xG:.2f}."
                ),
                tactical_shift_explanation=(
                    f"The defending team's low-block collapsed following sustained territorial pressure. "
                    f"With Control vs Chaos sitting at {rhythm.control_vs_chaos_index:.1f}%, the attacking team "
                    f"capitalized on a delayed recovery run by the defensive midfielders."
                ),
                pattern_detected="Half-Space Overload & Rapid Vertical Transition",
                key_contributing_factors=[
                    f"Shot velocity: {event.shot_speed_kmh or event.ball_speed_kmh or 85} km/h",
                    f"xG probability: {event.xG:.2f}",
                    "Failure to track secondary runner into penalty box"
                ]
            )
            return self.active_insight
            
        elif event.event_type == EventType.CORNER:
            self.active_insight = ExplainabilityInsight(
                insight_id=f"ins_{self.insight_counter}",
                minute=event.minute,
                second=event.second,
                title="Set-Piece: Near-Post Overload Corner",
                why_it_matters=(
                    f"A pinpoint inswinging delivery from {event.player.name} targeting the 6-yard corridor. "
                    f"Modern Premier League set pieces account for over 30% of goals; clustering aerial threats "
                    f"forces defensive zone disorientation."
                ),
                tactical_shift_explanation=(
                    f"The defending side deployed a hybrid zonal-man marking scheme, but the attacking side's "
                    f"screens and delayed second-phase runs unlocked an aerial duel with {event.xG:.2f} xG."
                ),
                pattern_detected="Near-Post Screen & Zonal Overload Routine",
                key_contributing_factors=[
                    "Curling delivery into the 6-yard corridor",
                    f"High aerial threat xG: {event.xG:.2f}",
                    "Defensive zonal marking breached by coordinated block"
                ]
            )
            return self.active_insight

        elif event.event_type == EventType.PENALTY:
            self.active_insight = ExplainabilityInsight(
                insight_id=f"ins_{self.insight_counter}",
                minute=event.minute,
                second=event.second,
                title="High-Drama Penalty Kick Duel (xG: 0.79)",
                why_it_matters=(
                    f"{event.player.name} stands 12 yards out for the ultimate psychological duel. "
                    f"Penalties are the highest expected-goal event in football (0.79 Opta baseline), "
                    f"often deciding the tactical momentum of entire matches."
                ),
                tactical_shift_explanation=(
                    f"Following an infringement inside the 18-yard box, 20 players cleared outside the D-arc. "
                    f"The goalkeeper must balance split-second anticipation against a {event.shot_speed_kmh or 112} km/h strike."
                ),
                pattern_detected="High-Stakes 1v1 Penalty Inflection Point",
                key_contributing_factors=[
                    "Elite xG benchmark: 0.79",
                    f"Strike velocity: {event.shot_speed_kmh or 112} km/h",
                    "100% isolated 1v1 psychological execution"
                ]
            )
            return self.active_insight

        elif event.event_type == EventType.FREE_KICK:
            self.active_insight = ExplainabilityInsight(
                insight_id=f"ins_{self.insight_counter}",
                minute=event.minute,
                second=event.second,
                title="Direct Free Kick: Danger Zone Geometry",
                why_it_matters=(
                    f"Direct set-piece specialist {event.player.name} tests the defensive 4-man wall from ~24 meters. "
                    f"Curling trajectories over a 9.15m wall force goalkeepers to freeze until the ball clears the heads of defenders."
                ),
                tactical_shift_explanation=(
                    f"The defending team aligned a 4-man wall to protect the near post, conceding the far angle. "
                    f"Curling ball flight at {event.shot_speed_kmh or 100} km/h generated an acute scoring window."
                ),
                pattern_detected="Wall-Clearing Top-Corner Trajectory",
                key_contributing_factors=[
                    "Ball placed in high-danger central corridor (24m)",
                    "4-man defensive wall organized at 9.15m regulation distance",
                    f"Curling trajectory at {event.shot_speed_kmh or 100} km/h"
                ]
            )
            return self.active_insight

        # Disciplinary Card Decision
        elif event.event_type == EventType.CARD:
            is_red = getattr(event, "card_type", "yellow") == "red"
            card_title = "Red Card Dismissal" if is_red else "Yellow Card Caution"
            self.active_insight = ExplainabilityInsight(
                insight_id=f"ins_{self.insight_counter}",
                minute=event.minute,
                second=event.second,
                title=f"Disciplinary: {card_title}",
                why_it_matters=(
                    f"Referee issues a {card_title.lower()} to {event.player.name}. "
                    f"{'A devastating dismissal forcing an immediate 10-man defensive reshuffle.' if is_red else 'The defender is now cautioned, severely curbing their aggressiveness in 1v1 challenges.'}"
                ),
                tactical_shift_explanation=(
                    f"Cynical tackle on {event.recipient.name if event.recipient else 'the attacker'} "
                    f"halts play in zone ({event.location.x:.1f}, {event.location.y:.1f}). "
                    f"{'Opponents will now press high with numerical superiority.' if is_red else 'Opposing wingers will aggressively isolate the booked player.'}"
                ),
                pattern_detected="Disciplinary Infraction / Tactical Foul",
                key_contributing_factors=[
                    f"Official disciplinary sanction: {card_title}",
                    f"Infraction coordinate: ({event.location.x:.1f}, {event.location.y:.1f})",
                    "Defensive caution constraint active"
                ]
            )
            return self.active_insight

        # Tactical Foul Stoppage
        elif event.event_type == EventType.FOUL:
            self.active_insight = ExplainabilityInsight(
                insight_id=f"ins_{self.insight_counter}",
                minute=event.minute,
                second=event.second,
                title="Referee Whistle: Tactical Foul",
                why_it_matters=(
                    f"Play is halted after {event.player.name} fouls {event.recipient.name if event.recipient else 'the attacker'}. "
                    f"Tactical fouls deliberately stop attacking transitions at the cost of surrendering set-piece positioning."
                ),
                tactical_shift_explanation=(
                    f"Intense pressure ({event.pressure_intensity:.0f}%) forced an illegal challenge. "
                    f"Attacking team regains dead-ball positional control."
                ),
                pattern_detected="Transition Stoppage via Tactical Foul",
                key_contributing_factors=[
                    "Match referee whistle blown",
                    f"Foul location: x={event.location.x:.1f}, y={event.location.y:.1f}",
                    "Free-kick dead ball situation"
                ]
            )
            return self.active_insight

        elif event.event_type == EventType.SHOT and event.xG and event.xG >= 0.20:
            self.active_insight = ExplainabilityInsight(
                insight_id=f"ins_{self.insight_counter}",
                minute=event.minute,
                second=event.second,
                title="High-xG Opportunity Created",
                why_it_matters=(
                    f"{event.player.name} penetrated the defensive shape for a {event.xG:.2f} xG chance. "
                    f"This matters because it signals a repeatable defensive vulnerability in the central channel."
                ),
                tactical_shift_explanation=(
                    f"Tactical pressure index is elevated at {rhythm.tactical_pressure_index:.1f}%. "
                    f"The attacking side bypassed the midfield pressing wave with high-speed ball circulation."
                ),
                pattern_detected="Between-the-Lines Penetration",
                key_contributing_factors=[
                    f"High-danger xG: {event.xG:.2f}",
                    f"Fast ball release: {event.shot_speed_kmh or 92} km/h",
                    "Defensive line caught stepping out too late"
                ]
            )
            return self.active_insight

        # 2. HIGH DIFFICULTY COMPLETED PASS (Tactical Unlock)
        elif (
            event.event_type == EventType.PASS and
            event.pass_difficulty_rating is not None and
            event.pass_difficulty_rating >= 0.65 and
            event.location.x > 45
        ):
            self.active_insight = ExplainabilityInsight(
                insight_id=f"ins_{self.insight_counter}",
                minute=event.minute,
                second=event.second,
                title="Line-Breaking Distribution Under Press",
                why_it_matters=(
                    f"{event.player.name} completed a high-risk pass (Difficulty: {event.pass_difficulty_rating:.2f}, "
                    f"Distance: {event.pass_distance_m}m at {event.ball_speed_kmh} km/h) under intense pressure."
                ),
                tactical_shift_explanation=(
                    f"Executing passes under {event.pressure_intensity:.1f}% pressure shifts the opposition from "
                    f"organized pressing into emergency recovery. This single pass eliminated 3 opposing players."
                ),
                pattern_detected="Third-Man Vertical Disruption",
                key_contributing_factors=[
                    f"Pass difficulty: {event.pass_difficulty_rating:.2f}/1.0",
                    f"Ball speed: {event.ball_speed_kmh} km/h",
                    "Line-breaking trajectory into attacking third"
                ]
            )
            return self.active_insight

        # 3. TRANSITION / CHAOS SURGE (Turnover or tackle)
        elif event.event_type in (EventType.TACKLE, EventType.INTERCEPTION) and rhythm.control_vs_chaos_index < 45.0:
            self.active_insight = ExplainabilityInsight(
                insight_id=f"ins_{self.insight_counter}",
                minute=event.minute,
                second=event.second,
                title="Tactical Counter-Pressing Trap",
                why_it_matters=(
                    f"{event.player.name} won possession in a high-chaos state (Control Index: {rhythm.control_vs_chaos_index:.1f}%). "
                    f"In modern football, 62% of transition goals occur within 8 seconds of tackles won in this exact zone."
                ),
                tactical_shift_explanation=(
                    f"The game rhythm has entered high volatility ({rhythm.pace_rating} pace). "
                    f"Both teams are stretched, leaving vast vertical passing corridors available for counter-attacks."
                ),
                pattern_detected="Counter-Pressing Trap Sprung",
                key_contributing_factors=[
                    f"Control vs Chaos dropped to {rhythm.control_vs_chaos_index:.1f}/100",
                    f"Sprint speed recorded at {event.player_speed_kmh} km/h",
                    "Immediate forward transition opportunity"
                ]
            )
            return self.active_insight

        # 4. CONTINUOUS TACTICAL PHASE EXPLAINABILITY (Ensures insight is always active)
        if self.active_insight is None or self.insight_counter % 3 == 0:
            phase_type = "Positional Buildup & Overload" if rhythm.control_vs_chaos_index >= 50 else "High-Intensity Spatial Transition"
            dominant_name = stats_home.team_id.upper() if rhythm.momentum_team_id == stats_home.team_id else stats_away.team_id.upper()
            
            self.active_insight = ExplainabilityInsight(
                insight_id=f"ins_phase_{self.insight_counter}",
                minute=event.minute,
                second=event.second,
                title=f"Tactical Phase: {phase_type}",
                why_it_matters=(
                    f"{dominant_name} is dictating match tempo inside the {rhythm.dominant_zone}. "
                    f"With Tactical Pressure at {rhythm.tactical_pressure_index:.0f}%, ball circulation is structured "
                    f"to bait defensive pressers out of position before launching vertical line-breaking balls."
                ),
                tactical_shift_explanation=(
                    f"Control vs Chaos is balanced at {rhythm.control_vs_chaos_index:.1f}%. "
                    f"Opposition defensive unit is maintaining horizontal compact spacing, forcing lateral progression."
                ),
                pattern_detected=f"Phase Progression: {rhythm.pace_rating} Tempo Strategy",
                key_contributing_factors=[
                    f"Zone of influence: {rhythm.dominant_zone}",
                    f"Tactical Pressure: {rhythm.tactical_pressure_index:.0f}%",
                    f"Control Index: {rhythm.control_vs_chaos_index:.1f}%"
                ]
            )

        return self.active_insight
