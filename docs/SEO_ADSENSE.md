# SEO and AdSense setup — POT BREAKER RE v1.0.89

## Search discovery
- The Worker serves `/robots.txt` and `/sitemap.xml`; the sitemap lists the game, game guide, and privacy/advertising notice.
- The home page, `/about`, and `/privacy` return HTML with Korean language metadata, a unique title/description, canonical URL, and Open Graph metadata.
- `/game.py` is a runtime resource and is sent with `X-Robots-Tag: noindex`; it is not included in the sitemap.
- In Search Console, verify the `potbreaker.com` domain property and submit `https://potbreaker.com/sitemap.xml`. Google may crawl and index eligible pages but submission does not guarantee indexing.

## AdSense activation (not enabled by this release)
The game screen does not load the AdSense library. This avoids placing ads next to mobile movement, dash, throw, or pause controls. The optional loader is limited to `/about` and requires all of these Cloudflare Worker variables:

- `ADSENSE_PUBLISHER_ID`: exact account ID in `ca-pub-0000000000000000` format (16 digits).
- `ADSENSE_ENABLED=true`: only after the site is added and approved in AdSense and an ad placement has been reviewed.
- `ADSENSE_PRIVACY_READY=true`: only after the privacy notice has been reviewed and reflects the actual account setup.
- `ADSENSE_CONSENT_READY=true`: only after any required consent platform is configured. Google requires its certified CMP integrated with IAB TCF for personalized ads shown to users in the EEA, UK, and Switzerland.

When a valid publisher ID is configured, the Worker exposes the AdSense account-verification meta tag and generates the publisher line at `/ads.txt`. Without the ID, no placeholder publisher ID is emitted and `/ads.txt` returns 404. The script loader does not create an ad unit; placement/Auto Ads still requires deliberate setup in the AdSense console.

Do not place ads adjacent to play, navigation, or game controls; do not use pre-roll or auto-refresh. Google warns these arrangements can cause accidental clicks or interrupt access to games.

## Privacy and accuracy
The privacy page describes game identifiers, selected difficulty, outcome, elapsed time, optional leaderboard nickname, Cloudflare D1 storage, and Google ad cookies when enabled. The current database does not implement automatic record expiry. Review the notice against the deployed data flow and applicable laws before enabling ads.

## Release verification
- Confirm production responses for `/`, `/about`, `/privacy`, `/robots.txt`, and `/sitemap.xml`.
- Confirm the publisher ID is absent until provided by the owner.
- Verify the deployed canonical host matches the Search Console property.
- Record Search Console crawl/index results separately; Worker deployment alone does not mean Google has indexed the site.
