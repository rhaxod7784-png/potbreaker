# Full production Worker v218 snapshot

The deployed Cloudflare script was archived in 12 contiguous UTF-8 files to accommodate the GitHub integration transfer limit.

Run `python scripts/restore_potbreaker_worker.py` from the repository root. The script reconstructs `cloudflare/production-v218.js` without editing the existing build inputs.

Production version: `9a789f8f-4ad9-49b3-8625-2f66789d0f02`.

**Do not deploy the older `cloudflare/worker.js` or legacy build scripts over production v218.** The snapshot preserves v218's game code and SEO patches; it has not been made the default build input.
