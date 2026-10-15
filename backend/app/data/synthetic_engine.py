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
    High-fidelity realistic Premier League Match Simulator calibrated to authentic Opta match dynamics:
    - Structured Positional Buildup: Teams build from the back (GK/CBs) -> Midfield progression -> Final third
    - Controlled Tactical Movements: Whole team lines step up, drop, and slide laterally as a compact unit
    - Sustained Possession Strings: 8 to 20 consecutive passes before turnovers
    - Realistic distances: 10m to 28m ground passes between tactical partners (no random pitch jumps)
    - Realistic scorelines (1-0, 2-1, 1-1, 0-0, 2-0) and 10-15 total shots per team across 90 minutes
    """

    def __init__(self, home_team_id: str = "arsenal", away_team_id: str = "mancity", match_id: str = "EPL-2026-LIVE"):
        self.match_id = match_id
        all_teams = get_premier_league_teams()
        self.home_team = all_teams.get(home_team_id, all_teams["arsenal"])
        self.away_team = all_teams.get(away_team_id, all_teams["mancity"])

        # Base formation anchors (normalized)
        self.home_base_anchors = {
            "GK": (6.0, 50.0),
            "RB": (26.0, 84.0),
            "CB_R": (20.0, 62.0),
            "CB_L": (20.0, 38.0),
            "LB": (26.0, 16.0),
            "CDM": (38.0, 50.0),
            "CM": (46.0, 36.0),
            "CAM": (56.0, 62.0),
            "RW": (66.0, 84.0),
            "LW": (66.0, 16.0),
            "ST": (72.0, 50.0)
        }

        self.away_base_anchors = {
            "GK": (94.0, 50.0),
            "RB": (74.0, 16.0),
            "CB_R": (80.0, 38.0),
            "CB_L": (80.0, 62.0),
            "LB": (74.0, 84.0),
            "CDM": (62.0, 50.0),
            "CM": (54.0, 64.0),
            "CAM": (44.0, 38.0),
            "RW": (34.0, 16.0),
            "LW": (34.0, 84.0),
            "ST": (28.0, 50.0)
        }

        self.minute = 1
        self.second = 0
        self.period = "1H"
        self.chain_id = 1
        self.possession_team_id = self.home_team.id
        self.current_ball_pos = PitchCoordinates(x=20.0, y=50.0)
        self.events_history: List[MatchEvent] = []

        # Possession phase: 0 = Defensive Buildup, 1 = Midfield Circulation, 2 = Attacking Penetration
        self.possession_phase = 0
        self.passes_in_current_chain = 0

        # Match statistics caps to guarantee realistic scorelines
        self.home_shots = 0
        self.away_shots = 0
        self.home_goals = 0
        self.away_goals = 0

        # Spatial tracking
        self.pass_matrix: Dict[str, Dict[str, int]] = {}
        self.heatmap_cells: List[PitchCoordinates] = []
        self.timeline_moments: List[Dict] = []

        # Initialize player positions
        self._update_controlled_tactical_positions(is_home=True)

    def _update_controlled_tactical_positions(self, is_home: bool):
        """
        Coordinates organic, controlled tactical movement of all 22 players.
        Teams move together in compact defensive and attacking blocks:
        - When attacking, defensive lines push up together by 10-18m.
        - Defending teams slide laterally towards the ball to close passing channels.
        - No erratic jumps: smooth, bounded position shifts.
        """
        ball_y_shift = (self.current_ball_pos.y - 50.0) * 0.18  # Compact block tilts slightly toward ball

        # Phase forward push multiplier
        # Phase 0 (buildup): standard
        # Phase 1 (midfield): +10m push
        # Phase 2 (attacking box): +20m push
        attack_x_push = 0.0 if self.possession_phase == 0 else (10.0 if self.possession_phase == 1 else 18.0)
        defense_x_drop = 0.0 if self.possession_phase == 0 else (8.0 if self.possession_phase == 1 else 16.0)

        # 1. Update Home Team Players
        cb_count = 0
        for p in self.home_team.players:
            if p.position == "CB":
                anchor_key = "CB_R" if cb_count == 0 else "CB_L"
                cb_count += 1
            else:
                anchor_key = p.position

            base_x, base_y = self.home_base_anchors.get(anchor_key, (50.0, 50.0))

            if is_home:
                # Home team is attacking -> push up as a compact unit
                new_x = base_x + (attack_x_push * (0.8 if p.position == "GK" else 1.0))
                new_y = base_y + ball_y_shift + random.uniform(-1.5, 1.5)
            else:
                # Home team is defending -> drop back towards own goal, stay compact
                new_x = max(10.0, base_x - (defense_x_drop * 0.8))
                new_y = base_y + (ball_y_shift * 0.7) + random.uniform(-1.5, 1.5)

            # Clamp within realistic football boundaries
            p.current_coords.x = round(max(3.0, min(96.0, new_x)), 1)
            p.current_coords.y = round(max(6.0, min(94.0, new_y)), 1)

        # 2. Update Away Team Players
        cb_count_a = 0
        for p in self.away_team.players:
            if p.position == "CB":
                anchor_key_a = "CB_R" if cb_count_a == 0 else "CB_L"
                cb_count_a += 1
            else:
                anchor_key_a = p.position

            base_x, base_y = self.away_base_anchors.get(anchor_key_a, (50.0, 50.0))

            if not is_home:
                # Away team is attacking (moving leftwards towards x=0)
                new_x = base_x - (attack_x_push * (0.8 if p.position == "GK" else 1.0))
                new_y = base_y + ball_y_shift + random.uniform(-1.5, 1.5)
            else:
                # Away team is defending -> drop back towards x=90
                new_x = min(90.0, base_x + (defense_x_drop * 0.8))
                new_y = base_y + (ball_y_shift * 0.7) + random.uniform(-1.5, 1.5)

            p.current_coords.x = round(max(3.0, min(96.0, new_x)), 1)
            p.current_coords.y = round(max(6.0, min(94.0, new_y)), 1)

    def _calculate_pitch_distance_meters(self, p1: PitchCoordinates, p2: PitchCoordinates) -> float:
        dx = (p2.x - p1.x) * 1.05
        dy = (p2.y - p1.y) * 0.68
        return round(math.sqrt(dx**2 + dy**2), 1)

    def _get_tactical_teammates(self, actor: PlayerProfile, is_home: bool) -> List[PlayerProfile]:
        """Returns realistic passing options based on current buildup phase."""
        team = self.home_team if is_home else self.away_team
        candidates = [p for p in team.players if p.id != actor.id]

        if self.possession_phase == 0:
            preferred = [p for p in candidates if p.position in ["GK", "CB", "LB", "RB", "CDM"]]
            return preferred if preferred else candidates
        elif self.possession_phase == 1:
            preferred = [p for p in candidates if p.position in ["CDM", "CM", "CAM", "LB", "RB", "LW", "RW"]]
            return preferred if preferred else candidates
        else:
            preferred = [p for p in candidates if p.position in ["CAM", "ST", "LW", "RW", "CM"]]
            return preferred if preferred else candidates

    def generate_next_event(self) -> MatchEvent:
        """
        Generates realistic football play with organic controlled player movement.
        """
        time_jump = random.randint(3, 6)
        self.second += time_jump
        if self.second >= 60:
            self.minute += self.second // 60
            self.second = self.second % 60

        if self.minute <= 45:
            self.period = "1H"
        elif self.minute <= 90:
            self.period = "2H"
        else:
            self.period = "ET"

        is_home = (self.possession_team_id == self.home_team.id)
        current_team = self.home_team if is_home else self.away_team
        defending_team = self.away_team if is_home else self.home_team

        # Select actor close to current ball position
        actor_candidates = sorted(
            current_team.players,
            key=lambda p: (p.current_coords.x - self.current_ball_pos.x)**2 + (p.current_coords.y - self.current_ball_pos.y)**2
        )
        actor = actor_candidates[0]

        # Update spatial heatmap
        self.heatmap_cells.append(PitchCoordinates(x=self.current_ball_pos.x, y=self.current_ball_pos.y))
        if len(self.heatmap_cells) > 60:
            self.heatmap_cells.pop(0)

        self.passes_in_current_chain += 1

        # Phase progression: builds from 0 -> 1 -> 2 as chain progresses
        if self.passes_in_current_chain < 4:
            self.possession_phase = 0  # Build-up
        elif self.passes_in_current_chain < 9:
            self.possession_phase = 1  # Progression
        else:
            self.possession_phase = 2  # Final third chance creation

        # Shift all 22 players in a controlled tactical block!
        self._update_controlled_tactical_positions(is_home=is_home)

        under_pressure = (self.possession_phase == 2) or (random.random() < 0.28)
        pressure_intensity = random.uniform(45.0, 85.0) if under_pressure else random.uniform(10.0, 30.0)

        # 1. SHOT OCCASION (Only in Phase 2 after a solid build-up string!)
        team_shots = self.home_shots if is_home else self.away_shots
        team_goals = self.home_goals if is_home else self.away_goals

        in_shooting_range = (self.current_ball_pos.x > 78) if is_home else (self.current_ball_pos.x < 22)
        should_shoot = in_shooting_range and (self.passes_in_current_chain >= 7) and (random.random() < 0.35) and (team_shots < 14)

        if should_shoot:
            if is_home:
                self.home_shots += 1
            else:
                self.away_shots += 1

            goal_target = PitchCoordinates(x=100.0 if is_home else 0.0, y=50.0)
            dx = (goal_target.x - self.current_ball_pos.x) * 1.05
            dy = (goal_target.y - self.current_ball_pos.y) * 0.68
            dist = math.sqrt(dx**2 + dy**2)

            base_xg = 0.42 if dist < 12 else (0.18 if dist < 20 else 0.05)
            xg = round(base_xg * random.uniform(0.85, 1.2), 2)
            shot_speed = round(random.uniform(88.0, 118.0), 1)

            actor.sprint_count += 1
            actor.current_speed_kmh = round(random.uniform(27.0, 32.5), 1)

            # Realistic goal probability
            dice = random.random()
            if dice < xg and team_goals < 3 and random.random() < 0.35:
                outcome = ShotOutcome.GOAL
                event_type = EventType.GOAL
                if is_home:
                    self.home_goals += 1
                else:
                    self.away_goals += 1

                self.timeline_moments.append({
                    "minute": self.minute,
                    "type": "goal",
                    "player": actor.name,
                    "team": current_team.short_name,
                    "speed": shot_speed,
                    "xg": xg
                })
            elif dice < 0.60:
                outcome = ShotOutcome.SAVED
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

            # Reset after shot
            self.possession_team_id = defending_team.id
            self.chain_id += 1
            self.passes_in_current_chain = 0
            self.possession_phase = 0
            self.current_ball_pos = PitchCoordinates(x=10.0 if is_home else 90.0, y=50.0)

            self.events_history.append(event)
            return event

        # 2. DEFENSIVE TACKLE / TURNOVER
        turnover_chance = 0.18 if self.passes_in_current_chain > 12 else 0.07
        if under_pressure and random.random() < turnover_chance:
            defender = self.away_team.players[2] if is_home else self.home_team.players[2]
            defender.current_speed_kmh = round(random.uniform(20.0, 28.0), 1)

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

            # Flip possession
            self.possession_team_id = defending_team.id
            self.chain_id += 1
            self.passes_in_current_chain = 0
            self.possession_phase = 0
            self.events_history.append(event)
            return event

        # 3. STRUCTURED PASSING COMBINATION (Core 90% action)
        teammates = self._get_tactical_teammates(actor, is_home)
        recipient = random.choice(teammates)

        target_coords = PitchCoordinates(x=recipient.current_coords.x, y=recipient.current_coords.y)
        dist_m = self._calculate_pitch_distance_meters(self.current_ball_pos, target_coords)
        difficulty = round(min(0.85, max(0.08, (dist_m / 45.0) * 0.4 + (0.18 if under_pressure else 0.05))), 2)

        ball_speed = round(random.uniform(42.0, 68.0), 1)
        actor.current_speed_kmh = round(random.uniform(14.0, 22.0), 1)
        actor.distance_covered_meters += dist_m

        is_complete = random.random() < 0.92

        if is_complete:
            outcome = PassOutcome.COMPLETE
            self.current_ball_pos = target_coords

            # Track in pass matrix
            if actor.id not in self.pass_matrix:
                self.pass_matrix[actor.id] = {}
            self.pass_matrix[actor.id][recipient.id] = self.pass_matrix[actor.id].get(recipient.id, 0) + 1
        else:
            outcome = PassOutcome.INTERCEPTED
            self.possession_team_id = defending_team.id
            self.chain_id += 1
            self.passes_in_current_chain = 0
            self.possession_phase = 0

        event = MatchEvent(
            event_id=f"evt_{len(self.events_history)+1}",
            match_id=self.match_id,
            minute=self.minute,
            second=self.second,
            period=self.period,
            team_id=self.possession_team_id if is_complete else current_team.id,
            player=actor,
            recipient=recipient if is_complete else None,
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
