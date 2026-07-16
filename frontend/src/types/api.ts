// ─── Search ────────────────────────────────────────────────────────────────

export interface PlayerSearchResult {
  player_id: number;
  player_name: string;
  position: string;
  current_club: string;
  current_league: string;
  current_league_tier: string;
  current_market_value_eur: number;
  image_url: string | null;
}

export interface PlayerSearchResponse {
  results: PlayerSearchResult[];
  total: number;
  limit: number;
  offset: number;
}

// ─── Profile ───────────────────────────────────────────────────────────────

export interface PlayerMetrics {
  minutes_played: number;
  goals: number;
  assists: number;
}

export interface PercentileMetrics {
  goals_percentile: number;
  assists_percentile: number;
  minutes_percentile: number;
  sample_size: number;
}

export interface PlayerProfileResponse {
  player_id: number;
  player_name: string;
  position: string;
  age: number;
  current_club: string;
  current_league: string;
  current_league_tier: string;
  current_market_value_eur: number;
  image_url: string | null;
  metrics: PlayerMetrics;
  position_percentiles: PercentileMetrics;
  league_percentiles: PercentileMetrics;
}

// ─── Transition Simulator ──────────────────────────────────────────────────

export interface SimilarTransition {
  player_name: string;
  position: string;
  origin_tier: string;
  destination_tier: string;
  age_at_transfer: number | null;
  value_before_eur: number;
  value_after_eur: number;
  value_change_pct: number;
  transfer_date: string;
}

export interface TransitionPrediction {
  player_id: number;
  player_name: string;
  current_value_eur: number;
  destination_tier: string;
  destination_club: string | null;
  value_range_low_eur: number;
  value_range_high_eur: number;
  predicted_change_pct_mean: number;
  confidence_level: string;
  confidence_score: number;
  sample_size: number;
  thin_sample_warning: boolean;
  comparable_transitions: SimilarTransition[];
  narrative: string;
}

// ─── Errors ────────────────────────────────────────────────────────────────

export interface ApiError {
  detail: string;
  code?: string;
}
