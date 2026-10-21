import math
import random
from typing import List, Optional, Tuple, Dict
from app.data.models import (
    MatchEvent, EventType, PassOutcome, ShotOutcome,
    PitchCoordinates, PlayerProfile, TeamProfile
)
from app.data.teams_data import get_premier_league_teams


# ─── GAME STATE MACHINE ───────────────────────────────────────────────
class GameState:
    BALANCED = "balanced"              # 0-0 or teams level
    ALL_OUT_ATTACK = "all_out_attack"  # Losing team throws everyone forward
    PARK_THE_BUS = "park_the_bus"      # Winning team sits deep, protects lead
    COUNTER_ATTACK = "counter_attack"  # Fast transition after winning ball
    HIGH_PRESS = "high_press"          # Aggressive pressing, hunting the ball
    TIME_WASTING = "time_wasting"      # Winning team in final minutes


# ─── POSITION CORRIDOR DEFINITIONS ────────────────────────────────────
# Each position has a movement corridor: (wander_x, wander_y) = how far from anchor they can roam
POSITION_CORRIDORS = {
    "GK":  (0.2, 1.2),  # GK stays strictly inside goalmouth
    "CB":  (4.0, 4.5),
    "RB":  (8.0, 5.0),
    "LB":  (8.0, 5.0),
    "CDM": (6.0, 6.0),
    "CM":  (7.0, 7.0),
    "CAM": (8.0, 7.0),
    "RW":  (8.0, 6.0),
    "LW":  (8.0, 6.0),
    "ST":  (9.0, 7.0),
}


class SyntheticMatchEngine:
    """
    High-fidelity Premier League Match Simulator v2.0
    
    Major systems:
    1. Game State Machine — tactical behavior changes based on score + minute
    2. Corridor Movement — players roam realistic areas, not fixed anchor points
    3. Off-Ball Runs — position-specific intelligent movement (overlaps, cutting inside, runs in behind)
    4. Lateral Ball Gravity — entire team slides toward the ball channel
    5. Momentum Surges — post-goal intensity spikes
    6. Fatigue System — stamina decreases, corridors shrink, speeds drop
    7. Half-Time Side Switch — teams swap ends at 45'
    """

    def __init__(self, home_team_id: str = "arsenal", away_team_id: str = "mancity", match_id: str = "EPL-2026-LIVE"):
        self.match_id = match_id
        all_teams = get_premier_league_teams()
        self.home_team = all_teams.get(home_team_id, all_teams["arsenal"])
        self.away_team = all_teams.get(away_team_id, all_teams["mancity"])

        # Base formation anchors (normalized 0-100m) — Home attacks RIGHT in 1H
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

        # Away attacks LEFT in 1H (mirrored)
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
        """Resets the match to minute 0:00 with center kickoff and pristine starting formations."""
        self.minute = 0
        self.second = 0
        self.period = "1H"
        self.is_finished = False
        self.is_half_time = False
        self.is_kickoff = True
        self.chain_id = 1
        self.possession_team_id = self.home_team.id
        self.events_history: List[MatchEvent] = []

        self.possession_phase = 0
        self.passes_in_current_chain = 0

        self.home_shots = 0
        self.away_shots = 0
        self.home_goals = 0
        self.away_goals = 0

        self.pass_matrix: Dict[str, Dict[str, int]] = {}
        self.heatmap_cells: List[PitchCoordinates] = []
        self.timeline_moments: List[Dict] = []

        # Game State Machine
        self.home_game_state = GameState.BALANCED
        self.away_game_state = GameState.BALANCED
        self.momentum_timer = 0        # ticks remaining of post-goal momentum surge
        self.momentum_team_id = ""     # team with the surge (the one that conceded)
        self.counter_attack_timer = 0  # ticks remaining of counter-attack burst
        self.pending_set_piece: Optional[str] = None  # "corner" | "penalty" | "free_kick"

        # Fatigue factors per player (1.0 = fresh, decreases over time)
        self.fatigue: Dict[str, float] = {}
        for p in self.home_team.players + self.away_team.players:
            self.fatigue[p.id] = 1.0

        # Reset player live match statistics
        for p in self.home_team.players + self.away_team.players:
            p.goals = 0
            p.shots = 0
            p.shots_on_target = 0
            p.passes_completed = 0
            p.passes_total = 0
            p.tackles_won = 0
            p.duels_won = 0
            p.interceptions = 0
            p.recoveries = 0
            p.fouls = 0
            p.saves = 0
            p.match_rating = 6.8
            p.distance_covered_meters = 0.0
            p.sprint_count = 0

        # Setup 1H Kickoff: ball at (50, 50), players arranged cleanly in their starting formation halves
        self._setup_kickoff_formation(is_2h=False)

        # Individual Player Heatmaps & Smooth Trajectory Tracking
        self.player_heatmaps: Dict[str, List[PitchCoordinates]] = {}
        self.player_momentum: Dict[str, Tuple[float, float]] = {}
        for p in self.home_team.players + self.away_team.players:
            self.player_heatmaps[p.id] = [PitchCoordinates(x=p.current_coords.x, y=p.current_coords.y)]
            self.player_momentum[p.id] = (0.0, 0.0)
            p.movement_angle_deg = 0.0
            p.target_coords = None
            p.heatmap = list(self.player_heatmaps[p.id])

    def _setup_kickoff_formation(self, is_2h: bool = False):
        """
        Positions all 22 players strictly inside their formation halves
        and places the ball precisely on the center circle mark (50.0, 50.0).

        1H (is_2h=False):
          - Home attacks Right (+x), takes kickoff from (50.0, 50.0)
          - Away defends Right, stays in their half (x >= 58.0)
        2H (is_2h=True):
          - Sides swap!
          - Away attacks Right (+x), takes kickoff from (50.0, 50.0)
          - Home defends Right, stays in their half (x >= 58.0)
        """
        self.current_ball_pos = PitchCoordinates(x=50.0, y=50.0)

        # Pristine Kickoff Formation Anchors (Left half of pitch: x <= 50, attacking Right)
        kickoff_kicking_team = {
            "GK": (6.0, 50.0),
            "LB": (20.0, 18.0),
            "CB_L": (16.0, 38.0),
            "CB_R": (16.0, 62.0),
            "RB": (20.0, 82.0),
            "CDM": (28.0, 50.0),
            "CM": (34.0, 36.0),
            "CAM": (36.0, 62.0),
            "LW": (42.0, 18.0),
            "RW": (42.0, 82.0),
            "ST": (49.5, 50.0)  # Exactly at the center spot touching the ball
        }

        # Pristine Kickoff Defending Team Anchors (Right half of pitch: x >= 50, outside 9.15m circle)
        kickoff_defending_team = {
            "GK": (94.0, 50.0),
            "RB": (80.0, 18.0),
            "CB_R": (84.0, 38.0),
            "CB_L": (84.0, 62.0),
            "LB": (80.0, 82.0),
            "CDM": (72.0, 50.0),
            "CM": (66.0, 64.0),
            "CAM": (64.0, 38.0),
            "RW": (60.0, 18.0),
            "LW": (60.0, 82.0),
            "ST": (60.5, 50.0)  # Outside the center circle
        }

        if not is_2h:
            # 1H: Home kicks off, Home attacks Right (+x)
            self.possession_team_id = self.home_team.id
            cb_idx = 0
            for p in self.home_team.players:
                key = self._get_anchor_key(p, cb_idx)
                if p.position == "CB":
                    cb_idx += 1
                pos = kickoff_kicking_team.get(key, (30.0, 50.0))
                p.current_coords = PitchCoordinates(x=pos[0], y=pos[1])
                p.target_coords = None
                p.movement_angle_deg = 0.0
                p.current_speed_kmh = 0.0

            cb_idx_a = 0
            for p in self.away_team.players:
                key = self._get_anchor_key(p, cb_idx_a)
                if p.position == "CB":
                    cb_idx_a += 1
                pos = kickoff_defending_team.get(key, (70.0, 50.0))
                p.current_coords = PitchCoordinates(x=pos[0], y=pos[1])
                p.target_coords = None
                p.movement_angle_deg = 180.0
                p.current_speed_kmh = 0.0

            # Kicker is Home Striker
            strikers = [p for p in self.home_team.players if p.position == "ST"]
            self.current_actor = strikers[0] if strikers else self.home_team.players[-1]

        else:
            # 2H: Away kicks off, Away attacks Right (+x), Home defends Right
            self.possession_team_id = self.away_team.id
            cb_idx_a = 0
            for p in self.away_team.players:
                key = self._get_anchor_key(p, cb_idx_a)
                if p.position == "CB":
                    cb_idx_a += 1
                pos = kickoff_kicking_team.get(key, (30.0, 50.0))
                p.current_coords = PitchCoordinates(x=pos[0], y=pos[1])
                p.target_coords = None
                p.movement_angle_deg = 0.0
                p.current_speed_kmh = 0.0

            cb_idx = 0
            for p in self.home_team.players:
                key = self._get_anchor_key(p, cb_idx)
                if p.position == "CB":
                    cb_idx += 1
                pos = kickoff_defending_team.get(key, (70.0, 50.0))
                p.current_coords = PitchCoordinates(x=pos[0], y=pos[1])
                p.target_coords = None
                p.movement_angle_deg = 180.0
                p.current_speed_kmh = 0.0

            # Kicker is Away Striker
            strikers = [p for p in self.away_team.players if p.position == "ST"]
            self.current_actor = strikers[0] if strikers else self.away_team.players[-1]

    def fast_forward_to(self, target_minute: int, score_h: int, score_a: int, goal_scorers: List[str] = None, is_finished: bool = False):
        """
        Fast-forwards the engine state to synchronize seamlessly with an ongoing live match,
        populating realistic cumulative statistics, player heatmaps, and pitch positions.
        """
        if target_minute == 0:
            self.minute = 0
            self.second = 0
            self.period = "1H"
            self.is_finished = False
            self.is_half_time = False
            self.is_kickoff = True
            self.home_goals = 0
            self.away_goals = 0
            self._setup_kickoff_formation(is_2h=False)
            return
        elif target_minute == 45:
            self.minute = 45
            self.second = 0
            self.period = "2H"
            self.is_finished = False
            self.is_half_time = False
            self.is_kickoff = True
            self.home_goals = score_h
            self.away_goals = score_a
            self._setup_kickoff_formation(is_2h=True)
            return

        self.minute = max(1, target_minute)
        self.second = random.randint(10, 50)
        self.period = "FT" if is_finished else ("2H" if self.minute > 45 else "1H")
        self.is_finished = is_finished
        self.is_half_time = False
        self.is_kickoff = False

        self.home_goals = score_h
        self.away_goals = score_a
        self.home_shots = max(score_h, int(self.minute * 0.16) + random.randint(0, 2) + score_h)
        self.away_shots = max(score_a, int(self.minute * 0.14) + random.randint(0, 2) + score_a)

        current_fatigue = max(0.65, 1.0 - (self.minute / 90.0) * 0.25)
        for p in self.home_team.players + self.away_team.players:
            stamina_factor = p.stamina / 100.0
            self.fatigue[p.id] = max(0.55, current_fatigue + (stamina_factor - 0.8) * 0.1)

        parsed_scorers = []
        if goal_scorers:
            for gs in goal_scorers:
                name_part = gs.split()[0] if gs else ""
                if name_part:
                    parsed_scorers.append(name_part.lower())

        home_scorers_assigned = 0
        away_scorers_assigned = 0

        # Assign home players realistic stats
        for p in self.home_team.players:
            is_gk = p.position == "GK"
            is_def = p.position in ["CB", "LB", "RB"]
            is_mid = p.position in ["CDM", "CM", "CAM"]
            is_fwd = p.position in ["RW", "LW", "ST"]

            dist_rate = 45.0 if is_gk else (120.0 if is_mid else 112.0)
            p.distance_covered_meters = round(self.minute * dist_rate * random.uniform(0.94, 1.06), 1)
            p.sprint_count = 1 if is_gk else int(self.minute * (0.28 if is_fwd else 0.20) * random.uniform(0.8, 1.2))

            pass_rate = 0.35 if is_gk else (0.85 if (is_mid or p.position == "CB") else 0.5)
            p.passes_total = max(1, int(self.minute * pass_rate * random.uniform(0.85, 1.15)))
            acc = 0.72 if is_gk else (0.88 if p.position == "CB" else 0.84)
            p.passes_completed = int(p.passes_total * acc)

            if is_def or p.position == "CDM":
                p.tackles_won = max(0, int(self.minute * 0.06 * random.uniform(0.7, 1.3)))
                p.duels_won = max(0, int(self.minute * 0.12 * random.uniform(0.7, 1.3)))
                p.interceptions = max(0, int(self.minute * 0.05 * random.uniform(0.7, 1.3)))
                p.recoveries = max(1, int(self.minute * 0.10 * random.uniform(0.8, 1.2)))
                p.fouls = max(0, int(self.minute * 0.02 * random.uniform(0.5, 1.5)))
            elif is_mid:
                p.tackles_won = max(0, int(self.minute * 0.04 * random.uniform(0.5, 1.3)))
                p.duels_won = max(0, int(self.minute * 0.09 * random.uniform(0.6, 1.3)))
                p.interceptions = max(0, int(self.minute * 0.04 * random.uniform(0.5, 1.3)))
                p.recoveries = max(1, int(self.minute * 0.12 * random.uniform(0.7, 1.3)))
                p.fouls = max(0, int(self.minute * 0.03 * random.uniform(0.5, 1.5)))
            elif is_fwd:
                p.tackles_won = max(0, int(self.minute * 0.015 * random.uniform(0.5, 1.2)))
                p.duels_won = max(0, int(self.minute * 0.05 * random.uniform(0.5, 1.2)))
                p.interceptions = max(0, int(self.minute * 0.01 * random.uniform(0.5, 1.2)))
                p.recoveries = max(0, int(self.minute * 0.04 * random.uniform(0.6, 1.2)))
                p.fouls = max(0, int(self.minute * 0.02 * random.uniform(0.5, 1.5)))
            else:
                p.saves = max(0, int(self.away_shots * random.uniform(0.5, 0.8)))

            p.goals = 0
            if any(name in p.name.lower() for name in parsed_scorers) and home_scorers_assigned < score_h:
                p.goals += 1
                home_scorers_assigned += 1

            if is_fwd:
                p.shots = max(p.goals, int(self.minute * 0.05 * random.uniform(0.6, 1.4)))
                p.shots_on_target = max(p.goals, int(p.shots * 0.55))
            elif is_mid:
                p.shots = max(p.goals, int(self.minute * 0.025 * random.uniform(0.4, 1.2)))
                p.shots_on_target = max(p.goals, int(p.shots * 0.5))

            base_r = 6.6 + (p.goals * 0.8) + (p.passes_completed * 0.01) + (p.tackles_won * 0.15)
            p.match_rating = round(min(9.5, max(5.9, base_r + random.uniform(-0.2, 0.2))), 1)

        while home_scorers_assigned < score_h:
            candidates = [p for p in self.home_team.players if p.position in ["ST", "RW", "LW", "CAM"]]
            if candidates:
                lucky = random.choice(candidates)
                lucky.goals += 1
                lucky.shots = max(lucky.shots, lucky.goals + 1)
                lucky.shots_on_target = max(lucky.shots_on_target, lucky.goals)
                lucky.match_rating = round(min(9.6, lucky.match_rating + 0.9), 1)
            home_scorers_assigned += 1

        # Assign away players realistic stats
        for p in self.away_team.players:
            is_gk = p.position == "GK"
            is_def = p.position in ["CB", "LB", "RB"]
            is_mid = p.position in ["CDM", "CM", "CAM"]
            is_fwd = p.position in ["RW", "LW", "ST"]

            dist_rate = 45.0 if is_gk else (118.0 if is_mid else 110.0)
            p.distance_covered_meters = round(self.minute * dist_rate * random.uniform(0.94, 1.06), 1)
            p.sprint_count = 1 if is_gk else int(self.minute * (0.26 if is_fwd else 0.19) * random.uniform(0.8, 1.2))

            pass_rate = 0.35 if is_gk else (0.80 if (is_mid or p.position == "CB") else 0.48)
            p.passes_total = max(1, int(self.minute * pass_rate * random.uniform(0.85, 1.15)))
            acc = 0.70 if is_gk else (0.87 if p.position == "CB" else 0.83)
            p.passes_completed = int(p.passes_total * acc)

            if is_def or p.position == "CDM":
                p.tackles_won = max(0, int(self.minute * 0.06 * random.uniform(0.7, 1.3)))
                p.duels_won = max(0, int(self.minute * 0.11 * random.uniform(0.7, 1.3)))
                p.interceptions = max(0, int(self.minute * 0.05 * random.uniform(0.7, 1.3)))
                p.recoveries = max(1, int(self.minute * 0.09 * random.uniform(0.8, 1.2)))
                p.fouls = max(0, int(self.minute * 0.02 * random.uniform(0.5, 1.5)))
            elif is_mid:
                p.tackles_won = max(0, int(self.minute * 0.04 * random.uniform(0.5, 1.3)))
                p.duels_won = max(0, int(self.minute * 0.08 * random.uniform(0.6, 1.3)))
                p.interceptions = max(0, int(self.minute * 0.04 * random.uniform(0.5, 1.3)))
                p.recoveries = max(1, int(self.minute * 0.11 * random.uniform(0.7, 1.3)))
                p.fouls = max(0, int(self.minute * 0.03 * random.uniform(0.5, 1.5)))
            elif is_fwd:
                p.tackles_won = max(0, int(self.minute * 0.015 * random.uniform(0.5, 1.2)))
                p.duels_won = max(0, int(self.minute * 0.05 * random.uniform(0.5, 1.2)))
                p.interceptions = max(0, int(self.minute * 0.01 * random.uniform(0.5, 1.2)))
                p.recoveries = max(0, int(self.minute * 0.04 * random.uniform(0.6, 1.2)))
                p.fouls = max(0, int(self.minute * 0.02 * random.uniform(0.5, 1.5)))
            else:
                p.saves = max(0, int(self.home_shots * random.uniform(0.5, 0.8)))

            p.goals = 0
            if any(name in p.name.lower() for name in parsed_scorers) and away_scorers_assigned < score_a:
                p.goals += 1
                away_scorers_assigned += 1

            if is_fwd:
                p.shots = max(p.goals, int(self.minute * 0.05 * random.uniform(0.6, 1.4)))
                p.shots_on_target = max(p.goals, int(p.shots * 0.55))
            elif is_mid:
                p.shots = max(p.goals, int(self.minute * 0.025 * random.uniform(0.4, 1.2)))
                p.shots_on_target = max(p.goals, int(p.shots * 0.5))

            base_r = 6.6 + (p.goals * 0.8) + (p.passes_completed * 0.01) + (p.tackles_won * 0.15)
            p.match_rating = round(min(9.5, max(5.9, base_r + random.uniform(-0.2, 0.2))), 1)

        while away_scorers_assigned < score_a:
            candidates = [p for p in self.away_team.players if p.position in ["ST", "RW", "LW", "CAM"]]
            if candidates:
                lucky = random.choice(candidates)
                lucky.goals += 1
                lucky.shots = max(lucky.shots, lucky.goals + 1)
                lucky.shots_on_target = max(lucky.shots_on_target, lucky.goals)
                lucky.match_rating = round(min(9.6, lucky.match_rating + 0.9), 1)
            away_scorers_assigned += 1

        # Populate heatmaps around player positions
        POSITION_CORRIDORS = {
            "GK": (4.0, 6.0), "CB": (8.0, 7.0), "RB": (14.0, 7.0), "LB": (14.0, 7.0),
            "CDM": (12.0, 10.0), "CM": (15.0, 12.0), "CAM": (14.0, 12.0),
            "RW": (16.0, 9.0), "LW": (16.0, 9.0), "ST": (13.0, 10.0)
        }
        num_touch_points = min(40, max(8, int(self.minute * 0.8)))
        for p in self.home_team.players + self.away_team.players:
            cx, cy = POSITION_CORRIDORS.get(p.position, (10.0, 10.0))
            anch_x, anch_y = p.current_coords.x, p.current_coords.y
            touches = []
            for _ in range(num_touch_points):
                tx = round(max(2.0, min(98.0, anch_x + random.gauss(0, cx * 0.5))), 1)
                ty = round(max(3.0, min(97.0, anch_y + random.gauss(0, cy * 0.5))), 1)
                touches.append(PitchCoordinates(x=tx, y=ty))
            self.player_heatmaps[p.id] = touches
            p.heatmap = list(touches)

        # Set game tactical states and refresh player positions
        self._update_game_states()
        self._update_all_positions()

        # Place the ball with an appropriate player
        poss_team = self.home_team if random.random() < 0.5 else self.away_team
        self.possession_team_id = poss_team.id
        self.current_actor = poss_team.players[random.choice([2, 3, 5, 6])]
        self.current_ball_pos = PitchCoordinates(x=self.current_actor.current_coords.x, y=self.current_actor.current_coords.y)

    # ─── GAME STATE MACHINE ───────────────────────────────────────────
    def _update_game_states(self):
        """Determines tactical game state for each team based on score, minute, and momentum."""
        goal_diff = self.home_goals - self.away_goals  # positive = home winning
        minute = self.minute

        # Counter-attack state (short burst after winning ball)
        if self.counter_attack_timer > 0:
            self.counter_attack_timer -= 1
            return  # Don't change state during counter

        # Momentum surge after conceding
        if self.momentum_timer > 0:
            self.momentum_timer -= 1
            if self.momentum_team_id == self.home_team.id:
                self.home_game_state = GameState.ALL_OUT_ATTACK
                self.away_game_state = GameState.PARK_THE_BUS
            else:
                self.away_game_state = GameState.ALL_OUT_ATTACK
                self.home_game_state = GameState.PARK_THE_BUS
            return

        if goal_diff == 0:
            # Level match
            if minute >= 80:
                # Both push for winner
                self.home_game_state = GameState.HIGH_PRESS
                self.away_game_state = GameState.HIGH_PRESS
            else:
                self.home_game_state = GameState.BALANCED
                self.away_game_state = GameState.BALANCED
        elif goal_diff > 0:
            # Home winning
            if minute >= 82:
                self.home_game_state = GameState.TIME_WASTING
                self.away_game_state = GameState.ALL_OUT_ATTACK
            elif minute >= 65:
                self.home_game_state = GameState.PARK_THE_BUS
                self.away_game_state = GameState.ALL_OUT_ATTACK
            else:
                self.home_game_state = GameState.BALANCED
                self.away_game_state = GameState.HIGH_PRESS
        else:
            # Away winning
            if minute >= 82:
                self.away_game_state = GameState.TIME_WASTING
                self.home_game_state = GameState.ALL_OUT_ATTACK
            elif minute >= 65:
                self.away_game_state = GameState.PARK_THE_BUS
                self.home_game_state = GameState.ALL_OUT_ATTACK
            else:
                self.away_game_state = GameState.BALANCED
                self.home_game_state = GameState.HIGH_PRESS

    # ─── FATIGUE SYSTEM ────────────────────────────────────────────────
    def _update_fatigue(self):
        """Decreases stamina over the match. Affects corridor size and speed."""
        base_decay = 0.0015  # per tick
        for p in self.home_team.players + self.away_team.players:
            stamina_factor = p.stamina / 100.0  # Higher stamina = slower decay
            decay = base_decay * (1.3 - stamina_factor)
            self.fatigue[p.id] = max(0.55, self.fatigue[p.id] - decay)

    # ─── POSITION MOVEMENT SYSTEM ─────────────────────────────────────
    def _get_anchor_key(self, player: PlayerProfile, cb_index: int) -> str:
        if player.position == "CB":
            return "CB_R" if cb_index == 0 else "CB_L"
        return player.position

    def _compute_tactical_shift(self, position: str, game_state: str, is_possessing: bool, is_attack_dir_positive: bool) -> Tuple[float, float]:
        """
        Returns (shift_x, shift_y) based on game state and possession.
        is_attack_dir_positive: True if team attacks toward x=100, False if toward x=0.
        GK NEVER shifts out of the goalmouth (always 0, 0).
        """
        if position == "GK":
            return (0.0, 0.0)

        sign = 1.0 if is_attack_dir_positive else -1.0

        if game_state == GameState.ALL_OUT_ATTACK:
            # Outfield players push forward with structured lines
            shifts = {
                "GK":  (0.0, 0.0),
                "CB":  (sign * 7.0, 0),
                "RB":  (sign * 11.0, -2.0),
                "LB":  (sign * 11.0, 2.0),
                "CDM": (sign * 10.0, 0),
                "CM":  (sign * 12.0, 0),
                "CAM": (sign * 12.0, 0),
                "RW":  (sign * 9.0, -2.0),
                "LW":  (sign * 9.0, 2.0),
                "ST":  (sign * 7.0, 0),
            }
            return shifts.get(position, (0, 0))

        elif game_state == GameState.PARK_THE_BUS:
            # Outfield players drop compact without collapsing on top of each other
            shifts = {
                "GK":  (0.0, 0.0),
                "CB":  (-sign * 4.0, 0),
                "RB":  (-sign * 6.0, 2.0),
                "LB":  (-sign * 6.0, -2.0),
                "CDM": (-sign * 7.0, 0),
                "CM":  (-sign * 8.0, 0),
                "CAM": (-sign * 9.0, 0),
                "RW":  (-sign * 9.0, 3.0),
                "LW":  (-sign * 9.0, -3.0),
                "ST":  (-sign * 7.0, 0),
            }
            return shifts.get(position, (0, 0))

        elif game_state == GameState.HIGH_PRESS:
            # Defensive line pushes high compactly
            shifts = {
                "GK":  (0.0, 0.0),
                "CB":  (sign * 6.0, 0),
                "RB":  (sign * 9.0, -1.0),
                "LB":  (sign * 9.0, 1.0),
                "CDM": (sign * 8.0, 0),
                "CM":  (sign * 9.0, 0),
                "CAM": (sign * 8.0, 0),
                "RW":  (sign * 6.0, 0),
                "LW":  (sign * 6.0, 0),
                "ST":  (sign * 4.0, 0),
            }
            return shifts.get(position, (0, 0))

        elif game_state == GameState.TIME_WASTING:
            shifts = {
                "GK":  (0.0, 0.0),
                "CB":  (-sign * 5.0, 0),
                "RB":  (-sign * 7.0, 2.0),
                "LB":  (-sign * 7.0, -2.0),
                "CDM": (-sign * 8.0, 0),
                "CM":  (-sign * 9.0, 0),
                "CAM": (-sign * 10.0, 0),
                "RW":  (-sign * 10.0, 3.0),
                "LW":  (-sign * 10.0, -3.0),
                "ST":  (-sign * 8.0, 0),
            }
            return shifts.get(position, (0, 0))

        elif game_state == GameState.COUNTER_ATTACK:
            # Forward players sprint, defense holds
            if is_possessing:
                shifts = {
                    "GK":  (0.0, 0.0),
                    "CB":  (sign * 3.0, 0),
                    "RB":  (sign * 6.0, 0),
                    "LB":  (sign * 6.0, 0),
                    "CDM": (sign * 7.0, 0),
                    "CM":  (sign * 11.0, 0),
                    "CAM": (sign * 12.0, 0),
                    "RW":  (sign * 12.0, -3.0),
                    "LW":  (sign * 12.0, 3.0),
                    "ST":  (sign * 11.0, 0),
                }
            else:
                shifts = {
                    "GK":  (0.0, 0.0),
                    "CB":  (-sign * 3.0, 0),
                    "RB":  (-sign * 4.0, 0),
                    "LB":  (-sign * 4.0, 0),
                    "CDM": (-sign * 3.0, 0),
                    "CM":  (-sign * 4.0, 0),
                    "CAM": (-sign * 5.0, 0),
                    "RW":  (-sign * 6.0, 0),
                    "LW":  (-sign * 6.0, 0),
                    "ST":  (-sign * 4.0, 0),
                }
            return shifts.get(position, (0, 0))

        else:  # BALANCED
            # Standard possession-based push/drop
            if is_possessing:
                phase_push = {0: 0.0, 1: 5.0, 2: 9.0}.get(self.possession_phase, 0)
                shifts = {
                    "GK":  (0.0, 0.0),
                    "CB":  (sign * phase_push * 0.3, 0),
                    "RB":  (sign * phase_push * 0.6, 0),
                    "LB":  (sign * phase_push * 0.6, 0),
                    "CDM": (sign * phase_push * 0.5, 0),
                    "CM":  (sign * phase_push * 0.7, 0),
                    "CAM": (sign * phase_push * 0.8, 0),
                    "RW":  (sign * phase_push * 0.8, 0),
                    "LW":  (sign * phase_push * 0.8, 0),
                    "ST":  (sign * phase_push * 0.7, 0),
                }
                return shifts.get(position, (0, 0))
            else:
                phase_drop = {0: 0.0, 1: 4.0, 2: 7.0}.get(self.possession_phase, 0)
                shifts = {
                    "GK":  (0.0, 0.0),
                    "CB":  (-sign * phase_drop * 0.3, 0),
                    "RB":  (-sign * phase_drop * 0.4, 0),
                    "LB":  (-sign * phase_drop * 0.4, 0),
                    "CDM": (-sign * phase_drop * 0.4, 0),
                    "CM":  (-sign * phase_drop * 0.5, 0),
                    "CAM": (-sign * phase_drop * 0.5, 0),
                    "RW":  (-sign * phase_drop * 0.5, 0),
                    "LW":  (-sign * phase_drop * 0.5, 0),
                    "ST":  (-sign * phase_drop * 0.3, 0),
                }
                return shifts.get(position, (0, 0))

    def _compute_off_ball_run(self, position: str, game_state: str, is_possessing: bool,
                               is_attack_dir_positive: bool, tick_seed: float) -> Tuple[float, float]:
        """
        Position-specific off-ball intelligent runs.
        tick_seed: random 0-1 value to decide which run to make this tick.
        """
        sign = 1.0 if is_attack_dir_positive else -1.0

        if not is_possessing:
            return (0, 0)  # Off-ball runs are mainly for the possessing team

        if position == "ST":
            if tick_seed < 0.3:
                return (sign * random.uniform(5, 12), random.uniform(-8, 8))   # Run in behind
            elif tick_seed < 0.5:
                return (-sign * random.uniform(3, 8), random.uniform(-5, 5))   # Drop deep to link
            else:
                return (random.uniform(-2, 2), random.uniform(-6, 6))          # Lateral drift

        elif position == "RW":
            if tick_seed < 0.25:
                return (sign * random.uniform(3, 8), random.uniform(-12, -4))  # Cut inside
            elif tick_seed < 0.5:
                return (sign * random.uniform(2, 6), random.uniform(2, 6))     # Hug touchline
            else:
                return (random.uniform(-3, 3), random.uniform(-4, 4))          # Drift

        elif position == "LW":
            if tick_seed < 0.25:
                return (sign * random.uniform(3, 8), random.uniform(4, 12))    # Cut inside
            elif tick_seed < 0.5:
                return (sign * random.uniform(2, 6), random.uniform(-6, -2))   # Hug touchline
            else:
                return (random.uniform(-3, 3), random.uniform(-4, 4))          # Drift

        elif position == "RB":
            if tick_seed < 0.3 and game_state in [GameState.ALL_OUT_ATTACK, GameState.BALANCED]:
                return (sign * random.uniform(8, 16), random.uniform(2, 6))    # Overlapping run
            else:
                return (random.uniform(-3, 3), random.uniform(-3, 3))

        elif position == "LB":
            if tick_seed < 0.3 and game_state in [GameState.ALL_OUT_ATTACK, GameState.BALANCED]:
                return (sign * random.uniform(8, 16), random.uniform(-6, -2))  # Overlapping run
            else:
                return (random.uniform(-3, 3), random.uniform(-3, 3))

        elif position == "CAM":
            if tick_seed < 0.3:
                return (sign * random.uniform(4, 10), random.uniform(-6, 6))   # Box run
            elif tick_seed < 0.5:
                return (-sign * random.uniform(2, 6), random.uniform(-4, 4))   # Drop to receive
            else:
                return (random.uniform(-3, 3), random.uniform(-5, 5))

        elif position in ["CM", "CDM"]:
            # Shuttling and covering
            return (random.uniform(-4, 4), random.uniform(-6, 6))

        elif position == "CB":
            if is_possessing and game_state != GameState.PARK_THE_BUS:
                if tick_seed < 0.2:
                    return (sign * random.uniform(2, 5), random.uniform(-4, 4))  # Step up
            return (random.uniform(-2, 2), random.uniform(-3, 3))

        elif position == "GK":
            return (0.0, 0.0)  # GK strictly holds goalmouth

        return (0, 0)

    def _compute_ball_gravity(self, player_y: float, ball_y: float, position: str = "") -> float:
        """Pull players toward the ball's lateral channel (compact shape) without collapsing flank width."""
        if position == "GK":
            return 0.0  # GK stays centered in the goalmouth, never pulled across field
        
        # Wide flank players (wingers & fullbacks) must preserve tactical width
        if position in ["RW", "LW", "RB", "LB"]:
            distance = ball_y - player_y
            return max(-2.0, min(2.0, distance * 0.05))

        distance = ball_y - player_y
        pull = distance * 0.10
        return max(-4.0, min(4.0, pull))

    def _update_all_positions(self):
        """Master position update: applies game state, corridors, off-ball runs, gravity, fatigue."""
        is_2h = (self.period == "2H")
        is_home_possessing = (self.possession_team_id == self.home_team.id)
        ball_y = self.current_ball_pos.y

        self._update_game_states()
        self._update_fatigue()

        # Update Home Team
        cb_idx = 0
        for p in self.home_team.players:
            # ── 1. GOALKEEPER LOCKED IN GOALMOUTH ──
            if p.position == "GK":
                gk_goal_x = 5.5 if not is_2h else 94.5
                gk_lateral = 50.0 + (ball_y - 50.0) * 0.08
                p.current_coords.x = gk_goal_x
                p.current_coords.y = round(max(47.0, min(53.0, gk_lateral)), 1)
                p.target_coords = None
                p.movement_angle_deg = 0.0 if not is_2h else 180.0
                p.current_speed_kmh = round(random.uniform(1.0, 3.2), 1)
                continue

            anchor_key = self._get_anchor_key(p, cb_idx)
            if p.position == "CB":
                cb_idx += 1

            orig_x, orig_y = self.home_base_anchors.get(anchor_key, (50.0, 50.0))

            # 2H: Flip sides
            if is_2h:
                orig_x, orig_y = 100.0 - orig_x, 100.0 - orig_y

            # Attack direction: 1H home attacks right (+x), 2H attacks left (-x)
            attack_positive = not is_2h

            # 1. Tactical shift from game state
            shift_x, shift_y = self._compute_tactical_shift(
                p.position, self.home_game_state, is_home_possessing, attack_positive
            )

            # 2. Off-ball intelligent run
            run_x, run_y = self._compute_off_ball_run(
                p.position, self.home_game_state, is_home_possessing,
                attack_positive, random.random()
            )

            # 3. Ball gravity (lateral compactness without collapsing width)
            gravity_y = self._compute_ball_gravity(orig_y + shift_y, ball_y, p.position)

            # 4. Corridor wandering with momentum (curved trajectory, not twitching)
            corr_x, corr_y = POSITION_CORRIDORS.get(p.position, (5.0, 5.0))
            fatigue_f = self.fatigue.get(p.id, 1.0)
            prev_mx, prev_my = self.player_momentum.get(p.id, (0.0, 0.0))
            new_mx = round(0.65 * prev_mx + 0.35 * random.gauss(0, corr_x * fatigue_f * 0.45), 2)
            new_my = round(0.65 * prev_my + 0.35 * random.gauss(0, corr_y * fatigue_f * 0.45), 2)
            self.player_momentum[p.id] = (new_mx, new_my)

            # 5. Target waypoint
            target_x = round(max(2.0, min(98.0, orig_x + shift_x + run_x * fatigue_f + new_mx)), 1)
            target_y = round(max(3.0, min(97.0, orig_y + shift_y + run_y * fatigue_f + gravity_y + new_my)), 1)

            # Flank preservation: wingers/fullbacks maintain width
            if orig_y < 30.0:
                target_y = round(max(8.0, min(34.0, target_y)), 1)
            elif orig_y > 70.0:
                target_y = round(max(66.0, min(92.0, target_y)), 1)

            # 6. Smooth trajectory interpolation towards target
            cur_x, cur_y = p.current_coords.x, p.current_coords.y
            dx = target_x - cur_x
            dy = target_y - cur_y
            dist = math.sqrt(dx**2 + dy**2)
            max_step = 5.0 if p.position in ["ST", "RW", "LW"] else (3.0 if p.position == "CB" else 4.0)

            if dist > 0.4:
                step = min(dist, max_step)
                angle_deg = math.degrees(math.atan2(dy, dx))
                p.current_coords.x = round(cur_x + (dx / dist) * step, 1)
                p.current_coords.y = round(cur_y + (dy / dist) * step, 1)
                p.target_coords = PitchCoordinates(x=target_x, y=target_y)
                p.movement_angle_deg = round(angle_deg, 1)
                p.current_speed_kmh = round(min(30.0, max(12.0, (step / 5.2) * 3.6 * 2.8)), 1)
            else:
                p.current_coords.x = target_x
                p.current_coords.y = target_y
                p.target_coords = None
                p.current_speed_kmh = round(random.uniform(3.0, 7.5), 1)

        # Update Away Team
        cb_idx_a = 0
        for p in self.away_team.players:
            # ── 1. GOALKEEPER LOCKED IN GOALMOUTH ──
            if p.position == "GK":
                gk_goal_x = 94.5 if not is_2h else 5.5
                gk_lateral = 50.0 + (ball_y - 50.0) * 0.08
                p.current_coords.x = gk_goal_x
                p.current_coords.y = round(max(47.0, min(53.0, gk_lateral)), 1)
                p.target_coords = None
                p.movement_angle_deg = 180.0 if not is_2h else 0.0
                p.current_speed_kmh = round(random.uniform(1.0, 3.2), 1)
                continue

            anchor_key = self._get_anchor_key(p, cb_idx_a)
            if p.position == "CB":
                cb_idx_a += 1

            orig_x, orig_y = self.away_base_anchors.get(anchor_key, (50.0, 50.0))

            # 2H: Flip sides
            if is_2h:
                orig_x, orig_y = 100.0 - orig_x, 100.0 - orig_y

            # Away attacks left in 1H (-x), right in 2H (+x)
            attack_positive = is_2h

            # 1. Tactical shift
            shift_x, shift_y = self._compute_tactical_shift(
                p.position, self.away_game_state, not is_home_possessing, attack_positive
            )

            # 2. Off-ball run
            run_x, run_y = self._compute_off_ball_run(
                p.position, self.away_game_state, not is_home_possessing,
                attack_positive, random.random()
            )

            # 3. Ball gravity (lateral compactness without collapsing width)
            gravity_y = self._compute_ball_gravity(orig_y + shift_y, ball_y, p.position)

            # 4. Corridor wandering with momentum
            corr_x, corr_y = POSITION_CORRIDORS.get(p.position, (5.0, 5.0))
            fatigue_f = self.fatigue.get(p.id, 1.0)
            prev_mx, prev_my = self.player_momentum.get(p.id, (0.0, 0.0))
            new_mx = round(0.65 * prev_mx + 0.35 * random.gauss(0, corr_x * fatigue_f * 0.45), 2)
            new_my = round(0.65 * prev_my + 0.35 * random.gauss(0, corr_y * fatigue_f * 0.45), 2)
            self.player_momentum[p.id] = (new_mx, new_my)

            # 5. Target waypoint
            target_x = round(max(2.0, min(98.0, orig_x + shift_x + run_x * fatigue_f + new_mx)), 1)
            target_y = round(max(3.0, min(97.0, orig_y + shift_y + run_y * fatigue_f + gravity_y + new_my)), 1)

            # Flank preservation: wingers/fullbacks maintain width
            if orig_y < 30.0:
                target_y = round(max(8.0, min(34.0, target_y)), 1)
            elif orig_y > 70.0:
                target_y = round(max(66.0, min(92.0, target_y)), 1)

            # 6. Smooth trajectory interpolation towards target
            cur_x, cur_y = p.current_coords.x, p.current_coords.y
            dx = target_x - cur_x
            dy = target_y - cur_y
            dist = math.sqrt(dx**2 + dy**2)
            max_step = 5.0 if p.position in ["ST", "RW", "LW"] else (3.0 if p.position == "CB" else 4.0)

            if dist > 0.4:
                step = min(dist, max_step)
                angle_deg = math.degrees(math.atan2(dy, dx))
                p.current_coords.x = round(cur_x + (dx / dist) * step, 1)
                p.current_coords.y = round(cur_y + (dy / dist) * step, 1)
                p.target_coords = PitchCoordinates(x=target_x, y=target_y)
                p.movement_angle_deg = round(angle_deg, 1)
                p.current_speed_kmh = round(min(30.0, max(12.0, (step / 5.2) * 3.6 * 2.8)), 1)
            else:
                p.current_coords.x = target_x
                p.current_coords.y = target_y
                p.target_coords = None
                p.current_speed_kmh = round(random.uniform(3.0, 7.5), 1)

        # ── 7. ANTI-CLUSTERING SEPARATION (Prevent teammates from dogpiling into one spot) ──
        for team_players in [self.home_team.players, self.away_team.players]:
            for i in range(len(team_players)):
                p1 = team_players[i]
                if p1.position == "GK":
                    continue
                for j in range(i + 1, len(team_players)):
                    p2 = team_players[j]
                    if p2.position == "GK":
                        continue
                    dx = p1.current_coords.x - p2.current_coords.x
                    dy = p1.current_coords.y - p2.current_coords.y
                    dist = math.hypot(dx, dy)
                    if dist < 3.2:
                        push = (3.2 - dist) * 0.5
                        if p1.current_coords.y >= p2.current_coords.y:
                            p1.current_coords.y = round(min(94.0, p1.current_coords.y + push), 1)
                            p2.current_coords.y = round(max(6.0, p2.current_coords.y - push), 1)
                        else:
                            p1.current_coords.y = round(max(6.0, p1.current_coords.y - push), 1)
                            p2.current_coords.y = round(min(94.0, p2.current_coords.y + push), 1)
                p.target_coords = PitchCoordinates(x=target_x, y=target_y)
                p.movement_angle_deg = round(angle_deg, 1)
                p.current_speed_kmh = round(min(32.0, max(12.0, (step / 5.2) * 3.6 * 2.8)), 1)
            else:
                p.current_coords.x = target_x
                p.current_coords.y = target_y
                p.target_coords = None
                p.current_speed_kmh = round(random.uniform(3.0, 7.5), 1)

    # ─── HELPERS ──────────────────────────────────────────────────────
    def _record_player_touch(self, player: PlayerProfile, coords: PitchCoordinates):
        """Records an Opta touch point in the individual player's heatmap."""
        if player.id not in self.player_heatmaps:
            self.player_heatmaps[player.id] = []
        self.player_heatmaps[player.id].append(PitchCoordinates(x=round(coords.x, 1), y=round(coords.y, 1)))
        if len(self.player_heatmaps[player.id]) > 120:
            self.player_heatmaps[player.id].pop(0)
        player.heatmap = list(self.player_heatmaps[player.id])

    def _calculate_pitch_distance_meters(self, p1: PitchCoordinates, p2: PitchCoordinates) -> float:
        dx = (p2.x - p1.x) * 1.05
        dy = (p2.y - p1.y) * 0.68
        return round(math.sqrt(dx**2 + dy**2), 1)

    def _get_tactical_pass_options(self, actor: PlayerProfile, is_home: bool) -> List[PlayerProfile]:
        """Returns realistic passing options according to the current buildup phase."""
        team = self.home_team if is_home else self.away_team
        candidates = [p for p in team.players if p.id != actor.id]

        game_state = self.home_game_state if is_home else self.away_game_state

        if game_state == GameState.COUNTER_ATTACK:
            # Direct forward passes
            preferred = [p for p in candidates if p.position in ["ST", "LW", "RW", "CAM"]]
            return preferred if preferred else candidates

        if game_state == GameState.ALL_OUT_ATTACK:
            # Skip buildup, push forward quickly
            if self.possession_phase < 1:
                preferred = [p for p in candidates if p.position in ["CM", "CDM", "CAM", "LW", "RW"]]
            else:
                preferred = [p for p in candidates if p.position in ["CAM", "ST", "LW", "RW", "CM"]]
            return preferred if preferred else candidates

        if game_state in [GameState.PARK_THE_BUS, GameState.TIME_WASTING]:
            # Safe passes, mostly backwards/lateral
            preferred = [p for p in candidates if p.position in ["GK", "CB", "LB", "RB", "CDM", "CM"]]
            return preferred if preferred else candidates

        # BALANCED / HIGH_PRESS — standard phase-based
        if self.possession_phase == 0:
            preferred = [p for p in candidates if p.position in ["GK", "CB", "LB", "RB", "CDM"]]
            return preferred if preferred else candidates
        elif self.possession_phase == 1:
            preferred = [p for p in candidates if p.position in ["CDM", "CM", "CAM", "LB", "RB", "LW", "RW"]]
            return preferred if preferred else candidates
        else:
            preferred = [p for p in candidates if p.position in ["CAM", "ST", "LW", "RW", "CM"]]
            return preferred if preferred else candidates

    def _select_pass_recipient(self, actor: PlayerProfile, options: List[PlayerProfile]) -> PlayerProfile:
        """
        Picks a realistic pass recipient prioritizing nearby passing lanes (12m-30m),
        preventing wild cross-pitch ping-pong passes and creating natural football combinations.
        """
        if not options:
            return actor
        if len(options) == 1:
            return options[0]

        weights = []
        for opt in options:
            dist = self._calculate_pitch_distance_meters(actor.current_coords, opt.current_coords)
            if 12.0 <= dist <= 30.0:
                # Optimal short-to-medium tactical pass
                w = 12.0
            elif 30.0 < dist <= 42.0:
                # Medium pass / through ball
                w = 4.0
            elif dist < 12.0:
                # Close-quarters pass
                w = 3.0
            else:
                # Long cross-pitch switch (>42m)
                w = 0.8
            weights.append(w)

        chosen = random.choices(options, weights=weights, k=1)[0]
        return chosen

    # ─── SET PIECE EXECUTOR (Corners, Penalties, Free Kicks) ─────────
    def _execute_set_piece(self) -> MatchEvent:
        """
        Executes realistic set-piece routines:
        - Corner Kick: Taker at corner flag, aerial threats pack the 6-yard box, curling cross & header duel.
        - Penalty Kick: 1v1 showdown at the 12-yard spot, 20 players cleared from the box, high-drama xG 0.79.
        - Direct Free Kick: 24m range with 4-man defensive wall, curling strike over the wall.
        """
        set_piece = self.pending_set_piece
        self.pending_set_piece = None

        is_home = (self.possession_team_id == self.home_team.id)
        current_team = self.home_team if is_home else self.away_team
        defending_team = self.away_team if is_home else self.home_team
        is_2h = (self.period == "2H")

        attacks_positive = (is_home and not is_2h) or (not is_home and is_2h)
        goal_x = 100.0 if attacks_positive else 0.0

        if set_piece == "corner":
            flag_x = 99.5 if attacks_positive else 0.5
            flag_y = 1.0 if random.random() < 0.5 else 99.0

            # Taker: Winger or attacking midfielder
            takers = [p for p in current_team.players if p.position in ["RW", "LW", "CAM"]]
            taker = takers[0] if takers else current_team.players[7]
            taker.current_coords = PitchCoordinates(x=flag_x, y=flag_y)
            taker.target_coords = None
            taker.current_speed_kmh = 0.0
            self.current_actor = taker
            self.current_ball_pos = PitchCoordinates(x=flag_x, y=flag_y)

            # Defending GK locked in 6-yard box
            def_gk = defending_team.players[0]
            def_gk.current_coords = PitchCoordinates(x=94.5 if attacks_positive else 5.5, y=50.0)

            # Danger delivery target in 6-yard box
            danger_x = goal_x - 8.0 if attacks_positive else 8.0
            danger_y = 50.0 + random.uniform(-6.0, 6.0)
            delivery_target = PitchCoordinates(x=round(danger_x, 1), y=round(danger_y, 1))

            aerial_attackers = [p for p in current_team.players if p.id != taker.id and p.position in ["ST", "CB", "CM"]][:4]
            defenders_in_box = [p for p in defending_team.players if p.position in ["CB", "CDM", "LB", "RB"]][:5]

            for i, p in enumerate(aerial_attackers):
                offset_x = (goal_x - 6.0 - i * 2.0) if attacks_positive else (6.0 + i * 2.0)
                p.current_coords = PitchCoordinates(x=round(offset_x, 1), y=round(40.0 + i * 5.0, 1))
            for i, p in enumerate(defenders_in_box):
                offset_x = (goal_x - 5.0 - i * 1.8) if attacks_positive else (5.0 + i * 1.8)
                p.current_coords = PitchCoordinates(x=round(offset_x, 1), y=round(41.0 + i * 4.5, 1))

            # Rest of players outside the box guarding transitions
            for p in current_team.players:
                if p.id != taker.id and p not in aerial_attackers and p.position != "GK":
                    p.current_coords.x = round(62.0 if attacks_positive else 38.0, 1)

            target_header = aerial_attackers[0] if aerial_attackers else taker
            target_header.current_coords = delivery_target

            # Real EPL Corner conversion: ~14% header goals
            dice = random.random()
            if dice < 0.16 and (self.home_goals + self.away_goals < 5):
                outcome = ShotOutcome.GOAL
                event_type = EventType.CORNER
                target_header.goals += 1
                target_header.shots_on_target += 1
                if is_home:
                    self.home_goals += 1
                else:
                    self.away_goals += 1
                self.timeline_moments.append({
                    "minute": self.minute,
                    "type": "goal",
                    "player": f"{target_header.name} (Corner Header)",
                    "team": current_team.short_name,
                    "speed": 82.0,
                    "xg": 0.28
                })
            elif dice < 0.60:
                outcome = ShotOutcome.SAVED
                event_type = EventType.CORNER
                def_gk.saves += 1
                target_header.shots_on_target += 1
            else:
                outcome = ShotOutcome.OFF_TARGET
                event_type = EventType.CORNER

            taker.passes_total += 1
            taker.passes_completed += 1

            event = MatchEvent(
                event_id=f"evt_{len(self.events_history)+1}",
                match_id=self.match_id,
                minute=self.minute,
                second=self.second,
                period=self.period,
                team_id=current_team.id,
                player=taker,
                recipient=target_header,
                event_type=event_type,
                set_piece_type="corner",
                location=PitchCoordinates(x=flag_x, y=flag_y),
                end_location=delivery_target,
                ball_speed_kmh=82.0,
                player_speed_kmh=round(random.uniform(12.0, 18.0), 1),
                xG=0.28 if outcome == ShotOutcome.GOAL else 0.14,
                shot_outcome=outcome,
                under_pressure=True,
                pressure_intensity=88.0,
                possession_chain_id=f"chain_{self.chain_id}"
            )
            self.events_history.append(event)
            return event

        elif set_piece == "penalty":
            spot_x = 88.5 if attacks_positive else 11.5
            spot_y = 50.0
            penalty_spot = PitchCoordinates(x=spot_x, y=spot_y)
            goal_target = PitchCoordinates(x=goal_x, y=50.0 + random.uniform(-4, 4))

            # Penalty specialist
            strikers = [p for p in current_team.players if p.position in ["ST", "RW", "CAM"]]
            taker = strikers[0] if strikers else current_team.players[-1]
            taker.current_coords = PitchCoordinates(x=spot_x - 2.5 if attacks_positive else spot_x + 2.5, y=50.0)
            self.current_actor = taker
            self.current_ball_pos = penalty_spot

            # Defending GK on the line
            def_gk = defending_team.players[0]
            def_gk.current_coords = PitchCoordinates(x=94.5 if attacks_positive else 5.5, y=50.0)

            # All 20 outfield players cleared outside the 18-yard box
            for p in current_team.players + defending_team.players:
                if p.position != "GK" and p.id != taker.id:
                    if attacks_positive:
                        p.current_coords.x = round(min(81.0, p.current_coords.x), 1)
                    else:
                        p.current_coords.x = round(max(19.0, p.current_coords.x), 1)

            # Official Opta Penalty calibrated conversion (~78% Goal, 18% Save, 4% Post)
            dice = random.random()
            shot_speed = round(random.uniform(108.0, 124.0), 1)
            xg = 0.79

            if dice < 0.78:
                outcome = ShotOutcome.GOAL
                event_type = EventType.PENALTY
                taker.goals += 1
                taker.shots += 1
                taker.shots_on_target += 1
                if is_home:
                    self.home_goals += 1
                else:
                    self.away_goals += 1
                self.timeline_moments.append({
                    "minute": self.minute,
                    "type": "goal",
                    "player": f"{taker.name} (Penalty)",
                    "team": current_team.short_name,
                    "speed": shot_speed,
                    "xg": xg
                })
            elif dice < 0.95:
                outcome = ShotOutcome.SAVED
                event_type = EventType.PENALTY
                taker.shots += 1
                taker.shots_on_target += 1
                def_gk.saves += 1
                def_gk.match_rating = round(min(10.0, def_gk.match_rating + 0.8), 1)
            else:
                outcome = ShotOutcome.POST
                event_type = EventType.PENALTY
                taker.shots += 1

            event = MatchEvent(
                event_id=f"evt_{len(self.events_history)+1}",
                match_id=self.match_id,
                minute=self.minute,
                second=self.second,
                period=self.period,
                team_id=current_team.id,
                player=taker,
                event_type=event_type,
                set_piece_type="penalty",
                location=penalty_spot,
                end_location=goal_target,
                shot_speed_kmh=shot_speed,
                ball_speed_kmh=shot_speed,
                player_speed_kmh=round(random.uniform(16.0, 22.0), 1),
                xG=xg,
                shot_outcome=outcome,
                under_pressure=True,
                pressure_intensity=98.0,
                possession_chain_id=f"chain_{self.chain_id}"
            )
            self.events_history.append(event)
            return event

        else:  # "free_kick"
            fk_x = 76.0 if attacks_positive else 24.0
            fk_y = 50.0 + random.uniform(-10.0, 10.0)
            ball_spot = PitchCoordinates(x=round(fk_x, 1), y=round(fk_y, 1))
            goal_target = PitchCoordinates(x=goal_x, y=50.0 + random.uniform(-4.0, 4.0))

            specialists = [p for p in current_team.players if p.position in ["CAM", "CM", "RW"]]
            specialist = specialists[0] if specialists else current_team.players[8]
            specialist.current_coords = PitchCoordinates(x=fk_x - 1.8 if attacks_positive else fk_x + 1.8, y=fk_y)
            self.current_actor = specialist
            self.current_ball_pos = ball_spot

            # Defensive Wall of 4 defenders lines up 9.15m away
            wall_x = fk_x + 8.5 if attacks_positive else fk_x - 8.5
            wall_defenders = [p for p in defending_team.players if p.position in ["CB", "CDM", "CM", "RB", "LB"]][:4]
            for i, p in enumerate(wall_defenders):
                p.current_coords = PitchCoordinates(x=round(wall_x, 1), y=round(fk_y - 2.5 + i * 1.6, 1))

            def_gk = defending_team.players[0]
            def_gk.current_coords = PitchCoordinates(x=94.5 if attacks_positive else 5.5, y=50.0)

            shot_speed = round(random.uniform(96.0, 114.0), 1)
            xg = 0.12
            dice = random.random()

            if dice < 0.20:
                outcome = ShotOutcome.GOAL
                event_type = EventType.FREE_KICK
                specialist.goals += 1
                specialist.shots += 1
                specialist.shots_on_target += 1
                if is_home:
                    self.home_goals += 1
                else:
                    self.away_goals += 1
                self.timeline_moments.append({
                    "minute": self.minute,
                    "type": "goal",
                    "player": f"{specialist.name} (Direct Free Kick)",
                    "team": current_team.short_name,
                    "speed": shot_speed,
                    "xg": xg
                })
            elif dice < 0.65:
                outcome = ShotOutcome.SAVED
                event_type = EventType.FREE_KICK
                specialist.shots += 1
                specialist.shots_on_target += 1
                def_gk.saves += 1
            else:
                outcome = ShotOutcome.OFF_TARGET
                event_type = EventType.FREE_KICK
                specialist.shots += 1

            event = MatchEvent(
                event_id=f"evt_{len(self.events_history)+1}",
                match_id=self.match_id,
                minute=self.minute,
                second=self.second,
                period=self.period,
                team_id=current_team.id,
                player=specialist,
                event_type=event_type,
                set_piece_type="free_kick",
                location=ball_spot,
                end_location=goal_target,
                shot_speed_kmh=shot_speed,
                ball_speed_kmh=shot_speed,
                player_speed_kmh=14.0,
                xG=xg,
                shot_outcome=outcome,
                under_pressure=True,
                pressure_intensity=75.0,
                possession_chain_id=f"chain_{self.chain_id}"
            )
            self.events_history.append(event)
            return event

    # ─── MAIN EVENT GENERATOR ─────────────────────────────────────────
    def generate_next_event(self) -> MatchEvent:
        """
        Generates realistic football play with:
        - Game State Machine affecting all 22 players
        - Exact ball-to-foot tracking
        - 90-minute Full-Time stop
        - Post-goal momentum surges
        - Counter-attacks after tackles
        """
        # If match is finished, keep emitting Full-Time state
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

        # ── KICKOFF EVENT EMISSION (Minute 0:00 or Minute 45:00) ──────
        if getattr(self, "is_kickoff", False):
            self.is_kickoff = False
            kicking_team = self.home_team if self.possession_team_id == self.home_team.id else self.away_team
            actor = self.current_actor

            # Receiver is central midfielder or CDM behind the striker
            potential_receivers = [p for p in kicking_team.players if p.position in ["CM", "CDM"] and p.id != actor.id]
            receiver = potential_receivers[0] if potential_receivers else kicking_team.players[5]

            start_coords = PitchCoordinates(x=50.0, y=50.0)
            target_coords = PitchCoordinates(x=receiver.current_coords.x, y=receiver.current_coords.y)

            actor.passes_total += 1
            actor.passes_completed += 1
            self.passes_in_current_chain = 1
            self.possession_phase = 0
            self.current_actor = receiver
            self.current_ball_pos = PitchCoordinates(x=target_coords.x, y=target_coords.y)
            self._record_player_touch(actor, start_coords)
            self._record_player_touch(receiver, target_coords)

            kickoff_event = MatchEvent(
                event_id=f"evt_{self.match_id}_{self.minute:02d}_{self.second:02d}_{len(self.events_history)}",
                match_id=self.match_id,
                minute=self.minute,
                second=self.second,
                period=self.period,
                team_id=kicking_team.id,
                player=actor,
                recipient=receiver,
                event_type=EventType.PASS,
                location=start_coords,
                end_location=target_coords,
                pass_outcome=PassOutcome.COMPLETE,
                pass_distance_m=round(math.hypot(target_coords.x - start_coords.x, target_coords.y - start_coords.y), 1),
                ball_speed_kmh=42.0,
                player_speed_kmh=round(random.uniform(5.0, 8.5), 1),
                pressure_intensity=10.0,
                xG=0.0
            )
            self.events_history.append(kickoff_event)
            return kickoff_event

        # Advance match clock naturally (8-14 seconds per phase of play)
        time_advance = random.randint(8, 14)
        possessing_state = self.home_game_state if self.possession_team_id == self.home_team.id else self.away_game_state
        if possessing_state == GameState.TIME_WASTING:
            time_advance = random.randint(12, 18)
        elif possessing_state == GameState.COUNTER_ATTACK:
            time_advance = random.randint(5, 8)  # Fast transition

        self.second += time_advance
        if self.second >= 60:
            self.minute += self.second // 60
            self.second = self.second % 60

        # Check Half-Time at 45' -> Transition directly to 2nd Half Kickoff from center
        if self.period == "1H" and self.minute >= 45:
            self.minute = 45
            self.second = 0
            self.period = "2H"
            self.is_half_time = False
            self.is_kickoff = True
            self._setup_kickoff_formation(is_2h=True)
            return self.generate_next_event()

        # Check Full-Time Stop at 90+3'
        if self.minute >= 93:
            self.minute = 90
            self.second = 0
            self.period = "FT"
            self.is_finished = True

        if not self.is_finished:
            self.period = "1H" if self.minute < 45 else "2H"

        # ── EXECUTE PENDING SET PIECE (Corner, Penalty, Free Kick) ────
        if getattr(self, "pending_set_piece", None):
            return self._execute_set_piece()

        is_home = (self.possession_team_id == self.home_team.id)
        current_team = self.home_team if is_home else self.away_team
        defending_team = self.away_team if is_home else self.home_team

        # Ensure current actor belongs to possession team
        if self.current_actor.team_id != self.possession_team_id:
            self.current_actor = current_team.players[2]

        actor = self.current_actor

        # Ball at actor's feet
        self.current_ball_pos = PitchCoordinates(x=actor.current_coords.x, y=actor.current_coords.y)

        # Record global heatmap
        self.heatmap_cells.append(PitchCoordinates(x=self.current_ball_pos.x, y=self.current_ball_pos.y))
        if len(self.heatmap_cells) > 80:
            self.heatmap_cells.pop(0)

        self.passes_in_current_chain += 1

        # Phase progression
        if self.passes_in_current_chain < 4:
            self.possession_phase = 0
        elif self.passes_in_current_chain < 9:
            self.possession_phase = 1
        else:
            self.possession_phase = 2

        # UPDATE ALL 22 PLAYERS with the full movement system
        self._update_all_positions()

        # Re-sync ball to actor after position update
        self.current_ball_pos = PitchCoordinates(x=actor.current_coords.x, y=actor.current_coords.y)

        # Record touches
        self._record_player_touch(actor, self.current_ball_pos)
        for p in random.sample(self.home_team.players + self.away_team.players, k=min(5, len(self.home_team.players + self.away_team.players))):
            self._record_player_touch(p, p.current_coords)

        under_pressure = (self.possession_phase == 2) or (random.random() < 0.25)
        pressure_intensity = random.uniform(40.0, 80.0) if under_pressure else random.uniform(10.0, 30.0)

        # ── 1. SHOT OCCASION ──────────────────────────────────────────
        team_shots = self.home_shots if is_home else self.away_shots
        team_goals = self.home_goals if is_home else self.away_goals
        game_state = self.home_game_state if is_home else self.away_game_state

        is_2h = (self.period == "2H")
        if not is_2h:
            in_shooting_range = (self.current_ball_pos.x > 74.0) if is_home else (self.current_ball_pos.x < 26.0)
            goal_x = 100.0 if is_home else 0.0
        else:
            in_shooting_range = (self.current_ball_pos.x < 26.0) if is_home else (self.current_ball_pos.x > 74.0)
            goal_x = 0.0 if is_home else 100.0

        # Adjust shot threshold based on game state
        min_passes_for_shot = 3 if game_state in [GameState.ALL_OUT_ATTACK, GameState.COUNTER_ATTACK] else 5
        shot_chance = 0.45 if game_state == GameState.ALL_OUT_ATTACK else 0.35
        should_shoot = (in_shooting_range and
                       self.passes_in_current_chain >= min_passes_for_shot and
                       random.random() < shot_chance and
                       team_shots < 16)

        if should_shoot:
            if is_home:
                self.home_shots += 1
            else:
                self.away_shots += 1

            goal_target = PitchCoordinates(x=goal_x, y=50.0 + random.uniform(-8, 8))
            dx = (goal_target.x - self.current_ball_pos.x) * 1.05
            dy = (goal_target.y - self.current_ball_pos.y) * 0.68
            dist = math.sqrt(dx**2 + dy**2)

            base_xg = 0.45 if dist < 12 else (0.18 if dist < 20 else 0.05)
            xg = round(base_xg * random.uniform(0.85, 1.15), 2)
            shot_speed = round(random.uniform(90.0, 122.0), 1)

            actor.sprint_count += 1
            actor.current_speed_kmh = round(random.uniform(27.0, 32.5), 1)

            # Record shot statistics
            actor.shots += 1

            dice = random.random()
            defending_gk = defending_team.players[0] if defending_team.players else None
            if dice < xg and team_goals < 4 and random.random() < 0.38:
                outcome = ShotOutcome.GOAL
                event_type = EventType.GOAL
                actor.goals += 1
                actor.shots_on_target += 1
                actor.match_rating = round(min(10.0, actor.match_rating + 1.2), 1)
                if defending_gk:
                    defending_gk.match_rating = round(max(5.0, defending_gk.match_rating - 0.3), 1)
                if is_home:
                    self.home_goals += 1
                else:
                    self.away_goals += 1

                # MOMENTUM SURGE: Team that conceded gets 6-8 ticks of fury
                self.momentum_timer = random.randint(6, 9)
                self.momentum_team_id = defending_team.id

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
                actor.shots_on_target += 1
                actor.match_rating = round(min(10.0, actor.match_rating + 0.2), 1)
                if defending_gk:
                    defending_gk.saves += 1
                    defending_gk.match_rating = round(min(10.0, defending_gk.match_rating + 0.4), 1)
                # 45% chance GK deflection results in a CORNER KICK for attacking team!
                if random.random() < 0.45:
                    self.pending_set_piece = "corner"
                    self.possession_team_id = current_team.id
            else:
                outcome = ShotOutcome.OFF_TARGET
                event_type = EventType.SHOT
                actor.match_rating = round(max(5.0, actor.match_rating - 0.1), 1)

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
            self.current_actor = defending_team.players[0] if outcome in [ShotOutcome.SAVED, ShotOutcome.OFF_TARGET] else defending_team.players[2]
            self.current_ball_pos = PitchCoordinates(x=self.current_actor.current_coords.x, y=self.current_actor.current_coords.y)
            self._record_player_touch(self.current_actor, self.current_ball_pos)

            self.events_history.append(event)
            return event

        # ── 2. DEFENSIVE TACKLE → triggers COUNTER ATTACK or SET PIECE ─────────────
        turnover_chance = 0.22 if self.passes_in_current_chain > 12 else (0.12 if game_state == GameState.ALL_OUT_ATTACK else 0.07)
        if under_pressure and random.random() < turnover_chance:
            attacks_pos = (is_home and not is_2h) or (not is_home and is_2h)
            is_in_box = (self.current_ball_pos.x > 84.0 and 22.0 <= self.current_ball_pos.y <= 78.0) if attacks_pos else (self.current_ball_pos.x < 16.0 and 22.0 <= self.current_ball_pos.y <= 78.0)

            # High-Drama Penalty Foul
            if is_in_box and random.random() < 0.28 and (self.home_goals + self.away_goals < 5):
                self.pending_set_piece = "penalty"
                self.possession_team_id = current_team.id
                def_player = defending_team.players[2]
                def_player.fouls += 1
                foul_event = MatchEvent(
                    event_id=f"evt_{len(self.events_history)+1}",
                    match_id=self.match_id,
                    minute=self.minute,
                    second=self.second,
                    period=self.period,
                    team_id=defending_team.id,
                    player=def_player,
                    recipient=actor,
                    event_type=EventType.FOUL,
                    set_piece_type="penalty",
                    location=self.current_ball_pos,
                    player_speed_kmh=22.0,
                    under_pressure=True,
                    pressure_intensity=96.0,
                    possession_chain_id=f"chain_{self.chain_id}"
                )
                self.events_history.append(foul_event)
                return foul_event

            # Dangerous Free Kick in Final Third (20-28m)
            is_danger_zone = (72.0 <= self.current_ball_pos.x <= 84.0 and 22.0 <= self.current_ball_pos.y <= 78.0) if attacks_pos else (16.0 <= self.current_ball_pos.x <= 28.0 and 22.0 <= self.current_ball_pos.y <= 78.0)
            if is_danger_zone and random.random() < 0.24:
                self.pending_set_piece = "free_kick"
                self.possession_team_id = current_team.id
                def_player = defending_team.players[3]
                def_player.fouls += 1
                fk_foul = MatchEvent(
                    event_id=f"evt_{len(self.events_history)+1}",
                    match_id=self.match_id,
                    minute=self.minute,
                    second=self.second,
                    period=self.period,
                    team_id=defending_team.id,
                    player=def_player,
                    recipient=actor,
                    event_type=EventType.FOUL,
                    set_piece_type="free_kick",
                    location=self.current_ball_pos,
                    player_speed_kmh=18.0,
                    under_pressure=True,
                    pressure_intensity=80.0,
                    possession_chain_id=f"chain_{self.chain_id}"
                )
                self.events_history.append(fk_foul)
                return fk_foul

            # Pick a defender close to the ball
            defenders = [p for p in defending_team.players if p.position in ["CB", "CDM", "CM", "RB", "LB"]]
            defender = min(defenders, key=lambda p: abs(p.current_coords.x - self.current_ball_pos.x) + abs(p.current_coords.y - self.current_ball_pos.y)) if defenders else defending_team.players[2]
            defender.current_speed_kmh = round(random.uniform(20.0, 28.0), 1)

            # ~18% of defensive challenges result in a whistle (Tactical Foul or Card)
            foul_roll = random.random()
            if foul_roll < 0.18:
                defender.fouls += 1
                defender.match_rating = round(max(4.5, defender.match_rating - 0.2), 1)
                
                # Check for Disciplinary Card (Yellow or Red)
                is_card = (foul_roll < 0.05) or (defender.fouls >= 3 and random.random() < 0.65)
                if is_card:
                    is_red = (defender.cards_yellow >= 1) or (random.random() < 0.03)
                    card_type = "red" if is_red else "yellow"
                    if is_red:
                        defender.cards_red += 1
                    else:
                        defender.cards_yellow += 1
                        
                    self.timeline_moments.append({
                        "minute": self.minute,
                        "type": "card",
                        "player": defender.name,
                        "team": defending_team.short_name,
                        "card": card_type
                    })
                    
                    card_event = MatchEvent(
                        event_id=f"evt_{len(self.events_history)+1}",
                        match_id=self.match_id,
                        minute=self.minute,
                        second=self.second,
                        period=self.period,
                        team_id=defending_team.id,
                        player=defender,
                        recipient=actor,
                        event_type=EventType.CARD,
                        card_type=card_type,
                        location=self.current_ball_pos,
                        player_speed_kmh=defender.current_speed_kmh,
                        under_pressure=True,
                        pressure_intensity=pressure_intensity,
                        possession_chain_id=f"chain_{self.chain_id}"
                    )
                    self.events_history.append(card_event)
                    self.possession_team_id = current_team.id
                    self.current_actor = actor
                    return card_event
                else:
                    foul_event = MatchEvent(
                        event_id=f"evt_{len(self.events_history)+1}",
                        match_id=self.match_id,
                        minute=self.minute,
                        second=self.second,
                        period=self.period,
                        team_id=defending_team.id,
                        player=defender,
                        recipient=actor,
                        event_type=EventType.FOUL,
                        location=self.current_ball_pos,
                        player_speed_kmh=defender.current_speed_kmh,
                        under_pressure=True,
                        pressure_intensity=pressure_intensity,
                        possession_chain_id=f"chain_{self.chain_id}"
                    )
                    self.events_history.append(foul_event)
                    self.possession_team_id = current_team.id
                    self.current_actor = actor
                    return foul_event

            defender.tackles_won += 1
            defender.duels_won += 1
            defender.recoveries += 1
            defender.match_rating = round(min(10.0, defender.match_rating + 0.3), 1)
            actor.match_rating = round(max(5.0, actor.match_rating - 0.1), 1)
            self._record_player_touch(defender, self.current_ball_pos)

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

            # Trigger counter-attack for 2-3 ticks
            def_state = self.home_game_state if defending_team.id == self.home_team.id else self.away_game_state
            if def_state not in [GameState.PARK_THE_BUS, GameState.TIME_WASTING]:
                self.counter_attack_timer = random.randint(2, 3)
                if defending_team.id == self.home_team.id:
                    self.home_game_state = GameState.COUNTER_ATTACK
                else:
                    self.away_game_state = GameState.COUNTER_ATTACK

            self.events_history.append(event)
            return event

        # ── 3. STRUCTURED PASSING ─────────────────────────────────────
        options = self._get_tactical_pass_options(actor, is_home)
        recipient = self._select_pass_recipient(actor, options)

        pass_start_pos = PitchCoordinates(
            x=actor.current_coords.x,
            y=actor.current_coords.y
        )

        target_coords = PitchCoordinates(
            x=recipient.current_coords.x,
            y=recipient.current_coords.y
        )

        dist_m = self._calculate_pitch_distance_meters(pass_start_pos, target_coords)
        difficulty = round(min(0.85, max(0.08, (dist_m / 45.0) * 0.4 + (0.18 if under_pressure else 0.05))), 2)

        ball_speed = round(random.uniform(42.0, 68.0), 1)
        fatigue_f = self.fatigue.get(actor.id, 1.0)
        actor.current_speed_kmh = round(random.uniform(14.0, 22.0) * fatigue_f, 1)
        actor.distance_covered_meters += dist_m

        # Pass accuracy affected by fatigue and game state frenzy
        accuracy_bonus = 0.0
        if game_state == GameState.ALL_OUT_ATTACK:
            accuracy_bonus = -0.06  # More rushed, more errors
        elif game_state in [GameState.PARK_THE_BUS, GameState.TIME_WASTING]:
            accuracy_bonus = 0.03   # Safe passes, higher accuracy
        is_complete = random.random() < (0.90 + accuracy_bonus) * fatigue_f

        actor.passes_total += 1
        final_recipient = recipient

        if is_complete:
            outcome = PassOutcome.COMPLETE
            actor.passes_completed += 1
            actor.match_rating = round(min(10.0, actor.match_rating + 0.02), 1)
            self.current_actor = recipient
            self.current_ball_pos = target_coords
            self._record_player_touch(recipient, target_coords)

            if actor.id not in self.pass_matrix:
                self.pass_matrix[actor.id] = {}
            self.pass_matrix[actor.id][recipient.id] = self.pass_matrix[actor.id].get(recipient.id, 0) + 1
        else:
            outcome = PassOutcome.INTERCEPTED
            actor.match_rating = round(max(5.0, actor.match_rating - 0.05), 1)
            self.possession_team_id = defending_team.id
            # Pick closest defender to interception point
            defenders = defending_team.players[1:6]
            intercepting_defender = min(defenders, key=lambda p: abs(p.current_coords.x - target_coords.x) + abs(p.current_coords.y - target_coords.y)) if defenders else defending_team.players[2]
            intercepting_defender.interceptions += 1
            intercepting_defender.recoveries += 1
            intercepting_defender.match_rating = round(min(10.0, intercepting_defender.match_rating + 0.2), 1)
            self.current_actor = intercepting_defender
            self.chain_id += 1
            self.passes_in_current_chain = 0
            self.possession_phase = 0
            final_recipient = intercepting_defender
            # Interception landing point is directly at the intercepting defender's feet
            target_coords = PitchCoordinates(x=intercepting_defender.current_coords.x, y=intercepting_defender.current_coords.y)
            self.current_ball_pos = target_coords
            self._record_player_touch(intercepting_defender, target_coords)

        event = MatchEvent(
            event_id=f"evt_{len(self.events_history)+1}",
            match_id=self.match_id,
            minute=self.minute,
            second=self.second,
            period=self.period,
            team_id=self.possession_team_id if is_complete else current_team.id,
            player=actor,
            recipient=final_recipient,
            event_type=EventType.INTERCEPTION if not is_complete else EventType.PASS,
            location=pass_start_pos,
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
