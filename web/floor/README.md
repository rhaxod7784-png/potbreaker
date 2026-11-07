# Floor Breaker

`index.html` is the editable page. `floor.css` contains the original board styles, `theme.css` the POT BREAKER comic palette, `game.js` the game and AI, `i18n.js` the Korean/English/Japanese/Chinese UI, and `art.js` the character asset paths. `assets/` contains the four comic panels and chess-piece images.

Run `python scripts/build_floor.py` from the repository root to create `web/floor-standalone.html`, the self-contained page served by the Cloudflare Worker at `/floor`. Do not edit the generated file directly. Run `node tests/test_floor_rules.cjs` to check the core move and ability rules.

Deployment is done by replacing only the Worker's `FLOOR_PAGE` constant with the generated page. This preserves the main POT BREAKER game and its D1 binding. The main menu entry at `/` links to `/floor` after production verification.
