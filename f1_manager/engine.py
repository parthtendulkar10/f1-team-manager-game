"""Core game engine for the F1 team manager simulation."""

from __future__ import annotations

import random
from dataclasses import asdict
from typing import Dict, List, Tuple

from .ai_service import AIService
from .data import DRIVER_POOL_STARTER, DRIVER_POOL_UNLOCKED, MANUFACTURERS, SPONSOR_TYPES, STAFF_TEMPLATES, TEAM_PRINCIPALS
from .models import GameState, Person, SeasonState, TeamState
from .prompts import (
    consequence_prompt,
    event_prompt,
    negotiation_prompt,
    personality_prompt,
    race_commentary_prompt,
    sponsorship_prompt,
)


class GameEngine:
    DECISIONS: Dict[str, Dict[str, int]] = {
        "1": {"aero": 4, "budget": -8_000_000, "chemistry": -1, "confidence": 1},
        "2": {"power_unit": 4, "budget": -9_500_000, "chemistry": -1, "confidence": 1},
        "3": {"chassis": 4, "budget": -7_000_000, "chemistry": 1, "confidence": 0},
        "4": {"budget": -4_000_000, "marketing": 3, "chemistry": 1, "confidence": 1},
        "5": {"budget": -3_000_000, "chemistry": 4, "confidence": 1},
    }

    def __init__(self, ai_service: AIService | None = None, seed: int | None = None):
        self.ai = ai_service or AIService()
        self.rng = random.Random(seed)

    def list_manufacturers(self) -> List[dict]:
        return MANUFACTURERS

    def list_principals(self) -> List[dict]:
        return TEAM_PRINCIPALS

    def start_new_game(self, team_name: str, manufacturer_index: int, principal_index: int) -> GameState:
        manufacturer = MANUFACTURERS[manufacturer_index]
        principal_template = TEAM_PRINCIPALS[principal_index]

        principal = Person(
            name=principal_template["name"],
            role=f"Team Principal ({principal_template['background']})",
            skill=int(sum(principal_template["stats"].values()) / 4),
            personality=self.ai.generate(
                personality_prompt(principal_template["name"], "team principal", f"stats: {principal_template['stats']}")
            ),
            morale=65,
            salary=5_000_000,
        )

        selected_drivers = self.rng.sample(DRIVER_POOL_STARTER, k=2)
        drivers = [
            Person(
                name=driver["name"],
                role=f"Driver ({driver['tier']})",
                skill=driver["skill"],
                personality=self.ai.generate(personality_prompt(driver["name"], "driver", f"tier: {driver['tier']}")),
                morale=60,
                salary=driver["market_value"],
            )
            for driver in selected_drivers
        ]

        staff = [
            Person(
                name=member["name"],
                role=member["name"],
                skill=member["skill"],
                personality=self.ai.generate(personality_prompt(member["name"], member["name"], "new expansion team")),
                morale=58,
                salary=2_000_000,
            )
            for member in STAFF_TEMPLATES
        ]

        sponsor_name = self.rng.choice(SPONSOR_TYPES)
        sponsor_value = 18_000_000 + self.rng.randint(-2_000_000, 2_000_000)

        state = GameState(
            team=TeamState(
                team_name=team_name,
                manufacturer=manufacturer["name"],
                principal=principal,
                drivers=drivers,
                staff=staff,
                budget=manufacturer["backing"],
                sponsor_value=sponsor_value,
                sponsor_name=sponsor_name,
            ),
            season=SeasonState(),
            history=[f"Team founded by {manufacturer['name']} with {principal.name} as principal."],
            ai_context={
                "manufacturer": manufacturer,
                "principal_template": principal_template,
                "sponsorship_intro": self.ai.generate(
                    sponsorship_prompt(f"manufacturer={manufacturer['name']}, budget={manufacturer['backing']}")
                ),
            },
        )
        return state

    def decision_menu(self) -> List[Tuple[str, str]]:
        return [
            ("1", "Aggressive Aero R&D (high cost, better pace)"),
            ("2", "Power Unit Upgrade (expensive, stronger race pace)"),
            ("3", "Chassis Reliability Program (stability focus)"),
            ("4", "Marketing & Sponsor Activation"),
            ("5", "Driver/Staff Harmony Initiative"),
            ("6", "Save and Exit"),
        ]

    def play_round(self, state: GameState, decision: str) -> Dict[str, str]:
        if decision == "6":
            return {"status": "save"}

        choice_impact = self.DECISIONS.get(decision)
        if not choice_impact:
            return {"status": "invalid", "message": "Invalid decision."}

        team = state.team
        season = state.season

        team.budget += choice_impact.get("budget", 0)
        team.development["aero"] += choice_impact.get("aero", 0)
        team.development["power_unit"] += choice_impact.get("power_unit", 0)
        team.development["chassis"] += choice_impact.get("chassis", 0)
        team.chemistry = max(20, min(95, team.chemistry + choice_impact.get("chemistry", 0)))
        team.owner_confidence = max(0, min(100, team.owner_confidence + choice_impact.get("confidence", 0)))

        base_pace = (team.development["aero"] + team.development["power_unit"] + team.development["chassis"]) / 3
        driver_strength = sum(driver.skill + driver.morale * 0.2 for driver in team.drivers) / len(team.drivers)
        staff_strength = sum(staff.skill for staff in team.staff) / len(team.staff)
        luck = self.rng.randint(-8, 8)
        pressure_penalty = 6 if team.budget < 15_000_000 else 0
        performance_index = base_pace * 0.45 + driver_strength * 0.35 + staff_strength * 0.20 + luck - pressure_penalty

        finish_position = max(1, min(20, int(round(21 - performance_index / 6))))
        points_gain = self._points_for_position(finish_position)
        income = self._calculate_income(points_gain, finish_position, team)
        team.budget += income
        season.points += points_gain

        event_context = self._state_summary(state)
        event_text = self.ai.generate(event_prompt(event_context))
        consequence_text = self.ai.generate(consequence_prompt(f"Option {decision}", event_context))
        commentary = self.ai.generate(race_commentary_prompt(event_context, finish_position))

        for driver in team.drivers:
            morale_shift = 2 if finish_position <= 10 else -2
            driver.morale = max(30, min(95, driver.morale + morale_shift + self.rng.randint(-1, 1)))

        if season.race_index == season.races_per_season:
            self._close_season(state)
        else:
            season.race_index += 1

        self._apply_owner_pressure(state)

        history_line = (
            f"Y{season.year} R{season.race_index}: Decision {decision}, finished P{finish_position}, "
            f"+{points_gain} pts, budget now {team.budget:,}."
        )
        state.history.append(history_line)

        return {
            "status": "ok",
            "event": event_text,
            "consequence": consequence_text,
            "commentary": commentary,
            "finish": f"P{finish_position}",
            "points": str(points_gain),
            "budget": f"{team.budget:,}",
            "standing": str(season.standing),
            "game_over": str(state.game_over),
        }

    def _calculate_income(self, points_gain: int, finish_position: int, team: TeamState) -> int:
        placement_prize = max(0, (12 - finish_position)) * 350_000
        sponsor_bonus = int(team.sponsor_value * (0.08 if finish_position <= 10 else 0.03))
        tv_money = points_gain * 180_000
        return placement_prize + sponsor_bonus + tv_money

    def _close_season(self, state: GameState) -> None:
        season = state.season
        team = state.team
        season.standing = max(1, 10 - season.points // 35)

        bonus = max(0, (11 - season.standing)) * 4_000_000
        team.budget += bonus
        team.owner_confidence = max(0, min(100, team.owner_confidence + (8 - season.standing)))

        self._attempt_driver_market_upgrade(state)

        season.year += 1
        season.race_index = 1
        season.points = 0

    def _attempt_driver_market_upgrade(self, state: GameState) -> None:
        team = state.team
        if team.owner_confidence < 68:
            return

        candidate = self.rng.choice(DRIVER_POOL_UNLOCKED)
        summary = self._state_summary(state)
        negotiation = self.ai.generate(negotiation_prompt(candidate["name"], candidate["tier"], summary))
        state.ai_context["latest_negotiation"] = negotiation

        if team.budget > candidate["market_value"] + 12_000_000:
            weakest_driver = min(team.drivers, key=lambda d: d.skill)
            team.drivers.remove(weakest_driver)
            team.drivers.append(
                Person(
                    name=candidate["name"],
                    role=f"Driver ({candidate['tier']})",
                    skill=candidate["skill"],
                    personality=self.ai.generate(personality_prompt(candidate["name"], "driver", "new signing")),
                    morale=64,
                    salary=candidate["market_value"],
                )
            )
            team.budget -= candidate["market_value"]
            state.history.append(f"Signed {candidate['name']} after negotiations: {negotiation}")
        else:
            state.history.append(f"Failed to sign {candidate['name']} due to budget pressure: {negotiation}")

    def _apply_owner_pressure(self, state: GameState) -> None:
        team = state.team
        if team.budget < 0:
            state.game_over = True
            state.history.append("Game over: bankruptcy.")
            return

        if team.owner_confidence < 25:
            state.game_over = True
            state.history.append("Game over: ownership lost confidence in project leadership.")

    def _state_summary(self, state: GameState) -> str:
        team = state.team
        season = state.season
        return (
            f"team={team.team_name}, manufacturer={team.manufacturer}, year={season.year}, race={season.race_index}, "
            f"budget={team.budget}, chemistry={team.chemistry}, owner_confidence={team.owner_confidence}, "
            f"development={team.development}, points={season.points}"
        )

    @staticmethod
    def _points_for_position(position: int) -> int:
        table = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}
        return table.get(position, 0)

    @staticmethod
    def state_snapshot(state: GameState) -> Dict[str, object]:
        return {
            "team": asdict(state.team),
            "season": asdict(state.season),
            "game_over": state.game_over,
        }
