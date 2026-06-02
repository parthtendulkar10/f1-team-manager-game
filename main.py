"""CLI entry point for the F1 Team Manager game."""

from __future__ import annotations

import os

from f1_manager.engine import GameEngine
from f1_manager.persistence import load_state, save_state

SAVE_FILE = "savegame.json"


def choose_option(prompt: str, options_count: int) -> int:
    while True:
        choice = input(prompt).strip()
        if choice.isdigit() and 1 <= int(choice) <= options_count:
            return int(choice) - 1
        print(f"Enter a number between 1 and {options_count}.")


def print_status(engine: GameEngine, state) -> None:
    snapshot = engine.state_snapshot(state)
    team = snapshot["team"]
    season = snapshot["season"]
    print("\n--- Team Status ---")
    print(f"Team: {team['team_name']} ({team['manufacturer']})")
    print(f"Season {season['year']} Race {season['race_index']}/{season['races_per_season']}")
    print(f"Budget: {team['budget']:,} | Chemistry: {team['chemistry']} | Owner confidence: {team['owner_confidence']}")
    print(f"Development: Aero {team['development']['aero']} / PU {team['development']['power_unit']} / Chassis {team['development']['chassis']}")
    print(f"Drivers: {', '.join(driver['name'] for driver in team['drivers'])}")


def setup_new_game(engine: GameEngine):
    team_name = input("Enter your team name: ").strip() or "Phoenix GP"

    manufacturers = engine.list_manufacturers()
    print("\nChoose manufacturer backing:")
    for idx, manufacturer in enumerate(manufacturers, start=1):
        print(f"{idx}. {manufacturer['name']} (budget {manufacturer['backing']:,})")
    manufacturer_index = choose_option("Manufacturer: ", len(manufacturers))

    principals = engine.list_principals()
    print("\nChoose Team Principal:")
    for idx, principal in enumerate(principals, start=1):
        print(f"{idx}. {principal['name']} - {principal['background']} | stats {principal['stats']}")
    principal_index = choose_option("Principal: ", len(principals))

    state = engine.start_new_game(team_name, manufacturer_index, principal_index)
    print("\nYour team is live.")
    print(state.ai_context.get("sponsorship_intro", ""))
    return state


def run_game_loop(engine: GameEngine, state) -> None:
    print("\nType option numbers to make decisions. Every race weekend has consequences.")
    while not state.game_over:
        print_status(engine, state)

        print("\nChoose your next action:")
        for key, label in engine.decision_menu():
            print(f"{key}. {label}")

        decision = input("Decision: ").strip()
        result = engine.play_round(state, decision)

        if result["status"] == "save":
            save_state(SAVE_FILE, state)
            print(f"Game saved to {SAVE_FILE}. Exiting.")
            return
        if result["status"] == "invalid":
            print(result["message"])
            continue

        print(f"\nResult: {result['finish']} | Points gained: {result['points']} | Budget: {result['budget']}")
        print("Dynamic Event:")
        print(result["event"])
        print("Consequence Analysis:")
        print(result["consequence"])
        print("Race Commentary:")
        print(result["commentary"])

        latest_negotiation = state.ai_context.get("latest_negotiation")
        if latest_negotiation:
            print("\nDriver Market Update:")
            print(latest_negotiation)
            state.ai_context.pop("latest_negotiation", None)

    print("\nGAME OVER")
    print(state.history[-1] if state.history else "Project collapsed.")


def main() -> None:
    engine = GameEngine()

    print("=== F1 Team Manager: AI Dynamics Edition ===")
    print("LLM provider:", engine.ai.provider)
    print("Set OPENAI_API_KEY or ANTHROPIC_API_KEY for live AI. Fallback generator works offline.")

    if os.path.exists(SAVE_FILE):
        choice = input("Load existing savegame? (y/n): ").strip().lower()
        if choice == "y":
            state = load_state(SAVE_FILE)
            run_game_loop(engine, state)
            return

    state = setup_new_game(engine)
    run_game_loop(engine, state)


if __name__ == "__main__":
    main()
