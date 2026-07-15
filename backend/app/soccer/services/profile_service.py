"""
profile_service.py
------------------
Player profile assembly and percentile computation.

Responsibility: given a player_id and a PlayerRepository, return a fully
contextualised PlayerProfileResponse — including performance percentiles
against position peers globally and within the same league.

No file I/O, no HTTP concerns, no dependency on the Transition service.
"""

from __future__ import annotations

from typing import Any, Optional

from app.soccer.repository import PlayerRepository
from app.soccer.schemas import (
    PercentileMetrics,
    PlayerMetrics,
    PlayerProfileResponse,
)


# ─── Percentile helpers ───────────────────────────────────────────────────────


def _percentile_of_score(values: list[float], score: float) -> float:
    """
    What percentage of *values* are **strictly below** *score*?

    Returns a float in [0, 100].  An empty list returns 0.0.
    This matches the 'weak' definition: a player at exactly the median
    is above ~50% of peers, not 100%.
    """
    if not values:
        return 0.0
    below = sum(1 for v in values if v < score)
    return round((below / len(values)) * 100, 1)


def _extract_metric(players: list[dict[str, Any]], key: str) -> list[float]:
    """Pull a single metric value from every player that has metrics."""
    return [
        float(p["metrics"][key])
        for p in players
        if p.get("metrics") and key in p["metrics"]
    ]


def compute_percentiles(
    player_metrics: dict[str, Any],
    peer_group: list[dict[str, Any]],
) -> PercentileMetrics:
    """
    Compute goal / assist / minutes percentiles for *player_metrics*
    relative to *peer_group*.

    Args:
        player_metrics: The ``metrics`` dict from the player's own record.
        peer_group:     List of player dicts to compare against.

    Returns:
        PercentileMetrics with all three percentile scores and the group size.
    """
    goals_values = _extract_metric(peer_group, "goals")
    assists_values = _extract_metric(peer_group, "assists")
    minutes_values = _extract_metric(peer_group, "minutes_played")

    return PercentileMetrics(
        goals_percentile=_percentile_of_score(
            goals_values, float(player_metrics.get("goals", 0))
        ),
        assists_percentile=_percentile_of_score(
            assists_values, float(player_metrics.get("assists", 0))
        ),
        minutes_percentile=_percentile_of_score(
            minutes_values, float(player_metrics.get("minutes_played", 0))
        ),
        sample_size=len(peer_group),
    )


# ─── Public service function ──────────────────────────────────────────────────


def get_player_profile(
    player_id: int,
    repo: PlayerRepository,
) -> Optional[PlayerProfileResponse]:
    """
    Build a full profile for *player_id*, including two sets of percentiles:

    - ``position_percentiles``  — vs all players at the same position
    - ``league_percentiles``    — vs players at the same position *and* league

    Returns ``None`` if the player_id does not exist in the repository.
    """
    player = repo.get_by_id(player_id)
    if player is None:
        return None

    raw_metrics: dict[str, Any] = player.get("metrics") or {
        "minutes_played": 0,
        "goals": 0,
        "assists": 0,
    }

    # Peer groups from the repository (pre-indexed, no re-filtering needed)
    position_peers = repo.get_by_position(player["position"])
    league_peers = repo.get_by_position_and_league(
        player["position"], player["current_league"]
    )

    return PlayerProfileResponse(
        player_id=player["player_id"],
        player_name=player["player_name"],
        position=player["position"],
        age=player["age"],
        current_club=player["current_club"],
        current_league=player["current_league"],
        current_league_tier=player["current_league_tier"],
        current_market_value_eur=player["current_market_value_eur"],
        image_url=player.get("image_url"),
        metrics=PlayerMetrics(
            minutes_played=raw_metrics.get("minutes_played", 0),
            goals=raw_metrics.get("goals", 0),
            assists=raw_metrics.get("assists", 0),
        ),
        position_percentiles=compute_percentiles(raw_metrics, position_peers),
        league_percentiles=compute_percentiles(raw_metrics, league_peers),
    )
