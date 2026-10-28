import json
import math
import re
import unittest
from pathlib import Path

from web.game import (
    CROW_DROP_SECONDS,
    CROW_RESPAWN_SECONDS,
    PLAYER_DASH_MOVE_INTERVAL,
    PLAYER_MOVE_INTERVAL,
    PLAYER_POT_CAP,
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

    def test_auto_aim_targets_opponent_and_has_no_visible_aim_line(self):
        game = PotBreaker(7)
        aim = game._aim([2, 2], [5, 4])
        self.assertAlmostEqual(aim[0], 3 / math.sqrt(13))
        self.assertAlmostEqual(aim[1], 2 / math.sqrt(13))

        html = Path(__file__).parents[1].joinpath("web", "index.html").read_text(encoding="utf-8")
        self.assertNotIn("drawAimRay", html)
        self.assertNotIn("aimArc(", html)
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
        self.assertEqual(game.pot_break_events, [])
        self.assertEqual(len(game.pots), 6)

    def test_character_hit_emits_pot_break_event(self):
        game = PotBreaker(4)
        game.player = [2, 2]
        game.boss = [5, 5]
        game.projectiles = [{'x': 4.5, 'y': 5.0, 'dx': 1.0, 'dy': 0.0,
                             'range': 4.0, 'boss': False}]

        game._advance_projectiles(.01)

        state = json.loads(game.state())
        self.assertEqual(game.boss_hp, 4)
        self.assertEqual(len(state["pot_breaks"]), 1)

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
        self.assertAlmostEqual(PLAYER_MOVE_INTERVAL, 0.0955)
        self.assertAlmostEqual(.105 / PLAYER_MOVE_INTERVAL - 1, .10, places=2)
        self.assertAlmostEqual(PLAYER_DASH_MOVE_INTERVAL, 0.09)
        self.assertLess(PLAYER_DASH_MOVE_INTERVAL, 0.095)

    def test_player_pot_capacity_is_three_and_start_is_inset(self):
        game = PotBreaker(3)
        self.assertEqual(game.ammo, PLAYER_POT_CAP)
        self.assertEqual(json.loads(game.state())["ammo"], 3)
        game.ammo = 2
        game.player = game.pots[0][:]
        game._pickups()
        self.assertEqual(game.ammo, 3)
        self.assertEqual(json.loads(game.state())["ammo_cap"], PLAYER_POT_CAP)

        game.player = game.pots[0][:]
        game._pickups()
        self.assertEqual(game.ammo, 3)

        for seed in range(30):
            player = PotBreaker(seed).player
            self.assertIn(player[0], (3, 15))
            self.assertIn(player[1], (3, 7))

    def test_mobile_controls_use_compact_dpad_and_transparent_buttons(self):
        html = Path(__file__).parents[1].joinpath("web", "index.html").read_text(encoding="utf-8")
        self.assertIn('id="dpad"', html)
        self.assertIn('data-dir="up"', html)
        self.assertNotIn('class="joystick"', html)
        self.assertIn("dpadDirection", html)
        self.assertIn("@media (pointer:coarse),(max-height:520px)", html)
        self.assertIn("opacity:.78", html)
        self.assertIn(".action.fire{width:clamp(64px,6.2cqw,88px)", html)

    def test_mobile_dpad_and_shatter_feedback_are_wired(self):
        html = Path(__file__).parents[1].joinpath("web", "index.html").read_text(encoding="utf-8")
        self.assertIn("button.setPointerCapture(e.pointerId)", html)
        self.assertIn("button.addEventListener('pointerup',release)", html)
        self.assertIn("button.addEventListener('pointercancel',release)", html)
        self.assertIn("fetch('/game.py'", html)
        self.assertNotIn('id="pythonEngine"', html)
        self.assertIn("breakParticles.push", html)
        self.assertIn("life:1.05,label:true", html)
        self.assertIn("function shatterSound()", html)
        self.assertIn("s.pot_breaks||[]", html)
        self.assertIn("shakeTimer=.3", html)
        self.assertIn("ctx.translate((Math.random()-.5)*.32", html)
        for color in ("#e65b58", "#5b91e8", "#f0c44e", "#62bd78"):
            self.assertIn(color, html)

    def test_opening_comic_has_four_equal_sized_panels(self):
        html = Path(__file__).parents[1].joinpath("web", "index.html").read_text(encoding="utf-8")
        match = re.search(r"const boxes=(\[[^;]+)", html)
        self.assertIsNotNone(match)
        boxes = [[int(value) for value in panel.split(",")] for panel in re.findall(r"\[([^\[\]]+)\]", match.group(1))]
        self.assertEqual(len(boxes), 4)
        self.assertEqual({(width, height) for _, _, width, height in boxes}, {(672, 409)})
        self.assertIn("POT BREAKER RE v1.0.21", html)
        build = Path(__file__).parents[1].joinpath("scripts", "build_worker.py").read_text(encoding="utf-8")
        self.assertIn('version:"1.0.21"', build)
        self.assertIn('id="rotateStart"', html)
        self.assertIn("(orientation:portrait) and (pointer:coarse)", html)
        self.assertIn('휴대폰을 가로로 돌려 주세요', html)
        self.assertIn("screen.orientation.lock('landscape')", html)
        self.assertIn("Promise.allSettled(requests)", html)
        self.assertIn("const orientationAttempt=requestLandscapeMode()", html)

        self.assertIn("requestLandscapeMode();show('intro')", html)

    def test_mobile_intro_uses_stage_height_and_scaled_copy(self):
        html = Path(__file__).parents[1].joinpath("web", "index.html").read_text(encoding="utf-8")
        self.assertIn(".intro{grid-template-rows:minmax(0,1fr);min-height:0}", html)
        self.assertIn("font-size:clamp(15px,3.15cqw,45px)", html)
        self.assertIn("min-height:0;max-height:100%", html)
        self.assertIn('document.documentElement', html)
        self.assertIn('fullscreen', html)
        self.assertIn('.legend{display:none}', html)


if __name__ == "__main__":
    unittest.main()
