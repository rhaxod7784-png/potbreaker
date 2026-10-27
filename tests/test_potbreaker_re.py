import json
import re
import unittest
from pathlib import Path

from web.game import CROW_DROP_SECONDS, CROW_RESPAWN_SECONDS, PotBreaker


class PotBreakerBalanceTests(unittest.TestCase):
    def test_deterministic_engine_ticks_preserve_core_bounds(self):
        game = PotBreaker(42)
        for i in range(2500):
            state = json.loads(game.step(.04, 1 if i % 6 < 3 else -1, 0, False, i % 17 == 0))
            self.assertEqual(len(state["pots"]), 6)
            self.assertTrue(0 <= state["boss_ammo"] <= 5)
            self.assertTrue(0 <= state["player_hp"] <= 3 and 0 <= state["boss_hp"] <= 5)
            if state["phase"] != "playing":
                game.reset()

    def test_boss_dash_stops_at_partition(self):
        game = PotBreaker(1)
        game.boss = [9, 5]
        game.moving_walls = {(10, 5)}
        game.boss_dash_cd = 0

        self.assertFalse(game._dash(game.boss, 1, 0, True))
        self.assertEqual(game.boss, [9, 5])

    def test_boss_projectile_collides_with_partition(self):
        game = PotBreaker(1)
        game.player = [15, 5]
        game.boss = [9, 5]
        game.walls = {(10, 5)}
        game._fire(game.boss, [1, 0], npc=True)

        game._advance_projectiles(.085)

        self.assertEqual(game.projectiles, [])

    def test_boss_pots_are_slower_and_crow_events_are_rebalanced(self):
        game = PotBreaker(1)
        game.boss = [4, 5]
        game.player = [15, 5]
        game._fire(game.boss, [1, 0], npc=True)
        game._advance_projectiles(.05)

        self.assertAlmostEqual(game.projectiles[0]["x"] - 4, .32, places=2)
        self.assertGreater(CROW_RESPAWN_SECONDS, 9.0)
        self.assertLess(CROW_DROP_SECONDS, 1.05)

        game = PotBreaker(2)
        game.crow_spawn_timer = 0
        created = 0
        for _ in range(95):
            before = game.crow_flight["drop"] if game.crow_flight else None
            game._update_crow(.05)
            after = game.crow_flight["drop"] if game.crow_flight else None
            if before is not None and after is not None and after > before:
                created += 1
        self.assertGreaterEqual(created, 6)

    def test_opening_comic_has_four_equal_sized_panels(self):
        html = Path(__file__).parents[1].joinpath("web", "index.html").read_text(encoding="utf-8")
        match = re.search(r"const boxes=(\[[^;]+)", html)
        self.assertIsNotNone(match)
        boxes = [[int(value) for value in panel.split(",")] for panel in re.findall(r"\[([^\[\]]+)\]", match.group(1))]
        self.assertEqual(len(boxes), 4)
        self.assertEqual({(width, height) for _, _, width, height in boxes}, {(672, 409)})
        self.assertIn("POT BREAKER RE v1.0.9", html)
        self.assertIn('transform:rotate(90deg)', html)
        self.assertIn('stage.requestFullscreen', html)
        self.assertIn('11cqw', html)
        self.assertIn('.legend{display:none}', html)


if __name__ == "__main__":
    unittest.main()