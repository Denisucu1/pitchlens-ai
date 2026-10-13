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
                
            # 2. Shot & xG Tracking
            elif event.event_type in [EventType.SHOT, EventType.GOAL]:
                team_stats.total_shots += 1
                if event.xG is not None:
                    team_stats.total_xG = round(team_stats.total_xG + event.xG, 2)
                    
                if event.shot_outcome in [ShotOutcome.GOAL, ShotOutcome.SAVED]:
                    team_stats.shots_on_target += 1
                    
                if event.shot_outcome == ShotOutcome.GOAL:
                    team_stats.goals += 1

            # 3. Defensive stats
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
