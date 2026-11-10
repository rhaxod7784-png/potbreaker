# Floor Breaker

`index.html` is the editable page. `floor.css` contains the original board styles, `theme.css` the POT BREAKER comic palette, `game.js` the game and AI, `i18n.js` the Korean/English/Japanese/Chinese UI, and `art.js` the character asset paths. `assets/` contains the four comic panels and chess-piece images.

Run `python scripts/build_floor.py` from the repository root to create `web/floor-standalone.html`, the self-contained page served by the Cloudflare Worker at `/floor`. Do not edit the generated file directly. Run `node tests/test_floor_rules.cjs` to check the core move and ability rules.

Deployment uses `scripts/replace_floor_page.py` to replace only the Worker's `FLOOR_PAGE` constant with the generated page. This preserves later Worker code, the main POT BREAKER game, and its D1 binding. `scripts/enable_floor_entry.py` enables the four-language game selector link on an older Worker, and `scripts/add_floor_home_link.py` adds the small four-language `/floor` link beside the Daejeon travel link on the home screen.
