"""POT BREAKER RE v1.0.91 \u2014 single-player deterministic Python game rules.
UI draws state with Canvas; Cloudflare only serves static assets / Python source.
"""
import json
import math
import random
from collections import deque

WIDTH, HEIGHT = 19, 11
DIRECTIONS = ((1, 0), (-1, 0), (0, 1), (0, -1))
# QA-only tunables; dash pad creation/expiry were not specified by the user.
PAD_SPAWN_SECONDS = 1.15
PAD_LIFETIME_SECONDS = 8.0
PAD_LIMIT = 8
PARTITION_MOVE_SECONDS = 1.7
FIELD_POT_COUNT = 4  # Four ammo pots plus one healing pot.
SPECIAL_POT_EFFECTS = ('heal',)
CROW_FIRST_APPEAR_SECONDS = 2.5
CROW_RESPAWN_SECONDS = 14.0
VISION_RANGE = None    # Boss can locate both player and pickup positions across entire map.
PLAYER_DASH_COOLDOWN = 3.0
BOSS_DASH_COOLDOWN = 5.0
PLAYER_MOVE_INTERVAL = 0.18  # One tile about every 0.18 seconds.
PLAYER_DASH_MOVE_INTERVAL = 0.09
PLAYER_HP = 3
PLAYER_POT_CAP = 3
BOSS_POT_CAP = 5
HIT_INVULNERABILITY = 0.72
CROW_FLIGHT_SECONDS = 4.2
CROW_DROP_SECONDS = 1.2  # Double the previous 0.6s interval.
MYSTERY_POTS_PER_DROP = 2
MYSTERY_POT_LIFETIME = 14.0
MYSTERY_POT_EFFECTS = ('heal', 'damage', 'refill', 'field_reset')


def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


class PotBreaker:
    def __init__(self, seed=None, difficulty='normal', components=None):
        self.rng = random.Random(seed)
        if 'POTBREAKER_MODULES' not in globals():
            from . import game_modules as _game_modules
            globals().update({
                'FieldModule': _game_modules.FieldModule,
                'CombatModule': _game_modules.CombatModule,
                'ActorModule': _game_modules.ActorModule,
                'POTBREAKER_MODULES': _game_modules.POTBREAKER_MODULES,
                'POTBREAKER_MODULE_GROUPS': _game_modules.POTBREAKER_MODULE_GROUPS,
                'FEATURE_METHODS': _game_modules.FEATURE_METHODS,
            })
        self.difficulty = difficulty if difficulty in ('normal', 'hard', 'very_hard') else 'normal'
        self.player_pot_cap = 3
        self.boss_hp_cap = {'normal': 5, 'hard': 7, 'very_hard': 10}[self.difficulty]
        legacy_classes = {
            'field': globals()['FieldModule'],
            'combat': globals()['CombatModule'],
            'actor': globals()['ActorModule'],
        }
        feature_classes_by_name = POTBREAKER_MODULES
        components = components or {}
        if not isinstance(components, dict) or not set(components).issubset(set(feature_classes_by_name) | set(legacy_classes)):
            available = ', '.join((*feature_classes_by_name, *legacy_classes))
            raise ValueError(f"PotBreaker components must be module instances: {available}")
        self._feature_modules = {}
        covered = set()
        for group_name, module_class in legacy_classes.items():
            if group_name not in components:
                continue
            keys = POTBREAKER_MODULE_GROUPS[group_name]
            if covered.intersection(keys) or any(key in components for key in keys):
                raise ValueError(f"Do not mix the legacy {group_name} module with its fine-grained modules")
            module = components[group_name]
            if not isinstance(module, module_class):
                raise TypeError(f"{group_name} must be an instance of {module_class.__name__}")
            module.bind(self)
            self._feature_modules.update({key: module for key in keys})
            covered.update(keys)
        for name, module_class in feature_classes_by_name.items():
            if name in covered:
                continue
            module = components[name] if name in components else module_class(self)
            if not isinstance(module, module_class):
                raise TypeError(f"{name} must be an instance of {module_class.__name__}")
            module.bind(self)
            self._feature_modules[name] = module
        self.reset()

    def __getattr__(self, name):
        module_name = FEATURE_METHODS.get(name)
        if module_name is not None:
            modules = object.__getattribute__(self, '_feature_modules')
            return getattr(modules[module_name], name)
        raise AttributeError(name)

    def reset(self):
        self.phase, self.clock = 'playing', 0.0
        # Keep the player clear of the touch controls at the lower screen corners.
        self.player = list(self.rng.choice([(3, 3), (3, HEIGHT - 4),
                                            (WIDTH - 4, 3), (WIDTH - 4, HEIGHT - 4)]))
        self.boss = [WIDTH // 2, HEIGHT // 2]
        self.face, self.boss_face = [1, 0], [-1, 0]
        self.walls, self.moving_walls = set(), set()  # All partition tiles are dynamic.
        safe = {tuple(self.player), tuple(self.boss)}
        for y in range(1, HEIGHT - 1):
            for x in range(1, WIDTH - 1):
                p = (x, y)
                if p in safe or min(distance(p, self.player), distance(p, self.boss)) < 2.3:
                    continue
                r = self.rng.random()
                if r < .20:
                    self.moving_walls.add(p)
        for _ in range(180):
            if self._path_step(self.player, self.boss) != tuple(self.player):
                break
            if self.moving_walls:
                self.moving_walls.remove(self.rng.choice(tuple(self.moving_walls)))
            else:
                break
        self.ammo, self.boss_ammo, self.max_boss_ammo = 0, 0, BOSS_POT_CAP
        self.charge_cap = 3
        self.charge_active = False
        self.charge_count = 0
        self.boss_pot_cap = BOSS_POT_CAP
        self.throw_cd, self.boss_throw_cd = 0.0, 1.2
        self.player_move_cd, self.boss_move_cd = 0.0, .5
        self.projectiles, self.pots, self.special_pots = [], [], []
        self.crow_flight, self.crow_bombs, self.mystery_pots = None, [], []
        self.hit_events = []
        self.hit_seq = 0
        self.pot_break_events = []
        self.pot_break_seq = 0
        self.crow_spawn_timer = CROW_FIRST_APPEAR_SECONDS
        self.player_hp, self.boss_hp = PLAYER_HP, self.boss_hp_cap
        self.player_invuln, self.boss_invuln = 0.0, 0.0
        self.player_dash_cd, self.boss_dash_cd = 0.0, 0.0
        self.partition_timer = PARTITION_MOVE_SECONDS
        self.notice, self.notice_time = '\uB300\uC2DC \uBC84\uD2BC: 3\uCE78 \uB3CC\uC9C4 \xB7 3\uCD08 \uC7AC\uC0AC\uC6A9 \uB300\uAE30', 2.2
        self.dash_effect = None
        self.boss_target = None
        for _ in range(FIELD_POT_COUNT): self._add_pot()
        for effect in SPECIAL_POT_EFFECTS: self._add_special_pot(effect)
        
        return self.state()

    def step(self, dt, mx=0, my=0, jump=False, fire=False, aimx=0, aimy=0, charging=False):
        # Keep previous API signature for the existing Pyodide front-end.
        if self.phase != 'playing': return self.state()
        dt = min(.085, max(.01, float(dt)))
        self.clock += dt
        self.player_dash_cd=max(0.,self.player_dash_cd-dt)
        self.boss_dash_cd=max(0.,self.boss_dash_cd-dt)
        self.player_invuln=max(0.,self.player_invuln-dt)
        self.boss_invuln=max(0.,self.boss_invuln-dt)
        self.throw_cd = max(0., self.throw_cd-dt)
        self.boss_throw_cd = max(0., self.boss_throw_cd-dt)
        self.player_move_cd -= dt
        self.boss_move_cd -= dt
        self.notice_time = max(0., self.notice_time-dt)
        self._move_partitions(dt)
        self._update_crow(dt)
        if self.dash_effect:
            self.dash_effect['age'] += dt
            if self.dash_effect['age'] > .35: self.dash_effect = None
        mx, my = float(mx), float(my)
        input_length = math.hypot(mx, my)
        strength = min(1.0, input_length)
        if input_length > 1.0:
            mx, my = mx / input_length, my / input_length
        dx = 1 if mx > 0 else -1 if mx < 0 else 0
        dy = 1 if my > 0 else -1 if my < 0 else 0
        if dx and dy:
            if abs(mx) >= abs(my): dy = 0
            else: dx = 0
        if dx or dy: self.face = [dx, dy]
        just_dashed = False
        if jump and self.player_dash_cd <= 0:
            dash_dx, dash_dy = (dx, dy) if (dx or dy) else tuple(self.face)
            just_dashed = self._dash(self.player, dash_dx, dash_dy, False)
            if just_dashed:
                self.player_move_cd = PLAYER_DASH_MOVE_INTERVAL
        if not just_dashed:
            if strength <= .001:
                self.player_move_cd = 0.0
            elif self.player_move_cd <= 0:
                moved = self._move_player(mx, my)
                self.player_move_cd = (PLAYER_MOVE_INTERVAL if moved else PLAYER_MOVE_INTERVAL / 2) / max(strength, .25)
        if self.phase != 'playing': return self.state()
        if charging:
            self._begin_charge()
        elif self.charge_active:
            self._release_charge()
        elif fire and self.throw_cd <= 0 and self.ammo:
            self._fire(self.player, self._aim(self.player, self.boss))
            self.throw_cd = .38
        if self.boss_move_cd <= 0:
            self._move_boss()
            self.boss_move_cd = .225
        if self.phase != 'playing': return self.state()
        self._pickups()
        if self.charge_active:
            self.charge_count = min(self.ammo, self.charge_cap)
        self._pick_special_pots()
        self._pick_mystery_pots()
        if self.phase != 'playing': return self.state()
        # Boss projectile decision depends on ammo but no field-of-view angle.
        if self.boss_throw_cd <= 0 and self.boss_ammo > 0 and distance(self.player, self.boss) < 7.3:
            aim = self._aim(self.boss, self.player)
            base_angle = math.atan2(aim[1], aim[0])
            # Paired projectiles converge around the swept automatic aim ray.
            for offset in (-.105, .105) if self.boss_ammo >= 2 else (0,):
                angle = base_angle + offset
                self._fire(self.boss, [math.cos(angle), math.sin(angle)], npc=True)
            self.boss_throw_cd = 1.1
        self._advance_projectiles(dt)
        self._maintain_field_pots()
        return self.state()

    def state(self):
        return json.dumps({'phase': self.phase, 'player': self.player, 'boss': self.boss,
                           'face': self.face, 'boss_face': self.boss_face,
                           'walls': sorted(self.walls), 'moving_walls': sorted(self.moving_walls),
                           'pots': self.pots, 'projectiles': self.projectiles,
                           'crow_flight': self.crow_flight, 'crow_bombs': self.crow_bombs,
                           'mystery_pots': self.mystery_pots, 'special_pots': self.special_pots,
                           'player_hp': self.player_hp, 'boss_hp': self.boss_hp,
                           'player_dash_cd': round(self.player_dash_cd,2), 'boss_dash_cd': round(self.boss_dash_cd,2),
                           'ammo': self.ammo, 'ammo_cap': self.player_pot_cap, 'boss_ammo': self.boss_ammo,
                           'charging': self.charge_active, 'charge_count': self.charge_count, 'charge_cap': self.charge_cap,
                           'boss_hp_cap': self.boss_hp_cap, 'difficulty': self.difficulty,
                           'dash_effect': self.dash_effect,
                           'notice': self.notice if self.notice_time else '',
                           'clock': round(self.clock, 2), 'hits': self.hit_events,
                           'pot_breaks': self.pot_break_events}, ensure_ascii=False)

    def module_report(self):
        """Return the active feature-instance map for QA and composition diagnostics."""
        return {
            name: {
                'instance': type(module).__name__,
                'methods': sorted(method for method, owner in FEATURE_METHODS.items() if owner == name),
            }
            for name, module in self._feature_modules.items()
        }


"""Reusable field, combat, and actor components for PotBreaker."""
import math
from collections import deque

# When imported for local Python use, resolve the shared constants from the
# engine module. The Worker build concatenates these files into one namespace.
try:
    from .game import (
        WIDTH, HEIGHT, DIRECTIONS, distance, PAD_SPAWN_SECONDS, PAD_LIFETIME_SECONDS,
        PAD_LIMIT, PARTITION_MOVE_SECONDS, FIELD_POT_COUNT, SPECIAL_POT_EFFECTS,
        CROW_FIRST_APPEAR_SECONDS, CROW_RESPAWN_SECONDS, VISION_RANGE,
        PLAYER_DASH_COOLDOWN, BOSS_DASH_COOLDOWN, PLAYER_DASH_MOVE_INTERVAL,
        PLAYER_MOVE_INTERVAL, PLAYER_HP, PLAYER_POT_CAP, BOSS_POT_CAP,
        HIT_INVULNERABILITY, CROW_FLIGHT_SECONDS, CROW_DROP_SECONDS,
        MYSTERY_POTS_PER_DROP, MYSTERY_POT_LIFETIME, MYSTERY_POT_EFFECTS,
    )
except ImportError:
    # In the bundled Pyodide source, constants already exist in this module.
    pass
class _FeatureModule:
    MODULE_NAME = "feature"

    def __init__(self, game=None):
        object.__setattr__(self, "game", game)
        object.__setattr__(self, "name", self.MODULE_NAME)

    def bind(self, game):
        object.__setattr__(self, "game", game)
        return self

    def __getattr__(self, name):
        game = object.__getattribute__(self, "game")
        if game is None:
            raise AttributeError(f"{name} requires this feature to be bound to a game instance")
        return getattr(game, name)

    def __setattr__(self, name, value):
        if name == "game":
            object.__setattr__(self, name, value)
        else:
            setattr(self.game, name, value)

class MazeGeometryModule(_FeatureModule):
    MODULE_NAME = "mazegeometry"

    def _free(self, x, y):
        return 0 <= x < WIDTH and 0 <= y < HEIGHT and (x, y) not in self.walls and (x, y) not in self.moving_walls

    def _free_step(self, x, y, dx, dy):
        nx, ny = x + dx, y + dy
        if not self._free(nx, ny): return False
        if dx and dy:
            return self._free(x + dx, y) and self._free(x, y + dy)
        return True

    def _path(self, start, goal):
        start = tuple(int(math.floor(value + .5)) for value in start)
        goal = tuple(int(math.floor(value + .5)) for value in goal)
        q = deque([start]); came = {start: None}
        while q:
            x, y = q.popleft()
            if (x, y) == goal: break
            for dx, dy in DIRECTIONS:
                p = (x + dx, y + dy)
                if p not in came and self._free(*p):
                    came[p] = (x, y); q.append(p)
        if goal not in came: return []
        result = [goal]
        while came[result[-1]] is not None: result.append(came[result[-1]])
        return list(reversed(result))

    def _path_step(self, start, goal):
        path = self._path(start, goal)
        return path[1] if len(path) >= 2 else tuple(start)

class PartitionModule(_FeatureModule):
    MODULE_NAME = "partition"

    def _move_partitions(self, dt):
        self.partition_timer -= dt
        if self.partition_timer > 0: return
        self.partition_timer = PARTITION_MOVE_SECONDS
        player_cell = tuple(int(math.floor(value + .5)) for value in self.player)
        occupied = {player_cell, tuple(self.boss), *[tuple(p) for p in self.pots],
                    *[(item['x'], item['y']) for item in self.special_pots]}
        # Every partition is movable: no static decorative blocking partitions.
        # Shuffle movement order, and allow entering already-vacated cells.
        pending = list(self.moving_walls)
        self.rng.shuffle(pending)
        new_positions = set(self.moving_walls)
        for old in pending:
            dirs = list(DIRECTIONS); self.rng.shuffle(dirs)
            for dx, dy in dirs:
                target = (old[0] + dx, old[1] + dy)
                if not (1 <= target[0] < WIDTH - 1 and 1 <= target[1] < HEIGHT - 1):
                    continue
                if target in new_positions or target in occupied:
                    continue
                new_positions.remove(old)
                new_positions.add(target)
                break
        self.moving_walls = new_positions

class PotFieldModule(_FeatureModule):
    MODULE_NAME = "potfield"

    def _add_pot(self):
        if len(self.pots) >= FIELD_POT_COUNT: return
        choices = [(x, y) for y in range(HEIGHT) for x in range(WIDTH)
                   if self._free(x, y) and [x, y] not in (self.player, self.boss)
                   and [x, y] not in self.pots
                   and all((x, y) != (item['x'], item['y']) for item in self.special_pots)]
        if choices:
            self.pots.append(list(self.rng.choice(choices)))

    def _add_special_pot(self, effect):
        if any(item['effect'] == effect for item in self.special_pots): return
        choices = [(x, y) for y in range(HEIGHT) for x in range(WIDTH)
                   if self._free(x, y) and [x, y] not in (self.player, self.boss)
                   and [x, y] not in self.pots
                   and all((x, y) != (item['x'], item['y']) for item in self.special_pots)]
        if choices:
            x, y = self.rng.choice(choices)
            self.special_pots.append({'x': x, 'y': y, 'effect': effect})

    def _maintain_field_pots(self):
        # Keep four ammo pots and exactly one healing pot available.
        while len(self.pots) < FIELD_POT_COUNT:
            before = len(self.pots)
            self._add_pot()
            if len(self.pots) == before: break
        self.pots[:] = self.pots[:FIELD_POT_COUNT]
        self._add_special_pot('heal')

    def _reset_field_pots(self):
        self.pots.clear()
        self.special_pots.clear()
        self._maintain_field_pots()

    def _nearest_pot(self, who):
        # Use walkable path distance, not straight-line distance, to avoid NPC freezing at a partition.
        best = None
        bestlen = float('inf')
        targets = [list(pot) for pot in self.pots]
        targets.extend([[item['x'], item['y']] for item in self.special_pots])
        for pot in targets:
            path = self._path(who, pot)
            if not path:
                continue  # Ignore temporarily sealed-off pickups; do not stand still.
            cost = len(path)
            if cost < bestlen:
                best, bestlen = list(pot), cost
        return best

    def _drop_pot(self, x, y):
        # Relocate an existing ordinary floor pot rather than creating extra items.
        # This retains the 'thrown pot lands on the floor' feedback without inflation.
        xx, yy = max(0, min(WIDTH-1, round(x))), max(0, min(HEIGHT-1, round(y)))
        for radius in range(5):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if abs(dx) + abs(dy) != radius: continue
                    nx, ny = xx + dx, yy + dy
                    if (not self._free(nx, ny) or [nx, ny] in self.pots
                            or [nx, ny] in (self.boss, self.player)
                            or any((nx, ny) == (item['x'], item['y']) for item in self.special_pots)):
                        continue
                    if len(self.pots) >= FIELD_POT_COUNT:
                        self.pots.pop(self.rng.randrange(len(self.pots)))
                    self.pots.append([nx, ny])
                    self._maintain_field_pots()
                    return

    def _break_pot(self, x, y):
        self.pot_break_seq += 1
        self.pot_break_events.append({'id': self.pot_break_seq, 'x': round(x, 2), 'y': round(y, 2)})
        self.pot_break_events = self.pot_break_events[-8:]
        self._drop_pot(x, y)

    def _pickups(self):
        for who, cap, attr in ((self.player, self.player_pot_cap, 'ammo'), (self.boss, self.boss_pot_cap, 'boss_ammo')):
            if getattr(self, attr) >= cap: continue
            for pot in list(self.pots):
                if distance(who, pot) < .62:
                    setattr(self, attr, getattr(self, attr) + 1)
                    self.pots.remove(pot)
                    self._maintain_field_pots()  # Keep four ammo pots and one healing pot.
                    break

    def _pick_special_pots(self):
        for item in list(self.special_pots):
            for npc, who in ((False, self.player), (True, self.boss)):
                if distance(who, (item['x'], item['y'])) >= .65:
                    continue
                self.special_pots.remove(item)
                attr, cap = ('boss_hp', self.boss_hp_cap) if npc else ('player_hp', PLAYER_HP)
                if getattr(self, attr) < cap:
                    setattr(self, attr, getattr(self, attr) + 1)
                    self.notice, self.notice_time = ('\uD06C\uB2E4' if npc else '\uAE30\uBB18') + ' \uD68C\uBCF5 \uD654\uBD84! HP +1', 1.3
                else:
                    self.notice, self.notice_time = '\uD68C\uBCF5 \uD654\uBD84\uC744 \uCC3E\uC558\uC9C0\uB9CC HP\uAC00 \uAC00\uB4DD \uCC3C\uC2B5\uB2C8\uB2E4.', 1.3
                self._maintain_field_pots()
                break

class MysteryPotModule(_FeatureModule):
    MODULE_NAME = "mysterypot"

    def _pick_mystery_pots(self):
        for item in list(self.mystery_pots):
            for npc, who in ((False, self.player), (True, self.boss)):
                if distance(who, (item['x'], item['y'])) >= .65:
                    continue
                self.mystery_pots.remove(item)
                attr, cap, name = ('boss_hp', self.boss_hp_cap, '\uD06C\uB2E4') if npc else ('player_hp', PLAYER_HP, '\uAE30\uBB18')
                effect = item['effect']
                if effect == 'damage':
                    self._damage(npc, bypass_invulnerability=True)
                    self.notice, self.notice_time = f"? \uD654\uBD84 \uD3ED\uBC1C! {name} HP -1", 1.3
                elif effect == 'heal':
                    setattr(self, attr, min(cap, getattr(self, attr) + 1))
                    self.notice, self.notice_time = f"? \uD654\uBD84 \uD68C\uBCF5! {name} HP +1", 1.3
                elif effect == 'refill':
                    ammo_attr = 'boss_ammo' if npc else 'ammo'
                    ammo_cap = self.boss_pot_cap if npc else self.player_pot_cap
                    setattr(self, ammo_attr, ammo_cap)
                    self.notice, self.notice_time = f"? \uD654\uBD84 \uD480\uCDA9\uC804! {name} \uD654\uBD84 {ammo_cap}/{ammo_cap}", 1.3
                else:
                    self._reset_field_pots()
                    self.notice, self.notice_time = '? \uD544\uB4DC \uD654\uBD84 \uB9AC\uC14B!', 1.3
                break

    def _spawn_mystery_pots(self, x, y):
        cx, cy = round(x), round(y)
        for _ in range(MYSTERY_POTS_PER_DROP):
            occupied = {tuple((item['x'], item['y'])) for item in self.mystery_pots}
            occupied.update((item['x'], item['y']) for item in self.special_pots)
            candidates = [(cx + dx, cy + dy) for radius in range(3)
                          for dx in range(-radius, radius + 1)
                          for dy in range(-radius, radius + 1)
                          if abs(dx) + abs(dy) == radius]
            candidates = [(px, py) for px, py in candidates
                          if self._free(px, py) and [px, py] not in (self.player, self.boss)
                          and [px, py] not in self.pots and (px, py) not in occupied]
            if not candidates:
                continue
            px, py = self.rng.choice(candidates)
            effect = self.rng.choice(MYSTERY_POT_EFFECTS)
            self.mystery_pots.append({'x': px, 'y': py, 'effect': effect,
                                      'ttl': MYSTERY_POT_LIFETIME})

class CrowHazardModule(_FeatureModule):
    MODULE_NAME = "crowhazard"

    def _update_crow(self, dt):
        self.crow_spawn_timer -= dt
        if self.crow_spawn_timer <= 0 and self.crow_flight is None:
            self.crow_flight = {'x': 1.0, 'y': float(self.rng.randint(1, HEIGHT-2)),
                                'ttl': CROW_FLIGHT_SECONDS, 'drop': CROW_DROP_SECONDS}
            self.crow_spawn_timer = CROW_RESPAWN_SECONDS
            self.notice, self.notice_time = '\uAC10 \uACFC\uC7A5 \uCD9C\uB3D9! ? \uD654\uBD84 \uD22C\uD558!', 1.0
        for item in self.mystery_pots:
            item['ttl'] -= dt
        self.mystery_pots[:] = [item for item in self.mystery_pots if item['ttl'] > 0]
        for bomb in list(self.crow_bombs):
            bomb['ttl'] -= dt
            if bomb['ttl'] <= 0:
                self.crow_bombs.remove(bomb)
                self._spawn_mystery_pots(bomb['x'], bomb['y'])
        bird = self.crow_flight
        if bird is None: return
        bird['ttl'] -= dt
        elapsed = CROW_FLIGHT_SECONDS - bird['ttl']
        bird['x'] = min(WIDTH-1.0, 1.0 + elapsed * (WIDTH-2)/CROW_FLIGHT_SECONDS)
        bird['y'] = max(.75, min(HEIGHT-1.3, 5.0 + math.sin(elapsed*3.2)*2.3))
        bird['drop'] -= dt
        if bird['drop'] <= 0:
            bird['drop'] = CROW_DROP_SECONDS
            # Local random target around either actor makes the thrown pots visible in play.
            center = self.player if self.rng.random() < .65 else self.boss
            candidates = [(center[0]+dx, center[1]+dy) for dx in range(-3,4) for dy in range(-3,4)]
            candidates = [(x,y) for x,y in candidates if 0 <= x < WIDTH and 0 <= y < HEIGHT]
            if candidates:
                tx,ty=self.rng.choice(candidates)
                flight_time=.98
                self.crow_bombs.append({'x':tx,'y':ty,'ttl':flight_time,'duration':flight_time,
                                        'from_x':round(bird['x'],2),'from_y':round(bird['y'],2)})
        if bird['ttl'] <= 0: self.crow_flight=None

class DamageModule(_FeatureModule):
    MODULE_NAME = "damage"

    def _damage(self, npc, bypass_invulnerability=False):
        if self.phase != 'playing': return False
        if npc:
            if self.boss_invuln > 0 and not bypass_invulnerability: return False
            self.boss_hp=max(0,self.boss_hp-1)
            self.boss_invuln=HIT_INVULNERABILITY
            pos=self.boss
            if self.boss_hp == 0: self.phase='win'
        else:
            if self.player_invuln > 0 and not bypass_invulnerability: return False
            self.player_hp=max(0,self.player_hp-1)
            self.player_invuln=HIT_INVULNERABILITY
            pos=self.player
            if self.player_hp == 0: self.phase='lose'
        self.hit_seq += 1
        self.hit_events.append({'id':self.hit_seq,'x':pos[0],'y':pos[1], 'target':'boss' if npc else 'player'})
        self.hit_events=self.hit_events[-5:]
        return True

    def _dash(self, who, dx, dy, npc):
        if not (dx or dy): return False
        attr = 'boss_dash_cd' if npc else 'player_dash_cd'
        if getattr(self,attr)>0: return False
        start=who[:] if npc else [int(math.floor(value + .5)) for value in who]; length=5 if npc else 3
        candidate=None
        for amount in range(length,0,-1):
            tx,ty=start[0]+dx*amount,start[1]+dy*amount
            if all(self._free_step(start[0]+dx*(step-1),start[1]+dy*(step-1),dx,dy)
                   for step in range(1,amount+1)):
                candidate=[tx,ty];break
        if candidate is None:return False
        # Collision during dash costs one player HP, respecting damage invulnerability.
        other=self.player if npc else self.boss
        other_cell=[int(math.floor(value + .5)) for value in other]
        crosses=(dx and other_cell[1]==start[1] and (other_cell[0]-start[0])*dx>0 and abs(other_cell[0]-start[0])<=abs(candidate[0]-start[0])) or (dy and other_cell[0]==start[0] and (other_cell[1]-start[1])*dy>0 and abs(other_cell[1]-start[1])<=abs(candidate[1]-start[1]))
        if crosses: self._damage(False)
        who[:]=candidate
        setattr(self,attr,BOSS_DASH_COOLDOWN if npc else PLAYER_DASH_COOLDOWN)
        self.dash_effect={'from':start,'to':candidate[:],'npc':npc,'age':0.0}
        self._contact()
        return True

    def _contact(self):
        if distance(self.player, self.boss) < .72: self._damage(False)

    def _aim(self, src, target):
        dx, dy = target[0] - src[0], target[1] - src[1]
        length = math.hypot(dx, dy)
        if length < 1e-9: return [1.0, 0.0]
        return [dx / length, dy / length]

class ProjectileModule(_FeatureModule):
    MODULE_NAME = "projectile"

    MAX_CHARGE_PENETRATION = 2

    def _begin_charge(self):
        """Charging is stored in the projectile feature, not a second engine."""
        if self.phase != 'playing':
            return
        self.charge_active = True
        self.charge_count = min(self.ammo, self.charge_cap)

    def _release_charge(self):
        """A charged throw auto-aims but must physically travel to hit."""
        if not self.charge_active:
            return 0
        amount = min(self.ammo, self.charge_cap)
        self.charge_active, self.charge_count = False, 0
        if amount == 0 or self.phase != 'playing':
            return 0
        self.ammo -= amount
        vec = self._aim(self.player, self.boss)
        self.projectiles.append({
            'x': float(self.player[0]), 'y': float(self.player[1]),
            'dx': vec[0], 'dy': vec[1],
            'range': math.hypot(WIDTH, HEIGHT) + 2.0,
            'boss': False, 'charged': True,
            'power': amount, 'penetrated': 0, 'last_wall': None,
        })
        self.throw_cd = .38
        return amount

    def _advance_charge_projectiles(self, dt):
        walls = self.walls | self.moving_walls
        for shot in list(self.projectiles):
            if not shot.get('charged'):
                continue
            travel = min(max(0., dt) * 9.4, shot['range'])
            if travel <= 0:
                self.projectiles.remove(shot)
                continue
            x0, y0 = shot['x'], shot['y']
            parts = max(1, math.ceil(travel * 16))
            blocked = False
            for index in range(1, parts + 1):
                distance_travelled = travel * index / parts
                x = x0 + shot['dx'] * distance_travelled
                y = y0 + shot['dy'] * distance_travelled
                if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
                    self.projectiles.remove(shot)
                    blocked = True
                    break
                cell = (round(x), round(y))
                if cell in walls:
                    if shot['last_wall'] != cell:
                        if shot['penetrated'] >= self.MAX_CHARGE_PENETRATION:
                            self._break_pot(x, y)
                            self.projectiles.remove(shot)
                            blocked = True
                            break
                        shot['penetrated'] += 1
                    shot['last_wall'] = cell
                else:
                    shot['last_wall'] = None
                if distance((x, y), self.boss) < .72:
                    for _ in range(shot['power']):
                        if not self._damage(True, bypass_invulnerability=True):
                            break
                    self._break_pot(x, y)
                    self.projectiles.remove(shot)
                    blocked = True
                    if self.phase != 'playing':
                        self.projectiles.clear()
                        return
                    break
            if blocked:
                continue
            shot['x'] = x0 + shot['dx'] * travel
            shot['y'] = y0 + shot['dy'] * travel
            shot['range'] -= travel
            if shot['range'] <= 0:
                self.projectiles.remove(shot)
                self._drop_pot(shot['x'], shot['y'])

    def _fire(self, who, vec, npc=False):
        attr = 'boss_ammo' if npc else 'ammo'
        if getattr(self, attr) <= 0: return
        magnitude = math.hypot(*vec)
        if magnitude < 1e-6: return
        setattr(self, attr, getattr(self, attr) - 1)
        self.projectiles.append({'x': float(who[0]), 'y': float(who[1]),
                                'dx': vec[0] / magnitude, 'dy': vec[1] / magnitude,
                                'range': 7.3 if npc else 4.4, 'boss': npc})

    def _advance_projectiles(self, dt):
        self._advance_charge_projectiles(dt)
        for p in list(self.projectiles):
            if p.get('charged'):
                continue
            x, y = p['x'], p['y']
            speed = 6.4 if p['boss'] else 9.4
            nx = x + p['dx'] * dt * speed
            ny = y + p['dy'] * dt * speed
            p['range'] -= dt * speed
            travel = max(abs(nx - x), abs(ny - y))
            samples = max(1, math.ceil(travel * 8))
            hit_wall = any((round(x + (nx-x)*i/samples), round(y + (ny-y)*i/samples)) in (self.walls | self.moving_walls)
                           for i in range(1, samples+1))
            outside = not (0 <= nx < WIDTH and 0 <= ny < HEIGHT)
            if p['range'] <= 0 or hit_wall or outside:
                self.projectiles.remove(p)
                self._drop_pot(x, y)
                continue
            target = self.player if p['boss'] else self.boss
            # Sweep the full frame segment so fast mobile throws cannot tunnel through a character.
            vx, vy = nx - x, ny - y
            segment_sq = vx * vx + vy * vy
            if segment_sq:
                contact_t = max(0.0, min(1.0, ((target[0] - x) * vx + (target[1] - y) * vy) / segment_sq))
            else:
                contact_t = 0.0
            contact_x, contact_y = x + vx * contact_t, y + vy * contact_t
            hit_radius = .72 if not p['boss'] else .68
            if distance((contact_x, contact_y), target) < hit_radius:
                p['x'], p['y'] = contact_x, contact_y
                self._damage(not p['boss'])
                self._break_pot(p['x'], p['y'])
                if p in self.projectiles:self.projectiles.remove(p)
                if self.phase != 'playing':
                    self.projectiles.clear()
                    return
                continue
            p['x'], p['y'] = nx, ny
            crow = self.crow_flight
            if not p['boss'] and crow and distance((p['x'], p['y']), (crow['x'], crow['y'])) < .62:
                if self.player_hp < PLAYER_HP:
                    self.player_hp += 1
                    self.notice, self.notice_time = '\uAC10 \uACFC\uC7A5 \uBA85\uC911! \uAE30\uBB18 HP +1', 1.5
                else:
                    self.notice, self.notice_time = '\uAC10 \uACFC\uC7A5 \uBA85\uC911!', 1.0
                self._break_pot(p['x'], p['y'])
                if p in self.projectiles:
                    self.projectiles.remove(p)
                continue

class ActorMovementModule(_FeatureModule):
    MODULE_NAME = "actormovement"

    def _move_player(self, mx, my):
        magnitude = math.hypot(mx, my)
        if magnitude < .001:
            return False
        # Choose one cardinal grid direction; diagonal movement is never applied.
        if abs(mx) >= abs(my):
            dx, dy = (1 if mx > 0 else -1), 0
        else:
            dx, dy = 0, (1 if my > 0 else -1)
        x, y = (int(math.floor(value + .5)) for value in self.player)
        if not self._free_step(x, y, dx, dy):
            return False
        self.player = [x + dx, y + dy]
        self._contact()
        return True

    def _move_boss(self):
        # Omniscient NPC: target the player when equipped; seek nearest pot otherwise.
        if self.boss_ammo == 0:
            target = self._nearest_pot(self.boss)
        elif self.boss_ammo <= 2 and self.pots:
            pickup = self._nearest_pot(self.boss)
            cost_pot = len(self._path(self.boss, pickup)) if pickup else 999
            cost_player = len(self._path(self.boss, self.player))
            target = pickup if pickup and cost_pot <= cost_player + 2 else self.player[:]
        else:
            target = self.player[:]
        if target is None:
            # Temporarily enclosed by moving partitions: patrol until a pickup path opens.
            reachable = [p for p in ((self.boss[0]+dx,self.boss[1]+dy) for dx,dy in DIRECTIONS) if self._free(*p)]
            if reachable:
                target = list(self.rng.choice(reachable))
            else:
                return
        self.boss_target = target
        next_step = self._path_step(self.boss, target)
        if next_step == tuple(self.boss):
            if target != self.boss and self.boss_dash_cd <= 0:
                dx = 0 if target[0]==self.boss[0] else (1 if target[0]>self.boss[0] else -1)
                dy = 0 if target[1]==self.boss[1] else (1 if target[1]>self.boss[1] else -1)
                if dx and dy: dy=0
                self._dash(self.boss,dx,dy,True)
            return
        if self.boss_dash_cd <= 0 and distance(self.boss,target)>=3.4 and self.rng.random()<.34:
            dx=next_step[0]-self.boss[0];dy=next_step[1]-self.boss[1]
            if self._dash(self.boss,dx,dy,True):return
        dx, dy = next_step[0] - self.boss[0], next_step[1] - self.boss[1]
        self.boss_face = [dx, dy]
        self.boss = list(next_step)
        self._contact()

class FieldModule(MazeGeometryModule, PartitionModule, PotFieldModule):
    """Backward-compatible field facade over the smaller field feature instances."""
    MODULE_NAME = "field"

class CombatModule(MysteryPotModule, CrowHazardModule, DamageModule, ProjectileModule):
    """Backward-compatible combat facade over the smaller combat feature instances."""
    MODULE_NAME = "combat"

class ActorModule(ActorMovementModule):
    """Backward-compatible actor movement facade."""
    MODULE_NAME = "actor"

POTBREAKER_MODULES = {
    "maze_geometry": MazeGeometryModule,
    "partitions": PartitionModule,
    "pot_field": PotFieldModule,
    "mystery_pots": MysteryPotModule,
    "crow_hazards": CrowHazardModule,
    "damage": DamageModule,
    "projectiles": ProjectileModule,
    "actor_movement": ActorMovementModule,
}
POTBREAKER_MODULE_GROUPS = {
    "field": ("maze_geometry", "partitions", "pot_field"),
    "combat": ("mystery_pots", "crow_hazards", "damage", "projectiles"),
    "actor": ("actor_movement",),
}
FEATURE_METHODS = {
    "_add_pot": "pot_field",
    "_add_special_pot": "pot_field",
    "_advance_projectiles": "projectiles",
    "_aim": "damage",
    "_break_pot": "pot_field",
    "_contact": "damage",
    "_damage": "damage",
    "_dash": "damage",
    "_drop_pot": "pot_field",
    "_fire": "projectiles",
    "_begin_charge": "projectiles",
    "_release_charge": "projectiles",
    "_advance_charge_projectiles": "projectiles",
    "_free": "maze_geometry",
    "_free_step": "maze_geometry",
    "_maintain_field_pots": "pot_field",
    "_move_boss": "actor_movement",
    "_move_partitions": "partitions",
    "_move_player": "actor_movement",
    "_nearest_pot": "pot_field",
    "_path": "maze_geometry",
    "_path_step": "maze_geometry",
    "_pick_mystery_pots": "mystery_pots",
    "_pick_special_pots": "pot_field",
    "_pickups": "pot_field",
    "_reset_field_pots": "pot_field",
    "_spawn_mystery_pots": "mystery_pots",
    "_update_crow": "crow_hazards",
}


"""Small, instance-based components for assembling browser game modes."""
import json


class GameComponent:
    """A stateful feature instance with shared assembly context and lifecycle hooks."""

    def __init__(self, name):
        self.name = name

    def reset(self, context):
        return None

    def step(self, context, dt, **inputs):
        return None

    def tap(self, context, index):
        return None

    def sync(self, context, payload):
        return None

    def state(self):
        return {}


class ComponentAssemblyMode:
    """Runs supplied component *instances* in order and merges their state."""

    def __init__(self, components, mode_name="composed"):
        self.components = tuple(components or ())
        if not self.components:
            raise ValueError("at least one component instance is required")
        names = [getattr(component, "name", None) for component in self.components]
        if any(not name for name in names) or len(names) != len(set(names)):
            raise ValueError("components need unique, non-empty names")
        if any(not isinstance(component, GameComponent) for component in self.components):
            raise TypeError("components must be GameComponent instances")
        self.mode_name = mode_name
        self.context = {component.name: component for component in self.components}
        self.reset()

    def reset(self):
        for component in self.components:
            component.reset(self.context)
        return self.state()

    def step(self, dt, mx=0, my=0, jump=False, fire=False, aimx=0, aimy=0, **inputs):
        inputs.update(mx=mx, my=my, jump=jump, fire=fire, aimx=aimx, aimy=aimy)
        for component in self.components:
            component.step(self.context, dt, **inputs)
        return self.state()

    def tap(self, index):
        result = None
        for component in self.components:
            handled = component.tap(self.context, index)
            if handled is not None:
                result = handled
        return result if result is not None else False

    def sync(self, payload):
        data = json.loads(payload) if isinstance(payload, str) else payload
        for component in self.components:
            component.sync(self.context, data)
        return self.state()

    def state(self):
        merged = {"mode": self.mode_name}
        for component in self.components:
            values = component.state()
            overlap = merged.keys() & values.keys()
            if overlap:
                raise ValueError(f"duplicate state fields: {sorted(overlap)}")
            merged.update(values)
        return json.dumps(merged, ensure_ascii=False)


"""Composable Ginkgo features built from reusable game component instances."""
import secrets

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

    def _next(self):
        x = self.rng_state
        x ^= (x << 13) & 0xFFFFFFFF
        x &= 0xFFFFFFFF
        x ^= x >> 17
        x ^= (x << 5) & 0xFFFFFFFF
        self.rng_state = x & 0xFFFFFFFF
        return self.rng_state / 4294967296.0

    def _new_sex(self):
        return 0 if self._next() < 0.5 else 1

    def reset(self, context):
        seed = self.seed if self.seed is not None else secrets.randbits(32)
        self.rng_state = int(seed) & 0xFFFFFFFF
        if not self.rng_state:
            self.rng_state = 987654321
        self.last_tick = 0
        self.cells = []
        for _ in range(self.TOTAL):
            phase = int(self._next() * 4)
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

    MULTIPLIERS = {"normal": 1, "hard": 2, "very_hard": 3}

    def __init__(self, difficulty="normal", name="scoring"):
        super().__init__(name)
        self.multiplier = self.MULTIPLIERS.get(difficulty, 1)
        self.reset({})

    def reset(self, context):
        self.score = 0
        self.combo = 0
        self.max_combo = 0

    def success(self):
        self.combo += 1
        self.score += self.combo * self.multiplier
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

    def __init__(self, seed=None, difficulty="normal", components=None):
        components = components or [
            RoundTimerModule(difficulty=difficulty),
            GinkgoBoardModule(seed=seed),
            ComboScoringModule(difficulty=difficulty),
            InputLockModule(duration=0.5),
            GinkgoTapRulesModule(),
        ]
        required = {"round_timer", "board", "scoring", "input_lock", "tap_rules"}
        supplied = {getattr(component, "name", None) for component in components}
        if supplied != required:
            raise ValueError("Ginkgo components must provide round_timer, board, scoring, input_lock, and tap_rules instances")
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


"""Parameter-driven Pyodide engine with legacy modes and component instances."""
try:
    from .game import PotBreaker
    from .game_components import ComponentAssemblyMode
    from .ginkgo_modules import GinkgoMode
except ImportError:
    # The Worker builder concatenates these sources into the browser namespace.
    if "PotBreaker" not in globals() or "ComponentAssemblyMode" not in globals() or "GinkgoMode" not in globals():
        raise


class GameEngine:
    """Stable game facade; modes can be selected or assembled from feature instances.

    Examples:
        GameEngine("potbreaker", seed=7)
        GameEngine("ginkgo", difficulty="hard")
        GameEngine("composed", components=[timer, board, scoring, rules])
    """

    MODES = {"potbreaker", "ginkgo", "composed"}

    def __init__(self, mode="potbreaker", seed=None, difficulty="normal", components=None):
        if mode not in self.MODES:
            raise ValueError("unknown game mode")
        if mode == "composed":
            if components is None:
                raise ValueError("composed mode requires component instances")
            self.mode = ComponentAssemblyMode(components)
        else:
            self.mode = (GinkgoMode(seed=seed, difficulty=difficulty, components=components)
                         if mode == "ginkgo" else
                         PotBreaker(seed=seed, difficulty=difficulty, components=components))
        self.mode_name = mode

    @classmethod
    def compose(cls, *components):
        """Create an engine from feature objects instead of a whole game mode."""
        return cls(mode="composed", components=components)

    def reset(self):
        return self.mode.reset()

    def step(self, dt, mx=0, my=0, jump=False, fire=False, aimx=0, aimy=0):
        return self.mode.step(dt, mx, my, jump, fire, aimx, aimy)

    def tap(self, index):
        if not hasattr(self.mode, "tap"):
            raise ValueError("tap input is not supported by this engine composition")
        return self.mode.tap(index)

    def sync(self, payload):
        if not hasattr(self.mode, "sync"):
            raise ValueError("sync input is not supported by this engine composition")
        return self.mode.sync(payload)

    def state(self):
        return self.mode.state()

    def component_report(self):
        """List the active component instances and lifecycle hooks for QA."""
        components = getattr(self.mode, "components", ())
        return {
            component.name: {
                "instance": type(component).__name__,
                "hooks": [name for name in ("reset", "step", "tap", "sync", "state")
                          if callable(getattr(component, name, None))],
            }
            for component in components
        }

    def destroy(self):
        return None



if __name__ == '__main__':
    g = PotBreaker(42)
    for i in range(2500):
        s = json.loads(g.step(.04, 1 if i % 6 < 3 else -1, 0, False, i % 17 == 0))
        assert len(s['pots']) == FIELD_POT_COUNT
        assert 0 <= s['boss_ammo'] <= BOSS_POT_CAP
        assert 0 <= s['player_hp'] <= PLAYER_HP and 0 <= s['boss_hp'] <= 7
        if s['phase'] != 'playing': g.reset()
    print('OK: 2500 deterministic engine ticks')
