"""
test_transition_service.py
--------------------------
Unit tests for the two pieces of logic that matter most:
  1. Comparable-transition matching (find_comparable_transitions)
  2. Value-delta modelling (predict_value_range)
  3. Narrative generation (generate_narrative)

All tests use small, hand-crafted fixture datasets — no JSON files are read.
"""

from __future__ import annotations

import pytest

from app.soccer.schemas import SimilarTransition
from app.soccer.services.transition_service import (
    THIN_SAMPLE_THRESHOLD,
    find_comparable_transitions,
    generate_narrative,
    predict_value_range,
)


# ─── Fixtures ─────────────────────────────────────────────────────────────────

def _make_transition(
    player_name: str = "Test Player",
    position: str = "FW",
    origin_tier: str = "Tier 2",
    destination_tier: str = "Tier 1",
    age_at_transfer: int | None = 26,
    value_before: float = 5_000_000.0,
    value_after: float = 7_500_000.0,
    value_change_pct: float = 50.0,
) -> dict:
    return {
        "player_name": player_name,
        "position": position,
        "age_at_transfer": age_at_transfer,
        "transfer_date": "2024-06-01",
        "origin": {"club_id": 1, "club_name": "Origin Club", "league_tier": origin_tier},
        "destination": {"club_id": 2, "club_name": "Dest Club", "league_tier": destination_tier},
        "financials": {
            "market_value_before_eur": value_before,
            "market_value_after_eur": value_after,
            "value_change_percentage": value_change_pct,
        },
    }


def _make_similar(
    player_name: str = "Comp Player",
    value_change_pct: float = 20.0,
    value_before: float = 5_000_000.0,
    value_after: float = 6_000_000.0,
) -> SimilarTransition:
    return SimilarTransition(
        player_name=player_name,
        position="FW",
        origin_tier="Tier 2",
        destination_tier="Tier 1",
        age_at_transfer=25,
        value_before_eur=value_before,
        value_after_eur=value_after,
        value_change_pct=value_change_pct,
        transfer_date="2024-06-01",
    )


TRANSITIONS = [
    _make_transition("Player A", "FW", "Tier 2", "Tier 1", 24, value_change_pct=30.0),
    _make_transition("Player B", "FW", "Tier 2", "Tier 1", 27, value_change_pct=50.0),
    _make_transition("Player C", "FW", "Tier 2", "Tier 1", 22, value_change_pct=20.0),
    _make_transition("Player D", "MF", "Tier 2", "Tier 1", 25, value_change_pct=40.0),  # wrong position
    _make_transition("Player E", "FW", "Tier 3", "Tier 1", 25, value_change_pct=60.0),  # wrong origin
    _make_transition("Player F", "FW", "Tier 2", "Tier 2", 25, value_change_pct=10.0),  # wrong dest
    _make_transition("Player G", "FW", "Tier 2", "Tier 1", 35, value_change_pct=5.0),   # too old (age 35, query 25)
    _make_transition("Player H", "FW", "Tier 2", "Tier 1", None, value_change_pct=25.0),  # null age — included
]


# ─── find_comparable_transitions ─────────────────────────────────────────────

class TestFindComparableTransitions:

    def test_exact_match_returns_correct_players(self) -> None:
        """Players A, B, C, H should match; D/E/F/G should be excluded."""
        result = find_comparable_transitions(
            transitions=TRANSITIONS,
            position="FW",
            origin_tier="Tier 2",
            destination_tier="Tier 1",
            age=25,
            age_window=5,
        )
        names = {r["player_name"] for r in result}
        assert "Player A" in names
        assert "Player B" in names
        assert "Player C" in names
        assert "Player H" in names  # null age — included

    def test_wrong_position_excluded(self) -> None:
        result = find_comparable_transitions(
            transitions=TRANSITIONS,
            position="FW",
            origin_tier="Tier 2",
            destination_tier="Tier 1",
            age=25,
        )
        names = {r["player_name"] for r in result}
        assert "Player D" not in names  # MF, not FW

    def test_wrong_origin_tier_excluded(self) -> None:
        result = find_comparable_transitions(
            transitions=TRANSITIONS,
            position="FW",
            origin_tier="Tier 2",
            destination_tier="Tier 1",
            age=25,
        )
        names = {r["player_name"] for r in result}
        assert "Player E" not in names  # origin is Tier 3

    def test_wrong_destination_tier_excluded(self) -> None:
        result = find_comparable_transitions(
            transitions=TRANSITIONS,
            position="FW",
            origin_tier="Tier 2",
            destination_tier="Tier 1",
            age=25,
        )
        names = {r["player_name"] for r in result}
        assert "Player F" not in names  # destination is Tier 2

    def test_age_outside_window_excluded(self) -> None:
        """Player G is 35; query age is 25 — outside ±5 window."""
        result = find_comparable_transitions(
            transitions=TRANSITIONS,
            position="FW",
            origin_tier="Tier 2",
            destination_tier="Tier 1",
            age=25,
            age_window=5,
        )
        names = {r["player_name"] for r in result}
        assert "Player G" not in names

    def test_null_age_is_included(self) -> None:
        """Player H has age_at_transfer=None — should not be filtered out."""
        result = find_comparable_transitions(
            transitions=TRANSITIONS,
            position="FW",
            origin_tier="Tier 2",
            destination_tier="Tier 1",
            age=25,
        )
        names = {r["player_name"] for r in result}
        assert "Player H" in names

    def test_no_match_returns_empty_list(self) -> None:
        result = find_comparable_transitions(
            transitions=TRANSITIONS,
            position="GK",
            origin_tier="Tier 1",
            destination_tier="Tier 4",
            age=25,
        )
        assert result == []

    def test_narrower_age_window_reduces_results(self) -> None:
        """With age_window=1, only players within ±1 of query age (25) are returned.

        Player A: age 24 → delta=1 → included (boundary is inclusive, abs(24-25)<=1)
        Player B: age 27 → delta=2 → excluded (abs(27-25) > 1)
        Player C: age 22 → delta=3 → excluded
        Player H: null age  → included (unknown age is never filtered)
        """
        result = find_comparable_transitions(
            transitions=TRANSITIONS,
            position="FW",
            origin_tier="Tier 2",
            destination_tier="Tier 1",
            age=25,
            age_window=1,
        )
        names = {r["player_name"] for r in result}
        assert "Player A" in names    # age 24 — delta=1, exactly at boundary → included
        assert "Player B" not in names  # age 27 — delta=2, outside window=1
        assert "Player C" not in names  # age 22 — delta=3, outside window=1
        assert "Player H" in names    # null age — always included


# ─── predict_value_range ──────────────────────────────────────────────────────

class TestPredictValueRange:

    def test_empty_comps_returns_unchanged_value(self) -> None:
        low, high, mean, score = predict_value_range(10_000_000.0, [])
        assert low == 10_000_000.0
        assert high == 10_000_000.0
        assert mean == 0.0
        assert score == 0.0

    def test_single_comp_both_bounds_equal(self) -> None:
        """With only one data point, low and high should be the same projected value."""
        low, high, mean, score = predict_value_range(10_000_000.0, [50.0])
        assert low == pytest.approx(high, rel=1e-6)
        assert mean == pytest.approx(50.0)
        assert score < 0.2  # low confidence for single comp

    def test_positive_mean_change_increases_value(self) -> None:
        changes = [20.0, 30.0, 40.0, 50.0, 60.0]
        low, high, mean, _ = predict_value_range(10_000_000.0, changes)
        assert low > 10_000_000.0
        assert high > low
        assert mean == pytest.approx(40.0)

    def test_negative_mean_change_decreases_value(self) -> None:
        changes = [-40.0, -30.0, -20.0, -10.0, -5.0]
        low, high, mean, _ = predict_value_range(10_000_000.0, changes)
        assert high < 10_000_000.0
        assert mean < 0

    def test_p25_p75_spread_is_applied(self) -> None:
        """
        changes = [0, 10, 20, 30, 40] sorted.
        p25 = 10, p75 = 30 (roughly).
        low  ≈ 10M * 1.10 = 11M
        high ≈ 10M * 1.30 = 13M
        """
        changes = [0.0, 10.0, 20.0, 30.0, 40.0]
        low, high, mean, _ = predict_value_range(10_000_000.0, changes)
        assert low == pytest.approx(11_000_000.0, rel=0.02)
        assert high == pytest.approx(13_000_000.0, rel=0.02)

    def test_low_is_always_lte_high(self) -> None:
        """Even with a distribution that decreases then increases, low ≤ high."""
        changes = [-50.0, -40.0, 100.0, 200.0, 300.0]
        low, high, _, _ = predict_value_range(5_000_000.0, changes)
        assert low <= high

    def test_thin_sample_gives_low_confidence(self) -> None:
        """Fewer than THIN_SAMPLE_THRESHOLD comps → confidence_score below threshold."""
        changes = [20.0, 30.0]  # n=2, below THIN_SAMPLE_THRESHOLD=5
        _, _, _, score = predict_value_range(10_000_000.0, changes)
        assert score < 0.40

    def test_high_sample_gives_high_confidence(self) -> None:
        changes = [i * 5.0 for i in range(15)]  # n=15
        _, _, _, score = predict_value_range(10_000_000.0, changes)
        assert score >= 0.70


# ─── generate_narrative ───────────────────────────────────────────────────────

class TestGenerateNarrative:

    def test_step_up_narrative_mentions_step_up(self) -> None:
        """Tier 2 → Tier 1 is an upgrade; narrative should say so."""
        comps = [_make_similar("Comp A"), _make_similar("Comp B")]
        text = generate_narrative(
            position="FW",
            origin_tier="Tier 2",
            destination_tier="Tier 1",
            mean_change=25.0,
            sample_size=5,
            comps=comps,
        )
        assert "step up" in text.lower() or "top-flight" in text.lower()

    def test_narrative_contains_top_two_comp_names(self) -> None:
        comps = [_make_similar("Marcus Rashford"), _make_similar("Bukayo Saka")]
        text = generate_narrative(
            position="FW",
            origin_tier="Tier 2",
            destination_tier="Tier 1",
            mean_change=20.0,
            sample_size=6,
            comps=comps,
        )
        assert "Marcus Rashford" in text
        assert "Bukayo Saka" in text

    def test_thin_sample_warning_in_narrative(self) -> None:
        """Fewer than THIN_SAMPLE_THRESHOLD → warning appears in narrative."""
        comps = [_make_similar("Only Player")]
        text = generate_narrative(
            position="DF",
            origin_tier="Tier 1",
            destination_tier="Tier 2",
            mean_change=-10.0,
            sample_size=1,
            comps=comps,
        )
        # Should flag the thin sample
        assert any(word in text for word in ["⚠", "only", "indicative"])

    def test_no_comps_returns_no_data_message(self) -> None:
        text = generate_narrative(
            position="GK",
            origin_tier="Tier 1",
            destination_tier="Tier 4",
            mean_change=0.0,
            sample_size=0,
            comps=[],
        )
        assert "no historical data" in text.lower() or "no direct precedent" in text.lower()

    def test_destination_club_appears_in_narrative(self) -> None:
        comps = [_make_similar("Some Player")]
        text = generate_narrative(
            position="MF",
            origin_tier="Tier 2",
            destination_tier="Tier 1",
            mean_change=15.0,
            sample_size=6,
            comps=comps,
            destination_club="Real Madrid",
        )
        assert "Real Madrid" in text

    def test_negative_mean_shows_lost_language(self) -> None:
        comps = [_make_similar("Player X"), _make_similar("Player Y")]
        text = generate_narrative(
            position="FW",
            origin_tier="Tier 1",
            destination_tier="Tier 3",
            mean_change=-25.0,
            sample_size=8,
            comps=comps,
        )
        assert "lost" in text.lower()
