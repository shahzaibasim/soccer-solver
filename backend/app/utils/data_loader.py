"""
data_loader.py
--------------
Low-level utility for reading JSON data files from the scripts directory.

This module is the ONLY place in the codebase that performs raw file I/O
for the flat-file data sources.  All higher-level abstractions (repositories,
services, routers) must go through this layer — never open data files directly.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


# Resolve once at import time: <repo>/backend/scripts/
_SCRIPTS_DIR: Path = Path(__file__).parent.parent.parent / "scripts"


def load_json_array(filename: str) -> list[dict[str, Any]]:
    """
    Load a JSON array from the scripts data directory.

    Args:
        filename: Bare filename of the JSON file, e.g. ``"current_players.json"``.
                  The ``scripts/`` prefix is added automatically.

    Returns:
        A list of record dicts as parsed from the file.

    Raises:
        FileNotFoundError: If the file does not exist at the expected path.
        ValueError: If the parsed JSON is not a list (unexpected format).
        json.JSONDecodeError: If the file contents are not valid JSON.
    """
    path = _SCRIPTS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Data file '{filename}' not found. "
            f"Expected path: {path}"
        )

    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh, parse_constant=lambda x: 0.0 if x == "NaN" else float(x))

    if not isinstance(data, list):
        raise ValueError(
            f"Expected a JSON array in '{filename}', "
            f"but got {type(data).__name__}."
        )

    return data


def get_scripts_dir() -> Path:
    """Return the resolved path to the scripts data directory (useful for tests)."""
    return _SCRIPTS_DIR
