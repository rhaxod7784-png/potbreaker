"""Game mode modules and the shared Pyodide game engine.

PotBreaker remains the original rules module. GinkgoMode adds the theme-two
rules behind the same step/state interface; GameEngine selects a mode from
parameters so browser screens can reuse one Python runtime and engine entry.
"""
import json
import random


class GinkgoMode:
    COLS = 13
    ROWS = 7
    TOTAL = COLS * ROWS
    INTERVALS = {"normal": 1.0, "hard": 0.7, "very_hard": 0.5}

    def __init__(self, seed=None, difficulty="normal"):
        self.difficulty = difficulty if difficulty in self.INTERVALS else "normal"
        self.interval = self.INTERVALS[self.difficulty]
        self.rng = random.Random(seed)
        self.reset()

    def _new_sex(self):
        return 1 if self.rng.random() < 0.5 else 0

    def reset(self):
        self.phase = "playing"
        self.elapsed = 0.0
        self.tick_count = 0
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.lock_until = 0.0
        self.cells = []
        for _ in range(self.TOTAL):
            phase = self.rng.randrange(4)
            sex = 1 if phase >= 2 else self._new_sex()
            self.cells.append({"phase": phase, "sex": sex})
        return self.state()

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

    def step(self, dt, mx=0, my=0, jump=False, fire=False, aimx=0, aimy=0):
        if self.phase != "playing":
            return self.state()
        dt = max(0.0, float(dt))
        self.elapsed = min(60.0, self.elapsed + dt)
        target_tick = min(120, int(self.elapsed / self.interval))
        while self.tick_count < target_tick:
            self.tick_count += 1
            self._cycle()
        if self.elapsed >= 60.0:
            self.phase = "finished"
        return self.state()

    def tap(self, index):
        if self.phase != "playing" or self.elapsed >= 60.0:
            return False
        if not isinstance(index, int) or index < 0 or index >= self.TOTAL:
            return False
        if self.elapsed < self.lock_until:
            return False
        cell = self.cells[index]
        if cell["phase"] == 2:
            self.combo += 1
            self.score += self.combo
            self.max_combo = max(self.max_combo, self.combo)
            cell["phase"] = 0
            cell["sex"] = self._new_sex()
        else:
            self.combo = 0
            if cell["phase"] == 3:
                self.lock_until = self.elapsed + 0.5
        return True

    def sync(self, payload):
        """Apply a server snapshot while keeping mode state in this engine."""
        data = json.loads(payload) if isinstance(payload, str) else payload
        phases = data.get("cells")
        if isinstance(phases, list) and len(phases) == self.TOTAL:
            for cell, phase in zip(self.cells, phases):
                if isinstance(phase, int) and 0 <= phase <= 3:
                    cell["phase"] = phase
        self.score = int(data.get("score", self.score))
        self.combo = int(data.get("combo", self.combo))
        self.max_combo = int(data.get("max_combo", self.max_combo))
        remaining = max(0, min(60000, int(data.get("remaining_ms", 60000))))
        self.elapsed = 60.0 - remaining / 1000.0
        self.tick_count = min(120, int(self.elapsed / self.interval))
        lock_remaining_ms = max(0, int(data.get("locked_until", 0)) - int(data.get("now_ms", 0)))\n        self.lock_until = self.elapsed + lock_remaining_ms / 1000.0
        self.phase = "finished" if data.get("done") or remaining <= 0 else "playing"
        return self.state()

    def state(self):
        remaining = max(0, 60000 - int(self.elapsed * 1000))
        return json.dumps({
            "mode": "ginkgo",
            "phase": self.phase,
            "difficulty": self.difficulty,
            "elapsed_ms": int(self.elapsed * 1000),
            "remaining_ms": remaining,
            "score": self.score,
            "combo": self.combo,
            "max_combo": self.max_combo,
            "locked": self.elapsed < self.lock_until,
            "cells": [cell["phase"] for cell in self.cells],
        })


class GameEngine:
    """Shared browser-facing engine API; game rules live in mode classes."""

    MODES = {"potbreaker", "ginkgo"}

    def __init__(self, mode="potbreaker", seed=None, difficulty="normal"):
        if mode not in self.MODES:
            raise ValueError("unknown game mode")
        self.mode_name = mode
        if mode == "ginkgo":
            self.mode = GinkgoMode(seed=seed, difficulty=difficulty)
        else:
            self.mode = PotBreaker(seed=seed, difficulty=difficulty)

    def reset(self):
        return self.mode.reset()

    def step(self, dt, mx=0, my=0, jump=False, fire=False, aimx=0, aimy=0):
        return self.mode.step(dt, mx, my, jump, fire, aimx, aimy)

    def tap(self, index):
        if self.mode_name != "ginkgo":
            raise ValueError("tap input is only supported by the ginkgo mode")
        return self.mode.tap(index)

    def sync(self, payload):
        if self.mode_name != "ginkgo":
            raise ValueError("sync is only supported by the ginkgo mode")
        return self.mode.sync(payload)

    def state(self):
        return self.mode.state()

    def destroy(self):
        return None
