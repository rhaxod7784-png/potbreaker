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
            self.assertEqual(len(state["pots"]) + len(state["special_pots"]), 5)
            self.assertTrue(0 <= state["boss_ammo"] <= 5)
            self.assertTrue(0 <= state["player_hp"] <= 3 and 0 <= state["boss_hp"] <= 10)
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
        game.boss_ammo = 1
        game._fire(game.boss, [1, 0], npc=True)

        game._advance_projectiles(.085)

        self.assertEqual(game.projectiles, [])
        self.assertEqual(game.pot_break_events, [])
        self.assertEqual(len(game.pots) + len(game.special_pots), 5)

    def test_character_hit_emits_pot_break_event(self):
        game = PotBreaker(4)
        game.player = [2, 2]
        game.boss = [5, 5]
        game.projectiles = [{'x': 4.5, 'y': 5.0, 'dx': 1.0, 'dy': 0.0,
                             'range': 4.0, 'boss': False}]

        game._advance_projectiles(.01)

        state = json.loads(game.state())
        self.assertEqual(game.boss_hp, 2)
        self.assertEqual(len(state["pot_breaks"]), 1)

    def test_boss_pots_are_slower_and_crow_events_are_rebalanced(self):
        game = PotBreaker(1)
        game.boss = [4, 5]
        game.player = [15, 5]
        game.boss_ammo = 1
        game._fire(game.boss, [1, 0], npc=True)
        game._advance_projectiles(.05)

        self.assertAlmostEqual(game.projectiles[0]["x"] - 4, .32, places=2)
        self.assertGreater(CROW_RESPAWN_SECONDS, 9.0)
        self.assertEqual(CROW_DROP_SECONDS, 1.2)

        game = PotBreaker(2)
        game.crow_spawn_timer = 0
        created = 0
        for _ in range(95):
            before = len(game.mystery_pots)
            game._update_crow(.05)
            created += len(game.mystery_pots) - before
        self.assertGreaterEqual(created, 6)
        self.assertEqual(created % 2, 0)
        self.assertTrue(all(item["effect"] in {"damage", "heal", "refill", "field_reset"} for item in game.mystery_pots))

    def test_crow_drops_two_question_pots_with_four_equal_effects(self):
        game = PotBreaker(21)
        seen = []
        def choose(options):
            if options and isinstance(options[0], str):
                seen.append(tuple(options))
                return "field_reset" if len(seen) == 1 else "refill"
            return options[0]
        game.rng.choice = choose
        game._spawn_mystery_pots(8, 5)
        self.assertEqual(len(game.mystery_pots), 2)
        self.assertEqual(seen, [("heal", "damage", "refill", "field_reset")] * 2)
        self.assertEqual({item["effect"] for item in game.mystery_pots}, {"field_reset", "refill"})
        self.assertTrue(all(item["ttl"] > 0 for item in game.mystery_pots))

    def test_mystery_pots_apply_same_hp_effects_to_kimyo_and_keuda(self):
        game = PotBreaker(22)
        game.player, game.boss = [2, 2], [6, 6]
        game.player_hp, game.boss_hp = 2, 2
        game.player_invuln = game.boss_invuln = .5
        game.mystery_pots = [
            {"x": 2, "y": 2, "effect": "damage", "ttl": 10},
            {"x": 6, "y": 6, "effect": "heal", "ttl": 10},
        ]
        game._pick_mystery_pots()
        self.assertEqual(game.player_hp, 1)
        self.assertEqual(game.boss_hp, 3)
        self.assertEqual(game.mystery_pots, [])

        game.player_hp, game.boss_hp = 2, 4
        game.mystery_pots = [
            {"x": 2, "y": 2, "effect": "heal", "ttl": 10},
            {"x": 6, "y": 6, "effect": "damage", "ttl": 10},
        ]
        game._pick_mystery_pots()
        self.assertEqual(game.player_hp, 3)
        self.assertEqual(game.boss_hp, 3)

    def test_kimyo_moves_on_grid_at_reduced_speed(self):
        self.assertAlmostEqual(PLAYER_MOVE_INTERVAL, 0.24)
        self.assertAlmostEqual(PLAYER_DASH_MOVE_INTERVAL, 0.09)
        game = PotBreaker(11)
        game.walls = set()
        game.moving_walls = set()
        game.player = [5, 5]
        self.assertTrue(game._move_player(1.0, 0.0))
        self.assertEqual(game.player, [6, 5])
        self.assertTrue(all(float(value).is_integer() for value in game.player))

    def test_player_pot_capacity_is_three_and_start_is_inset(self):
        game = PotBreaker(3)
        self.assertEqual(game.ammo, 0)
        self.assertEqual(json.loads(game.state())["ammo"], 0)
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

        self.assertEqual(len(game.special_pots), 1)
        self.assertEqual({item["effect"] for item in game.special_pots}, {"heal"})
        self.assertEqual(game.boss_ammo, 0)
        self.assertEqual(PotBreaker(1, "normal").boss_hp_cap, 5)
        self.assertEqual(PotBreaker(1, "hard").boss_hp_cap, 7)
        self.assertEqual(PotBreaker(1, "very_hard").boss_hp_cap, 10)
        self.assertEqual(PotBreaker(1, "hard").player_pot_cap, 2)
        self.assertEqual(PotBreaker(1, "very_hard").player_pot_cap, 2)

    def test_mobile_controls_use_touch_direction_without_movement_buttons(self):
        html = Path(__file__).parents[1].joinpath("web", "index.html").read_text(encoding="utf-8")
        self.assertNotIn('id="dpad"', html)
        self.assertNotIn('class="dpad-button', html)
        self.assertIn("canvas.addEventListener('pointerdown'", html)
        self.assertIn("function directionFromScreenDelta(dx,dy)", html)
        self.assertIn("threshold=hasDirection ? .21 : .1", html)
        self.assertIn("return touchActive?touchDirection:[0,0]", html)
        self.assertNotIn("touchPending", html)
        self.assertIn("canvas.addEventListener('pointermove'", html)
        self.assertIn("touchDirection", html)
        self.assertIn("keyDirections[code]", html)
        self.assertIn("@media (pointer:coarse),(max-height:520px)", html)
        self.assertIn("clamp(126px,16cqw,164px)", html)
        self.assertIn("function getMove()", html)
        self.assertIn("function safeLoop(now)", html)
        self.assertIn("typeof ctx.roundRect==='function'", html)
        self.assertIn(".action.fire{width:clamp(82px,8.5cqw,108px)", html)

    def test_fire_button_fires_while_held_and_stops_on_release(self):
        html = Path(__file__).parents[1].joinpath("web", "index.html").read_text(encoding="utf-8")
        self.assertIn("for(const type of ['pointerup','pointercancel','lostpointercapture'])fireButton.addEventListener(type,stopFiring)", html)
        self.assertIn("const fireNow=fire,dashNow=dash;dash=false;", html)
        self.assertNotIn("const fireNow=fire,dashNow=dash;fire=false;", html)
        self.assertIn("if(e.code==='Space')fire=false", html)

    def test_touch_movement_and_shatter_feedback_are_wired(self):
        html = Path(__file__).parents[1].joinpath("web", "index.html").read_text(encoding="utf-8")
        self.assertIn("canvas.setPointerCapture(e.pointerId)", html)
        self.assertIn("window.addEventListener('pageshow'", html)
        self.assertIn("window.addEventListener('pagehide',stop)", html)
        self.assertIn("function getMove()", html)
        self.assertIn("fetch('/game.py'", html)
        self.assertNotIn('id="pythonEngine"', html)
        self.assertIn("breakParticles.push", html)
        self.assertIn("kind==='mystery'", html)
        self.assertIn("s.mystery_pots||[]", html)
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
        self.assertIn("POT BREAKER RE v1.0.45", html)
        build = Path(__file__).parents[1].joinpath("scripts", "build_worker.py").read_text(encoding="utf-8")
        self.assertIn('version:"1.0.45"', build)
        self.assertIn("(orientation:portrait) and (pointer:coarse)", html)
        self.assertIn("position:fixed;inset:0;width:100vw;height:100dvh;display:block;overflow:hidden", html)
        self.assertIn("transform:translate(-50%,-50%) rotate(90deg)", html)
        self.assertIn("width:min(100dvh,177.778vw)", html)
        self.assertNotIn('id="rotate"', html)
        self.assertNotIn("screen.orientation.lock", html)
        self.assertNotIn("휴대폰을 가로로 돌려 주세요", html)
        self.assertIn("requestFullscreen", html)

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
