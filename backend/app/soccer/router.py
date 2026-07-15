"""
router.py
---------
FastAPI route definitions for the Soccer Solver API.

Handlers are deliberately thin: they validate inputs, call a service function,
and either return the result or raise an HTTPException.  No business logic lives
here; all logic is delegated to the service layer.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.soccer.repository import (
    PlayerRepository,
    TransitionRepository,
    get_player_repository,
    get_transition_repository,
)
from app.soccer.schemas import (
    PlayerProfileResponse,
    PlayerSearchResponse,
    TransitionPrediction,
)
from app.soccer.services import profile_service, search_service, transition_service
from app.soccer.services.transition_service import VALID_TIERS

router = APIRouter(prefix="/api/players", tags=["players"])


# ─── View 1: Player Search ────────────────────────────────────────────────────


@router.get(
    "/search",
    response_model=PlayerSearchResponse,
    summary="Search players by name",
    description=(
        "Case-insensitive substring match on player name. "
        "Returns enough information to identify each player at a glance."
    ),
)
def search_players(
    q: str = Query(
        ...,
        min_length=1,
        max_length=100,
        description="Player name search string",
    ),
    limit: int = Query(default=20, ge=1, le=100, description="Results per page"),
    offset: int = Query(default=0, ge=0, description="Pagination offset"),
    repo: PlayerRepository = Depends(get_player_repository),
) -> PlayerSearchResponse:
    return search_service.search_players(repo=repo, query=q, limit=limit, offset=offset)


# ─── View 2: Player Profile ───────────────────────────────────────────────────


@router.get(
    "/{player_id}",
    response_model=PlayerProfileResponse,
    summary="Get a player's full profile",
    description=(
        "Returns baseline player data plus performance percentiles relative "
        "to (a) all players at the same position, and (b) same-position players "
        "in the same league."
    ),
    responses={404: {"description": "Player not found"}},
)
def get_player_profile(
    player_id: int,
    repo: PlayerRepository = Depends(get_player_repository),
) -> PlayerProfileResponse:
    profile = profile_service.get_player_profile(player_id=player_id, repo=repo)
    if profile is None:
        raise HTTPException(
            status_code=404,
            detail=f"No player found with id {player_id}.",
        )
    return profile


# ─── View 3: Transition Simulator ────────────────────────────────────────────


@router.get(
    "/{player_id}/transitions/simulate",
    response_model=TransitionPrediction,
    summary="Simulate a player's value post-transition",
    description=(
        "Predicts a post-transition market value range (p25–p75 of comparable "
        "historical moves), surfaces similar real transfers with before/after values, "
        "and generates a plain-language summary. "
        "Confidence level and thin-sample warnings are always visible — "
        "the API never dresses up a small sample as a confident forecast."
    ),
    responses={
        400: {"description": "Invalid destination_tier value"},
        404: {"description": "Player not found"},
    },
)
def simulate_transition(
    player_id: int,
    destination_tier: str = Query(
        ...,
        description="Target league tier. One of: 'Tier 1', 'Tier 2', 'Tier 3', 'Tier 4'.",
    ),
    destination_club: Optional[str] = Query(
        default=None,
        description="Destination club name (optional — used in the narrative).",
    ),
    player_repo: PlayerRepository = Depends(get_player_repository),
    transition_repo: TransitionRepository = Depends(get_transition_repository),
) -> TransitionPrediction:
    if destination_tier not in VALID_TIERS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"'{destination_tier}' is not a valid tier. "
                f"Accepted values: {sorted(VALID_TIERS)}."
            ),
        )

    result = transition_service.simulate_transition(
        player_id=player_id,
        destination_tier=destination_tier,
        destination_club=destination_club,
        player_repo=player_repo,
        transition_repo=transition_repo,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"No player found with id {player_id}.",
        )

    return result
