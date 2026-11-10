"""Reconstruct the deployed v220 Worker from the exact v219 source plus Ginkgo tap patch.

Never deploys; never modifies the legacy cloudflare/worker.js.
"""
from hashlib import sha256
from pathlib import Path
import runpy

root = Path(__file__).resolve().parents[1]
runpy.run_path(str(root / "scripts" / "restore_potbreaker_worker_v219.py"))
old = (root / "cloudflare" / "production-v219.js").read_bytes()
patch = (root / "cloudflare" / "ginkgo-tap-snapshot-20261110.js").read_bytes()
marker = b"POTBREAKER_GINKGO_TAP_SNAPSHOT_20261110"
anchor = b"\nexport {\n  worker_default as default\n};"
if sha256(old).hexdigest() != "9aa34224d875ce155243650ec023e855d9aac2abbee76d6f0d1932931ff6b3c2":
    raise SystemExit("v219 source mismatch")
if not patch.startswith(b"/* ") or patch.count(marker) != 1 or old.count(anchor) != 1:
    raise SystemExit("Ginkgo patch or export anchor invalid")
updated = old.replace(anchor, b"\n" + patch + b"\n" + anchor, 1)
expected = "b682fa1561723a7d22911cefa4a5e83cc491d8636ead2835d918f168ee26bce8"
observed = sha256(updated).hexdigest()
if observed != expected:
    raise SystemExit(f"v220 checksum mismatch: {observed}")
output = root / "cloudflare" / "production-v220.js"
output.write_bytes(updated)
print(f"Restored {output} ({len(updated):,} bytes, SHA-256 {observed})")
