"""Composable Ginkgo features built from reusable game component instances."""
import random

try:
    from .game_components import GameComponent, ComponentAssemblyMode
except ImportError:
    # The Worker builder concatenates these modules into one Pyodide namespace.
    if "GameComponent" not in globals() or "ComponentAssemblyMode" not in globals():
        raise


class RoundTimerModule(GameComponent):
    """Reusable round clock with difficulty-driven beat intervals."""

    INTERVALS = {"normal": 3.0, "hard": 2.0, "very_hard": 1.0}

    def __init__(self, difficulty="normal", duration=60.0, name="round_timer"):
        super().__init__(name)
        self.difficulty = difficulty if difficulty in self.INTERVALS else "normal"
        self.interval = self.INTERVALS[self.difficulty]
        self.duration = float(duration)
        self.reset({})

    def reset(self, context):
        self.elapsed = 0.0
        self.tick_count = 0
        self.phase = "playing"

    def step(self, context, dt, **inputs):
        if self.phase != "playing":
            return
        self.elapsed = min(self.duration, self.elapsed + max(0.0, float(dt)))
        self.tick_count = int(self.elapsed / self.interval)
        if self.elapsed >= self.duration:
            self.phase = "finished"

    def sync(self, context, payload):
        remaining = max(0, min(int(self.duration * 1000), int(payload.get("remaining_ms", self.duration * 1000))))
        self.elapsed = self.duration - remaining / 1000.0
        self.tick_count = int(self.elapsed / self.interval)
        self.phase = "finished" if payload.get("done") or remaining <= 0 else "playing"

    def state(self):
        remaining = max(0, int((self.duration - self.elapsed) * 1000))
        return {"phase": self.phase, "difficulty": self.difficulty,
                "elapsed_ms": int(self.elapsed * 1000), "remaining_ms": remaining}


class GinkgoBoardModule(GameComponent):
    """Owns the 13 by 7 tree board and its female/male fruit cycle."""

    COLS = 13
    ROWS = 7
    TOTAL = COLS * ROWS

    def __init__(self, seed=None, name="board"):
        super().__init__(name)
        self.seed = seed
        self.reset({})

    def _new_sex(self):
        return 1 if self.rng.random() < 0.5 else 0

    def reset(self, context):
        self.rng = random.Random(self.seed)
        self.last_tick = 0
        self.cells = []
        for _ in range(self.TOTAL):
            phase = self.rng.randrange(4)
            sex = 1 if phase >= 2 else self._new_sex()
            self.cells.append({"phase": phase, "sex": sex})

    def step(self, context, dt, **inputs):
        timer = context.get("round_timer")
        if timer is None:
            return
        while self.last_tick < timer.tick_count:
            self.last_tick += 1
            self._cycle()

    def _cycle(self):
        for cell in self.cells:
            if cell["phase"] == 0:
                cell["phase"] = 1
            elif cell["phase"] == 1:
                if cell["sex"] == 1:
                    cell["phase"] = 2
                else:
                    cell["phase"] = 0
                    cell["sex"] = self._new_sex()
            elif cell["phase"] == 2:
                cell["phase"] = 3
            else:
                cell["phase"] = 0
                cell["sex"] = self._new_sex()

    def clear(self, index):
        cell = self.cells[index]
        cell["phase"] = 0
        cell["sex"] = self._new_sex()

    def sync(self, context, payload):
        phases = payload.get("cells")
        if isinstance(phases, list) and len(phases) == self.TOTAL:
            for cell, phase in zip(self.cells, phases):
                if isinstance(phase, int) and 0 <= phase <= 3:
                    cell["phase"] = phase
            timer = context.get("round_timer")
            self.last_tick = timer.tick_count if timer else self.last_tick

    def state(self):
        return {"cells": [cell["phase"] for cell in self.cells],
                "board_rows": self.ROWS, "board_cols": self.COLS}


class ComboScoringModule(GameComponent):
    """Reusable combo score feature; a miss clears the streak, not earned points."""

    def __init__(self, name="scoring"):
        super().__init__(name)
        self.reset({})

    def reset(self, context):
        self.score = 0
        self.combo = 0
        self.max_combo = 0

    def success(self):
        self.combo += 1
        self.score += self.combo
        self.max_combo = max(self.max_combo, self.combo)

    def miss(self):
        self.combo = 0

    def sync(self, context, payload):
        self.score = int(payload.get("score", self.score))
        self.combo = int(payload.get("combo", self.combo))
        self.max_combo = int(payload.get("max_combo", self.max_combo))

    def state(self):
        return {"score": self.score, "combo": self.combo, "max_combo": self.max_combo}


class InputLockModule(GameComponent):
    """Reusable timed input lock for hazards and temporary controls."""

    def __init__(self, duration=0.5, name="input_lock"):
        super().__init__(name)
        self.duration = float(duration)
        self.reset({})

    def reset(self, context):
        self.lock_until = 0.0
        self.elapsed = 0.0

    def step(self, context, dt, **inputs):
        timer = context.get("round_timer")
        if timer is not None:
            self.elapsed = timer.elapsed

    def locked(self, elapsed):
        return elapsed < self.lock_until

    def apply(self, elapsed, duration=None):
        self.lock_until = max(self.lock_until, elapsed + (self.duration if duration is None else float(duration)))

    def sync(self, context, payload):
        elapsed = context.get("round_timer").elapsed if context.get("round_timer") else 0.0
        self.elapsed = elapsed
        remaining = max(0, int(payload.get("locked_until", 0)) - int(payload.get("now_ms", 0)))
        self.lock_until = elapsed + remaining / 1000.0

    def state(self):
        return {"locked": self.elapsed < self.lock_until}


class GinkgoTapRulesModule(GameComponent):
    """Ginkgo-only tap rule composed from board, score, timer, and lock instances."""

    def __init__(self, name="tap_rules"):
        super().__init__(name)

    def tap(self, context, index):
        timer = context["round_timer"]
        board = context["board"]
        scoring = context["scoring"]
        input_lock = context["input_lock"]
        if timer.phase != "playing" or timer.elapsed >= timer.duration:
            return False
        if not isinstance(index, int) or index < 0 or index >= board.TOTAL:
            return False
        if input_lock.locked(timer.elapsed):
            return False
        cell = board.cells[index]
        if cell["phase"] == 2:
            scoring.success()
            board.clear(index)
        else:
            scoring.miss()
            if cell["phase"] == 3:
                input_lock.apply(timer.elapsed)
        return True

    def state(self):
        return {}


class GinkgoMode(ComponentAssemblyMode):
    """Theme-two mode assembled from independently configurable feature instances."""

    INTERVALS = RoundTimerModule.INTERVALS
    COLS = GinkgoBoardModule.COLS
    ROWS = GinkgoBoardModule.ROWS
    TOTAL = GinkgoBoardModule.TOTAL

    def __init__(self, seed=None, difficulty="normal"):
        components = [
            RoundTimerModule(difficulty=difficulty),
            GinkgoBoardModule(seed=seed),
            ComboScoringModule(),
            InputLockModule(duration=0.5),
            GinkgoTapRulesModule(),
        ]
        super().__init__(components, mode_name="ginkgo")

    @property
    def interval(self):
        return self.context["round_timer"].interval

    @property
    def cells(self):
        return self.context["board"].cells

    @property
    def elapsed(self):
        return self.context["round_timer"].elapsed

    @property
    def phase(self):
        return self.context["round_timer"].phase

    @property
    def score(self):
        return self.context["scoring"].score

    @property
    def combo(self):
        return self.context["scoring"].combo

    @property
    def max_combo(self):
        return self.context["scoring"].max_combo

    @property
    def lock_until(self):
        return self.context["input_lock"].lock_until
