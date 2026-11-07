"""Enable the Floor Breaker link in the production mode switcher.

The production Worker embeds MODE_SWITCHER as one JavaScript string. Keep this
replacement on a single line so that string syntax and the other game links stay intact.
"""
import re
import json
from pathlib import Path
import sys

ENTRY = ('<a id="pb-mode-floor" href="/floor">'
         '<span class="mode-ginkgo mode-ginkgo-ko">♟ 플로어 브레이커</span>'
         '<span class="mode-ginkgo mode-ginkgo-en">♟ Floor Breaker</span>'
         '<span class="mode-ginkgo mode-ginkgo-ja">♟ フロアブレイカー</span>'
         '<span class="mode-ginkgo mode-ginkgo-zh">♟ 地板破坏者</span></a>')
DISABLED = re.compile(r'<button id="pb-mode-floor"[^>]*>♟ FLOOR BREAKER · 준비 중</button>')
INJECTION = re.compile(r'(let localizedPage = PAGE\.replace\("</nav></details>", )(\"(?:[^\"\\]|\\.)*\")(\)\.replace)')

def enable(source: str) -> str:
    updated, count = DISABLED.subn(ENTRY, source)
    if count != 1:
        raise ValueError(f'Expected exactly one disabled Floor Breaker entry; found {count}')
    match = INJECTION.search(updated)
    if not match:
        raise ValueError('Could not find localized home page menu injection')
    menu = json.loads(match.group(2))
    menu, count = DISABLED.subn(ENTRY, menu)
    if count != 1:
        raise ValueError(f'Expected exactly one disabled localized entry; found {count}')
    updated = updated[:match.start(2)] + json.dumps(menu, ensure_ascii=False) + updated[match.end(2):]
    return updated

if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('Usage: enable_floor_entry.py input-worker.js output-worker.js')
    source = Path(sys.argv[1]).read_text(encoding='utf-8')
    Path(sys.argv[2]).write_bytes(enable(source).encode('utf-8'))
