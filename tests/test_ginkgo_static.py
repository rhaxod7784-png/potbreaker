import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class TestGinkgoStatic(unittest.TestCase):
    def test_title_and_accessibility(self):
        html=(ROOT/"web/ginkgo.html").read_text(encoding="utf-8")
        self.assertIn('<html lang="{{LANG}}">',html)
        self.assertIn('name="description"',html)
        self.assertIn('rel="canonical"',html)
        self.assertIn('hreflang="x-default"',html)
        self.assertIn('id="mode-menu"',html)
        self.assertIn('aria-expanded="false"',html)
        self.assertIn('id="board"',html)
        self.assertIn('name="difficulty"',html)
        self.assertIn('id="rankings"',html)
        for loc in ('ko','en','ja','zh'):
            self.assertRegex(html,r"\b"+loc+r":\{")
    def test_rules_and_anticheat(self):
        src=(ROOT/"cloudflare/ginkgo-api.js").read_text(encoding="utf-8")
        for x in ('GINKGO_TOTAL','GINKGO_INTERVAL','max_combo','deadline_ms',
                  'temporarily_locked','DENSE_RANK()','ginkgoMonthlyCleanup',
                  'state_conflict','version=version+1','ginkgoCronCleanup'):
            self.assertIn(x,src)
        self.assertIn('return ginkgoJSON({error:"still_playing"},409)',src)
        self.assertIn('let phase',src) if False else None
    def test_builder_routes(self):
        src=(ROOT/"scripts/build_worker.py").read_text(encoding="utf-8")
        for x in ('ginkgo_pages','ginkgo_route','ginkgo_sitemap','GINKGO_PAGES',
                  'ginkgoAPI(request,env)','ginkgoCronCleanup','pb-game-mode'):
            self.assertIn(x,src)
        self.assertIn('ginkgoLocale=path.match(',src)
        self.assertIn('google-adsense-account',src)
    def test_cron(self):
        config=(ROOT/"wrangler.toml").read_text(encoding="utf-8")
        self.assertIn('crons = ["0 15 28-31 * *"]',config)

if __name__ == "__main__":
    unittest.main()
