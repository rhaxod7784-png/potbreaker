import json
import unittest

from web.game_engine import GameEngine


class GinkgoModeTests(unittest.TestCase):
    def make_game(self, difficulty="normal"):
        return GameEngine("ginkgo", seed=41, difficulty=difficulty)

    def test_board_and_difficulty_parameters(self):
        game = self.make_game("very_hard")
        state = json.loads(game.state())
        self.assertEqual(len(state["cells"]), 13 * 7)
        self.assertEqual(state["difficulty"], "very_hard")
        self.assertEqual(state["remaining_ms"], 60000)

    def test_female_and_male_tree_transitions(self):
        female = self.make_game()
        female.mode.cells[0] = {"phase": 1, "sex": 1}
        female.step(female.mode.interval)
        self.assertEqual(json.loads(female.state())["cells"][0], 2)

        male = self.make_game()
        male.mode.cells[0] = {"phase": 1, "sex": 0}
        male.step(male.mode.interval)
        self.assertEqual(json.loads(male.state())["cells"][0], 0)

    def test_success_combo_and_leaf_reset_keep_earned_score(self):
        game = self.make_game()
        game.mode.cells[0]["phase"] = 2
        game.tap(0)
        self.assertEqual(json.loads(game.state())["score"], 1)

        game.mode.cells[1]["phase"] = 2
        game.tap(1)
        state = json.loads(game.state())
        self.assertEqual((state["score"], state["combo"], state["max_combo"]), (3, 2, 2))

        game.mode.cells[2]["phase"] = 1
        game.tap(2)
        state = json.loads(game.state())
        self.assertEqual((state["score"], state["combo"], state["max_combo"]), (3, 0, 2))

    def test_rotten_fruit_locks_input_for_half_a_second(self):
        game = self.make_game()
        game.mode.cells[0]["phase"] = 3
        self.assertTrue(game.tap(0))
        self.assertTrue(json.loads(game.state())["locked"])

        game.step(0.49)
        self.assertFalse(game.tap(1))
        game.step(0.02)
        self.assertTrue(game.tap(1))

    def test_timer_ends_game_and_rejects_later_taps(self):
        game = self.make_game()
        game.step(60.0)
        state = json.loads(game.state())
        self.assertEqual(state["phase"], "finished")
        self.assertEqual(state["remaining_ms"], 0)
        self.assertFalse(game.tap(0))


if __name__ == "__main__":
    unittest.main()
