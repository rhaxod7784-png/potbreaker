"""Regression tests for PotBreaker optional Space-held pot burst."""
import json
import unittest

from web.game import PotBreaker
from web.game_engine import GameEngine


class ChargeBurstTests(unittest.TestCase):
    def make_game(self, difficulty="normal"):
        game = PotBreaker(seed=3, difficulty=difficulty)
        game.boss_move_cd = 999
        game.boss_throw_cd = 999
        game.crow_spawn_timer = 999
        game.moving_walls = set()
        return game

    def test_difficulty_limits_are_independent_of_regular_ammo_capacity(self):
        for difficulty, limit in (("normal", 3), ("hard", 4), ("very_hard", 5)):
            with self.subTest(difficulty=difficulty):
                game = self.make_game(difficulty)
                self.assertEqual(game.charge_cap, limit)
                self.assertEqual(game.player_pot_cap, 3 if difficulty == "normal" else 2)

    def test_normal_uses_owned_ammo_then_deals_three_damage(self):
        game = self.make_game()
        game.ammo = 3
        game.step(.04, charge=True)
        self.assertEqual((game.ammo, game.charge_count), (0, 3))
        game.step(.04, charge=False)
        self.assertEqual(game.boss_hp, 2)
        self.assertEqual((game.charge_count, game.charge_active), (0, False))
        self.assertEqual(len(game.hit_events), 3)

    def test_hard_pickups_extend_burst_to_four(self):
        game = self.make_game("hard")
        game.ammo = 2
        game.step(.04, charge=True)
        self.assertEqual(game.charge_count, 2)
        self.assertTrue(game._charge_pickup())
        self.assertTrue(game._charge_pickup())
        self.assertFalse(game._charge_pickup())
        game.step(.04, charge=False)
        self.assertEqual(game.boss_hp, 3)

    def test_very_hard_collects_five_from_zero(self):
        game = self.make_game("very_hard")
        game.step(.04, charge=True)
        for _ in range(5):
            self.assertTrue(game._charge_pickup())
        self.assertFalse(game._charge_pickup())
        game.step(.04, charge=False)
        self.assertEqual(game.boss_hp, 5)

    def test_player_field_pickup_joins_charge_instead_of_ammo(self):
        game = self.make_game("hard")
        game.ammo = 2
        game.step(.04, charge=True)
        game.pots[:] = [game.player[:]]
        game._maintain_field_pots = lambda: None
        game._pickups()
        self.assertEqual(game.charge_count, 3)
        self.assertEqual(game.ammo, 0)
        self.assertNotIn(game.player, game.pots)

    def test_ordinary_fire_still_works_without_charging(self):
        game = self.make_game()
        game.ammo = 1
        game.step(.04, fire=True)
        self.assertEqual(game.ammo, 0)
        self.assertFalse(game.charge_active)

    def test_empty_charge_does_not_damage_boss(self):
        game = self.make_game()
        game.step(.04, charge=True)
        game.step(.04, charge=False)
        self.assertEqual(game.boss_hp, game.boss_hp_cap)
        self.assertEqual(game.phase, "playing")

    def test_burst_finishes_at_zero_boss_hp(self):
        game = self.make_game()
        game.boss_hp = 2
        game.ammo = 3
        game.step(.04, charge=True)
        game.step(.04, charge=False)
        self.assertEqual(game.boss_hp, 0)
        self.assertEqual(game.phase, "win")

    def test_reset_clears_charge(self):
        game = self.make_game()
        game.ammo = 2
        game.step(.04, charge=True)
        game.reset()
        self.assertEqual((game.charge_active, game.charge_count), (False, 0))

    def test_game_engine_supports_charge_and_legacy_step_signature(self):
        game = GameEngine("potbreaker", seed=5, difficulty="hard")
        self.assertEqual(json.loads(game.state())["charge_cap"], 4)
        game.mode.ammo = 2
        game.step(.04, charge=True)
        self.assertTrue(json.loads(game.state())["charging"])
        game.step(.04)
        self.assertFalse(json.loads(game.state())["charging"])


if __name__ == "__main__":
    unittest.main()
