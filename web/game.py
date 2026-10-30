"""POT BREAKER RE v1.0.91 — single-player deterministic Python game rules.
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
    def __init__(self, seed=None, difficulty='normal'):
        self.rng = random.Random(seed)
        if 'FieldModule' not in globals():
            from . import game_modules as _game_modules
            globals().update({
                'FieldModule': _game_modules.FieldModule,
                'CombatModule': _game_modules.CombatModule,
                'ActorModule': _game_modules.ActorModule,
                'FEATURE_METHODS': _game_modules.FEATURE_METHODS,
            })
        feature_classes = globals()
        self.difficulty = difficulty if difficulty in ('normal', 'hard', 'very_hard') else 'normal'
        self.player_pot_cap = 3 if self.difficulty == 'normal' else 2
        self.boss_hp_cap = {'normal': 5, 'hard': 7, 'very_hard': 10}[self.difficulty]
        self._feature_modules = {
            'field': feature_classes['FieldModule'](self),
            'combat': feature_classes['CombatModule'](self),
            'actor': feature_classes['ActorModule'](self),
        }
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
        self.notice, self.notice_time = '대시 버튼: 3칸 돌진 · 3초 재사용 대기', 2.2
        self.dash_effect = None
        self.boss_target = None
        for _ in range(FIELD_POT_COUNT): self._add_pot()
        for effect in SPECIAL_POT_EFFECTS: self._add_special_pot(effect)
        
        return self.state()

    def step(self, dt, mx=0, my=0, jump=False, fire=False, aimx=0, aimy=0):
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
        if fire and self.throw_cd <= 0 and self.ammo:
            self._fire(self.player, self._aim(self.player, self.boss))
            self.throw_cd = .38
        if self.boss_move_cd <= 0:
            self._move_boss()
            self.boss_move_cd = .225
        if self.phase != 'playing': return self.state()
        self._pickups()
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
                           'boss_hp_cap': self.boss_hp_cap, 'difficulty': self.difficulty,
                           'dash_effect': self.dash_effect,
                           'notice': self.notice if self.notice_time else '',
                           'clock': round(self.clock, 2), 'hits': self.hit_events,
                           'pot_breaks': self.pot_break_events}, ensure_ascii=False)

if __name__ == '__main__':
    g = PotBreaker(42)
    for i in range(2500):
        s = json.loads(g.step(.04, 1 if i % 6 < 3 else -1, 0, False, i % 17 == 0))
        assert len(s['pots']) == FIELD_POT_COUNT
        assert 0 <= s['boss_ammo'] <= BOSS_POT_CAP
        assert 0 <= s['player_hp'] <= PLAYER_HP and 0 <= s['boss_hp'] <= 7
        if s['phase'] != 'playing': g.reset()
    print('OK: 2500 deterministic engine ticks')
