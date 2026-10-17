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
    "GK":  (2.0, 3.0),
    "CB":  (5.0, 6.0),
    "RB":  (10.0, 8.0),
    "LB":  (10.0, 8.0),
    "CDM": (7.0, 8.0),
    "CM":  (10.0, 10.0),
    "CAM": (12.0, 10.0),
    "RW":  (14.0, 12.0),
    "LW":  (14.0, 12.0),
    "ST":  (15.0, 12.0),
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
        """Resets the match to minute 1:00."""
        self.minute = 1
        self.second = 0
        self.period = "1H"
        self.is_finished = False
        self.is_half_time = False
        self.chain_id = 1
        self.possession_team_id = self.home_team.id
        self.events_history: List[MatchEvent] = []

        # Current ball holder
        self.current_actor = self.home_team.players[2]  # CB
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

        # Game State Machine
        self.home_game_state = GameState.BALANCED
        self.away_game_state = GameState.BALANCED
        self.momentum_timer = 0        # ticks remaining of post-goal momentum surge
        self.momentum_team_id = ""     # team with the surge (the one that conceded)
        self.counter_attack_timer = 0  # ticks remaining of counter-attack burst

        # Fatigue factors per player (1.0 = fresh, decreases over time)
        self.fatigue: Dict[str, float] = {}
        for p in self.home_team.players + self.away_team.players:
            self.fatigue[p.id] = 1.0

        # Individual Player Heatmaps
        self.player_heatmaps: Dict[str, List[PitchCoordinates]] = {}
        for p in self.home_team.players + self.away_team.players:
            self.player_heatmaps[p.id] = [PitchCoordinates(x=p.current_coords.x, y=p.current_coords.y)]
            p.heatmap = list(self.player_heatmaps[p.id])

        self._update_all_positions()

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
        is_attack_dir_positive: True if team attacks toward x=100, False if toward x=0
        """
        sign = 1.0 if is_attack_dir_positive else -1.0

        if game_state == GameState.ALL_OUT_ATTACK:
            # Everyone pushes up aggressively
            shifts = {
                "GK":  (sign * 12.0, 0),
                "CB":  (sign * 15.0, 0),
                "RB":  (sign * 22.0, -3.0),
                "LB":  (sign * 22.0, 3.0),
                "CDM": (sign * 18.0, 0),
                "CM":  (sign * 20.0, 0),
                "CAM": (sign * 16.0, 0),
                "RW":  (sign * 12.0, -5.0),
                "LW":  (sign * 12.0, 5.0),
                "ST":  (sign * 8.0, 0),
            }
            return shifts.get(position, (0, 0))

        elif game_state == GameState.PARK_THE_BUS:
            # Everyone drops deep and compact
            shifts = {
                "GK":  (-sign * 2.0, 0),
                "CB":  (-sign * 6.0, 0),
                "RB":  (-sign * 12.0, 5.0),
                "LB":  (-sign * 12.0, -5.0),
                "CDM": (-sign * 10.0, 0),
                "CM":  (-sign * 14.0, 0),
                "CAM": (-sign * 18.0, 0),
                "RW":  (-sign * 22.0, 8.0),
                "LW":  (-sign * 22.0, -8.0),
                "ST":  (-sign * 15.0, 0),
            }
            return shifts.get(position, (0, 0))

        elif game_state == GameState.HIGH_PRESS:
            # Defensive line pushes very high
            shifts = {
                "GK":  (sign * 8.0, 0),
                "CB":  (sign * 12.0, 0),
                "RB":  (sign * 16.0, -2.0),
                "LB":  (sign * 16.0, 2.0),
                "CDM": (sign * 14.0, 0),
                "CM":  (sign * 12.0, 0),
                "CAM": (sign * 10.0, 0),
                "RW":  (sign * 8.0, 0),
                "LW":  (sign * 8.0, 0),
                "ST":  (sign * 5.0, 0),
            }
            return shifts.get(position, (0, 0))

        elif game_state == GameState.TIME_WASTING:
            # Similar to park the bus but even deeper, slow tempo
            shifts = {
                "GK":  (-sign * 3.0, 0),
                "CB":  (-sign * 8.0, 0),
                "RB":  (-sign * 14.0, 6.0),
                "LB":  (-sign * 14.0, -6.0),
                "CDM": (-sign * 12.0, 0),
                "CM":  (-sign * 16.0, 0),
                "CAM": (-sign * 20.0, 0),
                "RW":  (-sign * 24.0, 8.0),
                "LW":  (-sign * 24.0, -8.0),
                "ST":  (-sign * 18.0, 0),
            }
            return shifts.get(position, (0, 0))

        elif game_state == GameState.COUNTER_ATTACK:
            # Forward players sprint, defense holds
            if is_possessing:
                shifts = {
                    "GK":  (0, 0),
                    "CB":  (sign * 4.0, 0),
                    "RB":  (sign * 8.0, 0),
                    "LB":  (sign * 8.0, 0),
                    "CDM": (sign * 10.0, 0),
                    "CM":  (sign * 16.0, 0),
                    "CAM": (sign * 20.0, 0),
                    "RW":  (sign * 22.0, -6.0),
                    "LW":  (sign * 22.0, 6.0),
                    "ST":  (sign * 18.0, 0),
                }
            else:
                shifts = {
                    "GK":  (0, 0),
                    "CB":  (-sign * 4.0, 0),
                    "RB":  (-sign * 6.0, 0),
                    "LB":  (-sign * 6.0, 0),
                    "CDM": (-sign * 2.0, 0),
                    "CM":  (-sign * 4.0, 0),
                    "CAM": (-sign * 8.0, 0),
                    "RW":  (-sign * 10.0, 0),
                    "LW":  (-sign * 10.0, 0),
                    "ST":  (-sign * 6.0, 0),
                }
            return shifts.get(position, (0, 0))

        else:  # BALANCED
            # Standard possession-based push/drop
            if is_possessing:
                phase_push = {0: 0.0, 1: 8.0, 2: 15.0}.get(self.possession_phase, 0)
                shifts = {
                    "GK":  (sign * phase_push * 0.3, 0),
                    "CB":  (sign * phase_push * 0.4, 0),
                    "RB":  (sign * phase_push * 0.7, 0),
                    "LB":  (sign * phase_push * 0.7, 0),
                    "CDM": (sign * phase_push * 0.6, 0),
                    "CM":  (sign * phase_push * 0.8, 0),
                    "CAM": (sign * phase_push * 0.9, 0),
                    "RW":  (sign * phase_push * 1.0, 0),
                    "LW":  (sign * phase_push * 1.0, 0),
                    "ST":  (sign * phase_push * 0.9, 0),
                }
                return shifts.get(position, (0, 0))
            else:
                phase_drop = {0: 0.0, 1: 6.0, 2: 12.0}.get(self.possession_phase, 0)
                shifts = {
                    "GK":  (-sign * phase_drop * 0.2, 0),
                    "CB":  (-sign * phase_drop * 0.3, 0),
                    "RB":  (-sign * phase_drop * 0.5, 0),
                    "LB":  (-sign * phase_drop * 0.5, 0),
                    "CDM": (-sign * phase_drop * 0.5, 0),
                    "CM":  (-sign * phase_drop * 0.6, 0),
                    "CAM": (-sign * phase_drop * 0.7, 0),
                    "RW":  (-sign * phase_drop * 0.8, 0),
                    "LW":  (-sign * phase_drop * 0.8, 0),
                    "ST":  (-sign * phase_drop * 0.4, 0),
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
            return (0, random.uniform(-1, 1))  # Minimal lateral shuffle

        return (0, 0)

    def _compute_ball_gravity(self, player_y: float, ball_y: float) -> float:
        """Pull players toward the ball's lateral channel (compact shape)."""
        distance = ball_y - player_y
        # Stronger pull when ball is far, but capped
        pull = distance * 0.18
        return max(-8.0, min(8.0, pull))

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

            # 3. Ball gravity (lateral compactness)
            gravity_y = self._compute_ball_gravity(orig_y + shift_y, ball_y)

            # 4. Corridor wandering (Gaussian, scaled by fatigue)
            corr_x, corr_y = POSITION_CORRIDORS.get(p.position, (5.0, 5.0))
            fatigue_f = self.fatigue.get(p.id, 1.0)
            wander_x = random.gauss(0, corr_x * fatigue_f * 0.5)
            wander_y = random.gauss(0, corr_y * fatigue_f * 0.5)

            # 5. Combine everything
            new_x = orig_x + shift_x + run_x * fatigue_f + wander_x
            new_y = orig_y + shift_y + run_y * fatigue_f + gravity_y + wander_y

            # Clamp to pitch bounds
            p.current_coords.x = round(max(2.0, min(98.0, new_x)), 1)
            p.current_coords.y = round(max(3.0, min(97.0, new_y)), 1)

        # Update Away Team
        cb_idx_a = 0
        for p in self.away_team.players:
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

            # 3. Ball gravity
            gravity_y = self._compute_ball_gravity(orig_y + shift_y, ball_y)

            # 4. Corridor wandering
            corr_x, corr_y = POSITION_CORRIDORS.get(p.position, (5.0, 5.0))
            fatigue_f = self.fatigue.get(p.id, 1.0)
            wander_x = random.gauss(0, corr_x * fatigue_f * 0.5)
            wander_y = random.gauss(0, corr_y * fatigue_f * 0.5)

            # 5. Combine
            new_x = orig_x + shift_x + run_x * fatigue_f + wander_x
            new_y = orig_y + shift_y + run_y * fatigue_f + gravity_y + wander_y

            p.current_coords.x = round(max(2.0, min(98.0, new_x)), 1)
            p.current_coords.y = round(max(3.0, min(97.0, new_y)), 1)

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

        # Advance match clock
        time_advance = random.randint(15, 28)
        # Time wasting: slower clock
        possessing_state = self.home_game_state if self.possession_team_id == self.home_team.id else self.away_game_state
        if possessing_state == GameState.TIME_WASTING:
            time_advance = random.randint(22, 38)
        elif possessing_state == GameState.COUNTER_ATTACK:
            time_advance = random.randint(8, 15)  # Fast action

        self.second += time_advance
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
            self.period = "1H" if self.minute <= 45 else "2H"

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

            dice = random.random()
            if dice < xg and team_goals < 4 and random.random() < 0.38:
                outcome = ShotOutcome.GOAL
                event_type = EventType.GOAL
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
            self.current_actor = defending_team.players[0] if outcome in [ShotOutcome.SAVED, ShotOutcome.OFF_TARGET] else defending_team.players[2]
            self.current_ball_pos = PitchCoordinates(x=self.current_actor.current_coords.x, y=self.current_actor.current_coords.y)
            self._record_player_touch(self.current_actor, self.current_ball_pos)

            self.events_history.append(event)
            return event

        # ── 2. DEFENSIVE TACKLE → triggers COUNTER ATTACK ─────────────
        turnover_chance = 0.22 if self.passes_in_current_chain > 12 else (0.12 if game_state == GameState.ALL_OUT_ATTACK else 0.07)
        if under_pressure and random.random() < turnover_chance:
            # Pick a defender close to the ball
            defenders = [p for p in defending_team.players if p.position in ["CB", "CDM", "CM", "RB", "LB"]]
            defender = min(defenders, key=lambda p: abs(p.current_coords.x - self.current_ball_pos.x) + abs(p.current_coords.y - self.current_ball_pos.y)) if defenders else defending_team.players[2]
            defender.current_speed_kmh = round(random.uniform(20.0, 28.0), 1)
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
        recipient = random.choice(options)

        target_coords = PitchCoordinates(
            x=recipient.current_coords.x,
            y=recipient.current_coords.y
        )

        dist_m = self._calculate_pitch_distance_meters(self.current_ball_pos, target_coords)
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

        if is_complete:
            outcome = PassOutcome.COMPLETE
            self.current_actor = recipient
            self.current_ball_pos = target_coords
            self._record_player_touch(recipient, target_coords)

            if actor.id not in self.pass_matrix:
                self.pass_matrix[actor.id] = {}
            self.pass_matrix[actor.id][recipient.id] = self.pass_matrix[actor.id].get(recipient.id, 0) + 1
        else:
            outcome = PassOutcome.INTERCEPTED
            self.possession_team_id = defending_team.id
            # Pick closest defender to interception point
            defenders = defending_team.players[1:6]
            self.current_actor = min(defenders, key=lambda p: abs(p.current_coords.x - target_coords.x) + abs(p.current_coords.y - target_coords.y)) if defenders else defending_team.players[2]
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
