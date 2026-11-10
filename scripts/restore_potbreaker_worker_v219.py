"""Reconstruct the exact deployed potbreaker v219 Worker from archived v218 source and its SEO delta.

Does not deploy or alter the legacy cloudflare/worker.js file.
"""
from hashlib import sha256
from pathlib import Path

root = Path(__file__).resolve().parents[1]
parts = sorted((root / "cloudflare" / "snapshots" / "v218").glob("worker.part-*"))
if len(parts) != 12:
    raise SystemExit(f"Expected 12 archived v218 parts; found {len(parts)}")
base = b"".join(p.read_bytes() for p in parts)
expected_base = "860217cf734b7f3ba1cceb00407cf74552f05d2a2da7bb4927b99bcac9c4fb7c"
if sha256(base).hexdigest() != expected_base:
    raise SystemExit("v218 snapshot checksum mismatch; refusing reconstruction")
patch = (root / "cloudflare" / "about-seo-20261110.js").read_bytes()
if b"POTBREAKER_ABOUT_SEO_20261110" not in patch or not patch.startswith(b"\n//"):
    raise SystemExit("Missing or invalid v219 SEO delta")
anchor = b"\nexport {\n  worker_default as default\n};"
if base.count(anchor) != 1 or b"POTBREAKER_ABOUT_SEO_20261110" in base:
    raise SystemExit("Unexpected archived source; refusing reconstruction")
source = base.replace(anchor, patch + anchor, 1)
expected_v219 = "9aa34224d875ce155243650ec023e855d9aac2abbee76d6f0d1932931ff6b3c2"
if sha256(source).hexdigest() != expected_v219:
    raise SystemExit("v219 reconstructed bundle checksum mismatch")
output = root / "cloudflare" / "production-v219.js"
output.write_bytes(source)
print(f"Restored {output} ({len(source):,} bytes, SHA-256 {expected_v219})")
