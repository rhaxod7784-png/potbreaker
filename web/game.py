import random, math, json

WIDTH, HEIGHT = 19, 11


def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


class PotBreaker:
    """Single-player office maze rules; deterministic JSON state for Canvas UI."""

    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.reset()

    def reset(self):
        self.phase = 'playing'
        self.clock = 0.0
        self.player = list(self.rng.choice([(1, 1), (1, HEIGHT - 2), (WIDTH - 2, 1), (WIDTH - 2, HEIGHT - 2)]))
        self.boss = [WIDTH // 2, HEIGHT // 2]
        self.face = [1, 0]
        self.boss_face = [1, 0]
        self.walls = set()
        safe = {tuple(self.player), tuple(self.boss)}
        for y in range(1, HEIGHT-1):
            for x in range(1, WIDTH-1):
                if (x, y) not in safe and abs(x - self.player[0]) + abs(y - self.player[1]) > 2 and abs(x - self.boss[0]) + abs(y - self.boss[1]) > 2 and self.rng.random() < 0.23:
                    self.walls.add((x, y))
        # Carve openings if a random partition layout blocks every route.
        while self.walls and not self._is_connected(self.player, self.boss):
            self.walls.remove(self.rng.choice(tuple(self.walls)))
        self.ammo = 1
        self.boss_ammo = 2
        self.jump_stacks = 1.0
        self.boss_jump_cd = 0.0
        self.throw_cd = 0.0
        self.boss_throw_cd = 1.5
        self.player_move_cd = 0.0
        self.boss_move_cd = 0.4
        self.alert = 0.0
        self.last_seen = None
        self.bell = 0.0
        self.notice = '크다 부장의 시야를 피해 이동하세요.'
        self.notice_time = 2.2
        self.projectiles = []
        self.pots = []
        self.roam = None
        for _ in range(3):
            self._add_pot()
        return self.state()

    def _free(self, x, y):
        return 0 <= x < WIDTH and 0 <= y < HEIGHT and (x, y) not in self.walls

    def _is_connected(self, start, goal):
        q, seen = [tuple(start)], {tuple(start)}
        for x, y in q:
            if (x, y) == tuple(goal):
                return True
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if self._free(nx, ny) and (nx, ny) not in seen:
                    seen.add((nx, ny))
                    q.append((nx, ny))
        return False

    def _add_pot(self):
        choices = [(x, y) for x in range(WIDTH) for y in range(HEIGHT)
                   if self._free(x, y) and [x, y] not in (self.player, self.boss) and [x, y] not in self.pots]
        if choices:
            self.pots.append(list(self.rng.choice(choices)))

    def _path_step(self, start, goal):
        start, goal = tuple(start), tuple(goal)
        if start == goal:
            return start
        q = [start]
        came = {start: None}
        for p in q:
            if p == goal:
                break
            for dx, dy in self.rng.sample([(0,1),(1,0),(0,-1),(-1,0)], 4):
                n = (p[0]+dx, p[1]+dy)
                if self._free(*n) and n not in came:
                    came[n] = p
                    q.append(n)
        if goal not in came:
            return start
        p = goal
        while came[p] not in (None, start):
            p = came[p]
        return p

    def _sees_player(self):
        # Partition walls do NOT obstruct vision; configurable distance is in grid cells.
        if distance(self.player, self.boss) > 3.4:
            return False
        dx, dy = self.player[0] - self.boss[0], self.player[1] - self.boss[1]
        theta = abs(math.degrees(math.atan2(self.boss_face[0]*dy-self.boss_face[1]*dx,
                                             self.boss_face[0]*dx+self.boss_face[1]*dy)))
        return 5 <= theta <= 155

    def _pickups(self):
        for who, cap, attr in ((self.player, 1, 'ammo'), (self.boss, 2, 'boss_ammo')):
            if getattr(self, attr) >= cap:
                continue
            for pot in list(self.pots):
                if distance(who, pot) < 0.65:
                    setattr(self, attr, getattr(self, attr) + 1)
                    self.pots.remove(pot)
                    self._add_pot()
                    break

    def _fire(self, who, vec, boss=False):
        ammo_field = 'boss_ammo' if boss else 'ammo'
        if getattr(self, ammo_field) < 1:
            return
        length = math.hypot(*vec)
        if length < 0.001:
            vec, length = [1, 0], 1
        setattr(self, ammo_field, getattr(self, ammo_field) - 1)
        self.projectiles.append({'x':float(who[0]),'y':float(who[1]),
                                 'dx':vec[0]/length,'dy':vec[1]/length,
                                 'range':7.3 if boss else 4.2,'boss':boss})

    def _jump_player(self, dx, dy):
        if self.jump_stacks < 1 or not (dx or dy):
            return False
        x, y = self.player
        if (x+dx,y+dy) not in self.walls or not self._free(x+2*dx,y+2*dy):
            return False
        self.player = [x+2*dx,y+2*dy]
        self.jump_stacks -= 1
        return True

    def _move_boss(self):
        visible = self._sees_player()
        if visible:
            self.last_seen = list(self.player)
            self.alert = 2.8
        target = self.last_seen if self.alert > 0 and self.last_seen else None
        if not target:
            if self.roam is None or self.boss == self.roam or self.rng.random() < .10:
                self.roam = [self.rng.randrange(1,WIDTH-1), self.rng.randrange(1,HEIGHT-1)]
            target = self.roam
        dx = 0 if target[0] == self.boss[0] else (1 if target[0] > self.boss[0] else -1)
        dy = 0 if target[1] == self.boss[1] else (1 if target[1] > self.boss[1] else -1)
        primary = (dx,0) if abs(target[0]-self.boss[0]) >= abs(target[1]-self.boss[1]) else (0,dy)
        if primary == (0,0):
            primary = (dx,dy)
        if visible and self.boss_jump_cd <= 0 and self.boss_ammo > 0:
            for d in ([primary,(0,dy),(dx,0)]):
                if d == (0,0):
                    continue
                tx, ty = self.boss
                count = 0
                while (tx+d[0],ty+d[1]) in self.walls and count < 3:
                    tx += d[0]
                    ty += d[1]
                    count += 1
                if count and self._free(tx+d[0],ty+d[1]):
                    self.boss = [tx+d[0], ty+d[1]]
                    self.boss_face = list(d)
                    self.boss_jump_cd = 15.0
                    self.notice, self.notice_time = '쾅! 크다 부장이 파티션을 뚫었습니다!', 0.9
                    return
        nxt = self._path_step(self.boss, target)
        if nxt != tuple(self.boss):
            self.boss_face = [nxt[0]-self.boss[0],nxt[1]-self.boss[1]]
            self.boss = list(nxt)
        elif not visible:
            self.roam = None

    def _advance_projectiles(self, dt):
        for p in list(self.projectiles):
            p['x'] += p['dx'] * dt * (7.1 if p['boss'] else 9.6)
            p['y'] += p['dy'] * dt * (7.1 if p['boss'] else 9.6)
            p['range'] -= dt * (7.1 if p['boss'] else 9.6)
            if p['range'] <= 0 or not (0 <= p['x'] < WIDTH and 0 <= p['y'] < HEIGHT):
                self.projectiles.remove(p)
                continue
            if not p['boss'] and (round(p['x']),round(p['y'])) in self.walls:
                self.projectiles.remove(p)
                continue
            for other in list(self.projectiles):
                if other is p or other['boss'] == p['boss']:
                    continue
                if math.hypot(p['x']-other['x'],p['y']-other['y']) < .5:
                    small = p if not p['boss'] else other
                    if small in self.projectiles:
                        self.projectiles.remove(small)
                    break
            if p not in self.projectiles:
                continue
            target = self.player if p['boss'] else self.boss
            if distance((p['x'],p['y']),target) < .56:
                self.phase = 'lose' if p['boss'] else 'win'
                self.projectiles.clear()
                break

    def step(self, dt, mx=0, my=0, jump=False, fire=False, aimx=0, aimy=0):
        if self.phase != 'playing':
            return self.state()
        dt = min(.085,max(0.01,float(dt)))
        self.clock += dt
        self.jump_stacks = min(3.,self.jump_stacks+dt/5.)
        self.boss_jump_cd = max(0.,self.boss_jump_cd-dt)
        self.throw_cd = max(0.,self.throw_cd-dt)
        self.boss_throw_cd = max(0.,self.boss_throw_cd-dt)
        self.player_move_cd -= dt
        self.boss_move_cd -= dt
        self.notice_time = max(0.,self.notice_time-dt)
        self.bell = max(0.,self.bell-dt)
        self.alert = max(0.,self.alert-dt)
        dx, dy = int(mx), int(my)
        if dx and dy:
            dy = 0
        if dx or dy:
            self.face = [dx,dy]
        if jump and (dx or dy):
            if self._jump_player(dx,dy):
                self.player_move_cd = .10
        if self.player_move_cd <= 0 and (dx or dy):
            tx,ty = self.player[0]+dx,self.player[1]+dy
            if self._free(tx,ty):
                self.player = [tx,ty]
            self.player_move_cd = .115
        if fire and self.throw_cd <= 0 and self.ammo:
            self._fire(self.player,[float(aimx) if aimx or aimy else self.face[0],
                                    float(aimy) if aimx or aimy else self.face[1]])
            self.throw_cd = .40
        if self.boss_move_cd <= 0:
            self._move_boss()
            self.boss_move_cd = .32
        if self.boss_throw_cd <= 0 and self.boss_ammo and distance(self.player,self.boss) < 7.4 and self._sees_player():
            self._fire(self.boss,[self.player[0]-self.boss[0],self.player[1]-self.boss[1]],True)
            self.boss_throw_cd = 2.8
        if (dx or dy) and distance(self.player,self.boss) <= 5:
            self.bell = .7
        self._advance_projectiles(dt)
        self._pickups()
        return self.state()

    def state(self):
        return json.dumps({'phase':self.phase,'player':self.player,'boss':self.boss,
            'face':self.face,'boss_face':self.boss_face,'walls':list(self.walls),'pots':self.pots,
            'ammo':self.ammo,'boss_ammo':self.boss_ammo,'stacks':int(self.jump_stacks),
            'jump_progress':round(self.jump_stacks%1,2),'boss_cd':round(self.boss_jump_cd,1),
            'bell':self.bell>0,'notice':self.notice if self.notice_time else '',
            'projectiles':self.projectiles,'vision_radius':3.4},ensure_ascii=False)

if __name__ == '__main__' and not globals().get('IN_BROWSER', False):
    game=PotBreaker(9)
    for i in range(2000):
        s=json.loads(game.step(.04,1 if i%6 < 3 else -1, 0, i%30==0, i%18==0,1,0))
        assert len(s['pots'])==3 and 0<=s['stacks']<=3
        if s['phase']!='playing': game.reset()
    print('OK: 2000 ticks')
