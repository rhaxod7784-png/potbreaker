import json
import re
import unittest
from pathlib import Path

from web.game import (
    CROW_DROP_SECONDS,
    CROW_RESPAWN_SECONDS,
    PLAYER_DASH_MOVE_INTERVAL,
    PLAYER_MOVE_INTERVAL,
    PotBreaker,
)


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
        self.assertEqual(len(game.pot_break_events), 1)
        self.assertEqual(json.loads(game.state())["pot_breaks"][0]["id"], 1)

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

    def test_kimyo_movement_is_slightly_faster(self):
        self.assertAlmostEqual(PLAYER_MOVE_INTERVAL, 0.105)
        self.assertAlmostEqual(PLAYER_DASH_MOVE_INTERVAL, 0.09)
        self.assertLess(PLAYER_MOVE_INTERVAL, 0.115)
        self.assertLess(PLAYER_DASH_MOVE_INTERVAL, 0.095)

    def test_diagonal_player_movement_and_corner_collision(self):
        game = PotBreaker(3)
        game.player = [5, 5]
        game.walls = {(6, 5)}
        game.player_move_cd = 0
        game.step(.04, 1, 1)
        self.assertEqual(game.player, [5, 5])

        game.walls.clear()
        game.player_move_cd = 0
        game.step(.04, 1, 1)
        self.assertEqual(game.player, [6, 6])
        self.assertAlmostEqual(game.player_move_cd, PLAYER_MOVE_INTERVAL * 2**0.5)

    def test_partial_stick_pressure_moves_and_scales_speed(self):
        game = PotBreaker(7)
        game.player = [5, 5]
        game.player_move_cd = 0
        game.walls.clear()
        game.moving_walls.clear()
        game.step(.04, .15, 0)
        self.assertEqual(game.player, [6, 5])
        self.assertAlmostEqual(game.player_move_cd, PLAYER_MOVE_INTERVAL / .7)

    def test_mobile_controls_allow_diagonal_and_large_throw_target(self):
        html = Path(__file__).parents[1].joinpath("web", "index.html").read_text(encoding="utf-8")
        self.assertIn("magnitude<.12", html)
        self.assertIn("Math.round(Math.atan2(y,x)/(Math.PI/4))", html)
        self.assertIn("@media (pointer:coarse),(max-height:520px)", html)
        self.assertIn(".action.fire{width:clamp(112px,17cqw,152px);min-width:112px;min-height:112px}", html)

    def test_mobile_stick_capture_and_shatter_audio_are_wired(self):
        html = Path(__file__).parents[1].joinpath("web", "index.html").read_text(encoding="utf-8")
        self.assertIn("window.addEventListener('pointermove'", html)
        self.assertIn("window.addEventListener(event,release)", html)
        self.assertIn("function shatterSound()", html)
        self.assertIn("unlockGameAudio();requestLandscapeMode();show('intro')", html)
        self.assertIn("unlockGameAudio();requestLandscapeMode();stop()", html)
        self.assertIn("s.pot_breaks||[]", html)

    def test_opening_comic_has_four_equal_sized_panels(self):
        html = Path(__file__).parents[1].joinpath("web", "index.html").read_text(encoding="utf-8")
        match = re.search(r"const boxes=(\[[^;]+)", html)
        self.assertIsNotNone(match)
        boxes = [[int(value) for value in panel.split(",")] for panel in re.findall(r"\[([^\[\]]+)\]", match.group(1))]
        self.assertEqual(len(boxes), 4)
        self.assertEqual({(width, height) for _, _, width, height in boxes}, {(672, 409)})
        self.assertIn("POT BREAKER RE v1.0.13", html)
        self.assertIn('transform:rotate(90deg)', html)
        self.assertIn('id="rotateStart"', html)
        self.assertIn("(orientation:portrait) and (max-width:900px)", html)
        self.assertIn("position:fixed;z-index:100", html)
        self.assertIn("requestLandscapeMode();show('intro')", html)

    def test_mobile_intro_uses_stage_height_and_scaled_copy(self):
        html = Path(__file__).parents[1].joinpath("web", "index.html").read_text(encoding="utf-8")
        self.assertIn(".intro{grid-template-rows:minmax(0,1fr);min-height:0}", html)
        self.assertIn("font-size:clamp(15px,3.15cqw,45px)", html)
        self.assertIn("min-height:0;max-height:100%", html)
        self.assertIn('stage.requestFullscreen', html)
        self.assertIn('11cqw', html)
        self.assertIn('.legend{display:none}', html)


if __name__ == "__main__":
    unittest.main()
