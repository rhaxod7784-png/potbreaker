"""Floor Breaker component regression tests; no live matchmaking is implied."""
import json
import unittest

from web.game_engine import GameEngine
from web.floor_modules import CHARACTERS, TRAP_TYPES


def snapshot(game):
    return json.loads(game.state())


class FloorBreakerTests(unittest.TestCase):
    def make_game(self, characters=("gimyo", "keuda")):
        return GameEngine("floor", seed=74, characters=characters)

    def test_board_setup_and_traps(self):
        game = self.make_game()
        state = snapshot(game)
        board = game.mode.board
        self.assertEqual((state["board_cols"], state["board_rows"]), (10, 20))
        self.assertEqual(len(board.pieces), 10)
        self.assertEqual([len(board.active(i)) for i in (0, 1)], [5, 5])
        self.assertEqual(len(board.traps), 30)
        self.assertEqual([list(board.traps.values()).count(k) for k in TRAP_TYPES],
                         [10, 10, 10])
        self.assertTrue(all(3 <= y <= 16 for x, y in board.traps))
        self.assertTrue(all((17 <= p["y"] <= 19 if p["team"] == 0
                             else 0 <= p["y"] <= 2) for p in board.pieces))
        self.assertEqual(state["characters"], ["gimyo", "keuda"])
        self.assertEqual(state["turn"], 1)
        self.assertEqual(state["remaining_ms"], 10000)

    def test_player_selects_a_unit_and_moves_legal_destination(self):
        game = self.make_game()
        board = game.mode.board
        # Bottom-side pieces can step forward into unoccupied cells.
        piece = next(p for p in board.active(0)
                     if not board.piece_at((p["x"], p["y"] - 1)))
        self.assertTrue(game.tap(piece["y"] * 10 + piece["x"]))
        state = snapshot(game)
        targets = [t for t in state["targets"] if t["kind"] == "move"]
        self.assertTrue(targets)
        self.assertTrue(game.tap(targets[0]["index"]))
        self.assertEqual(snapshot(game)["turn"], 2)
        self.assertEqual(snapshot(game)["current_team"], 1)

    def test_three_timeouts_and_erosion(self):
        game = self.make_game()
        board, clock, rules = game.mode.board, game.mode.clock, game.mode.rules
        clock.turn = 11
        self.assertEqual(clock.team, 0)
        game.step(10.0)
        state = snapshot(game)
        self.assertIn(19, state["eroded_rows"])
        self.assertEqual(state["turn"], 12)
        self.assertEqual(state["consecutive_timeouts"], [1, 0])
        # Artificially set state to test consecutive timeouts without moves.
        clock.team = 0
        clock.turn = 13
        clock.timeouts[0] = 2
        clock.elapsed = 0
        game.step(10.0)
        self.assertEqual(snapshot(game)["winner"], 1)
        self.assertEqual(snapshot(game)["result_reason"], "three_consecutive_timeouts")

    def test_trap_resolution_and_used_cell(self):
        game = self.make_game()
        board, clock, rules = game.mode.board, game.mode.clock, game.mode.rules
        pit = next(pos for pos, kind in board.traps.items() if kind == "pit")
        piece = board.active(0)[0]
        piece["x"], piece["y"] = 0, 19
        # Keep the destination unoccupied before applying a special movement.
        self.assertIsNone(board.piece_at(pit))
        rules._land(board, clock, piece, pit)
        self.assertNotIn(piece, board.pieces)
        self.assertIn(pit, board.used)
        self.assertTrue(board.blocked(pit))

    def test_gimyo_skill_reduces_turn_options_only_until_use(self):
        game = self.make_game()
        board, clock, rules = game.mode.board, game.mode.clock, game.mode.rules
        piece = board.active(0)[0]
        piece["x"], piece["y"] = 5, 15
        for other in list(board.pieces):
            if (other is not piece and other["team"] == 0 and
                    other["x"] == 5 and other["y"] == 15):
                board.remove(other)
        clock.turn = 5
        game.tap(piece["y"] * 10 + piece["x"])
        normal = {t["index"] for t in snapshot(game)["targets"]}
        game.sync({"ability": True})
        boosted = {t["index"] for t in snapshot(game)["targets"]}
        self.assertTrue(snapshot(game)["skill_armed"])
        self.assertTrue(boosted.issuperset(normal))
        self.assertGreater(len(boosted), len(normal))

    def test_gam_reveals_one_unspent_trap(self):
        game = self.make_game(("gam", "keuda"))
        board, clock = game.mode.board, game.mode.clock
        clock.turn = 5
        piece = board.active(0)[0]
        self.assertTrue(game.tap(piece["y"] * 10 + piece["x"]))
        self.assertTrue(snapshot(game)["skill_ready"])
        game.sync({"ability": True})
        state = snapshot(game)
        # After the reveal, the turn changes: verify the private map directly.
        self.assertEqual(state["turn"], 6)
        self.assertEqual(len(board.revealed[0]), 1)
        self.assertEqual(len(board.revealed[1]), 0)
        self.assertTrue(next(iter(board.revealed[0])) in board.traps)

    def test_turn_thirty_draw(self):
        game = self.make_game()
        board, clock, rules = game.mode.board, game.mode.clock, game.mode.rules
        clock.turn = 30
        rules._end_action(board, clock)
        self.assertEqual(snapshot(game)["phase"], "finished")
        self.assertEqual(snapshot(game)["result_reason"], "turn_limit")
        self.assertIsNone(snapshot(game)["winner"])

    def test_each_character_is_selectable(self):
        for name in CHARACTERS:
            with self.subTest(character=name):
                game = self.make_game((name, "gimyo"))
                self.assertEqual(snapshot(game)["characters"][0], name)


if __name__ == "__main__":
    unittest.main()
