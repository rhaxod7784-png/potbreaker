"""FLOOR BREAKER: reusable board, turn clock and rules components.

Two players each choose one CBZP chess-piece character and control five pieces.
This mode is deliberately *local two-player* until an authoritative online
matchmaking/session backend is available; it must not pretend to find opponents.
"""
import json
import random

try:
    from .game_components import GameComponent, ComponentAssemblyMode
except ImportError:
    if "GameComponent" not in globals() or "ComponentAssemblyMode" not in globals():
        raise

CHARACTERS = ("gimyo", "keuda", "gam")
TRAP_TYPES = ("pit", "retreat", "jump")
FLOOR_COLS, FLOOR_ROWS = 10, 20


class FloorBoardModule(GameComponent):
    """Parametric grid positions and hidden hazards; no UI concerns."""

    def __init__(self, seed=None, cols=FLOOR_COLS, rows=FLOOR_ROWS, name="floor_board"):
        super().__init__(name)
        if cols != 10 or rows != 20:
            raise ValueError("Floor Breaker currently requires the confirmed 10x20 board")
        self.seed, self.cols, self.rows = seed, cols, rows
        self.reset({})

    def reset(self, context):
        self.rng = random.Random(self.seed)
        self.pieces = []
        self.traps = {}
        self.used = set()
        self.eroded = set()
        self.revealed = [set(), set()]
        self.erode_count = [0, 0]
        for team, base in ((0, 17), (1, 0)):
            squares = self.rng.sample([(x, y) for y in range(base, base + 3)
                                       for x in range(self.cols)], 5)
            for number, (x, y) in enumerate(squares):
                self.pieces.append({"id": team * 5 + number, "team": team,
                                    "x": x, "y": y, "last_skill": None})
        middle = self.rng.sample([(x, y) for y in range(3, 17)
                                  for x in range(self.cols)], 30)
        for i, location in enumerate(middle):
            self.traps[location] = TRAP_TYPES[i // 10]

    def inside(self, pos):
        x, y = pos
        return 0 <= x < self.cols and 0 <= y < self.rows

    def blocked(self, pos):
        return not self.inside(pos) or pos[1] in self.eroded or pos in self.used

    def piece_at(self, pos):
        return next((p for p in self.pieces if (p["x"], p["y"]) == pos), None)

    def active(self, team):
        return [p for p in self.pieces if p["team"] == team]

    def remove(self, piece):
        if piece in self.pieces:
            self.pieces.remove(piece)

    def state(self):
        return {"board_cols": self.cols, "board_rows": self.rows,
                "pieces": [{"id": p["id"], "team": p["team"],
                            "x": p["x"], "y": p["y"]} for p in self.pieces],
                "spent_traps": [y * self.cols + x for x, y in sorted(self.used)],
                "eroded_rows": sorted(self.eroded)}


class FloorTurnClockModule(GameComponent):
    """Shared per-turn 10-second timer. Counts completed actions, not rounds."""

    def __init__(self, seconds=10, max_turns=30, name="floor_clock"):
        super().__init__(name)
        self.seconds = float(seconds)
        self.max_turns = int(max_turns)
        self.reset({})

    def reset(self, context):
        self.turn = 1
        self.team = 0
        self.elapsed = 0.0
        self.timeouts = [0, 0]
        self.phase = "playing"
        self.winner = None
        self.reason = ""

    def step(self, context, dt, **inputs):
        if self.phase == "playing":
            self.elapsed = min(self.seconds, self.elapsed + max(0.0, float(dt)))

    def next_turn(self, acted):
        if acted:
            self.timeouts[self.team] = 0
        else:
            self.timeouts[self.team] += 1
        self.turn += 1
        self.team = 1 - self.team
        self.elapsed = 0.0

    def finish(self, winner, reason):
        self.phase = "finished"
        self.winner, self.reason = winner, reason

    def state(self):
        return {"phase": self.phase, "turn": self.turn, "current_team": self.team,
                "remaining_ms": max(0, int((self.seconds - self.elapsed) * 1000)),
                "consecutive_timeouts": list(self.timeouts),
                "winner": self.winner, "result_reason": self.reason}


class FloorRulesModule(GameComponent):
    """Move/capture/trap/erosion rules using board and clock *instances*.

    Provisional skill interaction until playtest: first use is unlocked on global
    turn 5, then each individual piece has a 5-global-turn cooldown. A skill
    modifies one move/attack; Gam's trap reveal consumes one action. No stacking.
    """

    def __init__(self, characters=("gimyo", "keuda"), skill_interval=5, name="floor_rules"):
        super().__init__(name)
        if len(characters) != 2 or any(c not in CHARACTERS for c in characters):
            raise ValueError("Two valid character selections are required")
        self.characters = tuple(characters)
        self.skill_interval = int(skill_interval)
        self.reset({})

    def reset(self, context):
        self.selected = None
        self.skill_armed = False
        self.notice = "말 하나를 선택하세요."
        self.last_action = None

    def _refs(self, context):
        return context["floor_board"], context["floor_clock"]

    @staticmethod
    def forward(team):
        return -1 if team == 0 else 1

    def _selected_piece(self, board, clock):
        return next((p for p in board.pieces if p["id"] == self.selected
                     and p["team"] == clock.team), None)

    def skill_ready(self, piece, clock):
        if piece is None or clock.turn < self.skill_interval:
            return False
        last = piece["last_skill"]
        return last is None or clock.turn - last >= self.skill_interval

    def _move_offsets(self, team, boosted=False):
        direction = self.forward(team)
        offsets = {(0, direction), (0, 2 * direction),
                   (-1, direction), (1, direction),
                   (-2, 2 * direction), (2, 2 * direction),
                   (-1, 2 * direction), (1, 2 * direction)}
        if boosted:
            # Maximum travel distance is doubled, including mixed vectors.
            offsets |= {(dx, dy * direction) for dy in (3, 4)
                        for dx in range(-dy, dy + 1)}
        return offsets

    def _attack_offsets(self, team, boosted=False):
        direction = self.forward(team)
        offsets = {(0, direction), (-1, direction), (1, direction),
                   (-1, 0), (1, 0)}
        if boosted:
            offsets |= {(0, 2 * direction), (-2, 2 * direction),
                        (2, 2 * direction), (-2, 0), (2, 0)}
        return offsets

    def legal_targets(self, board, clock, piece):
        if piece is None or clock.phase != "playing":
            return {}
        origin = (piece["x"], piece["y"])
        char = self.characters[clock.team]
        ready = self.skill_armed and self.skill_ready(piece, clock)
        boosted_move = ready and char == "gimyo"
        boosted_attack = ready and char == "keuda"
        targets = {}
        for dx, dy in self._move_offsets(clock.team, boosted_move):
            target = (origin[0] + dx, origin[1] + dy)
            if board.blocked(target) or board.piece_at(target):
                continue
            targets[target] = "move"
        for dx, dy in self._attack_offsets(clock.team, boosted_attack):
            target = (origin[0] + dx, origin[1] + dy)
            other = board.piece_at(target)
            if board.blocked(target) or not other or other["team"] == clock.team:
                continue
            # Ranged Keuda attack cannot pass through another piece.
            if max(abs(dx), abs(dy)) == 2:
                midpoint = (origin[0] + dx // 2, origin[1] + dy // 2)
                if board.blocked(midpoint) or board.piece_at(midpoint):
                    continue
            targets[target] = "attack"
        return targets

    def _land(self, board, clock, piece, pos, forced=False):
        """Resolve repeated trap effects; each trap can trigger only once."""
        for _ in range(32):
            if board.blocked(pos) or board.piece_at(pos):
                board.remove(piece)
                return
            piece["x"], piece["y"] = pos
            trap = board.traps.get(pos)
            if not trap:
                return
            board.used.add(pos)
            if trap == "pit" or (forced and trap == "retreat"):
                board.remove(piece)
                return
            delta = 3 * self.forward(piece["team"]) * (1 if trap == "jump" else -1)
            pos = (pos[0], pos[1] + delta)
            forced = False
        # Prevent an accidental unbounded chain if the trap design changes.
        board.remove(piece)

    def _erode(self, board, clock, acting_team):
        row = (19 - board.erode_count[acting_team] if acting_team == 0
               else board.erode_count[acting_team])
        board.erode_count[acting_team] += 1
        if row < 0 or row >= board.rows:
            return
        board.eroded.add(row)
        displaced = [p for p in list(board.pieces) if p["y"] == row]
        for piece in displaced:
            target = (piece["x"], row + self.forward(piece["team"]))
            self._land(board, clock, piece, target, forced=True)

    def _result(self, board, clock):
        # Reaching the farthest opponent row wins immediately.
        finishers = [p["team"] for p in board.pieces
                     if p["y"] == (0 if p["team"] == 0 else 19)]
        if finishers:
            clock.finish(finishers[0], "opponent_end")
            return
        remaining = [len(board.active(0)), len(board.active(1))]
        if not remaining[0] or not remaining[1]:
            winner = 0 if remaining[0] else 1 if remaining[1] else None
            clock.finish(winner, "elimination" if winner is not None else "draw")
        elif clock.turn >= clock.max_turns:
            clock.finish(None, "turn_limit")

    def _end_action(self, board, clock, acted=True):
        actor = clock.team
        if not acted and clock.timeouts[actor] + 1 >= 3:
            clock.finish(1 - actor, "three_consecutive_timeouts")
            return
        if clock.turn >= 11:
            self._erode(board, clock, actor)
        self._result(board, clock)
        if clock.phase == "playing":
            clock.next_turn(acted)
        self.selected = None
        self.skill_armed = False

    def step(self, context, dt, **inputs):
        board, clock = self._refs(context)
        if clock.phase == "playing" and clock.elapsed >= clock.seconds:
            self.notice = "시간 초과: 행동 없이 턴을 종료합니다."
            self._end_action(board, clock, acted=False)

    def tap(self, context, index):
        board, clock = self._refs(context)
        if clock.phase != "playing" or type(index) is not int or not 0 <= index < board.cols * board.rows:
            return False
        x, y = index % board.cols, index // board.cols
        piece = board.piece_at((x, y))
        if piece and piece["team"] == clock.team:
            self.selected = piece["id"]
            self.skill_armed = False
            self.notice = "이동 위치를 선택하거나 특수 기능을 사용하세요."
            return True
        selected = self._selected_piece(board, clock)
        if selected is None:
            return False
        kind = self.legal_targets(board, clock, selected).get((x, y))
        if kind is None:
            self.notice = "선택한 칸으로는 이동하거나 공격할 수 없습니다."
            return False
        if kind == "attack":
            board.remove(piece)
            # Entering the enemy's square constitutes the attack.
            selected["x"], selected["y"] = x, y
        else:
            self._land(board, clock, selected, (x, y))
        if self.skill_armed:
            selected["last_skill"] = clock.turn
        self.notice = "공격 성공." if kind == "attack" else "이동 완료."
        self.last_action = {"team": clock.team, "target": index, "kind": kind}
        self._end_action(board, clock)
        return True

    def sync(self, context, payload):
        board, clock = self._refs(context)
        if not isinstance(payload, dict) or not payload.get("ability"):
            return
        selected = self._selected_piece(board, clock)
        if not self.skill_ready(selected, clock) or clock.phase != "playing":
            self.notice = "아직 특수 기능을 사용할 수 없습니다."
            return
        character = self.characters[clock.team]
        if character == "gam":
            remaining = [pos for pos in board.traps
                         if pos not in board.used and pos[1] not in board.eroded
                         and pos not in board.revealed[clock.team]]
            if remaining:
                chosen = board.rng.choice(remaining)
                board.revealed[clock.team].add(chosen)
                selected["last_skill"] = clock.turn
                self.notice = "감 과장이 남아 있는 함정 한 곳을 확인했습니다."
                self._end_action(board, clock)
            else:
                self.notice = "확인할 함정이 남아 있지 않습니다."
        else:
            self.skill_armed = not self.skill_armed
            self.notice = "특수 기능이 다음 행동에 적용됩니다." if self.skill_armed else "특수 기능 취소."

    def state(self):
        # Context is injected by the subclass facade for state serialization.
        board, clock = self.board, self.clock
        piece = self._selected_piece(board, clock)
        targets = self.legal_targets(board, clock, piece)
        return {"characters": list(self.characters), "selected_piece": self.selected,
                "skill_armed": self.skill_armed,
                "skill_ready": self.skill_ready(piece, clock),
                "skill_interval": self.skill_interval,
                "targets": [{"index": y * board.cols + x, "kind": kind}
                            for (x, y), kind in sorted(targets.items())],
                "revealed_traps": [{"index": y * board.cols + x, "type": board.traps[(x, y)]}
                                   for x, y in sorted(board.revealed[clock.team])
                                   if (x, y) not in board.used],
                "notice": self.notice, "last_action": self.last_action}


class FloorMode(ComponentAssemblyMode):
    """Theme 3 using the same instance-based lifecycle as the Ginkgo mode."""

    def __init__(self, seed=None, characters=("gimyo", "keuda"), skill_interval=5):
        self.board = FloorBoardModule(seed)
        self.clock = FloorTurnClockModule(seconds=10, max_turns=30)
        self.rules = FloorRulesModule(characters, skill_interval)
        self.rules.board, self.rules.clock = self.board, self.clock
        super().__init__([self.board, self.clock, self.rules], mode_name="floor")
