"""Execution checks for the exact v188 runtime extracted from Cloudflare."""
import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODE = (ROOT / "snapshots/v188/game.py").read_text(encoding="utf-8")
ast.parse(CODE)
namespace = {"__name__": "potbreaker_v111_qa"}
exec(compile(CODE, "snapshots/v188/game.py", "exec"), namespace)
PotBreaker = namespace["PotBreaker"]

for difficulty in ("normal", "hard", "very_hard"):
    game = PotBreaker(seed=7, difficulty=difficulty)
    assert game.player_pot_cap == 3, (difficulty, game.player_pot_cap)
    assert json.loads(game.state())["phase"] == "playing"
    game.step(.04)
    game.ammo = 3
    game.player = [2, 2]
    game.boss = [14, 2]
    game.walls = set()
    game.moving_walls = set()
    game.boss_move_cd = 999
    game.partition_timer = 999
    game.crow_spawn_timer = 999
    before = game.boss_hp
    game.step(.04, charging=True)
    assert json.loads(game.state())["charge_count"] == 3, difficulty
    game.step(.04, charging=False)
    charged = [p for p in game.projectiles if p.get("charged")]
    assert len(charged) == 1, charged
    assert charged[0]["power"] == 3
    assert game.boss_hp == before, "Do not instantly hit the boss"
    assert game.ammo == 0
    # Consecutive obstacles: third one must stop the charged projectile.
    game.reset()
    game.player = [2, 2]
    game.boss = [14, 2]
    game.walls = {(4, 2), (5, 2), (6, 2)}
    game.moving_walls = set()
    game.boss_move_cd = 999
    game.partition_timer = 999
    game.crow_spawn_timer = 999
    game.ammo = 3
    game.step(.04, charging=True)
    game.step(.04, charging=False)
    for i in range(50):
        if game.phase != "playing":
            break
        game.step(.04)
    assert not any(p.get("charged") for p in game.projectiles)
    assert game.boss_hp == game.boss_hp_cap
    print("PASS", difficulty)
print("PASS: v1.1.1 boot and charge regression")
