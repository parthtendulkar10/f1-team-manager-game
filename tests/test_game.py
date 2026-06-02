import tempfile
import unittest
from pathlib import Path

from f1_manager.ai_service import AIService
from f1_manager.engine import GameEngine
from f1_manager.persistence import load_state, save_state


class F1ManagerTests(unittest.TestCase):
    def test_ai_fallback_and_cache(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            cache_file = str(Path(tmp_dir) / "cache.json")
            ai = AIService(cache_path=cache_file, provider="fallback")
            prompt = "Generate dynamic driver dispute"
            first = ai.generate(prompt)
            second = ai.generate(prompt)
            self.assertTrue(first)
            self.assertEqual(first, second)

    def test_new_game_and_round_progression(self):
        ai = AIService(provider="fallback", cache_path="/tmp/f1_manager_test_cache.json")
        engine = GameEngine(ai_service=ai, seed=7)
        state = engine.start_new_game("Nova GP", 0, 0)

        result = engine.play_round(state, "1")
        self.assertEqual(result["status"], "ok")
        self.assertIn("finish", result)
        self.assertGreaterEqual(state.season.race_index, 1)
        self.assertFalse(state.game_over)

    def test_save_and_load_preserves_core_state(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            save_path = str(Path(tmp_dir) / "savegame.json")
            ai = AIService(provider="fallback", cache_path=str(Path(tmp_dir) / "cache.json"))
            engine = GameEngine(ai_service=ai, seed=5)
            state = engine.start_new_game("Atlas Racing", 1, 2)
            engine.play_round(state, "3")

            save_state(save_path, state)
            loaded = load_state(save_path)

            self.assertEqual(loaded.team.team_name, state.team.team_name)
            self.assertEqual(loaded.team.manufacturer, state.team.manufacturer)
            self.assertEqual(loaded.season.year, state.season.year)
            self.assertEqual(len(loaded.team.drivers), 2)


if __name__ == "__main__":
    unittest.main()
