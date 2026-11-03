"""Regression tests for independent large charged pot projectiles."""
import json
import unittest
from pathlib import Path
from web.game import PotBreaker
from web.game_engine import GameEngine


class ChargeV111Tests(unittest.TestCase):
    def make_game(self, difficulty="normal"):
        g = PotBreaker(seed=42, difficulty=difficulty)
        g.player, g.boss = [1, 5], [10, 5]
        g.walls, g.moving_walls = set(), set()
        g.boss_move_cd = g.boss_throw_cd = g.crow_spawn_timer = 999
        return g

    def shoot(self, g, count=3):
        g.ammo = count
        g._begin_charge()
        self.assertEqual(g.charge_count, count)
        g._release_charge()
        self.assertEqual(len(g.charge_projectiles), 1)
        return g.charge_projectiles[0]

    def advance(self, g):
        for _ in range(60):
            if not g.charge_projectiles:
                break
            g._advance_charge_projectiles(.08)

    def test_all_difficulties_have_three_ammo_and_charge(self):
        for diff in ("normal", "hard", "very_hard"):
            with self.subTest(diff=diff):
                g = self.make_game(diff)
                self.assertEqual((g.player_pot_cap, g.charge_cap), (3, 3))
                g.ammo = 3
                g._begin_charge()
                self.assertEqual(g.charge_count, 3)
                self.assertFalse(g._charge_pickup())

    def test_pickups_during_charge_stop_at_three(self):
        g = self.make_game("hard")
        g.ammo = 2
        g._begin_charge()
        self.assertTrue(g._charge_pickup())
        self.assertFalse(g._charge_pickup())

    def test_release_not_automatic_hit_and_large_shot_in_state(self):
        g = self.make_game()
        hp = g.boss_hp
        shot = self.shoot(g)
        self.assertEqual(g.boss_hp, hp)
        self.assertEqual(shot["damage"], 3)
        self.assertTrue(shot["large"])
        self.assertTrue(shot["charged"])
        self.assertEqual(len(json.loads(g.state())["projectiles"]), 1)

    def test_actual_hit_deals_collected_count_damage(self):
        g = self.make_game()
        hp = g.boss_hp
        self.shoot(g)
        self.advance(g)
        self.assertEqual(g.boss_hp, hp - 3)
        self.assertFalse(g.charge_projectiles)

    def test_pierces_two_partitions_and_hits(self):
        g = self.make_game()
        g.walls = {(3, 5), (6, 5)}
        shot = self.shoot(g)
        hp = g.boss_hp
        self.advance(g)
        self.assertEqual(shot["penetrated"], 2)
        self.assertEqual(g.boss_hp, hp - 3)

    def test_static_and_moving_partition_both_count(self):
        g = self.make_game()
        g.walls = {(3, 5)}
        g.moving_walls = {(6, 5)}
        shot = self.shoot(g)
        self.advance(g)
        self.assertEqual(shot["penetrated"], 2)
        self.assertEqual(g.boss_hp, g.boss_hp_cap - 3)

    def test_third_partition_blocks_with_no_damage(self):
        g = self.make_game()
        g.walls = {(3, 5), (5, 5), (7, 5)}
        shot = self.shoot(g)
        hp = g.boss_hp
        self.advance(g)
        self.assertEqual(shot["penetrated"], 2)
        self.assertEqual(g.boss_hp, hp)
        self.assertFalse(g.charge_projectiles)

    def test_boss_can_dodge_aim_locked_at_release(self):
        g = self.make_game()
        hp = g.boss_hp
        self.shoot(g)
        g.boss = [10, 8]
        self.advance(g)
        self.assertEqual(g.boss_hp, hp)
        self.assertFalse(g.charge_projectiles)

    def test_empty_charge_does_not_fire(self):
        g = self.make_game()
        g._begin_charge()
        g._release_charge()
        self.assertFalse(g.charge_projectiles)
        self.assertEqual(g.boss_hp, g.boss_hp_cap)

    def test_regular_throw_remains_separate_and_wall_blocked(self):
        g = self.make_game()
        g.ammo = 1
        g.walls = {(3, 5)}
        g._fire(g.player, [1, 0])
        self.assertEqual(len(g.projectiles), 1)
        self.assertFalse(g.charge_projectiles)
        for _ in range(30):
            g._advance_projectiles(.04)
        self.assertEqual(g.boss_hp, g.boss_hp_cap)

    def test_reset_clears_charge_shot(self):
        g = self.make_game()
        self.shoot(g)
        g.reset()
        self.assertFalse(g.charge_projectiles)
        self.assertEqual((g.charge_active, g.charge_count), (False, 0))

    def test_game_engine_accepts_legacy_and_charge_step(self):
        g = GameEngine("potbreaker", seed=5, difficulty="very_hard")
        self.assertEqual(json.loads(g.state())["charge_cap"], 3)
        g.mode.ammo = 2
        g.step(.04, charge=True)
        self.assertTrue(json.loads(g.state())["charging"])
        g.step(.04)
        self.assertFalse(json.loads(g.state())["charging"])

    def test_builder_uses_boss_sized_sprite_for_large_projectile(self):
        src = (Path(__file__).resolve().parents[1] / "scripts/build_worker.py").read_text("utf-8")
        self.assertIn("(p.boss||p.large)?.92:.52", src)


if __name__ == "__main__":
    unittest.main()
