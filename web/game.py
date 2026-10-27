"""POT BREAKER RE v1.0.3 — single-player deterministic Python game rules.
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
PARTITION_MOVE_SECONDS = 1.1
VISION_RANGE = None    # Boss can locate both player and pickup positions across entire map.
AIM_SWEEP_DEGREES = 30.0
AIM_SWEEP_SPEED = 8.5  # QA default: faster ±30° automatic targeting
MONITOR_FREEZE_SECONDS = 2.1  # QA provisional; user did not define duration
CROW_FLIGHT_SECONDS = 6.0
CROW_DROP_SECONDS = 0.75  # ±30° gives a full 60° arc.


def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


class PotBreaker:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.reset()

    def reset(self):
        self.phase, self.clock = 'playing', 0.0
        self.player = list(self.rng.choice([(1, 1), (1, HEIGHT - 2),
                                            (WIDTH - 2, 1), (WIDTH - 2, HEIGHT - 2)]))
        self.boss = [WIDTH // 2, HEIGHT // 2]
        self.face, self.boss_face = [1, 0], [-1, 0]
        self.walls, self.moving_walls = set(), set()
        safe = {tuple(self.player), tuple(self.boss)}
        for y in range(1, HEIGHT - 1):
            for x in range(1, WIDTH - 1):
                p = (x, y)
                if p in safe or min(distance(p, self.player), distance(p, self.boss)) < 2.3:
                    continue
                r = self.rng.random()
                if r < .135:
                    self.walls.add(p)
                elif r < .20:
                    self.moving_walls.add(p)
        for _ in range(180):
            if self._path_step(self.player, self.boss) != tuple(self.player):
                break
            if self.walls:
                self.walls.remove(self.rng.choice(tuple(self.walls)))
            elif self.moving_walls:
                self.moving_walls.remove(self.rng.choice(tuple(self.moving_walls)))
            else:
                break
        self.ammo, self.boss_ammo, self.max_boss_ammo = 1, 5, 5
        self.throw_cd, self.boss_throw_cd = 0.0, 1.2
        self.player_move_cd, self.boss_move_cd = 0.0, .5
        self.projectiles, self.pots, self.pads = [], [], []
        self.monitors, self.crows, self.crow_flight = [], [], None
        self.player_freeze = self.boss_freeze = 0.0
        self.monitor_spawn_timer = 1.4
        self.crow_spawn_timer = 3.0
        self.pad_spawn_timer, self.partition_timer = .3, 1.1
        self.notice, self.notice_time = '대시 패드를 밟으면 기묘는 3칸 이동합니다.', 2.2
        self.bell = 0.0
        self.dash_effect = None
        self.boss_target = None
        for _ in range(3): self._add_pot()
        for _ in range(4): self._spawn_pad()
        self._spawn_collectible('monitor')
        self._spawn_collectible('crow')
        return self.state()

    def _free(self, x, y):
        return 0 <= x < WIDTH and 0 <= y < HEIGHT and (x, y) not in self.walls and (x, y) not in self.moving_walls

    def _add_pot(self):
        choices = [(x, y) for y in range(HEIGHT) for x in range(WIDTH)
                   if self._free(x, y) and [x, y] not in (self.player, self.boss)
                   and [x, y] not in self.pots]
        if choices:
            self.pots.append(list(self.rng.choice(choices)))

    def _nearest_pot(self, who):
        # Use walkable path distance, not straight-line distance, to avoid NPC freezing at a partition.
        best = None
        bestlen = float('inf')
        for pot in self.pots:
            path = self._path(who, pot)
            if not path:
                continue  # Ignore temporarily sealed-off pickups; do not stand still.
            cost = len(path)
            if cost < bestlen:
                best, bestlen = list(pot), cost
        return best

    def _path(self, start, goal):
        start, goal = tuple(start), tuple(goal)
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

    def _spawn_collectible(self, kind):
        target = self.monitors if kind == 'monitor' else self.crows
        occupied = {tuple(self.player), tuple(self.boss)}
        occupied.update(tuple(q) for q in self.pots)
        occupied.update((q['x'], q['y']) for q in self.pads)
        occupied.update(tuple(q) for q in self.monitors + self.crows)
        options = [(x, y) for y in range(1, HEIGHT-1) for x in range(1, WIDTH-1)
                   if self._free(x, y) and (x, y) not in occupied]
        if options and len(target) < 2:
            target.append(list(self.rng.choice(options)))

    def _collect_special(self):
        for who, npc in ((self.player, False), (self.boss, True)):
            for pos in list(self.monitors):
                if who != pos: continue
                self.monitors.remove(pos)
                if npc: self.boss_freeze = MONITOR_FREEZE_SECONDS
                else: self.player_freeze = MONITOR_FREEZE_SECONDS
                self.notice, self.notice_time = ('크다 부장 모니터 정지!' if npc else '기묘 모니터 정지!'), 1.1
                self.monitor_spawn_timer = max(self.monitor_spawn_timer, 2.0)
            for pos in list(self.crows):
                if who != pos: continue
                self.crows.remove(pos)
                self.crow_flight = {'x': float(who[0]), 'y': float(who[1]),
                                    'ttl': CROW_FLIGHT_SECONDS, 'drop': .20}
                self.notice, self.notice_time = '감 과장 출동! 화분 투하!', 1.35
                self.crow_spawn_timer = max(self.crow_spawn_timer, CROW_FLIGHT_SECONDS + 1)

    def _update_special(self, dt):
        self.player_freeze = max(0., self.player_freeze-dt)
        self.boss_freeze = max(0., self.boss_freeze-dt)
        self.monitor_spawn_timer -= dt
        self.crow_spawn_timer -= dt
        if self.monitor_spawn_timer <= 0:
            self.monitor_spawn_timer = 5.5
            self._spawn_collectible('monitor')
        if self.crow_spawn_timer <= 0:
            self.crow_spawn_timer = 12.0
            self._spawn_collectible('crow')
        bird = self.crow_flight
        if not bird: return
        bird['ttl'] -= dt
        t = CROW_FLIGHT_SECONDS - bird['ttl']
        bird['x'] = (t * 3.0 + 1.0) % (WIDTH - 2) + 1.0
        bird['y'] = max(.7, min(HEIGHT-1.5, HEIGHT/2 + math.sin(t*2.4)*3.1))
        bird['drop'] -= dt
        if bird['drop'] <= 0:
            bird['drop'] = CROW_DROP_SECONDS
            # The crow adds real collectible flowerpots on the field.
            self._drop_pot(bird['x'], bird['y'])
        if bird['ttl'] <= 0: self.crow_flight = None

    def _spawn_pad(self):
        positions = {(p['x'], p['y']) for p in self.pads}
        choices = [(x, y) for y in range(1, HEIGHT - 1) for x in range(1, WIDTH - 1)
                   if self._free(x, y) and (x, y) not in positions
                   and [x, y] not in self.pots and [x, y] not in (self.player, self.boss)]
        if choices:
            x, y = self.rng.choice(choices)
            self.pads.append({'x': x, 'y': y, 'ttl': PAD_LIFETIME_SECONDS})

    def _update_pads(self, dt):
        for pad in list(self.pads):
            pad['ttl'] -= dt
            if pad['ttl'] <= 0: self.pads.remove(pad)
        self.pad_spawn_timer -= dt
        if self.pad_spawn_timer <= 0:
            self.pad_spawn_timer = PAD_SPAWN_SECONDS
            if len(self.pads) < PAD_LIMIT: self._spawn_pad()

    def _move_partitions(self, dt):
        self.partition_timer -= dt
        if self.partition_timer > 0: return
        self.partition_timer = PARTITION_MOVE_SECONDS
        occupied = {tuple(self.player), tuple(self.boss), *[tuple(p) for p in self.pots]}
        occupied.update((pad['x'], pad['y']) for pad in self.pads)
        occupied.update(tuple(p) for p in self.monitors + self.crows)
        new_positions = set(self.moving_walls)
        for old in self.rng.sample(sorted(self.moving_walls), min(5, len(self.moving_walls))):
            dirs = list(DIRECTIONS); self.rng.shuffle(dirs)
            for dx, dy in dirs:
                target = (old[0] + dx, old[1] + dy)
                if target[0] < 1 or target[0] >= WIDTH - 1 or target[1] < 1 or target[1] >= HEIGHT - 1:
                    continue
                if target in self.walls or target in new_positions or target in occupied: continue
                new_positions.remove(old)
                new_positions.add(target)
                break
        self.moving_walls = new_positions

    def _dash(self, who, dx, dy, npc):
        if not (dx or dy): return False
        start = who[:]
        length = 5 if npc else 3
        # Skip barriers while dashing; only free landing tiles are allowed.
        candidate = None
        for amount in range(length, 0, -1):
            tx, ty = start[0] + dx * amount, start[1] + dy * amount
            if self._free(tx, ty):
                candidate = [tx, ty]
                break
        if candidate is None: return False
        who[:] = candidate
        self.dash_effect = {'from': start, 'to': candidate[:], 'npc': npc, 'age': 0.0}
        self.notice, self.notice_time = ('쾅! 크다 부장 5칸 대시!' if npc else '슝! 기묘 3칸 대시!'), .55
        self._contact()
        return True

    def _activate_pad(self, who, direction, npc=False):
        for pad in list(self.pads):
            if [pad['x'], pad['y']] != who: continue
            if self._dash(who, direction[0], direction[1], npc):
                self.pads.remove(pad)
                return True
        return False

    def _contact(self):
        if self.player == self.boss: self.phase = 'lose'

    def _pickups(self):
        for who, cap, attr in ((self.player, 1, 'ammo'), (self.boss, 5, 'boss_ammo')):
            if getattr(self, attr) >= cap: continue
            for pot in list(self.pots):
                if who == pot:
                    setattr(self, attr, getattr(self, attr) + 1)
                    self.pots.remove(pot)
                    self._add_pot()   # Field always has at least 3 ordinary pickups.
                    break

    def _drop_pot(self, x, y):
        xx, yy = max(0, min(WIDTH-1, round(x))), max(0, min(HEIGHT-1, round(y)))
        for radius in range(5):
            for dx in range(-radius, radius+1):
                for dy in range(-radius, radius+1):
                    if abs(dx) + abs(dy) != radius: continue
                    nx, ny = xx+dx, yy+dy
                    if self._free(nx, ny) and [nx, ny] not in self.pots and [nx, ny] not in (self.boss, self.player):
                        self.pots.append([nx, ny]); return

    def _aim(self, src, target):
        base = math.atan2(target[1] - src[1], target[0] - src[0])
        swing = math.radians(AIM_SWEEP_DEGREES) * math.sin(self.clock * AIM_SWEEP_SPEED)
        angle = base + swing
        return [math.cos(angle), math.sin(angle)]

    def _fire(self, who, vec, npc=False):
        attr = 'boss_ammo' if npc else 'ammo'
        if getattr(self, attr) <= 0: return
        magnitude = math.hypot(*vec)
        if magnitude < 1e-6: return
        setattr(self, attr, getattr(self, attr) - 1)
        self.projectiles.append({'x': float(who[0]), 'y': float(who[1]),
                                'dx': vec[0] / magnitude, 'dy': vec[1] / magnitude,
                                'range': 7.3 if npc else 4.4, 'boss': npc})

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
        if self.boss_freeze > 0: return
        next_step = self._path_step(self.boss, target)
        if next_step == tuple(self.boss): return
        dx, dy = next_step[0] - self.boss[0], next_step[1] - self.boss[1]
        self.boss_face = [dx, dy]
        self.boss = list(next_step)
        self._contact()
        if self.phase == 'playing': self._activate_pad(self.boss, (dx, dy), npc=True)

    def _advance_projectiles(self, dt):
        for p in list(self.projectiles):
            x, y = p['x'], p['y']
            speed = 7.2 if p['boss'] else 9.4
            p['x'] += p['dx'] * dt * speed
            p['y'] += p['dy'] * dt * speed
            p['range'] -= dt * speed
            hit_wall = not p['boss'] and (round(p['x']), round(p['y'])) in (self.walls | self.moving_walls)
            outside = not (0 <= p['x'] < WIDTH and 0 <= p['y'] < HEIGHT)
            if p['range'] <= 0 or hit_wall or outside:
                self.projectiles.remove(p)
                self._drop_pot(x, y)
                continue
            target = self.player if p['boss'] else self.boss
            if distance((p['x'], p['y']), target) < .55:
                self.phase = 'lose' if p['boss'] else 'win'
                self.projectiles.clear()
                return
            for other in list(self.projectiles):
                if p is other or other['boss'] == p['boss']: continue
                if distance((p['x'], p['y']), (other['x'], other['y'])) < .48:
                    small = p if not p['boss'] else other
                    if small in self.projectiles:
                        self.projectiles.remove(small)
                        self._drop_pot(small['x'], small['y'])
                    break

    def step(self, dt, mx=0, my=0, jump=False, fire=False, aimx=0, aimy=0):
        # Keep previous API signature for the existing Pyodide front-end.
        if self.phase != 'playing': return self.state()
        dt = min(.085, max(.01, float(dt)))
        self.clock += dt
        self.throw_cd = max(0., self.throw_cd-dt)
        self.boss_throw_cd = max(0., self.boss_throw_cd-dt)
        self.player_move_cd -= dt
        self.boss_move_cd -= dt
        self.notice_time = max(0., self.notice_time-dt)
        self.bell = max(0., self.bell-dt)
        self._move_partitions(dt)
        self._update_pads(dt)
        self._update_special(dt)
        if self.dash_effect:
            self.dash_effect['age'] += dt
            if self.dash_effect['age'] > .35: self.dash_effect = None
        dx, dy = int(mx), int(my)
        if dx and dy: dy = 0
        if dx or dy: self.face = [dx, dy]
        if self.player_freeze <= 0 and self.player_move_cd <= 0 and (dx or dy):
            tx, ty = self.player[0] + dx, self.player[1] + dy
            if self._free(tx, ty):
                self.player = [tx, ty]
                self._contact()
                if self.phase == 'playing': self._activate_pad(self.player, (dx, dy))
            self.player_move_cd = .115
        if self.phase != 'playing': return self.state()
        if self.player_freeze <= 0 and fire and self.throw_cd <= 0 and self.ammo:
            self._fire(self.player, self._aim(self.player, self.boss))
            self.throw_cd = .38
        if self.boss_move_cd <= 0 and self.boss_freeze <= 0:
            self._move_boss()
            self.boss_move_cd = .225
        if self.phase != 'playing': return self.state()
        self._pickups()
        self._collect_special()
        # Boss projectile decision depends on ammo but no field-of-view angle.
        if self.boss_freeze <= 0 and self.boss_throw_cd <= 0 and self.boss_ammo > 0 and distance(self.player, self.boss) < 7.3:
            aim = self._aim(self.boss, self.player)
            base_angle = math.atan2(aim[1], aim[0])
            # Paired projectiles converge around the swept automatic aim ray.
            for offset in (-.105, .105) if self.boss_ammo >= 2 else (0,):
                angle = base_angle + offset
                self._fire(self.boss, [math.cos(angle), math.sin(angle)], npc=True)
            self.boss_throw_cd = 1.1
        if (dx or dy) and distance(self.player, self.boss) <= 5:
            self.bell = .65
        self._advance_projectiles(dt)
        return self.state()

    def state(self):
        return json.dumps({'phase': self.phase, 'player': self.player, 'boss': self.boss,
                           'face': self.face, 'boss_face': self.boss_face,
                           'walls': sorted(self.walls), 'moving_walls': sorted(self.moving_walls),
                           'pots': self.pots, 'pads': self.pads, 'projectiles': self.projectiles,
                           'monitors': self.monitors, 'crows': self.crows, 'crow_flight': self.crow_flight,
                           'player_freeze': round(self.player_freeze,2), 'boss_freeze': round(self.boss_freeze,2),
                           'ammo': self.ammo, 'boss_ammo': self.boss_ammo,
                           'aim': self._aim(self.player, self.boss),
                           'boss_aim': self._aim(self.boss, self.player),
                           'aim_sweep_degrees': 60,
                           'dash_effect': self.dash_effect,
                           'bell': self.bell > 0,
                           'notice': self.notice if self.notice_time else '',
                           'clock': round(self.clock, 2)}, ensure_ascii=False)

if __name__ == '__main__':
    g = PotBreaker(42)
    for i in range(2500):
        s = json.loads(g.step(.04, 1 if i % 6 < 3 else -1, 0, False, i % 17 == 0))
        assert len(s['pots']) >= 3
        assert 0 <= s['boss_ammo'] <= 5
        if s['phase'] != 'playing': g.reset()
    print('OK: 2500 deterministic engine ticks')
