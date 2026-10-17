export type EventType =
  | "pass"
  | "shot"
  | "tackle"
  | "interception"
  | "pressure"
  | "carry"
  | "recovery"
  | "foul"
  | "card"
  | "goal"
  | "offside"
  | "corner"
  | "free_kick"
  | "substitution"
  | "save";

export type PersonaMode = "casual_fan" | "data_analyst" | "player_focus";
export type Language = "en" | "ro" | "es";

export interface PitchCoordinates {
  x: number;
  y: number;
}

export interface PlayerProfile {
  id: string;
  name: string;
  number: number;
  position: string;
  team_id: string;
  pace: number;
  stamina: number;
  passing_skill: number;
  shooting_skill: number;
  current_speed_kmh: number;
  distance_covered_meters: number;
  sprint_count: number;
  current_coords: PitchCoordinates;
  heatmap?: PitchCoordinates[];
}

export interface TeamProfile {
  id: string;
  name: string;
  short_name: string;
  primary_color: string;
  secondary_color: string;
  formation: string;
  manager: string;
  tactical_style: string;
  players: PlayerProfile[];
}

export interface MatchEvent {
  event_id: string;
  match_id: string;
  minute: number;
  second: number;
  period: "1H" | "2H" | "ET";
  team_id: string;
  player: PlayerProfile;
  recipient?: PlayerProfile | null;
  event_type: EventType;
  location: PitchCoordinates;
  end_location?: PitchCoordinates | null;
  ball_speed_kmh?: number | null;
  shot_speed_kmh?: number | null;
  player_speed_kmh: number;
  pass_distance_m?: number | null;
  pass_difficulty_rating?: number | null;
  pass_outcome?: string | null;
  xG?: number | null;
  xA?: number | null;
  shot_outcome?: string | null;
  under_pressure: boolean;
  pressure_intensity: number;
  possession_chain_id: string;
}

export interface TeamMatchStats {
  team_id: string;
  possession_pct: number;
  total_passes: number;
  successful_passes: number;
  pass_accuracy_pct: number;
  average_pass_difficulty: number;
  total_shots: number;
  shots_on_target: number;
  goals: number;
  total_xG: number;
  tackles_won: number;
  pressures_applied: number;
  avg_ball_speed_kmh: number;
  distance_covered_km: number;
}

export interface RhythmState {
  control_vs_chaos_index: number;
  tactical_pressure_index: number;
  momentum_team_id: string;
  dominant_zone: string;
  pace_rating: string;
}

export interface ExplainabilityInsight {
  insight_id: string;
  minute: number;
  second: number;
  title: string;
  why_it_matters: string;
  tactical_shift_explanation: string;
  pattern_detected: string;
  key_contributing_factors: string[];
  confidence_score: number;
}

export interface BroadcastOverlay {
  graphic_id: string;
  graphic_type: "lower_third" | "tactical_radar" | "shot_map_card" | "speed_pass_badge" | "momentum_gauge" | "player_spotlight";
  display_title: string;
  primary_metric: string;
  secondary_metric?: string | null;
  detail_text: string;
  duration_seconds: number;
  is_active: boolean;
  accent_color: string;
}

export interface PersonalizedNarrative {
  minute: number;
  second: number;
  casual_fan_narrative: string;
  data_analyst_narrative: string;
  player_focus_narrative?: string | null;
  language: Language;
}

export interface AgentLog {
  agent_name: string;
  role: string;
  message: string;
  timestamp: string;
  status: "processing" | "handoff" | "success" | "alert";
}

export interface PassLink {
  source_player_id: string;
  target_player_id: string;
  count: number;
}

export interface TimelineMoment {
  minute: number;
  type: string;
  player: string;
  team: string;
  speed: number;
  xg: number;
}

export interface MatchScoreSummary {
  match_id: string;
  home_team_id: string;
  away_team_id: string;
  home_team_name: string;
  away_team_name: string;
  home_short_name: string;
  away_short_name: string;
  score_home: number;
  score_away: number;
  minute: number;
  period: string;
  is_finished: boolean;
  latest_event_text: string;
}

export interface LeagueTeamStanding {
  rank: number;
  previous_rank: number;
  team_id: string;
  team_name: string;
  short_name: string;
  primary_color: string;
  played: number;
  won: number;
  drawn: number;
  lost: number;
  goals_for: number;
  goals_against: number;
  goal_diff: number;
  points: number;
  form: string[];
}

export interface GoalAlert {
  alert_id: string;
  match_id: string;
  minute: number;
  text: string;
  scorer: string;
  team_name: string;
  home_name: string;
  away_name: string;
  score_home: number;
  score_away: number;
}

export interface LiveMatchPayload {
  match_id: string;
  current_minute: number;
  current_second: number;
  score_home: number;
  score_away: number;
  is_finished?: boolean;
  is_half_time?: boolean;
  latest_event: MatchEvent;
  stats_home: TeamMatchStats;
  stats_away: TeamMatchStats;
  rhythm: RhythmState;
  active_overlay?: BroadcastOverlay | null;
  latest_insight?: ExplainabilityInsight | null;
  narrative: PersonalizedNarrative;
  focused_player?: PlayerProfile | null;
  agent_logs: AgentLog[];
  pass_links: PassLink[];
  heatmap_points: PitchCoordinates[];
  timeline_moments: TimelineMoment[];
  home_players?: PlayerProfile[];
  away_players?: PlayerProfile[];
  league_standings?: LeagueTeamStanding[];
  matchweek_matches?: MatchScoreSummary[];
  latest_goal_alert?: GoalAlert | null;
  player_heatmaps?: Record<string, PitchCoordinates[]>;
}

export interface ClubSummary {
  id: string;
  name: string;
  short_name: string;
  primary_color: string;
  secondary_color: string;
  manager: string;
  tactical_style: string;
}
