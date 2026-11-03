"""PotBreaker-only modular charge and multi-hit burst attack."""
try:
    from .game_modules import _FeatureModule
except ImportError:
    # The Cloudflare build concatenates the feature modules into one script.
    pass


class ChargeModule(_FeatureModule):
    MODULE_NAME = "charge"

    def _begin_charge(self):
        if self.phase != "playing" or self.charge_active:
            return
        self.charge_active = True
        # Move existing ammo into the burst. Each ordinary pot counts once.
        self.charge_count = min(self.ammo, self.charge_cap)
        self.ammo -= self.charge_count

    def _charge_pickup(self):
        """While holding Space, collect field pots beyond ordinary ammo capacity."""
        if not self.charge_active or self.charge_count >= self.charge_cap:
            return False
        self.charge_count += 1
        return True

    def _release_charge(self):
        """Release a burst with one HP of damage per collected ordinary pot."""
        if not self.charge_active:
            return 0
        count = self.charge_count
        self.charge_count = 0
        self.charge_active = False
        if not count or self.phase != "playing":
            return 0
        before = self.boss_hp
        for _ in range(count):
            if not self._damage(True, bypass_invulnerability=True):
                break
        dealt = before - self.boss_hp
        self.notice = f"화분 {count}개 모아 공격! 크다 HP -{dealt}"
        self.notice_time = 1.4
        return dealt
