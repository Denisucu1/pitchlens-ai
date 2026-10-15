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
    - 90-minute hard stop (Full-Time lock at 90+3', Half-Time at 45')
    - Exact Ball-to-Player Tracking: The ball ALWAYS travels directly to the receiving player's feet
    - Consecutive Possession Chains: Saliba -> Gabriel -> Rice -> Odegaard -> Saka
    - Controlled Tactical Movements: Whole team lines step up, drop, and slide laterally as a compact unit
    - Realistic scorelines (1-0, 2-1, 1-1, 0-0, 2-0)
    """

    def __init__(self, home_team_id: str = "arsenal", away_team_id: str = "mancity", match_id: str = "EPL-2026-LIVE"):
        self.match_id = match_id
        all_teams = get_premier_league_teams()
        self.home_team = all_teams.get(home_team_id, all_teams["arsenal"])
        self.away_team = all_teams.get(away_team_id, all_teams["mancity"])

        # Base formation anchors (normalized 0-100m)
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

        self.reset_match()

    def reset_match(self):
        """Resets the match to minute 1:00."""
        self.minute = 1
        self.second = 0
        self.period = "1H"
        self.is_finished = False
        self.is_half_time = False
        self.chain_id = 1
        self.possession_team_id = self.home_team.id
        self.events_history: List[MatchEvent] = []

        # Current ball holder (Starts with Home Centre-back)
        self.current_actor = self.home_team.players[2]  # Saliba / CB
        self.current_ball_pos = PitchCoordinates(
            x=self.current_actor.current_coords.x,
            y=self.current_actor.current_coords.y
        )

        self.possession_phase = 0
        self.passes_in_current_chain = 0

        self.home_shots = 0
        self.away_shots = 0
        self.home_goals = 0
        self.away_goals = 0

        self.pass_matrix: Dict[str, Dict[str, int]] = {}
        self.heatmap_cells: List[PitchCoordinates] = []
        self.timeline_moments: List[Dict] = []

        self._update_controlled_tactical_positions(is_home=True)

    def _update_controlled_tactical_positions(self, is_home: bool):
        """
        Coordinates organic, compact tactical block movement for all 22 players.
        Lines push up, drop back, and slide laterally towards the ball channel.
        """
        ball_y_shift = (self.current_ball_pos.y - 50.0) * 0.16

        attack_x_push = 0.0 if self.possession_phase == 0 else (10.0 if self.possession_phase == 1 else 18.0)
        defense_x_drop = 0.0 if self.possession_phase == 0 else (8.0 if self.possession_phase == 1 else 15.0)

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
                new_x = base_x + (attack_x_push * (0.4 if p.position == "GK" else 1.0))
                new_y = base_y + ball_y_shift + random.uniform(-1.0, 1.0)
            else:
                new_x = max(10.0, base_x - (defense_x_drop * 0.8))
                new_y = base_y + (ball_y_shift * 0.6) + random.uniform(-1.0, 1.0)

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
                new_x = base_x - (attack_x_push * (0.4 if p.position == "GK" else 1.0))
                new_y = base_y + ball_y_shift + random.uniform(-1.0, 1.0)
            else:
                new_x = min(90.0, base_x + (defense_x_drop * 0.8))
                new_y = base_y + (ball_y_shift * 0.6) + random.uniform(-1.0, 1.0)

            p.current_coords.x = round(max(3.0, min(96.0, new_x)), 1)
            p.current_coords.y = round(max(6.0, min(94.0, new_y)), 1)

    def _calculate_pitch_distance_meters(self, p1: PitchCoordinates, p2: PitchCoordinates) -> float:
        dx = (p2.x - p1.x) * 1.05
        dy = (p2.y - p1.y) * 0.68
        return round(math.sqrt(dx**2 + dy**2), 1)

    def _get_tactical_pass_options(self, actor: PlayerProfile, is_home: bool) -> List[PlayerProfile]:
        """Returns realistic passing options according to the current buildup phase."""
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
        Generates realistic football play with exact ball-to-foot tracking and 90-minute Full-Time stop.
        """
        # If match is finished, keep emitting Full-Time state without advancing clock
        if self.is_finished:
            return self.events_history[-1] if self.events_history else MatchEvent(
                event_id="evt_ft",
                match_id=self.match_id,
                minute=90,
                second=0,
                period="FT",
                team_id=self.home_team.id,
                player=self.home_team.players[0],
                event_type=EventType.SAVE,
                location=PitchCoordinates(x=50.0, y=50.0),
                player_speed_kmh=0.0
            )

        # Advance match clock by 15-30 seconds per action cycle (realistic 90-minute progression)
        self.second += random.randint(15, 28)
        if self.second >= 60:
            self.minute += self.second // 60
            self.second = self.second % 60

        # Check Half-Time at 45'
        if self.minute == 45 and not self.is_half_time and self.second < 30:
            self.is_half_time = True
            self.period = "1H"

        # Check Full-Time Stop at 90+3'
        if self.minute >= 93:
            self.minute = 90
            self.second = 0
            self.period = "FT"
            self.is_finished = True

        if not self.is_finished:
            if self.minute <= 45:
                self.period = "1H"
            else:
                self.period = "2H"

        is_home = (self.possession_team_id == self.home_team.id)
        current_team = self.home_team if is_home else self.away_team
        defending_team = self.away_team if is_home else self.home_team

        # Ensure current actor belongs to possession team
        if self.current_actor.team_id != self.possession_team_id:
            self.current_actor = current_team.players[2]  # Default to CB if flipped

        actor = self.current_actor

        # The ball starts EXACTLY at the feet of the current actor!
        self.current_ball_pos = PitchCoordinates(x=actor.current_coords.x, y=actor.current_coords.y)

        # Record spatial heatmap
        self.heatmap_cells.append(PitchCoordinates(x=self.current_ball_pos.x, y=self.current_ball_pos.y))
        if len(self.heatmap_cells) > 80:
            self.heatmap_cells.pop(0)

        self.passes_in_current_chain += 1

        # Phase progression: 0 (Buildup) -> 1 (Midfield) -> 2 (Box)
        if self.passes_in_current_chain < 4:
            self.possession_phase = 0
        elif self.passes_in_current_chain < 9:
            self.possession_phase = 1
        else:
            self.possession_phase = 2

        # Shift all 22 players in a coordinated tactical block!
        self._update_controlled_tactical_positions(is_home=is_home)

        # Make sure actor position matches updated coordinates
        self.current_ball_pos = PitchCoordinates(x=actor.current_coords.x, y=actor.current_coords.y)

        under_pressure = (self.possession_phase == 2) or (random.random() < 0.25)
        pressure_intensity = random.uniform(40.0, 80.0) if under_pressure else random.uniform(10.0, 30.0)

        # 1. SHOT OCCASION (Only in Phase 2 in attacking zone!)
        team_shots = self.home_shots if is_home else self.away_shots
        team_goals = self.home_goals if is_home else self.away_goals

        in_shooting_range = (self.current_ball_pos.x > 75) if is_home else (self.current_ball_pos.x < 25)
        should_shoot = in_shooting_range and (self.passes_in_current_chain >= 6) and (random.random() < 0.35) and (team_shots < 14)

        if should_shoot:
            if is_home:
                self.home_shots += 1
            else:
                self.away_shots += 1

            goal_target = PitchCoordinates(x=100.0 if is_home else 0.0, y=50.0)
            dx = (goal_target.x - self.current_ball_pos.x) * 1.05
            dy = (goal_target.y - self.current_ball_pos.y) * 0.68
            dist = math.sqrt(dx**2 + dy**2)

            base_xg = 0.45 if dist < 12 else (0.18 if dist < 20 else 0.05)
            xg = round(base_xg * random.uniform(0.85, 1.15), 2)
            shot_speed = round(random.uniform(90.0, 122.0), 1)

            actor.sprint_count += 1
            actor.current_speed_kmh = round(random.uniform(27.0, 32.5), 1)

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

            # Flip possession after shot
            self.possession_team_id = defending_team.id
            self.chain_id += 1
            self.passes_in_current_chain = 0
            self.possession_phase = 0
            # Next actor is opposition GK or CB
            self.current_actor = defending_team.players[0] if outcome in [ShotOutcome.SAVED, ShotOutcome.OFF_TARGET] else defending_team.players[2]
            self.current_ball_pos = PitchCoordinates(x=self.current_actor.current_coords.x, y=self.current_actor.current_coords.y)

            self.events_history.append(event)
            return event

        # 2. DEFENSIVE TACKLE (Rare: only ~8% chance per event)
        turnover_chance = 0.18 if self.passes_in_current_chain > 12 else 0.07
        if under_pressure and random.random() < turnover_chance:
            defender = defending_team.players[2]
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

            self.possession_team_id = defending_team.id
            self.current_actor = defender
            self.chain_id += 1
            self.passes_in_current_chain = 0
            self.possession_phase = 0
            self.events_history.append(event)
            return event

        # 3. STRUCTURED PASSING COMBINATION (The core ~88% of action)
        # Select recipient from teammates
        options = self._get_tactical_pass_options(actor, is_home)
        recipient = random.choice(options)

        # EXACT BALL-TO-PLAYER CONNECTION:
        # The pass destination is EXACTLY the recipient's coordinates!
        target_coords = PitchCoordinates(
            x=recipient.current_coords.x,
            y=recipient.current_coords.y
        )

        dist_m = self._calculate_pitch_distance_meters(self.current_ball_pos, target_coords)
        difficulty = round(min(0.85, max(0.08, (dist_m / 45.0) * 0.4 + (0.18 if under_pressure else 0.05))), 2)

        ball_speed = round(random.uniform(42.0, 68.0), 1)
        actor.current_speed_kmh = round(random.uniform(14.0, 22.0), 1)
        actor.distance_covered_meters += dist_m

        is_complete = random.random() < 0.93

        if is_complete:
            outcome = PassOutcome.COMPLETE
            # The recipient becomes the new current_actor for the next pass!
            self.current_actor = recipient
            self.current_ball_pos = target_coords

            if actor.id not in self.pass_matrix:
                self.pass_matrix[actor.id] = {}
            self.pass_matrix[actor.id][recipient.id] = self.pass_matrix[actor.id].get(recipient.id, 0) + 1
        else:
            outcome = PassOutcome.INTERCEPTED
            self.possession_team_id = defending_team.id
            self.current_actor = defending_team.players[2]
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
