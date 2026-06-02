"""Dataclasses for game state and entities."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass
class Person:
    name: str
    role: str
    skill: int
    personality: str
    morale: int = 60
    salary: int = 0


@dataclass
class TeamState:
    team_name: str
    manufacturer: str
    principal: Person
    drivers: List[Person]
    staff: List[Person]
    budget: int
    sponsor_value: int
    sponsor_name: str
    development: Dict[str, int] = field(default_factory=lambda: {"aero": 55, "power_unit": 55, "chassis": 55})
    chemistry: int = 55
    owner_confidence: int = 70


@dataclass
class SeasonState:
    year: int = 1
    race_index: int = 1
    races_per_season: int = 10
    points: int = 0
    standing: int = 10


@dataclass
class GameState:
    team: TeamState
    season: SeasonState
    history: List[str] = field(default_factory=list)
    ai_context: Dict[str, Any] = field(default_factory=dict)
    game_over: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "GameState":
        team = payload["team"]
        return cls(
            team=TeamState(
                team_name=team["team_name"],
                manufacturer=team["manufacturer"],
                principal=Person(**team["principal"]),
                drivers=[Person(**driver) for driver in team["drivers"]],
                staff=[Person(**staff_member) for staff_member in team["staff"]],
                budget=team["budget"],
                sponsor_value=team["sponsor_value"],
                sponsor_name=team["sponsor_name"],
                development=team.get("development", {"aero": 55, "power_unit": 55, "chassis": 55}),
                chemistry=team.get("chemistry", 55),
                owner_confidence=team.get("owner_confidence", 70),
            ),
            season=SeasonState(**payload["season"]),
            history=payload.get("history", []),
            ai_context=payload.get("ai_context", {}),
            game_over=payload.get("game_over", False),
        )
