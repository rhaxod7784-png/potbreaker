# SEO and AdSense setup — POT BREAKER RE v1.0.97

## Search discovery
- The Worker serves a crawlable `/robots.txt`, a plain-text `/sitemap.txt` containing 12 absolute canonical URLs, and an XML `/sitemap.xml` with localized alternate links. `/robots.txt` advertises `/sitemap.txt`, the supported one-URL-per-line format. Submit `https://potbreaker.com/sitemap.txt` in Search Console.
- The home page, `/about`, and `/privacy` return HTML with Korean language metadata, a unique title/description, canonical URL, and Open Graph metadata.
- `/game.py` is a runtime resource and is sent with `X-Robots-Tag: noindex`; it is not included in the sitemap. All 12 sitemap URLs return HTTP 200 and use matching self-canonical URLs.
- In Search Console, verify the `potbreaker.com` domain property and submit `https://potbreaker.com/sitemap.txt`. Google may crawl and index eligible pages but submission does not guarantee indexing.

## AdSense script

The provided AdSense library tag is injected into the `<head>` of every HTML response: the home page and its language variants, `/about`, `/privacy`, and their localized routes. The publisher ID in the script is `ca-pub-7687564326575687`.

The script loads the library; it does not add an in-body ad unit. AdSense Auto Ads can still be controlled through the publisher account. The game page currently has no manually inserted ad unit beside its controls.

The editable source is `cloudflare/worker.template.js`; `cloudflare/worker.js` is generated and should not be edited by hand. The `ADSENSE_PUBLISHER_ID` Worker variable controls the AdSense account-verification meta tag. `/ads.txt` is served at the root independently of that variable and contains `google.com, pub-7687564326575687, DIRECT, f08c47fec0942fa0`.

Before serving Google ads to users in the EEA, UK, or Switzerland, configure a Google-certified CMP and meet the applicable consent requirements. Keep this account-level setting aligned with the privacy notice.

The game response has no manually inserted ad unit. If Auto Ads is enabled in AdSense, review its placements on gameplay pages to keep ads clearly separate from play, navigation, and game controls. Do not use pre-roll or auto-refresh.

## Privacy and accuracy
The privacy page describes game identifiers, selected difficulty, outcome, elapsed time, optional leaderboard nickname, Cloudflare D1 storage, and Google ad cookies when enabled. The current database does not implement automatic record expiry. Review the notice against the deployed data flow and applicable laws before enabling ads.

## Release verification
- Confirm production responses for `/`, `/about`, `/privacy`, `/ads.txt`, `/robots.txt`, `/sitemap.txt`, and `/sitemap.xml`.
- Confirm `https://potbreaker.com/ads.txt` returns HTTP 200 with the publisher line, and that `robots.txt` allows crawling and points to `/sitemap.txt`.
- Verify the deployed canonical host matches the Search Console property.
- Record Search Console crawl/index results separately; Worker deployment alone does not mean Google has indexed the site.
