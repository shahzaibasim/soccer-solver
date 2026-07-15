"""
search_service.py
-----------------
Player name search logic.

Responsibility: accept a raw text query and a PlayerRepository, return a
paginated PlayerSearchResponse.  No file I/O, no HTTP concerns.
"""

from __future__ import annotations

from app.soccer.repository import PlayerRepository
from app.soccer.schemas import PlayerSearchResponse, PlayerSearchResult


def search_players(
    repo: PlayerRepository,
    query: str,
    limit: int = 20,
    offset: int = 0,
) -> PlayerSearchResponse:
    """
    Search for players whose name contains *query* (case-insensitive).

    Args:
        repo:   The PlayerRepository singleton injected by the router.
        query:  Free-text search string.
        limit:  Maximum number of results to return.
        offset: Number of results to skip (for pagination).

    Returns:
        A PlayerSearchResponse with paginated results and total match count.
    """
    stripped = query.strip()
    if not stripped:
        return PlayerSearchResponse(results=[], total=0, limit=limit, offset=offset)

    matches = repo.search_by_name(stripped)
    total = len(matches)
    page = matches[offset : offset + limit]

    results: list[PlayerSearchResult] = [
        PlayerSearchResult(
            player_id=p["player_id"],
            player_name=p["player_name"],
            position=p["position"],
            current_club=p["current_club"],
            current_league=p["current_league"],
            current_league_tier=p["current_league_tier"],
            current_market_value_eur=p["current_market_value_eur"],
            image_url=p.get("image_url"),
        )
        for p in page
    ]

    return PlayerSearchResponse(
        results=results,
        total=total,
        limit=limit,
        offset=offset,
    )
