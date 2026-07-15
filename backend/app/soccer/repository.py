"""
repository.py
-------------
In-memory data stores for player and transition data.

Both repositories are singletons populated once at first access via
``app.utils.data_loader``.  No file I/O ever happens inside a service or
endpoint — callers always go through the repository interface.

Usage (in endpoints via FastAPI Depends):

    from app.soccer.repository import get_player_repository, get_transition_repository

    @router.get("/search")
    def search(repo = Depends(get_player_repository)):
        ...
"""

from __future__ import annotations

from typing import Any, Optional

from app.utils.data_loader import load_json_array


# ─── Player Repository ────────────────────────────────────────────────────────


class PlayerRepository:
    """
    In-memory store for ``current_players.json``.

    Indexes built at construction time:
    - ``_by_id``          — O(1) player lookup by ``player_id``
    - ``_by_position``    — pre-grouped list by position string
    - ``_by_pos_league``  — pre-grouped list by (position, league) tuple
    """

    def __init__(self, players: list[dict[str, Any]]) -> None:
        self._players: list[dict[str, Any]] = players

        self._by_id: dict[int, dict[str, Any]] = {
            p["player_id"]: p for p in players
        }

        self._by_position: dict[str, list[dict[str, Any]]] = {}
        self._by_pos_league: dict[tuple[str, str], list[dict[str, Any]]] = {}

        for p in players:
            pos = p["position"]
            league = p["current_league"]

            self._by_position.setdefault(pos, []).append(p)
            self._by_pos_league.setdefault((pos, league), []).append(p)

    # ── Public interface ──────────────────────────────────────────────────────

    def get_all(self) -> list[dict[str, Any]]:
        """Return all players (read-only — do not mutate)."""
        return self._players

    def get_by_id(self, player_id: int) -> Optional[dict[str, Any]]:
        """O(1) lookup by player_id.  Returns ``None`` if not found."""
        return self._by_id.get(player_id)

    def search_by_name(self, query: str) -> list[dict[str, Any]]:
        """Case-insensitive substring search on ``player_name``."""
        q = query.lower()
        return [p for p in self._players if q in p["player_name"].lower()]

    def get_by_position(self, position: str) -> list[dict[str, Any]]:
        """All players sharing the given position code (e.g. ``'FW'``)."""
        return self._by_position.get(position, [])

    def get_by_position_and_league(
        self, position: str, league: str
    ) -> list[dict[str, Any]]:
        """All players with matching position *and* league code."""
        return self._by_pos_league.get((position, league), [])


# ─── Transition Repository ────────────────────────────────────────────────────


class TransitionRepository:
    """
    In-memory store for ``historical_transitions.json``.
    """

    def __init__(self, transitions: list[dict[str, Any]]) -> None:
        self._transitions: list[dict[str, Any]] = transitions

    def get_all(self) -> list[dict[str, Any]]:
        """Return all transition records (read-only)."""
        return self._transitions


# ─── Singleton factories ──────────────────────────────────────────────────────

_player_repo: Optional[PlayerRepository] = None
_transition_repo: Optional[TransitionRepository] = None


def get_player_repository() -> PlayerRepository:
    """
    Return (or lazily initialise) the singleton PlayerRepository.

    FastAPI ``Depends`` calls this on every request; the actual JSON load
    happens only once at first call.  Subsequent calls return the cached
    instance in O(1).
    """
    global _player_repo
    if _player_repo is None:
        players = load_json_array("current_players.json")
        _player_repo = PlayerRepository(players)
    return _player_repo


def get_transition_repository() -> TransitionRepository:
    """
    Return (or lazily initialise) the singleton TransitionRepository.
    """
    global _transition_repo
    if _transition_repo is None:
        transitions = load_json_array("historical_transitions.json")
        _transition_repo = TransitionRepository(transitions)
    return _transition_repo


def reset_repositories() -> None:
    """
    Reset both singletons to ``None``.
    Intended for use in tests only — allows injecting mock data without
    touching the real JSON files.
    """
    global _player_repo, _transition_repo
    _player_repo = None
    _transition_repo = None
