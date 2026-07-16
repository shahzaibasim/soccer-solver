"""
test_profile_service.py
-----------------------
Unit tests for profile_service percentile computation and profile assembly.

All tests use in-memory mock data — no JSON files are read.
"""

from __future__ import annotations

import pytest

from app.soccer.repository import PlayerRepository
from app.soccer.services.profile_service import (
    _percentile_of_score,
    compute_percentiles,
    get_player_profile,
)


# ─── Fixtures ─────────────────────────────────────────────────────────────────

def _make_player(
    player_id: int,
    player_name: str = "Test Player",
    position: str = "FW",
    age: int = 25,
    current_club: str = "Test FC",
    current_league: str = "GB1",
    current_league_tier: str = "Tier 1",
    current_market_value_eur: float = 5_000_000.0,
    goals: int = 10,
    assists: int = 5,
    minutes_played: int = 1800,
) -> dict:
    return {
        "player_id": player_id,
        "player_name": player_name,
        "position": position,
        "age": age,
        "current_club": current_club,
        "current_league": current_league,
        "current_league_tier": current_league_tier,
        "current_market_value_eur": current_market_value_eur,
        "image_url": None,
        "metrics": {
            "goals": goals,
            "assists": assists,
            "minutes_played": minutes_played,
        },
    }


# A pool of 5 forwards in the same league, plus our query player (player_id=1)
QUERY_PLAYER = _make_player(1, goals=20, assists=8, minutes_played=2500)
PEER_PLAYERS = [
    _make_player(2, goals=5, assists=2, minutes_played=1200),
    _make_player(3, goals=8, assists=4, minutes_played=1600),
    _make_player(4, goals=12, assists=6, minutes_played=2000),
    _make_player(5, goals=15, assists=7, minutes_played=2200),
    _make_player(6, goals=18, assists=9, minutes_played=2400),
]
ALL_PLAYERS = [QUERY_PLAYER] + PEER_PLAYERS


def _make_repo(players: list[dict]) -> PlayerRepository:
    return PlayerRepository(players)


# ─── _percentile_of_score ────────────────────────────────────────────────────

class TestPercentileOfScore:

    def test_empty_list_returns_zero(self) -> None:
        assert _percentile_of_score([], 10.0) == 0.0

    def test_top_scorer_gets_near_100(self) -> None:
        values = [1.0, 5.0, 10.0, 15.0, 20.0]
        # Score 20 is the maximum — 4 values are strictly below it → 80%
        pct = _percentile_of_score(values, 20.0)
        assert pct == pytest.approx(80.0)

    def test_bottom_scorer_gets_zero(self) -> None:
        values = [5.0, 10.0, 15.0, 20.0]
        pct = _percentile_of_score(values, 1.0)
        assert pct == 0.0  # nobody is below 1

    def test_median_score_is_around_50(self) -> None:
        values = [10.0, 20.0, 30.0, 40.0, 50.0]
        # Score 30 — 2 values below → 40%
        pct = _percentile_of_score(values, 30.0)
        assert pct == pytest.approx(40.0)

    def test_all_equal_values_gives_zero(self) -> None:
        """If everyone has the same score, nobody is 'below' — percentile = 0."""
        values = [10.0, 10.0, 10.0]
        assert _percentile_of_score(values, 10.0) == 0.0


# ─── compute_percentiles ──────────────────────────────────────────────────────

class TestComputePercentiles:

    def test_top_scorer_goals_percentile_is_high(self) -> None:
        """QUERY_PLAYER has 20 goals — highest in the pool → should be near 100."""
        result = compute_percentiles(QUERY_PLAYER["metrics"], ALL_PLAYERS)
        # 5 out of 6 players score below 20 goals → 5/6 ≈ 83.3%
        assert result.goals_percentile >= 80.0

    def test_sample_size_matches_peer_group(self) -> None:
        result = compute_percentiles(QUERY_PLAYER["metrics"], ALL_PLAYERS)
        assert result.sample_size == len(ALL_PLAYERS)

    def test_assists_percentile_is_in_valid_range(self) -> None:
        result = compute_percentiles(QUERY_PLAYER["metrics"], ALL_PLAYERS)
        assert 0.0 <= result.assists_percentile <= 100.0

    def test_minutes_percentile_is_in_valid_range(self) -> None:
        result = compute_percentiles(QUERY_PLAYER["metrics"], ALL_PLAYERS)
        assert 0.0 <= result.minutes_percentile <= 100.0

    def test_empty_peer_group_gives_zero_percentiles(self) -> None:
        result = compute_percentiles(QUERY_PLAYER["metrics"], [])
        assert result.goals_percentile == 0.0
        assert result.assists_percentile == 0.0
        assert result.minutes_percentile == 0.0
        assert result.sample_size == 0


# ─── get_player_profile ───────────────────────────────────────────────────────

class TestGetPlayerProfile:

    def test_returns_none_for_missing_player(self) -> None:
        repo = _make_repo(ALL_PLAYERS)
        result = get_player_profile(player_id=99999, repo=repo)
        assert result is None

    def test_returns_profile_for_existing_player(self) -> None:
        repo = _make_repo(ALL_PLAYERS)
        result = get_player_profile(player_id=1, repo=repo)
        assert result is not None
        assert result.player_id == 1
        assert result.player_name == "Test Player"

    def test_profile_has_two_percentile_sets(self) -> None:
        repo = _make_repo(ALL_PLAYERS)
        result = get_player_profile(player_id=1, repo=repo)
        assert result is not None
        assert result.position_percentiles is not None
        assert result.league_percentiles is not None

    def test_position_percentile_sample_size_correct(self) -> None:
        """All players in ALL_PLAYERS are position='FW' — sample should be all."""
        repo = _make_repo(ALL_PLAYERS)
        result = get_player_profile(player_id=1, repo=repo)
        assert result is not None
        assert result.position_percentiles.sample_size == len(ALL_PLAYERS)

    def test_metrics_values_match_source_data(self) -> None:
        repo = _make_repo(ALL_PLAYERS)
        result = get_player_profile(player_id=1, repo=repo)
        assert result is not None
        assert result.metrics.goals == QUERY_PLAYER["metrics"]["goals"]
        assert result.metrics.assists == QUERY_PLAYER["metrics"]["assists"]
        assert result.metrics.minutes_played == QUERY_PLAYER["metrics"]["minutes_played"]

    def test_player_with_no_metrics_does_not_crash(self) -> None:
        """A player dict missing 'metrics' should return zeroes, not raise."""
        player_no_metrics = _make_player(999)
        player_no_metrics.pop("metrics")
        repo = _make_repo([player_no_metrics])
        result = get_player_profile(player_id=999, repo=repo)
        assert result is not None
        assert result.metrics.goals == 0
