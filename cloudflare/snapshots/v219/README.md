# Complete production potbreaker Worker v219 (reconstructable)

v219 is reconstructed from the existing, exact v218 snapshot (12 parts) plus the small deployed v219 patch at `cloudflare/about-seo-20261110.js`.

Run `python scripts/restore_potbreaker_worker_v219.py` from the repository root. It verifies SHA-256 of both the v218 baseline and reconstructed v219 source before writing `cloudflare/production-v219.js`. It never deploys.

Cloudflare deployed Worker version: `f56b3d7f-1d73-4756-b36c-950c259cb50a`. This archive preserves the full game bundle and the earlier v216-v218 SEO patches.

**Do not deploy the legacy `cloudflare/worker.js` or run the legacy v184 build script over production.** The archived source is a reconstructed reference, not yet wired to automated deployment.
