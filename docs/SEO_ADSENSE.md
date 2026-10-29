# SEO and AdSense setup — POT BREAKER RE v1.0.97

## Search discovery
- The Worker serves `/robots.txt` and `/sitemap.xml`; the sitemap lists the game, game guide, and privacy/advertising notice.
- The home page, `/about`, and `/privacy` return HTML with Korean language metadata, a unique title/description, canonical URL, and Open Graph metadata.
- `/game.py` is a runtime resource and is sent with `X-Robots-Tag: noindex`; it is not included in the sitemap.
- In Search Console, verify the `potbreaker.com` domain property and submit `https://potbreaker.com/sitemap.xml`. Google may crawl and index eligible pages but submission does not guarantee indexing.

## AdSense script

The provided AdSense library tag is injected into the `<head>` of every HTML response: the home page and its language variants, `/about`, `/privacy`, and their localized routes. The publisher ID in the script is `ca-pub-7687564326575687`.

The script loads the library; it does not add an in-body ad unit. AdSense Auto Ads can still be controlled through the publisher account. The game page currently has no manually inserted ad unit beside its controls.

The editable source is `cloudflare/worker.template.js`; `cloudflare/worker.js` is generated and should not be edited by hand. The `ADSENSE_PUBLISHER_ID` Worker variable still controls the verification meta tag and `/ads.txt`. Without that variable, `/ads.txt` returns 404 even though the page-head script is present.

For personalized ads to users in the EEA, UK, or Switzerland, configure a Google-certified CMP and meet the applicable consent requirements before serving personalized ads. Keep the privacy notice aligned with actual advertising behavior.

Do not place ad units next to play, navigation, or game controls, or use pre-roll or auto-refresh.

## Privacy and accuracy
The privacy page describes game identifiers, selected difficulty, outcome, elapsed time, optional leaderboard nickname, Cloudflare D1 storage, and Google ad cookies when enabled. The current database does not implement automatic record expiry. Review the notice against the deployed data flow and applicable laws before enabling ads.

## Release verification
- Confirm production responses for `/`, `/about`, `/privacy`, `/robots.txt`, and `/sitemap.xml`.
- Confirm the publisher ID is absent until provided by the owner.
- Verify the deployed canonical host matches the Search Console property.
- Record Search Console crawl/index results separately; Worker deployment alone does not mean Google has indexed the site.
