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
    def __init__(self, game):
        object.__setattr__(self, "game", game)

    def __getattr__(self, name):
        return getattr(self.game, name)

    def __setattr__(self, name, value):
        if name == "game":
            object.__setattr__(self, name, value)
        else:
            setattr(self.game, name, value)

class FieldModule(_FeatureModule):
    def _free(self, x, y):
        return 0 <= x < WIDTH and 0 <= y < HEIGHT and (x, y) not in self.walls and (x, y) not in self.moving_walls
    def _free_step(self, x, y, dx, dy):
        nx, ny = x + dx, y + dy
        if not self._free(nx, ny): return False
        if dx and dy:
            return self._free(x + dx, y) and self._free(x, y + dy)
        return True
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
                    self.notice, self.notice_time = ('크다' if npc else '기묘') + ' 회복 화분! HP +1', 1.3
                else:
                    self.notice, self.notice_time = '회복 화분을 찾았지만 HP가 가득 찼습니다.', 1.3
                self._maintain_field_pots()
                break
    def _pick_mystery_pots(self):
        for item in list(self.mystery_pots):
            for npc, who in ((False, self.player), (True, self.boss)):
                if distance(who, (item['x'], item['y'])) >= .65:
                    continue
                self.mystery_pots.remove(item)
                attr, cap, name = ('boss_hp', self.boss_hp_cap, '크다') if npc else ('player_hp', PLAYER_HP, '기묘')
                effect = item['effect']
                if effect == 'damage':
                    self._damage(npc, bypass_invulnerability=True)
                    self.notice, self.notice_time = f"? 화분 폭발! {name} HP -1", 1.3
                elif effect == 'heal':
                    setattr(self, attr, min(cap, getattr(self, attr) + 1))
                    self.notice, self.notice_time = f"? 화분 회복! {name} HP +1", 1.3
                elif effect == 'refill':
                    ammo_attr = 'boss_ammo' if npc else 'ammo'
                    ammo_cap = self.boss_pot_cap if npc else self.player_pot_cap
                    setattr(self, ammo_attr, ammo_cap)
                    self.notice, self.notice_time = f"? 화분 풀충전! {name} 화분 {ammo_cap}/{ammo_cap}", 1.3
                else:
                    self._reset_field_pots()
                    self.notice, self.notice_time = '? 필드 화분 리셋!', 1.3
                break

class CombatModule(_FeatureModule):
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
    def _update_crow(self, dt):
        self.crow_spawn_timer -= dt
        if self.crow_spawn_timer <= 0 and self.crow_flight is None:
            self.crow_flight = {'x': 1.0, 'y': float(self.rng.randint(1, HEIGHT-2)),
                                'ttl': CROW_FLIGHT_SECONDS, 'drop': CROW_DROP_SECONDS}
            self.crow_spawn_timer = CROW_RESPAWN_SECONDS
            self.notice, self.notice_time = '감 과장 출동! ? 화분 투하!', 1.0
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
        for p in list(self.projectiles):
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
                    self.notice, self.notice_time = '감 과장 명중! 기묘 HP +1', 1.5
                else:
                    self.notice, self.notice_time = '감 과장 명중!', 1.0
                self._break_pot(p['x'], p['y'])
                if p in self.projectiles:
                    self.projectiles.remove(p)
                continue

class ActorModule(_FeatureModule):
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

FEATURE_METHODS = {
    "_free": "field",
    "_free_step": "field",
    "_add_pot": "field",
    "_add_special_pot": "field",
    "_maintain_field_pots": "field",
    "_reset_field_pots": "field",
    "_nearest_pot": "field",
    "_path": "field",
    "_path_step": "field",
    "_move_partitions": "field",
    "_drop_pot": "field",
    "_break_pot": "field",
    "_pickups": "field",
    "_pick_special_pots": "field",
    "_pick_mystery_pots": "field",
    "_spawn_mystery_pots": "combat",
    "_update_crow": "combat",
    "_damage": "combat",
    "_dash": "combat",
    "_contact": "combat",
    "_aim": "combat",
    "_fire": "combat",
    "_advance_projectiles": "combat",
    "_move_player": "actor",
    "_move_boss": "actor",
}
