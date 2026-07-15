"""
schemas.py
----------
All Pydantic v2 request/response models for the Soccer Solver API.

Kept in one place so that the shape of every public API contract is visible
at a glance and changes can be tracked in a single file.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


# ─── Player Search ────────────────────────────────────────────────────────────


class PlayerSearchResult(BaseModel):
    """A single player card returned by the search endpoint."""

    player_id: int
    player_name: str
    position: str
    current_club: str
    current_league: str
    current_league_tier: str
    current_market_value_eur: float
    image_url: Optional[str] = None


class PlayerSearchResponse(BaseModel):
    """Paginated list of player search results."""

    results: list[PlayerSearchResult]
    total: int
    limit: int
    offset: int


# ─── Player Profile ───────────────────────────────────────────────────────────


class PlayerMetrics(BaseModel):
    """Raw performance counters for a player."""

    minutes_played: int
    goals: int
    assists: int


class PercentileMetrics(BaseModel):
    """
    How this player's output metrics compare to a peer group.
    All percentile values are in the range [0, 100].
    A value of 80 means the player outperforms 80% of peers.
    """

    goals_percentile: float = Field(ge=0.0, le=100.0)
    assists_percentile: float = Field(ge=0.0, le=100.0)
    minutes_percentile: float = Field(ge=0.0, le=100.0)
    sample_size: int = Field(ge=0, description="Number of players in the comparison group")


class PlayerProfileResponse(BaseModel):
    """Full player profile including contextualised performance percentiles."""

    player_id: int
    player_name: str
    position: str
    age: int
    current_club: str
    current_league: str
    current_league_tier: str
    current_market_value_eur: float
    image_url: Optional[str] = None
    metrics: PlayerMetrics
    # vs all players with the same position, any league
    position_percentiles: PercentileMetrics
    # vs players with the same position in the same league
    league_percentiles: PercentileMetrics


# ─── Transition Simulator ─────────────────────────────────────────────────────


class SimilarTransition(BaseModel):
    """
    A single real historical transfer used as a comparable precedent.
    Includes both the before and after value so the pattern is visible.
    """

    player_name: str
    position: str
    origin_tier: str
    destination_tier: str
    age_at_transfer: Optional[int] = None
    value_before_eur: float
    value_after_eur: float
    value_change_pct: float
    transfer_date: str


class TransitionPrediction(BaseModel):
    """
    Full output of the Transition Simulator for one player × destination.

    ``value_range_low_eur`` / ``value_range_high_eur`` represent the p25–p75
    band of observed post-transition value changes applied to the player's
    current market value.  A ``thin_sample_warning`` is set when fewer than
    five comparable transfers exist so the UI can surface the uncertainty.
    """

    player_id: int
    player_name: str
    current_value_eur: float
    destination_tier: str
    destination_club: Optional[str] = None
    # Predicted value band (12-month horizon)
    value_range_low_eur: float
    value_range_high_eur: float
    predicted_change_pct_mean: float
    confidence_level: str = Field(
        description="'High' (n≥10), 'Medium' (n≥5), 'Low' (n<5)"
    )
    confidence_score: float = Field(ge=0.0, le=1.0)
    sample_size: int
    thin_sample_warning: bool
    comparable_transitions: list[SimilarTransition]
    narrative: str


# ─── Generic error shape ──────────────────────────────────────────────────────


class ErrorResponse(BaseModel):
    detail: str
    code: str
