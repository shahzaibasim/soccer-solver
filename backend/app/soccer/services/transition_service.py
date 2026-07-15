"""
transition_service.py
---------------------
Core engine for the Transition Simulator.

Three clearly separated responsibilities:

1. ``find_comparable_transitions`` — comparable-player matching from historical data.
2. ``predict_value_range``         — value-delta modelling using p25–p75 spread.
3. ``generate_narrative``          — plain-language summary a club owner would say aloud.
4. ``simulate_transition``         — orchestrator that wires the three together.

No file I/O, no HTTP concerns.  All data access via injected repositories.
"""

from __future__ import annotations

import statistics
from typing import Any, Optional

from app.soccer.repository import PlayerRepository, TransitionRepository
from app.soccer.schemas import SimilarTransition, TransitionPrediction


# ─── Constants ────────────────────────────────────────────────────────────────

VALID_TIERS: frozenset[str] = frozenset({"Tier 1", "Tier 2", "Tier 3", "Tier 4"})

# Confidence thresholds
_HIGH_N: int = 10
_MEDIUM_N: int = 5

# A thin sample is fewer than this many comparable transfers
THIN_SAMPLE_THRESHOLD: int = _MEDIUM_N

_POSITION_LABELS: dict[str, str] = {
    "FW": "forwards",
    "MF": "midfielders",
    "DF": "defenders",
    "GK": "goalkeepers",
}

_TIER_LABELS: dict[str, str] = {
    "Tier 1": "top-flight",
    "Tier 2": "second-tier",
    "Tier 3": "third-tier",
    "Tier 4": "fourth-tier",
}


# ─── 1. Comparable-transition matching ───────────────────────────────────────


def find_comparable_transitions(
    transitions: list[dict[str, Any]],
    position: str,
    origin_tier: str,
    destination_tier: str,
    age: int,
    age_window: int = 5,
) -> list[dict[str, Any]]:
    """
    Filter *transitions* to those that are genuinely comparable.

    Matching criteria (all must hold):
    - Same playing position (FW / MF / DF / GK)
    - Same origin league tier → same destination league tier
    - Age at transfer within ±*age_window* years of the query player

    Players whose ``age_at_transfer`` is ``None`` in the data are included
    because we cannot rule them out — absence of data is not a disqualifier.

    Args:
        transitions:      All records from the TransitionRepository.
        position:         The query player's position code.
        origin_tier:      The query player's current league tier.
        destination_tier: The target league tier chosen by the user.
        age:              The query player's current age.
        age_window:       Inclusive ± tolerance on age (default 5 years).

    Returns:
        Filtered list of matching transition records, ordered as they appear
        in the source file (most recent first if the data is pre-sorted).
    """
    comps: list[dict[str, Any]] = []

    for t in transitions:
        # Position must match
        if t.get("position") != position:
            continue

        # Tier route must match (origin → destination)
        if t.get("origin", {}).get("league_tier") != origin_tier:
            continue
        if t.get("destination", {}).get("league_tier") != destination_tier:
            continue

        # Age filter — include if age is unknown, exclude if clearly outside window
        t_age: Optional[int] = t.get("age_at_transfer")
        if t_age is not None and abs(t_age - age) > age_window:
            continue

        comps.append(t)

    return comps


# ─── 2. Value-range modelling ─────────────────────────────────────────────────


def _interpolated_percentile(sorted_data: list[float], p: float) -> float:
    """
    Linear interpolation for the *p*-th percentile of *sorted_data*.

    Args:
        sorted_data: Ascending list of floats.
        p:           Percentile in [0, 100].
    """
    n = len(sorted_data)
    if n == 1:
        return sorted_data[0]

    idx = (n - 1) * p / 100.0
    lo = int(idx)
    hi = lo + 1
    if hi >= n:
        return sorted_data[lo]

    frac = idx - lo
    return sorted_data[lo] + (sorted_data[hi] - sorted_data[lo]) * frac


def predict_value_range(
    current_value: float,
    comparable_changes: list[float],
) -> tuple[float, float, float, float]:
    """
    Model post-transition value using the p25–p75 interquartile range of
    observed value-change percentages.

    The IQR is used deliberately (not min/max) because it is robust to the
    extreme outliers that are common in transfer valuations.

    Args:
        current_value:      Player's current market value in EUR.
        comparable_changes: List of ``value_change_percentage`` floats
                            from matching historical transitions.

    Returns:
        Tuple of (low_eur, high_eur, mean_change_pct, confidence_score).

        - ``low_eur``  / ``high_eur``   — predicted band (p25/p75 applied to current value)
        - ``mean_change_pct``           — arithmetic mean of comparable changes
        - ``confidence_score``          — float in [0.0, 1.0]
    """
    n = len(comparable_changes)

    if n == 0:
        return current_value, current_value, 0.0, 0.0

    sorted_changes = sorted(comparable_changes)
    mean_change = statistics.mean(comparable_changes)

    if n == 1:
        projected = current_value * (1.0 + mean_change / 100.0)
        return projected, projected, mean_change, 0.1

    p25 = _interpolated_percentile(sorted_changes, 25.0)
    p75 = _interpolated_percentile(sorted_changes, 75.0)

    low = current_value * (1.0 + p25 / 100.0)
    high = current_value * (1.0 + p75 / 100.0)

    # Ensure low ≤ high regardless of sign conventions in the data
    if low > high:
        low, high = high, low

    # Confidence score: climbs toward 0.90 as n grows beyond the High threshold
    if n >= _HIGH_N:
        confidence_score = min(0.90, 0.70 + (n - _HIGH_N) * 0.01)
    elif n >= _MEDIUM_N:
        confidence_score = 0.40 + (n - _MEDIUM_N) * 0.06  # 0.40 → 0.64
    else:
        confidence_score = max(0.10, n * 0.08)  # 0.08 → 0.32

    return low, high, mean_change, confidence_score


def _confidence_label(sample_size: int) -> str:
    """Map sample size to a human-readable confidence tier."""
    if sample_size >= _HIGH_N:
        return "High"
    if sample_size >= _MEDIUM_N:
        return "Medium"
    return "Low"


# ─── 3. Narrative generation ──────────────────────────────────────────────────


def generate_narrative(
    position: str,
    origin_tier: str,
    destination_tier: str,
    mean_change: float,
    sample_size: int,
    comps: list[SimilarTransition],
    destination_club: Optional[str] = None,
) -> str:
    """
    Generate a plain-language transition summary that a club owner could
    read in 30 seconds and find convincing enough to reference in negotiations.

    The narrative:
    - States the direction and type of move in plain words
    - Anchors to the historical average value movement
    - Names the top 2 comparable players for credibility
    - Explicitly flags thin-sample uncertainty rather than hiding it

    Args:
        position:         Player's position code.
        origin_tier:      Current league tier.
        destination_tier: Target league tier.
        mean_change:      Mean value-change percentage across comps.
        sample_size:      Total number of comparable transfers found.
        comps:            SimilarTransition objects (top N already trimmed).
        destination_club: Optional specific destination club name.

    Returns:
        A single-paragraph string ready to display verbatim.
    """
    pos_label = _POSITION_LABELS.get(position, f"{position.lower()}s")
    origin_label = _TIER_LABELS.get(origin_tier, origin_tier.lower())
    dest_label = _TIER_LABELS.get(destination_tier, destination_tier.lower())

    # Determine move direction
    try:
        origin_num = int(origin_tier.split()[-1])
        dest_num = int(destination_tier.split()[-1])
    except (ValueError, IndexError):
        origin_num = dest_num = 0

    if dest_num < origin_num:
        move_phrase = f"making the step up from {origin_label} into {dest_label} football"
    elif dest_num > origin_num:
        move_phrase = f"dropping from {origin_label} into {dest_label} football"
    else:
        move_phrase = f"moving laterally within {origin_label} football"

    dest_suffix = f" to {destination_club}" if destination_club else ""

    # Value direction phrasing
    abs_change = abs(round(mean_change, 1))
    if sample_size == 0:
        return (
            f"No historical data found for {pos_label} {move_phrase}{dest_suffix}. "
            "This profile has no direct precedent in our dataset — "
            "any valuation figure here would be speculation, not analysis."
        )

    if mean_change >= 0:
        value_direction = f"gained an average of {abs_change}% in market value"
    else:
        value_direction = f"lost an average of {abs_change}% in market value"

    # Build comp player name mention
    comp_names = [c.player_name for c in comps[:2]]
    if len(comp_names) == 2:
        comp_mention = (
            f" {comp_names[0]} and {comp_names[1]} are the closest precedents"
        )
    elif len(comp_names) == 1:
        comp_mention = f" {comp_names[0]} is the closest precedent"
    else:
        comp_mention = ""

    # Transfer volume phrasing
    transfer_word = "transfer" if sample_size == 1 else "transfers"
    volume_phrase = (
        f", drawn from {sample_size} comparable {transfer_word} in our dataset."
    )

    # Thin-sample caveat
    if sample_size < THIN_SAMPLE_THRESHOLD:
        caveat = (
            f" ⚠ Only {sample_size} comparable {transfer_word} exist for this "
            "exact profile — the predicted range is indicative. "
            "Treat it as a directional signal, not a precise forecast."
        )
    else:
        caveat = ""

    return (
        f"{pos_label.capitalize()} {move_phrase}{dest_suffix} have historically "
        f"{value_direction} within 6–12 months of the move."
        f"{comp_mention}{volume_phrase}"
        f"{caveat}"
    )


# ─── 4. Orchestrator ─────────────────────────────────────────────────────────


def simulate_transition(
    player_id: int,
    destination_tier: str,
    destination_club: Optional[str],
    player_repo: PlayerRepository,
    transition_repo: TransitionRepository,
) -> Optional[TransitionPrediction]:
    """
    Run a full transition simulation for a player to a destination tier.

    Orchestrates: repository lookup → comparable matching → value modelling
    → narrative generation → response assembly.

    Args:
        player_id:        The query player's ID.
        destination_tier: Target league tier (must be in VALID_TIERS).
        destination_club: Optional destination club name for display purposes.
        player_repo:      Injected PlayerRepository.
        transition_repo:  Injected TransitionRepository.

    Returns:
        A complete TransitionPrediction, or ``None`` if the player is not found.
    """
    player = player_repo.get_by_id(player_id)
    if player is None:
        return None

    origin_tier: str = player["current_league_tier"]
    current_value: float = player["current_market_value_eur"]

    # Step 1: find comparables
    raw_comps = find_comparable_transitions(
        transitions=transition_repo.get_all(),
        position=player["position"],
        origin_tier=origin_tier,
        destination_tier=destination_tier,
        age=player["age"],
    )

    # Step 2: model value range
    changes: list[float] = [
        c["financials"]["value_change_percentage"] for c in raw_comps
    ]
    low, high, mean_change, confidence_score = predict_value_range(
        current_value, changes
    )

    # Step 3: build SimilarTransition objects — cap at 10 for the response
    similar: list[SimilarTransition] = [
        SimilarTransition(
            player_name=c["player_name"],
            position=c["position"],
            origin_tier=c["origin"]["league_tier"],
            destination_tier=c["destination"]["league_tier"],
            age_at_transfer=c.get("age_at_transfer"),
            value_before_eur=c["financials"]["market_value_before_eur"],
            value_after_eur=c["financials"]["market_value_after_eur"],
            value_change_pct=c["financials"]["value_change_percentage"],
            transfer_date=c["transfer_date"],
        )
        for c in raw_comps[:10]
    ]

    # Step 4: generate narrative
    narrative = generate_narrative(
        position=player["position"],
        origin_tier=origin_tier,
        destination_tier=destination_tier,
        mean_change=mean_change,
        sample_size=len(raw_comps),
        comps=similar,
        destination_club=destination_club,
    )

    return TransitionPrediction(
        player_id=player_id,
        player_name=player["player_name"],
        current_value_eur=current_value,
        destination_tier=destination_tier,
        destination_club=destination_club,
        value_range_low_eur=round(low, 2),
        value_range_high_eur=round(high, 2),
        predicted_change_pct_mean=round(mean_change, 2),
        confidence_level=_confidence_label(len(raw_comps)),
        confidence_score=round(confidence_score, 3),
        sample_size=len(raw_comps),
        thin_sample_warning=len(raw_comps) < THIN_SAMPLE_THRESHOLD,
        comparable_transitions=similar,
        narrative=narrative,
    )
