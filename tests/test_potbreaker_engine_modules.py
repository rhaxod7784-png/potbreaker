import json
import unittest

from web.game import PotBreaker


class PotBreakerFeatureModuleTests(unittest.TestCase):
    def test_legacy_engine_api_routes_to_composed_modules(self):
        game = PotBreaker(42)
        self.assertEqual(
            set(game._feature_modules),
            {"field", "combat", "actor"},
        )
        self.assertIs(game._free.__self__, game._feature_modules["field"])
        self.assertIs(game._damage.__self__, game._feature_modules["combat"])
        self.assertIs(game._move_player.__self__, game._feature_modules["actor"])

    def test_composed_engine_keeps_deterministic_step_and_state(self):
        left = PotBreaker(17)
        right = PotBreaker(17)
        left_state = json.loads(left.step(.04, 1, 0))
        right_state = json.loads(right.step(.04, 1, 0))
        self.assertEqual(left_state, right_state)
        self.assertEqual(len(left_state["pots"]), 4)
        self.assertEqual(left_state["phase"], "playing")

    def test_feature_methods_can_call_across_modules(self):
        game = PotBreaker(9)
        self.assertEqual(game._free(game.player[0], game.player[1]), True)
        aim = game._aim([2, 2], [5, 4])
        self.assertAlmostEqual(aim[0], 3 / (13 ** .5))
        self.assertAlmostEqual(aim[1], 2 / (13 ** .5))


if __name__ == "__main__":
    unittest.main()
