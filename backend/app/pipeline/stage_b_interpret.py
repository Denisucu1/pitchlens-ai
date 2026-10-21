from typing import Dict, List, Tuple
from collections import deque
from app.data.models import (
    MatchEvent, TeamMatchStats, RhythmState, EventType,
    PassOutcome, ShotOutcome
)

class MatchInterpretationEngine:
    """
    Stage B: Interpretation Layer
    Interprets incoming match events into meaningful football statistics, patterns,
    and game rhythm dynamics:
    - Pass quality aggregation (distance, accuracy, difficulty rating)
    - Speed metrics (ball speed, shot speed)
    - Control vs Chaos index calculation
    - Dynamic momentum tracking
    """
    def __init__(self, home_team_id: str, away_team_id: str):
        self.home_team_id = home_team_id
        self.away_team_id = away_team_id
        
        self.stats: Dict[str, TeamMatchStats] = {
            home_team_id: TeamMatchStats(team_id=home_team_id),
            away_team_id: TeamMatchStats(team_id=away_team_id)
        }
        
        # Sliding window for rhythm and momentum calculations (last 15 events)
        self.recent_events: deque = deque(maxlen=15)
        self.recent_pass_difficulties: Dict[str, List[float]] = {
            home_team_id: [],
            away_team_id: []
        }

    def process_event(self, event: MatchEvent) -> Tuple[TeamMatchStats, TeamMatchStats, RhythmState]:
        self.recent_events.append(event)
        team_stats = self.stats.get(event.team_id)
        
        if team_stats:
            # 1. Pass Quality & Tracking
            if event.event_type == EventType.PASS:
                team_stats.total_passes += 1
                if event.pass_outcome == PassOutcome.COMPLETE:
                    team_stats.successful_passes += 1
                    
                if event.pass_difficulty_rating is not None:
                    self.recent_pass_difficulties[event.team_id].append(event.pass_difficulty_rating)
                    all_diffs = self.recent_pass_difficulties[event.team_id]
                    team_stats.average_pass_difficulty = round(sum(all_diffs) / len(all_diffs), 2)
                    
                team_stats.pass_accuracy_pct = round(
                    (team_stats.successful_passes / max(1, team_stats.total_passes)) * 100.0, 1
                )
                
            # 2. Shot, Penalty & xG Tracking
            elif event.event_type in [EventType.SHOT, EventType.GOAL, EventType.PENALTY, EventType.FREE_KICK]:
                team_stats.total_shots += 1
                if event.xG is not None:
                    team_stats.total_xG = round(team_stats.total_xG + event.xG, 2)
                    
                if event.shot_outcome in [ShotOutcome.GOAL, ShotOutcome.SAVED]:
                    team_stats.shots_on_target += 1
                    
                if event.shot_outcome == ShotOutcome.GOAL:
                    team_stats.goals += 1

            # 3. Corners Tracking
            elif event.event_type == EventType.CORNER:
                team_stats.corners += 1

            # 4. Fouls Tracking
            elif event.event_type == EventType.FOUL:
                team_stats.fouls += 1

            # 5. Cards Tracking
            elif event.event_type == EventType.CARD:
                team_stats.fouls += 1
                if getattr(event, "card_type", "yellow") == "red":
                    team_stats.cards_red += 1
                else:
                    team_stats.cards_yellow += 1

            # 6. Defensive stats
            elif event.event_type == EventType.TACKLE:
                team_stats.tackles_won += 1
                
            if event.under_pressure:
                team_stats.pressures_applied += 1
                
            # 4. Ball speed running average
            if event.ball_speed_kmh:
                if team_stats.avg_ball_speed_kmh == 0.0:
                    team_stats.avg_ball_speed_kmh = event.ball_speed_kmh
                else:
                    team_stats.avg_ball_speed_kmh = round(
                        (team_stats.avg_ball_speed_kmh * 0.9) + (event.ball_speed_kmh * 0.1), 1
                    )

        # 5. Compute Possession %
        total_home_passes = self.stats[self.home_team_id].total_passes
        total_away_passes = self.stats[self.away_team_id].total_passes
        total_passes = total_home_passes + total_away_passes
        
        if total_passes > 0:
            self.stats[self.home_team_id].possession_pct = round((total_home_passes / total_passes) * 100.0, 1)
            self.stats[self.away_team_id].possession_pct = round(100.0 - self.stats[self.home_team_id].possession_pct, 1)

        # 6. Calculate Control vs Chaos and Rhythm
        rhythm = self._calculate_rhythm_state(event)
        
        return self.stats[self.home_team_id], self.stats[self.away_team_id], rhythm

    def _calculate_rhythm_state(self, current_event: MatchEvent) -> RhythmState:
        """
        Computes the Control vs Chaos Index:
        - 100 = Total Tactical Control (sustained passing strings, low turnover, controlled tempo)
        - 0 = Total Chaos (rapid turnovers, high tackle density, frenetic transitional play)
        """
        if not self.recent_events:
            return RhythmState()
            
        recent_list = list(self.recent_events)
        turnovers = sum(1 for e in recent_list if e.event_type in [EventType.TACKLE, EventType.INTERCEPTION])
        pressured_count = sum(1 for e in recent_list if e.under_pressure)
        completed_passes = sum(1 for e in recent_list if e.event_type == EventType.PASS and e.pass_outcome == PassOutcome.COMPLETE)
        
        # Chaos score rises with turnovers and pressure, falls with completed passes
        chaos_factor = (turnovers * 12.0) + (pressured_count * 4.0) - (completed_passes * 3.5)
        control_index = round(max(5.0, min(95.0, 65.0 - chaos_factor)), 1)
        
        # Pressure index
        recent_pressure = sum(e.pressure_intensity for e in recent_list) / len(recent_list)
        
        # Momentum leader
        home_recent = sum(1 for e in recent_list if e.team_id == self.home_team_id)
        momentum_team = self.home_team_id if home_recent >= (len(recent_list) / 2) else self.away_team_id
        
        # Dominant Zone
        avg_x = sum(e.location.x for e in recent_list) / len(recent_list)
        if avg_x < 33:
            zone = "Defensive Third"
        elif avg_x < 66:
            zone = "Midfield Battleground"
        else:
            zone = "Attacking Final Third"
            
        pace = "Frenetic" if control_index < 35 else ("High" if control_index < 55 else ("Medium" if control_index < 75 else "Controlled"))
        
        return RhythmState(
            control_vs_chaos_index=control_index,
            tactical_pressure_index=round(recent_pressure, 1),
            momentum_team_id=momentum_team,
            dominant_zone=zone,
            pace_rating=pace
        )

    def seed_stats(self, minute: int, home_goals: int, away_goals: int, home_shots: int, away_shots: int):
        """Seeds cumulative team stats when synchronizing to an ongoing live match."""
        h = self.stats[self.home_team_id]
        a = self.stats[self.away_team_id]

        h.goals = home_goals
        h.total_shots = max(home_goals, home_shots)
        h.shots_on_target = max(home_goals, int(h.total_shots * 0.46))
        h.total_xG = round(home_goals * 0.82 + (h.total_shots - home_goals) * 0.08, 2)
        h.corners = max(0, int(minute * 0.12))
        h.fouls = max(0, int(minute * 0.11))
        h.cards_yellow = min(4, int(minute * 0.025))
        h.cards_red = 0
        h.total_passes = max(10, int(minute * 5.4))
        h.successful_passes = int(h.total_passes * 0.85)
        h.pass_accuracy_pct = 85.0
        h.possession_pct = 52.0
        h.avg_ball_speed_kmh = 54.0
        h.tackles_won = max(1, int(minute * 0.18))

        a.goals = away_goals
        a.total_shots = max(away_goals, away_shots)
        a.shots_on_target = max(away_goals, int(a.total_shots * 0.44))
        a.total_xG = round(away_goals * 0.82 + (a.total_shots - away_goals) * 0.08, 2)
        a.corners = max(0, int(minute * 0.09))
        a.fouls = max(0, int(minute * 0.13))
        a.cards_yellow = min(5, int(minute * 0.035))
        a.cards_red = 0
        a.total_passes = max(10, int(minute * 4.9))
        a.successful_passes = int(a.total_passes * 0.83)
        a.pass_accuracy_pct = 83.0
        a.possession_pct = 48.0
        a.avg_ball_speed_kmh = 55.0
        a.tackles_won = max(1, int(minute * 0.19))
