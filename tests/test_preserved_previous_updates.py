"""Guard existing PotBreaker/Ginkgo rules when adding the Space-held burst.

This is additive regression coverage, not a substitute for comparing the
November 2 production Worker source against the November 3 release.
"""
import json
import unittest

from web.game import (
    PotBreaker, PLAYER_HP, PLAYER_DASH_COOLDOWN, BOSS_DASH_COOLDOWN,
    BOSS_POT_CAP, FIELD_POT_COUNT,
)
from web.game_engine import GameEngine


class PreviousUpdateCompatibilityTests(unittest.TestCase):
    def test_original_potbreaker_health_dash_and_difficulty_rules(self):
        self.assertEqual(PLAYER_HP, 3)
        self.assertEqual(PLAYER_DASH_COOLDOWN, 3.0)
        self.assertEqual(BOSS_DASH_COOLDOWN, 5.0)
        self.assertEqual(BOSS_POT_CAP, 5)
        for difficulty, boss_hp, ammo_cap in (
            ("normal", 5, 3), ("hard", 7, 3), ("very_hard", 10, 3),
        ):
            with self.subTest(difficulty=difficulty):
                game = PotBreaker(seed=5, difficulty=difficulty)
                state = json.loads(game.state())
                self.assertEqual(state["player_hp"], 3)
                self.assertEqual(state["boss_hp_cap"], boss_hp)
                self.assertEqual(state["ammo_cap"], ammo_cap)
                self.assertEqual(len(state["pots"]), FIELD_POT_COUNT)
                self.assertEqual(len(state["special_pots"]), 1)
                self.assertEqual(len(state["pots"]) + len(state["special_pots"]), 6)

    def test_field_pots_are_recycled_not_infinitely_added(self):
        game = PotBreaker(seed=5)
        game.moving_walls = set()
        for i in range(20):
            game._drop_pot((i * 3) % 19, (i * 2) % 11)
            self.assertEqual(len(game.pots), FIELD_POT_COUNT)
        self.assertEqual({pot["effect"] for pot in game.special_pots}, {"heal"})

    def test_boss_projectiles_still_respect_partitions(self):
        game = PotBreaker(seed=5)
        game.boss = [1, 5]
        game.player = [8, 5]
        game.moving_walls = {(3, 5)}
        game.walls = set()
        game.boss_ammo = 1
        game._fire(game.boss, [1, 0], npc=True)
        self.assertEqual(len(game.projectiles), 1)
        for _ in range(25):
            game._advance_projectiles(.04)
        self.assertEqual(game.player_hp, PLAYER_HP)
        self.assertEqual(len(game.projectiles), 0)

    def test_new_charge_does_not_disable_ordinary_throw(self):
        game = PotBreaker(seed=8)
        game.ammo = 2
        game.step(.04, charge=True)
        self.assertEqual(game.charge_count, 2)
        game.step(.04, charge=False)
        self.assertEqual(game.boss_hp, game.boss_hp_cap)
        self.assertEqual(len(game.charge_projectiles), 1)
        game.reset()
        game.ammo = 1
        game.boss_move_cd = 999
        game.step(.04, fire=True)
        self.assertEqual(game.ammo, 0)
        self.assertFalse(game.charge_active)

    def test_ginkgo_and_original_engine_share_facade_without_mode_replacement(self):
        ginkgo = GameEngine("ginkgo", seed=41, difficulty="hard")
        self.assertEqual(json.loads(ginkgo.state())["difficulty"], "hard")
        self.assertEqual(ginkgo.mode.interval, 2.0)
        pot = GameEngine("potbreaker", seed=41, difficulty="hard")
        self.assertEqual(json.loads(pot.state())["charge_cap"], 3)
        self.assertNotIn("cells", json.loads(pot.state()))


if __name__ == "__main__":
    unittest.main()
