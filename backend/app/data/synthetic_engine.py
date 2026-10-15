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
    - Sustained Possession Strings: 8 to 20 consecutive passes before turnovers
    - Realistic distances: 10m to 28m ground passes between tactical partners (no random pitch jumps)
    - Realistic scorelines (1-0, 2-1, 1-1, 0-0, 2-0) and 10-15 total shots per team across 90 minutes
    """

    def __init__(self, home_team_id: str = "arsenal", away_team_id: str = "mancity", match_id: str = "EPL-2026-LIVE"):
        self.match_id = match_id
        all_teams = get_premier_league_teams()
        self.home_team = all_teams.get(home_team_id, all_teams["arsenal"])
        self.away_team = all_teams.get(away_team_id, all_teams["mancity"])

        # Reset initial tactical positions
        self._reset_player_base_positions()

        self.minute = 1
        self.second = 0
        self.period = "1H"
        self.chain_id = 1
        self.possession_team_id = self.home_team.id
        self.current_ball_pos = PitchCoordinates(x=20.0, y=50.0)  # Starts with CBs building up
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

    def _reset_player_base_positions(self):
        """Sets standard tactical coordinates for 4-3-3 / 4-2-3-1 formations."""
        # Home team (plays Left to Right: attacking x=100)
        h_pos = {
            "GK": (6.0, 50.0),
            "RB": (28.0, 84.0),
            "CB": [(22.0, 62.0), (22.0, 38.0)],
            "LB": (28.0, 16.0),
            "CDM": (40.0, 50.0),
            "CM": (48.0, 36.0),
            "CAM": (56.0, 62.0),
            "RW": (68.0, 82.0),
            "LW": (68.0, 18.0),
            "ST": (72.0, 50.0)
        }
        cb_idx = 0
        for p in self.home_team.players:
            if p.position == "CB":
                coords = h_pos["CB"][cb_idx]
                cb_idx = (cb_idx + 1) % 2
            else:
                coords = h_pos.get(p.position, (50.0, 50.0))
            p.current_coords = PitchCoordinates(x=coords[0], y=coords[1])

        # Away team (plays Right to Left: attacking x=0)
        a_pos = {
            "GK": (94.0, 50.0),
            "RB": (72.0, 16.0),
            "CB": [(78.0, 38.0), (78.0, 62.0)],
            "LB": (72.0, 84.0),
            "CDM": (60.0, 50.0),
            "CM": (52.0, 64.0),
            "CAM": (44.0, 38.0),
            "RW": (32.0, 18.0),
            "LW": (32.0, 82.0),
            "ST": (28.0, 50.0)
        }
        cb_idx_a = 0
        for p in self.away_team.players:
            if p.position == "CB":
                coords = a_pos["CB"][cb_idx_a]
                cb_idx_a = (cb_idx_a + 1) % 2
            else:
                coords = a_pos.get(p.position, (50.0, 50.0))
            p.current_coords = PitchCoordinates(x=coords[0], y=coords[1])

    def _calculate_pitch_distance_meters(self, p1: PitchCoordinates, p2: PitchCoordinates) -> float:
        dx = (p2.x - p1.x) * 1.05
        dy = (p2.y - p1.y) * 0.68
        return round(math.sqrt(dx**2 + dy**2), 1)

    def _get_tactical_teammates(self, actor: PlayerProfile, is_home: bool) -> List[PlayerProfile]:
        """Returns realistic passing options based on current buildup phase."""
        team = self.home_team if is_home else self.away_team
        candidates = [p for p in team.players if p.id != actor.id]

        # Phase 0: Buildup -> pass to nearby CBs, FBs, or CDMs
        if self.possession_phase == 0:
            preferred = [p for p in candidates if p.position in ["GK", "CB", "LB", "RB", "CDM"]]
            return preferred if preferred else candidates

        # Phase 1: Progression -> pass to CDMs, CMs, CAM, or advancing FBs
        elif self.possession_phase == 1:
            preferred = [p for p in candidates if p.position in ["CDM", "CM", "CAM", "LB", "RB", "LW", "RW"]]
            return preferred if preferred else candidates

        # Phase 2: Final Third -> pass to Wingers, ST, or CAM in the box
        else:
            preferred = [p for p in candidates if p.position in ["CAM", "ST", "LW", "RW", "CM"]]
            return preferred if preferred else candidates

    def generate_next_event(self) -> MatchEvent:
        """
        Generates realistic football play following genuine tactical phases.
        """
        # Clock progression: 3-6 seconds per pass/action
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

            # Realistic xG calculation
            base_xg = 0.42 if dist < 12 else (0.18 if dist < 20 else 0.05)
            xg = round(base_xg * random.uniform(0.85, 1.2), 2)
            shot_speed = round(random.uniform(88.0, 118.0), 1)

            actor.sprint_count += 1
            actor.current_speed_kmh = round(random.uniform(27.0, 32.5), 1)

            # Realistic goal probability: only 1 to 3 goals per full match
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

        # 2. DEFENSIVE TACKLE / TURNOVER (Rare: only ~8% chance per event, mostly after 10+ passes)
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

            # Flip possession and reset buildup phase for new team
            self.possession_team_id = defending_team.id
            self.chain_id += 1
            self.passes_in_current_chain = 0
            self.possession_phase = 0
            self.events_history.append(event)
            return event

        # 3. STRUCTURED PASSING COMBINATION (90%+ of standard play)
        teammates = self._get_tactical_teammates(actor, is_home)
        recipient = random.choice(teammates)

        # Natural incremental shift towards target zone
        step_forward = random.uniform(8.0, 18.0) if is_home else random.uniform(-18.0, -8.0)
        lateral_step = random.uniform(-15.0, 15.0)

        target_x = max(8.0, min(92.0, recipient.current_coords.x + (step_forward * 0.3)))
        target_y = max(10.0, min(90.0, recipient.current_coords.y + lateral_step))
        target_coords = PitchCoordinates(x=round(target_x, 1), y=round(target_y, 1))

        dist_m = self._calculate_pitch_distance_meters(self.current_ball_pos, target_coords)
        difficulty = round(min(0.88, max(0.08, (dist_m / 45.0) * 0.4 + (0.2 if under_pressure else 0.05))), 2)

        ball_speed = round(random.uniform(42.0, 68.0), 1)
        actor.current_speed_kmh = round(random.uniform(14.0, 22.0), 1)
        actor.distance_covered_meters += dist_m

        # Premier League high completion rate (88-94%)
        is_complete = random.random() < 0.91

        if is_complete:
            outcome = PassOutcome.COMPLETE
            self.current_ball_pos = target_coords
            recipient.current_coords = target_coords

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
