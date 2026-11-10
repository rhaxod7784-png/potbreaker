"""Replace only the standalone Floor page in a deployed Worker source bundle.

The surrounding Worker may gain unrelated code after FLOOR_PAGE, so find the
string assignment's own terminator instead of assuming it precedes exports.
"""
from pathlib import Path
import json
import sys


def replace_floor_page(source: str, page: str) -> str:
    start = source.rfind('var FLOOR_PAGE=')
    if start < 0:
        raise ValueError('FLOOR_PAGE assignment not found')
    end = source.find(';\n', start)
    if end < 0 or not source[start + len('var FLOOR_PAGE='):end].startswith('"'):
        raise ValueError('FLOOR_PAGE assignment terminator not found')
    return source[:start] + 'var FLOOR_PAGE=' + json.dumps(page, ensure_ascii=False) + source[end:]


if __name__ == '__main__':
    if len(sys.argv) != 4:
        raise SystemExit('Usage: replace_floor_page.py input-worker.js page.html output-worker.js')
    source = Path(sys.argv[1]).read_text(encoding='utf-8')
    page = Path(sys.argv[2]).read_text(encoding='utf-8')
    Path(sys.argv[3]).write_text(replace_floor_page(source, page), encoding='utf-8')
