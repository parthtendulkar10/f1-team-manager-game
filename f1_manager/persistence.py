"""Game save/load utilities."""

from __future__ import annotations

import json
from pathlib import Path

from .models import GameState


def save_state(file_path: str, state: GameState) -> None:
    Path(file_path).write_text(json.dumps(state.to_dict(), indent=2), encoding="utf-8")


def load_state(file_path: str) -> GameState:
    payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
    return GameState.from_dict(payload)
