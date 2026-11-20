#!/usr/bin/env python3
"""Patch a downloaded *current live Cloudflare bundled* Worker, never legacy GitHub main.

Does not deploy. Cloudflare version 8e69221c-95db-414d-a268-297d27faa2f1
already contains the same patch.
"""
from pathlib import Path
import sys

OLD = 'if (path.startsWith("/api/") || path === "/game.py" || path === "/ginkgo/game.py" || path === "/floor" || path === "/floor/") {'
NEW = 'if (path.startsWith("/api/") || path === "/game.py" || path === "/ginkgo/game.py") {'
MARKER = "ADSENSE_REVIEW_FIX_20261121"
SNIPPET = """
/* ADSENSE_REVIEW_FIX_20261121: keep gameplay intact; correct Floor indexing. */
FLOOR_PAGE = FLOOR_PAGE.replace("</head>", '<meta name="robots" content="index,follow"><link rel="canonical" href="https://potbreaker.com/floor"><meta name="google-adsense-account" content="ca-pub-7687564326575687"></head>');
"""
EXPORT = "export {\n  worker_default as default\n};"

def main(source: str, destination: str) -> None:
    data = Path(source).read_text(encoding="utf-8")
    if MARKER in data:
        raise SystemExit("Already patched: do not patch again")
    if data.count(OLD) != 1:
        raise SystemExit("Expected live SEO guard missing or changed; not legacy main")
    if "var FLOOR_PAGE=" not in data or data.count(EXPORT) != 1:
        raise SystemExit("Live bundled Worker structure changed; abort")
    data = data.replace(OLD, NEW, 1)
    data = data.replace(EXPORT, SNIPPET + "\n" + EXPORT, 1)
    Path(destination).write_text(data, encoding="utf-8")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: patch_live_worker_adsense_review.py LIVE_BUNDLE.js PATCHED.js")
    main(sys.argv[1], sys.argv[2])
