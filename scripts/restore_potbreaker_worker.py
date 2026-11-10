"""Reconstruct the exact archived Cloudflare potbreaker Worker v218 bundle."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
parts = sorted((root / "cloudflare" / "snapshots" / "v218").glob("worker.part-*"))
if len(parts) != 12:
    raise SystemExit(f"Expected 12 parts; found {len(parts)}")
code = b"".join(part.read_bytes() for part in parts)
if b"POTBREAKER_GINKGO_SEO_20261110" not in code or b"POTBREAKER_SEO_ASSETS_20261110" not in code:
    raise SystemExit("Incomplete source bundle: SEO patch markers missing")
output = root / "cloudflare" / "production-v218.js"
output.write_bytes(code)
print(f"Restored {output} ({len(code):,} bytes)")
