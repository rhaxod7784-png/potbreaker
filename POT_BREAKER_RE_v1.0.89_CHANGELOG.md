# POT BREAKER RE v1.0.89 — SEO and AdSense readiness

**Release type:** PATCH  
**Date:** 2026-10-29

## Changed
- Added Korean-language title and description metadata, canonical URL, Open Graph metadata, and crawlable game guidance.
- Added `/about` and `/privacy` pages with semantic headings and internal navigation.
- Added `/robots.txt` and `/sitemap.xml` Worker routes.
- Added optional AdSense site-verification metadata and dynamic `/ads.txt` output when a valid publisher ID is configured.
- Gated the optional AdSense loader behind explicit Cloudflare variables and limited it to `/about`; the active game UI does not load ads.

## Fixed
- Made the game engine source non-indexable using the `X-Robots-Tag: noindex` response header.
- Added accessible, visible game instructions and links from the title screen.

## Code
- `scripts/build_worker.py`
- Generated `cloudflare/worker.js`
- `docs/SEO_ADSENSE.md`

## Reason
- Improve standards-based metadata, crawler discovery, useful indexable content, and safe ad readiness without putting advertisements beside game controls.

## AdSense activation
- No publisher ID was available during this release, so the live ad loader remains disabled.
- Do not enable the Cloudflare variables until the AdSense site is approved and privacy/consent requirements are ready.
