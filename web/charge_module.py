"""PotBreaker v1.1.1: separate charged-pot projectile feature."""
import math
try:
    from .game_modules import _FeatureModule
except ImportError:
    pass


class ChargeModule(_FeatureModule):
    MODULE_NAME = "charge"
    MAX_PENETRATION = 2

    def _begin_charge(self):
        if self.phase != "playing" or self.charge_active:
            return
        self.charge_active = True
        self.charge_count = min(self.ammo, self.charge_cap)
        self.ammo -= self.charge_count

    def _charge_pickup(self):
        if not self.charge_active or self.charge_count >= self.charge_cap:
            return False
        self.charge_count += 1
        return True

    def _release_charge(self):
        """Aim on release, then launch; NO instant damage to the boss."""
        if not self.charge_active:
            return 0
        count = self.charge_count
        self.charge_active, self.charge_count = False, 0
        if not count or self.phase != "playing":
            return 0
        direction = self._aim(self.player, self.boss)
        self.charge_projectiles.append({
            "x": float(self.player[0]), "y": float(self.player[1]),
            "dx": direction[0], "dy": direction[1],
            "range": math.hypot(WIDTH, HEIGHT) + 2.0,
            "boss": False, "charged": True, "large": True,
            "damage": count, "penetrated": 0, "last_wall": None,
        })
        self.notice, self.notice_time = f"모은 화분 {count}개 발사!", 1.1
        return count

    def _advance_charge_projectiles(self, dt):
        """Separate from regular throws; first two partitions pass, third blocks."""
        walls = self.walls | self.moving_walls
        for p in list(self.charge_projectiles):
            travel = min(max(0., dt) * 9.4, p["range"])
            if travel <= 0:
                self.charge_projectiles.remove(p)
                continue
            x0, y0 = p["x"], p["y"]
            stopped = False
            for i in range(1, max(1, math.ceil(travel * 16)) + 1):
                d = travel * i / max(1, math.ceil(travel * 16))
                x, y = x0 + p["dx"] * d, y0 + p["dy"] * d
                if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
                    self.charge_projectiles.remove(p)
                    stopped = True
                    break
                cell = (round(x), round(y))
                if cell in walls:
                    if p["last_wall"] != cell:
                        if p["penetrated"] >= self.MAX_PENETRATION:
                            self._break_pot(x, y)
                            self.charge_projectiles.remove(p)
                            stopped = True
                            break
                        p["penetrated"] += 1
                    p["last_wall"] = cell
                else:
                    p["last_wall"] = None
                if distance((x, y), self.boss) < .72:
                    for _ in range(p["damage"]):
                        if not self._damage(True, bypass_invulnerability=True):
                            break
                    self._break_pot(x, y)
                    self.charge_projectiles.remove(p)
                    stopped = True
                    if self.phase != "playing":
                        self.charge_projectiles.clear()
                        self.projectiles.clear()
                        return
                    break
            if stopped:
                continue
            p["x"], p["y"] = x0 + p["dx"] * travel, y0 + p["dy"] * travel
            p["range"] -= travel
            if p["range"] <= 0:
                self.charge_projectiles.remove(p)
                self._drop_pot(p["x"], p["y"])
