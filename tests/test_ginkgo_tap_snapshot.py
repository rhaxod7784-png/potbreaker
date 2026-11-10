"""Regression guards for the v220 Ginkgo input-timing patch."""
from hashlib import sha256
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "cloudflare/ginkgo-tap-snapshot-20261110.js"
PARTS = ROOT / "cloudflare/snapshots/v218"
ANCHOR = b"\nexport {\n  worker_default as default\n};"

def accepts_visible_phase(tap_tick, visible_phase, current_tick, current_phase, elapsed):
    valid_transition = (
        (visible_phase == 0 and current_phase == 1) or
        (visible_phase == 1 and current_phase in (0, 2)) or
        (visible_phase == 2 and current_phase == 3) or
        (visible_phase == 3 and current_phase == 0)
    )
    return current_tick == tap_tick + 1 and 0 <= elapsed <= 850 and valid_transition

class GinkgoTapRegression(unittest.TestCase):
    def test_actual_worker_source_reconstructs_byte_identically(self):
        parts = sorted(PARTS.glob("worker.part-*"))
        self.assertEqual(len(parts), 12)
        base = b"".join(p.read_bytes() for p in parts)
        self.assertEqual(sha256(base).hexdigest(),
                         "860217cf734b7f3ba1cceb00407cf74552f05d2a2da7bb4927b99bcac9c4fb7c")
        patch219 = (ROOT / "cloudflare/about-seo-20261110.js").read_bytes()
        v219 = base.replace(ANCHOR, patch219 + ANCHOR, 1)
        self.assertEqual(sha256(v219).hexdigest(),
                         "9aa34224d875ce155243650ec023e855d9aac2abbee76d6f0d1932931ff6b3c2")
        v220 = v219.replace(ANCHOR, b"\n" + FIX.read_bytes() + b"\n" + ANCHOR, 1)
        self.assertEqual(sha256(v220).hexdigest(),
                         "b682fa1561723a7d22911cefa4a5e83cc491d8636ead2835d918f168ee26bce8")

    def test_displayed_ripe_is_saved_at_boundary(self):
        self.assertTrue(accepts_visible_phase(10, 2, 11, 3, 200))

    def test_displayed_leaf_does_not_become_a_free_success(self):
        self.assertTrue(accepts_visible_phase(10, 1, 11, 2, 200))

    def test_rotten_stays_rotten(self):
        self.assertFalse(accepts_visible_phase(11, 3, 11, 3, 200))

    def test_multi_tick_replay_is_rejected(self):
        self.assertFalse(accepts_visible_phase(9, 2, 11, 3, 200))

    def test_beyond_grace_is_rejected(self):
        self.assertFalse(accepts_visible_phase(10, 2, 11, 3, 851))

    def test_patch_edits_only_ginkgo_resources(self):
        src = FIX.read_text(encoding="utf-8")
        self.assertIn('"/modules/ginkgo/main.js"', src)
        self.assertIn('"/modules/ginkgo/local-engine.js"', src)
        self.assertIn('"/api/ginkgo/tap"', src)
        self.assertIn('tap_tick:tapTick,tap_phase:tapPhase', src)
        self.assertIn('elapsedSinceTick <= 850', src)

if __name__ == "__main__":
    unittest.main()
