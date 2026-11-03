function patchWorkerBundle(source) {
  const applied = [];
  const once = (s, before, after, name, expected = 1) => {
    const count = s.split(before).length - 1;
    if (count !== expected) throw Error(name + ": expected " + expected + " occurrence(s), found " + count);
    applied.push(name);
    return s.replace(before, after);
  };
  function template(key, edit) {
    const marker = "var " + key + " = " + String.fromCharCode(96);
    const begin = source.indexOf(marker);
    const from = begin + marker.length;
    const end = source.indexOf(String.fromCharCode(96) + ";\nvar ", from);
    if (begin < 0 || end < 0) throw Error("Missing v184 template " + key);
    source = source.slice(0, from) + edit(source.slice(from, end)) + source.slice(end);
  }
  function module(path, edit) {
    const key = JSON.stringify(path) + ": ";
    const n = source.indexOf(key);
    if (n < 0 || source.indexOf(key, n + 1) !== -1) throw Error("Missing/duplicate module " + path);
    const start = n + key.length;
    if (source[start] !== '"') throw Error("Expected string literal for " + path);
    let end = -1;
    for (let i = start + 1; i < source.length; i++) {
      if (source[i] === "\\") i++;
      else if (source[i] === '"') { end = i; break; }
    }
    if (end < 0) throw Error("Missing string end " + path);
    const jsString = source.slice(start, end + 1).replace(/\\x([0-9A-Fa-f]{2})/g, (_, hex) => "\\u00" + hex).replace(/\\u\{([0-9a-fA-F]+)\}/g, (_, hex) => String.fromCodePoint(parseInt(hex, 16)));
    const oldCode = JSON.parse(jsString);
    const newCode = edit(oldCode);
    source = source.slice(0, start) + JSON.stringify(newCode) + source.slice(end + 1);
  }

  template("GAME", p => {
    p = once(p, "self.player_pot_cap = 3 if self.difficulty == 'normal' else 2", "self.player_pot_cap = 3", "capacity all difficulties");
    p = once(p, "self.ammo, self.boss_ammo, self.max_boss_ammo = 0, 0, BOSS_POT_CAP", "self.ammo, self.boss_ammo, self.max_boss_ammo = 0, 0, BOSS_POT_CAP\n        self.charge_cap = 3\n        self.charge_active = False\n        self.charge_count = 0", "reset charge");
    p = once(p, "def step(self, dt, mx=0, my=0, jump=False, fire=False, aimx=0, aimy=0):", "def step(self, dt, mx=0, my=0, jump=False, fire=False, aimx=0, aimy=0, charging=False):", "step charge input", 2);
    p = once(p, "        if fire and self.throw_cd <= 0 and self.ammo:\n            self._fire(self.player, self._aim(self.player, self.boss))\n            self.throw_cd = .38", "        if charging:\n            self._begin_charge()\n        elif self.charge_active:\n            self._release_charge()\n        elif fire and self.throw_cd <= 0 and self.ammo:\n            self._fire(self.player, self._aim(self.player, self.boss))\n            self.throw_cd = .38", "hold and release charge");
    p = once(p, "        self._pickups()\n        self._pick_special_pots()", "        self._pickups()\n        if self.charge_active:\n            self.charge_count = min(self.ammo, self.charge_cap)\n        self._pick_special_pots()", "pickup increases charge");
    p = once(p, "'ammo': self.ammo, 'ammo_cap': self.player_pot_cap, 'boss_ammo': self.boss_ammo,", "'ammo': self.ammo, 'ammo_cap': self.player_pot_cap, 'boss_ammo': self.boss_ammo,\n                           'charging': self.charge_active, 'charge_count': self.charge_count, 'charge_cap': self.charge_cap,", "charge state");
    const methods = `
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
`;
    p = once(p, 'class ProjectileModule(_FeatureModule):\n    MODULE_NAME = "projectile"\n\n    def _fire', 'class ProjectileModule(_FeatureModule):\n    MODULE_NAME = "projectile"\n' + methods + '\n    def _fire', "projectile charge functions");
    p = once(p, "    def _advance_projectiles(self, dt):\n        for p in list(self.projectiles):", "    def _advance_projectiles(self, dt):\n        self._advance_charge_projectiles(dt)\n        for p in list(self.projectiles):\n            if p.get('charged'):\n                continue", "charge projectile dispatch");
    p = once(p, '    "_fire": "projectiles",', '    "_fire": "projectiles",\n    "_begin_charge": "projectiles",\n    "_release_charge": "projectiles",\n    "_advance_charge_projectiles": "projectiles",', "feature map");
    return p;
  });
  template("PAGE", p => once(p, "</style>", `
/* v184 result-screen QA: actions remain in the viewport in compact landscape. */
#end .end-panel{z-index:20!important;left:50%!important;width:min(96%,740px)!important;max-width:96%!important;min-height:44px;bottom:max(3%,env(safe-area-inset-bottom))!important;overflow:visible!important;box-sizing:border-box}
#end .end-btns{display:flex!important;flex-wrap:wrap!important;align-items:center!important;justify-content:center!important;gap:clamp(6px,1vw,14px)!important}
#end .end-btns .cta{display:inline-flex;align-items:center;justify-content:center;position:relative;z-index:2;min-height:36px;white-space:nowrap}
#end .end-btns .cta.hidden{display:none!important}
</style>`, "result actions CSS"));
  module("/modules/potbreaker/input.js", p => {
    p = once(p, "    this.fire = false;\n    this.dash = false;", "    this.fire = false;\n    this.fireReleasePending = false;\n    this.dash = false;", "input latch init");
    p = once(p, "    this.onFireUp = () => { this.fire = false; };", "    this.onFireUp = () => { if (this.fire) this.fireReleasePending = true; this.fire = false; };", "pointer release");
    p = once(p, "      if (event.code === 'Space') this.fire = false;", "      if (event.code === 'Space') { if (this.fire) this.fireReleasePending = true; this.fire = false; }", "space release");
    p = once(p, "this.fire = false; this.dash = false; };", "this.fire = false; this.fireReleasePending = false; this.dash = false; };", "blur cleanup");
    p = once(p, "    const actions = {fire: this.fire, dash: this.dash};\n    this.dash = false;", "    const actions = {fire: this.fireReleasePending, charging: this.fire, dash: this.dash};\n    this.fireReleasePending = false;\n    this.dash = false;", "charge input actions");
    p = once(p, "this.fire = false; this.dash = false;\n  }", "this.fire = false; this.fireReleasePending = false; this.dash = false;\n  }", "stop cleanup");
    return p;
  });
  module("/modules/potbreaker/main.js", p => {
    p = once(p, "{fire:fireNow,dash:dashNow}=controls.consumeActions();", "const {fire:fireNow,charging:chargingNow,dash:dashNow}=controls.consumeActions();", "forward charging");
    p = once(p, "game.step(.04,mx,my,dashNow,fireNow,0,0)", "game.step(.04,mx,my,dashNow,fireNow,0,0,chargingNow)", "step argument");
    p = once(p, "if(win)$('registerScore').classList.remove('hidden')}catch(error)", "}catch(error)", "remove async ranking gating");
    p = once(p, "if(activeRunId){try{await api('/api/runs/finish'", "if(win)$('registerScore').classList.remove('hidden');if(activeRunId){try{await api('/api/runs/finish'", "immediate victory ranking button");
    p = once(p, "if(!activeRunId||!nickname)return;", "if(!nickname)return;if(!activeRunId){$('rankingMessage').textContent='랭킹 등록을 위한 게임 기록이 없습니다. 다시 시작해 주세요.';return;}", "ranking session error");
    return p;
  });
  module("/modules/potbreaker/renderer.js", p => {
    const sparks = `
  function drawChargeSparks(s) {
    if (!s.charging) return;
    const n = Math.max(0, Math.min(3, s.charge_count || 0));
    for (let i = 0; i < n; i++) {
      const angle = tick * 3 + i * Math.PI * 2 / n - Math.PI / 2;
      const x = s.player[0] + .5 + Math.cos(angle) * .92;
      const y = s.player[1] + .15 + Math.sin(angle) * .68;
      ctx.save();ctx.translate(x,y);ctx.rotate(angle + Math.PI / 3);
      ctx.shadowColor='#a9efff';ctx.shadowBlur=.18;
      ctx.strokeStyle='#ffdf6b';ctx.lineWidth=.085;
      ctx.lineCap='round';ctx.lineJoin='round';
      ctx.beginPath();ctx.moveTo(-.12,-.22);ctx.lineTo(.02,-.04);
      ctx.lineTo(-.05,.02);ctx.lineTo(.16,.23);ctx.stroke();ctx.restore();
    }
  }
`;
    p = once(p, "  function draw(s){", sparks + "  function draw(s){", "1-3 sparks");
    p = once(p, "actor('keuda',s.boss,'boss');actor('gimyo',s.player,'player');for(const p of s.projectiles){plant(p.x+.5,p.y+.26,p.boss?.92:.52,true,p.boss?'boss':'player')}shatterFx();", "actor('keuda',s.boss,'boss');actor('gimyo',s.player,'player');drawChargeSparks(s);for(const p of s.projectiles){plant(p.x+.5,p.y+.26,(p.boss||p.charged)?.92:.52,true,p.boss?'boss':'player')}shatterFx();", "charged projectile big size");
    return p;
  });
  if (!source.includes("var GAME = `") || !source.includes("var BROWSER_MODULES = ")) throw Error("Invalid v184 bundle layout");
  return {code:source, applied};
}
module.exports = {patchWorkerBundle};
