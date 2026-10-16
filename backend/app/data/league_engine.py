import random
from typing import List, Dict, Optional, Tuple
from app.data.models import LeagueTeamStanding, MatchScoreSummary, GoalAlert
from app.data.teams_data import get_premier_league_teams

class PremierLeagueMatchweekEngine:
    """
    Simulates a full 20-team Premier League Matchweek (10 simultaneous fixtures),
    computing real-time 'As It Stands' standings (Flashscore style) and generating
    live goal alerts from concurrent matches.
    """

    def __init__(self):
        self.teams_metadata = get_premier_league_teams()
        
        # Pre-Matchweek 28 Baseline Standings (Authentic EPL point distribution)
        # played=27 matches before this matchweek
        self.baseline_stats: Dict[str, Dict[str, int]] = {
            "liverpool":     {"p": 27, "w": 19, "d": 7, "l": 1,  "gf": 64, "ga": 23, "pts": 64, "form": ["W", "W", "D", "W", "W"]},
            "mancity":       {"p": 27, "w": 19, "d": 5, "l": 3,  "gf": 61, "ga": 26, "pts": 62, "form": ["W", "D", "W", "W", "L"]},
            "arsenal":       {"p": 27, "w": 18, "d": 7, "l": 2,  "gf": 58, "ga": 22, "pts": 61, "form": ["W", "W", "W", "D", "W"]},
            "chelsea":       {"p": 27, "w": 15, "d": 6, "l": 6,  "gf": 53, "ga": 33, "pts": 51, "form": ["W", "L", "W", "W", "D"]},
            "astonvilla":    {"p": 27, "w": 15, "d": 5, "l": 7,  "gf": 48, "ga": 37, "pts": 50, "form": ["L", "W", "D", "W", "W"]},
            "tottenham":     {"p": 27, "w": 14, "d": 4, "l": 9,  "gf": 55, "ga": 38, "pts": 46, "form": ["W", "W", "L", "L", "W"]},
            "newcastle":     {"p": 27, "w": 13, "d": 6, "l": 8,  "gf": 46, "ga": 35, "pts": 45, "form": ["D", "W", "W", "L", "D"]},
            "brighton":      {"p": 27, "w": 11, "d": 10,"l": 6,  "gf": 42, "ga": 38, "pts": 43, "form": ["W", "D", "D", "W", "L"]},
            "nottingham":    {"p": 27, "w": 12, "d": 6, "l": 9,  "gf": 36, "ga": 33, "pts": 42, "form": ["W", "W", "L", "W", "D"]},
            "bournemouth":   {"p": 27, "w": 11, "d": 8, "l": 8,  "gf": 41, "ga": 34, "pts": 41, "form": ["D", "W", "L", "W", "W"]},
            "fulham":        {"p": 27, "w": 10, "d": 9, "l": 8,  "gf": 39, "ga": 36, "pts": 39, "form": ["D", "L", "W", "D", "W"]},
            "brentford":     {"p": 27, "w": 11, "d": 4, "l": 12, "gf": 45, "ga": 44, "pts": 37, "form": ["L", "W", "W", "L", "D"]},
            "manunited":     {"p": 27, "w": 10, "d": 6, "l": 11, "gf": 33, "ga": 36, "pts": 36, "form": ["L", "D", "W", "L", "W"]},
            "westham":       {"p": 27, "w": 8,  "d": 6, "l": 13, "gf": 31, "ga": 49, "pts": 30, "form": ["L", "L", "D", "W", "L"]},
            "crystalpalace": {"p": 27, "w": 7,  "d": 8, "l": 12, "gf": 29, "ga": 39, "pts": 29, "form": ["D", "W", "L", "D", "L"]},
            "everton":       {"p": 27, "w": 6,  "d": 9, "l": 12, "gf": 26, "ga": 37, "pts": 27, "form": ["D", "D", "L", "W", "D"]},
            "wolves":        {"p": 27, "w": 6,  "d": 4, "l": 17, "gf": 35, "ga": 54, "pts": 22, "form": ["L", "L", "W", "L", "L"]},
            "leicester":     {"p": 27, "w": 4,  "d": 5, "l": 18, "gf": 28, "ga": 57, "pts": 17, "form": ["L", "D", "L", "L", "L"]},
            "ipswich":       {"p": 27, "w": 3,  "d": 8, "l": 16, "gf": 24, "ga": 53, "pts": 17, "form": ["L", "L", "D", "L", "D"]},
            "southampton":   {"p": 27, "w": 2,  "d": 3, "l": 22, "gf": 19, "ga": 63, "pts": 9,  "form": ["L", "L", "L", "L", "L"]}
        }

        # 10 Concurrent Fixtures of Matchweek 28
        self.fixtures_config = [
            ("arsenal", "mancity"),
            ("liverpool", "chelsea"),
            ("manunited", "tottenham"),
            ("astonvilla", "newcastle"),
            ("brighton", "westham"),
            ("bournemouth", "brentford"),
            ("fulham", "wolves"),
            ("everton", "crystalpalace"),
            ("nottingham", "leicester"),
            ("ipswich", "southampton"),
        ]

        # In-memory match state for all 10 fixtures
        self.matches: Dict[str, Dict] = {}
        self.previous_ranks: Dict[str, int] = {}
        self.latest_goal_alert: Optional[GoalAlert] = None
        self.alert_counter = 0
        self.last_simulated_minute = 0
        
        self.init_matchweek()

    def init_matchweek(self):
        """Initializes all 10 fixtures with 0-0 and pre-computes initial ranks."""
        self.matches.clear()
        for h_id, a_id in self.fixtures_config:
            m_id = f"mw28_{h_id}_{a_id}"
            h_meta = self.teams_metadata.get(h_id)
            a_meta = self.teams_metadata.get(a_id)
            
            self.matches[m_id] = {
                "match_id": m_id,
                "home_id": h_id,
                "away_id": a_id,
                "home_name": h_meta.name if h_meta else h_id.title(),
                "away_name": a_meta.name if a_meta else a_id.title(),
                "home_short": h_meta.short_name if h_meta else h_id[:3].upper(),
                "away_short": a_meta.short_name if a_meta else a_id[:3].upper(),
                "score_home": 0,
                "score_away": 0,
                "minute": 1,
                "period": "1H",
                "is_finished": False,
                "latest_event_text": "Kickoff at Matchweek 28",
                "goal_scorers": []
            }

        # Calculate initial ranks at 0-0
        initial_standings = self.compute_standings()
        for idx, s in enumerate(initial_standings):
            self.previous_ranks[s.team_id] = idx + 1

    def sync_featured_match(self, home_id: str, away_id: str, score_h: int, score_a: int, minute: int, is_finished: bool):
        """Synchronizes the featured on-screen pitch match with the league matchweek."""
        featured_key = None
        for m_id, m in self.matches.items():
            if m["home_id"] == home_id and m["away_id"] == away_id:
                featured_key = m_id
                break
        
        if featured_key:
            self.matches[featured_key]["score_home"] = score_h
            self.matches[featured_key]["score_away"] = score_a
            self.matches[featured_key]["minute"] = minute
            self.matches[featured_key]["is_finished"] = is_finished
            self.matches[featured_key]["period"] = "FT" if is_finished else ("2H" if minute > 45 else "1H")

    def tick_background_matches(self, current_minute: int, featured_home_id: str, featured_away_id: str):
        """
        Advances the 9 background matches synchronously with the broadcast clock,
        generating realistic football goals and alerts.
        """
        if current_minute <= self.last_simulated_minute:
            return

        self.last_simulated_minute = current_minute
        self.latest_goal_alert = None  # Clear previous alert unless new one occurs

        # Top tier weights
        team_weights = {
            "liverpool": 1.4, "mancity": 1.4, "arsenal": 1.35, "chelsea": 1.2,
            "astonvilla": 1.2, "tottenham": 1.15, "newcastle": 1.15, "brighton": 1.1,
            "bournemouth": 1.05, "nottingham": 1.05, "fulham": 1.0, "brentford": 1.0,
            "manunited": 1.0, "westham": 0.95, "crystalpalace": 0.9, "everton": 0.85,
            "wolves": 0.85, "leicester": 0.8, "ipswich": 0.75, "southampton": 0.7
        }

        for m_id, match in self.matches.items():
            h_id = match["home_id"]
            a_id = match["away_id"]

            # Skip the featured match (that is updated directly by SyntheticMatchEngine)
            if h_id == featured_home_id and a_id == featured_away_id:
                continue

            match["minute"] = current_minute
            if current_minute >= 90:
                match["is_finished"] = True
                match["period"] = "FT"
            elif current_minute > 45:
                match["period"] = "2H"
            else:
                match["period"] = "1H"

            # Check for goals in background matches (realistic football probability ~0.012 per minute)
            # Maximum ~4 goals per match
            if not match["is_finished"] and (match["score_home"] + match["score_away"]) < 5:
                hw = team_weights.get(h_id, 1.0)
                aw = team_weights.get(a_id, 1.0)

                # Home goal roll
                if random.random() < (0.012 * hw):
                    match["score_home"] += 1
                    scorer = self._pick_goalscorer(h_id)
                    alert_text = f"⚽ GOAL! {scorer} scores for {match['home_name']} ({match['score_home']} - {match['score_away']}) at {current_minute}'!"
                    match["latest_event_text"] = f"Goal: {scorer} ({current_minute}')"
                    match["goal_scorers"].append(f"{scorer} {current_minute}'")
                    
                    self.alert_counter += 1
                    self.latest_goal_alert = GoalAlert(
                        alert_id=f"alt_{self.alert_counter}_{current_minute}",
                        match_id=m_id,
                        minute=current_minute,
                        text=alert_text,
                        scorer=scorer,
                        team_name=match["home_name"],
                        home_name=match["home_name"],
                        away_name=match["away_name"],
                        score_home=match["score_home"],
                        score_away=match["score_away"]
                    )

                # Away goal roll
                elif random.random() < (0.009 * aw):
                    match["score_away"] += 1
                    scorer = self._pick_goalscorer(a_id)
                    alert_text = f"⚽ GOAL! {scorer} strikes for {match['away_name']} ({match['score_home']} - {match['score_away']}) at {current_minute}'!"
                    match["latest_event_text"] = f"Goal: {scorer} ({current_minute}')"
                    match["goal_scorers"].append(f"{scorer} {current_minute}'")
                    
                    self.alert_counter += 1
                    self.latest_goal_alert = GoalAlert(
                        alert_id=f"alt_{self.alert_counter}_{current_minute}",
                        match_id=m_id,
                        minute=current_minute,
                        text=alert_text,
                        scorer=scorer,
                        team_name=match["away_name"],
                        home_name=match["home_name"],
                        away_name=match["away_name"],
                        score_home=match["score_home"],
                        score_away=match["score_away"]
                    )

    def _pick_goalscorer(self, team_id: str) -> str:
        """Picks a realistic attacker / midfielder goalscorer from the squad."""
        meta = self.teams_metadata.get(team_id)
        if not meta or not meta.players:
            return "Striker"
        # Favor attacking players (positions ST, RW, LW, CAM)
        attackers = [p.name for p in meta.players if p.position in ("ST", "RW", "LW", "CAM")]
        if attackers:
            return random.choice(attackers)
        return meta.players[-1].name

    def compute_standings(self) -> List[LeagueTeamStanding]:
        """
        Computes dynamic 'As It Stands' Premier League table factoring in
        the live scores of all 10 ongoing matches.
        """
        table_dict: Dict[str, Dict] = {}
        for t_id, base in self.baseline_stats.items():
            meta = self.teams_metadata.get(t_id)
            table_dict[t_id] = {
                "team_id": t_id,
                "team_name": meta.name if meta else t_id.title(),
                "short_name": meta.short_name if meta else t_id[:3].upper(),
                "primary_color": meta.primary_color if meta else "#FFFFFF",
                "played": base["p"] + 1,  # Matchweek 28 counts as played
                "won": base["w"],
                "drawn": base["d"],
                "lost": base["l"],
                "goals_for": base["gf"],
                "goals_against": base["ga"],
                "points": base["pts"],
                "form": list(base["form"])
            }

        # Apply live match scores
        for m in self.matches.values():
            h_id = m["home_id"]
            a_id = m["away_id"]
            sh = m["score_home"]
            sa = m["score_away"]

            if h_id in table_dict and a_id in table_dict:
                table_dict[h_id]["goals_for"] += sh
                table_dict[h_id]["goals_against"] += sa
                table_dict[a_id]["goals_for"] += sa
                table_dict[a_id]["goals_against"] += sh

                if sh > sa:
                    table_dict[h_id]["won"] += 1
                    table_dict[h_id]["points"] += 3
                    table_dict[a_id]["lost"] += 1
                elif sh == sa:
                    table_dict[h_id]["drawn"] += 1
                    table_dict[h_id]["points"] += 1
                    table_dict[a_id]["drawn"] += 1
                    table_dict[a_id]["points"] += 1
                else:
                    table_dict[h_id]["lost"] += 1
                    table_dict[a_id]["won"] += 1
                    table_dict[a_id]["points"] += 3

        # Convert to list and compute Goal Difference
        rows = list(table_dict.values())
        for r in rows:
            r["goal_diff"] = r["goals_for"] - r["goals_against"]

        # Sort criteria: Points DESC -> Goal Difference DESC -> Goals For DESC -> Name ASC
        rows.sort(key=lambda x: (x["points"], x["goal_diff"], x["goals_for"]), reverse=True)

        standings: List[LeagueTeamStanding] = []
        for rank_idx, r in enumerate(rows, start=1):
            t_id = r["team_id"]
            prev_rank = self.previous_ranks.get(t_id, rank_idx)
            
            standings.append(LeagueTeamStanding(
                rank=rank_idx,
                previous_rank=prev_rank,
                team_id=t_id,
                team_name=r["team_name"],
                short_name=r["short_name"],
                primary_color=r["primary_color"],
                played=r["played"],
                won=r["won"],
                drawn=r["drawn"],
                lost=r["lost"],
                goals_for=r["goals_for"],
                goals_against=r["goals_against"],
                goal_diff=r["goal_diff"],
                points=r["points"],
                form=r["form"]
            ))

        return standings

    def get_matchweek_summaries(self) -> List[MatchScoreSummary]:
        """Returns the status and score of all 10 Matchweek 28 fixtures."""
        summaries: List[MatchScoreSummary] = []
        for m in self.matches.values():
            summaries.append(MatchScoreSummary(
                match_id=m["match_id"],
                home_team_id=m["home_id"],
                away_team_id=m["away_id"],
                home_team_name=m["home_name"],
                away_team_name=m["away_name"],
                home_short_name=m["home_short"],
                away_short_name=m["away_short"],
                score_home=m["score_home"],
                score_away=m["score_away"],
                minute=m["minute"],
                period=m["period"],
                is_finished=m["is_finished"],
                latest_event_text=m["latest_event_text"]
            ))
        return summaries
