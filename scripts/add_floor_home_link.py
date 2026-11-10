"""Add Floor Breaker to the home page's small cross-game links.

The production Worker embeds the home HTML in its PAGE template literal.
This changes only that HTML, next to the existing Daejeon travel link.
"""
from pathlib import Path
import sys

LINK = ('<a id="openFloor" href="/floor">'
        '<span class="info-ko">♟ 플로어 브레이커</span>'
        '<span class="info-en">♟ Floor Breaker</span>'
        '<span class="info-zh">♟ 地板破坏者</span>'
        '<span class="info-ja">♟ フロアブレイカー</span></a>')


def add_link(source: str) -> str:
    if 'id="openFloor"' in source:
        return source
    travel = source.index('https://djgimyo.com/home.html')
    nav_end = source.index('</nav></section>', travel)
    if nav_end - travel > 2000:
        raise ValueError('Home cross-game links were not found near the travel link')
    return source[:nav_end] + LINK + source[nav_end:]


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('Usage: add_floor_home_link.py input-worker.js output-worker.js')
    source = Path(sys.argv[1]).read_text(encoding='utf-8')
    Path(sys.argv[2]).write_text(add_link(source), encoding='utf-8')
