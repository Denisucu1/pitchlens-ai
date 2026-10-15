import math
import random
from typing import List, Optional, Tuple, Dict
from app.data.models import (
    MatchEvent, EventType, PassOutcome, ShotOutcome,
    PitchCoordinates, PlayerProfile, TeamProfile
)
from app.data.teams_data import get_premier_league_teams

class SyntheticMatchEngine:
    """
    Realistic Premier League Match Simulator calibrated to real-world Opta statistics:
    - 90-minute realistic clock progression (advancing 3-8s per event)
    - Realistic event distribution: ~82% passes, ~3% shots, ~7% tackles/interceptions
    - Real-world Premier League scorelines: 1-0, 2-1, 1-1, 2-2, 3-1 (typically 1 to 4 goals per match)
    - Pass network matrix & pitch heatmap tracking
    - Real physical speed calculations (ball velocity, sprint speed, pass difficulty)
    """

    def __init__(self, home_team_id: str = "arsenal", away_team_id: str = "mancity", match_id: str = "EPL-2026-LIVE"):
        self.match_id = match_id
        all_teams = get_premier_league_teams()
        self.home_team = all_teams.get(home_team_id, all_teams["arsenal"])
        self.away_team = all_teams.get(away_team_id, all_teams["mancity"])

        self.minute = 1
        self.second = 0
        self.period = "1H"
        self.chain_id = 1
        self.possession_team_id = self.home_team.id
        self.current_ball_pos = PitchCoordinates(x=50.0, y=50.0)
        self.events_history: List[MatchEvent] = []

        # Real-world counters to guarantee realistic match stats
        self.home_shots_count = 0
        self.away_shots_count = 0
        self.home_goals_count = 0
        self.away_goals_count = 0

        # Spatial Analytics Data
        self.pass_matrix: Dict[str, Dict[str, int]] = {}  # {player_from: {player_to: count}}
        self.heatmap_cells: List[PitchCoordinates] = []   # Last 60 ball positions for density map
        self.timeline_moments: List[Dict] = []            # Key events for timeline bar

    def _calculate_pitch_distance_meters(self, p1: PitchCoordinates, p2: PitchCoordinates) -> float:
        """Converts normalized 100x100 pitch coordinates to meters on a standard 105x68m pitch."""
        dx = (p2.x - p1.x) * 1.05
        dy = (p2.y - p1.y) * 0.68
        return round(math.sqrt(dx**2 + dy**2), 1)

    def _calculate_pass_difficulty(self, distance_m: float, under_pressure: bool, pressure_intensity: float) -> float:
        """
        Calculates normalized pass difficulty (0.00 to 1.00) based on distance,
        defensive pressure, and field congestion.
        """
        dist_factor = min(1.0, distance_m / 65.0) * 0.52
        pressure_factor = (pressure_intensity / 100.0) * 0.38 if under_pressure else 0.05
        difficulty = dist_factor + pressure_factor + random.uniform(-0.04, 0.04)
        return round(max(0.06, min(0.96, difficulty)), 2)

    def _calculate_xg(self, shot_pos: PitchCoordinates, goal_x: float = 100.0, goal_y: float = 50.0) -> float:
        """
        Calibrated Premier League Expected Goals (xG) model:
        Average shot in Premier League has ~0.10 xG. Prime chances inside six-yard box ~0.45 - 0.70 xG.
        """
        dx = (goal_x - shot_pos.x) * 1.05
        dy = (goal_y - shot_pos.y) * 0.68
        distance = math.sqrt(dx**2 + dy**2)

        if distance < 7:
            base_xg = 0.52
        elif distance < 14:
            base_xg = 0.28
        elif distance < 22:
            base_xg = 0.12
        elif distance < 32:
            base_xg = 0.04
        else:
            base_xg = 0.01

        angle_rad = math.atan2(abs(dy), max(0.1, dx))
        angle_factor = max(0.25, math.cos(angle_rad))
        xg = base_xg * angle_factor * random.uniform(0.85, 1.15)
        return round(max(0.01, min(0.85, xg)), 2)

    def _get_active_players(self, team_id: str) -> List[PlayerProfile]:
        team = self.home_team if team_id == self.home_team.id else self.away_team
        return team.players

    def _select_actor_by_proximity(self, team_id: str, near_pos: PitchCoordinates) -> PlayerProfile:
        players = self._get_active_players(team_id)
        # Weight by distance to ball
        sorted_players = sorted(
            players,
            key=lambda p: (p.current_coords.x - near_pos.x)**2 + (p.current_coords.y - near_pos.y)**2
        )
        return random.choice(sorted_players[:3]) if len(sorted_players) >= 3 else sorted_players[0]

    def generate_next_event(self) -> MatchEvent:
        """
        Generates the next event with real Premier League pacing and statistical distribution.
        """
        # Realistic time increment: 3 to 7 seconds per football action
        time_jump = random.randint(3, 7)
        self.second += time_jump
        if self.second >= 60:
            self.minute += self.second // 60
            self.second = self.second % 60

        # Handle half-time and full-time transitions
        if self.minute <= 45:
            self.period = "1H"
        elif self.minute <= 90:
            self.period = "2H"
        else:
            self.period = "ET"

        current_team = self.home_team if self.possession_team_id == self.home_team.id else self.away_team
        defending_team = self.away_team if self.possession_team_id == self.home_team.id else self.home_team
        is_home = (self.possession_team_id == self.home_team.id)

        actor = self._select_actor_by_proximity(self.possession_team_id, self.current_ball_pos)

        # Track spatial position for heatmap
        self.heatmap_cells.append(PitchCoordinates(x=self.current_ball_pos.x, y=self.current_ball_pos.y))
        if len(self.heatmap_cells) > 80:
            self.heatmap_cells.pop(0)

        # Tactical context
        under_pressure = random.random() < 0.38
        pressure_intensity = random.uniform(30.0, 92.0) if under_pressure else random.uniform(5.0, 25.0)

        # Check field location
        in_attacking_third = (self.current_ball_pos.x > 75) if is_home else (self.current_ball_pos.x < 25)

        # REALISTIC SHOT FREQUENCY:
        # Shots only happen ~3.5% of the time, and only in attacking positions!
        # Total team shots over 90 mins will naturally be ~10-15 per match.
        rand_event = random.random()
        can_shoot = in_attacking_third and (rand_event < 0.12)
        
        # Max limit check so scorelines remain realistic (1-0, 2-1, 1-1, etc.)
        team_shots = self.home_shots_count if is_home else self.away_shots_count
        team_goals = self.home_goals_count if is_home else self.away_goals_count
        
        # 1. SHOT / GOAL OCCASION
        if can_shoot and team_shots < 18:
            if is_home:
                self.home_shots_count += 1
            else:
                self.away_shots_count += 1

            goal_target = PitchCoordinates(x=100.0 if is_home else 0.0, y=50.0)
            xg = self._calculate_xg(self.current_ball_pos, goal_target.x, goal_target.y)
            shot_speed = round(random.uniform(84.0, 124.5), 1)

            actor.sprint_count += 1
            actor.current_speed_kmh = round(random.uniform(26.0, 33.5), 1)

            # Realistic goal probability based on xG & max score bounds
            dice = random.random()
            # In football, ~10% of total shots become goals
            if dice < xg and team_goals < 4 and random.random() < 0.40:
                outcome = ShotOutcome.GOAL
                event_type = EventType.GOAL
                if is_home:
                    self.home_goals_count += 1
                else:
                    self.away_goals_count += 1
                
                # Record to timeline moments
                self.timeline_moments.append({
                    "minute": self.minute,
                    "type": "goal",
                    "player": actor.name,
                    "team": current_team.short_name,
                    "speed": shot_speed,
                    "xg": xg
                })
            elif dice < 0.55:
                outcome = ShotOutcome.SAVED
                event_type = EventType.SHOT
            elif dice < 0.78:
                outcome = ShotOutcome.BLOCKED
                event_type = EventType.SHOT
            else:
                outcome = ShotOutcome.OFF_TARGET
                event_type = EventType.SHOT

            event = MatchEvent(
                event_id=f"evt_{len(self.events_history)+1}",
                match_id=self.match_id,
                minute=self.minute,
                second=self.second,
                period=self.period,
                team_id=self.possession_team_id,
                player=actor,
                event_type=event_type,
                location=self.current_ball_pos,
                end_location=goal_target,
                shot_speed_kmh=shot_speed,
                ball_speed_kmh=shot_speed,
                player_speed_kmh=actor.current_speed_kmh,
                xG=xg,
                shot_outcome=outcome,
                under_pressure=under_pressure,
                pressure_intensity=pressure_intensity,
                possession_chain_id=f"chain_{self.chain_id}"
            )

            # Reset ball or change possession
            if outcome == ShotOutcome.GOAL:
                self.current_ball_pos = PitchCoordinates(x=50.0, y=50.0)
                self.possession_team_id = defending_team.id
                self.chain_id += 1
            elif outcome in [ShotOutcome.SAVED, ShotOutcome.OFF_TARGET]:
                self.possession_team_id = defending_team.id
                self.chain_id += 1
                self.current_ball_pos = PitchCoordinates(x=6.0 if is_home else 94.0, y=50.0)

            self.events_history.append(event)
            return event

        # 2. DEFENSIVE TACKLE / TURNOVER (~12% probability under pressure)
        elif under_pressure and rand_event < 0.16:
            defender = self._select_actor_by_proximity(defending_team.id, self.current_ball_pos)
            defender.current_speed_kmh = round(random.uniform(21.0, 29.5), 1)
            defender.sprint_count += 1

            event = MatchEvent(
                event_id=f"evt_{len(self.events_history)+1}",
                match_id=self.match_id,
                minute=self.minute,
                second=self.second,
                period=self.period,
                team_id=defending_team.id,
                player=defender,
                event_type=EventType.TACKLE,
                location=self.current_ball_pos,
                player_speed_kmh=defender.current_speed_kmh,
                under_pressure=True,
                pressure_intensity=pressure_intensity,
                possession_chain_id=f"chain_{self.chain_id}"
            )

            # Possession flips
            self.possession_team_id = defending_team.id
            self.chain_id += 1
            self.events_history.append(event)
            return event

        # 3. PASSING COMBINATION (Standard core football action, ~82% of all events)
        else:
            candidates = [p for p in self._get_active_players(self.possession_team_id) if p.id != actor.id]
            recipient = random.choice(candidates)

            # Progressive ball movement
            forward_bias = random.uniform(4.0, 18.0) if is_home else random.uniform(-18.0, -4.0)
            flank_shift = random.uniform(-18.0, 18.0)

            target_x = max(3.0, min(97.0, self.current_ball_pos.x + forward_bias))
            target_y = max(6.0, min(94.0, self.current_ball_pos.y + flank_shift))
            target_coords = PitchCoordinates(x=round(target_x, 1), y=round(target_y, 1))

            dist_m = self._calculate_pitch_distance_meters(self.current_ball_pos, target_coords)
            difficulty = self._calculate_pass_difficulty(dist_m, under_pressure, pressure_intensity)

            ball_speed = round(random.uniform(36.0, 72.0) + (dist_m * 0.35), 1)
            actor.current_speed_kmh = round(random.uniform(12.0, 24.5), 1)
            actor.distance_covered_meters += dist_m

            # Realistic pass completion rate (~80-88% in Premier League)
            success_threshold = (actor.passing_skill / 100.0) * (1.18 - (difficulty * 0.45))
            if random.random() < success_threshold:
                outcome = PassOutcome.COMPLETE
                self.current_ball_pos = target_coords
                recipient.current_coords = target_coords

                # Record into pass matrix for Pass Network visualizer
                if actor.id not in self.pass_matrix:
                    self.pass_matrix[actor.id] = {}
                self.pass_matrix[actor.id][recipient.id] = self.pass_matrix[actor.id].get(recipient.id, 0) + 1
            else:
                outcome = PassOutcome.INTERCEPTED
                self.possession_team_id = defending_team.id
                self.chain_id += 1

            event = MatchEvent(
                event_id=f"evt_{len(self.events_history)+1}",
                match_id=self.match_id,
                minute=self.minute,
                second=self.second,
                period=self.period,
                team_id=self.possession_team_id if outcome == PassOutcome.COMPLETE else current_team.id,
                player=actor,
                recipient=recipient if outcome == PassOutcome.COMPLETE else None,
                event_type=EventType.PASS,
                location=self.current_ball_pos,
                end_location=target_coords,
                ball_speed_kmh=ball_speed,
                player_speed_kmh=actor.current_speed_kmh,
                pass_distance_m=dist_m,
                pass_difficulty_rating=difficulty,
                pass_outcome=outcome,
                under_pressure=under_pressure,
                pressure_intensity=pressure_intensity,
                possession_chain_id=f"chain_{self.chain_id}"
            )

            self.events_history.append(event)
            return event
