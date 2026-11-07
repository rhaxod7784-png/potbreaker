"""Build the self-contained Floor Breaker page from its HTML, CSS, JS and image modules."""
from pathlib import Path
import base64
import json
import mimetypes
import re

root = Path(__file__).resolve().parents[1]
floor = root / 'web' / 'floor'
page = (floor / 'index.html').read_text(encoding='utf-8')
css = (floor / 'floor.css').read_text(encoding='utf-8') + '\n' + (floor / 'theme.css').read_text(encoding='utf-8')
i18n = (floor / 'i18n.js').read_text(encoding='utf-8')
game = (floor / 'game.js').read_text(encoding='utf-8')
art_source = (floor / 'art.js').read_text(encoding='utf-8')

def data_url(path):
    file = floor / path.removeprefix('./')
    mime = mimetypes.guess_type(file.name)[0] or 'application/octet-stream'
    return f'data:{mime};base64,{base64.b64encode(file.read_bytes()).decode("ascii")}'

css = re.sub(r'url\(["\']?(\./assets/[^)"\']+)["\']?\)',
             lambda m: f'url("{data_url(m.group(1))}")', css)

art_paths = json.loads(re.search(r'export const ART=(\{.*?\});', art_source).group(1))
art = {name: data_url(path) for name, path in art_paths.items()}
cleric_path = re.search(r'export const CLERIC_ART="([^"]+)";', art_source).group(1)
game = game.replace("import './i18n.js';", '', 1)
game = game.replace("import { ART, CLERIC_ART } from './art.js';", '', 1)
assert 'import ' not in game
i18n = re.sub(r'\bexport (function|const)\b', r'\1', i18n)
bundle = ('"use strict";\nconst ART=' + json.dumps(art, ensure_ascii=False) + ';\n'
          + 'const CLERIC_ART=' + json.dumps(data_url(cleric_path)) + ';\n'
          + i18n + '\n' + game)

page = page.replace('<link rel="stylesheet" href="./floor.css"><link rel="stylesheet" href="./theme.css">', '<style>' + css + '</style>', 1)
page = page.replace('<script type="module" src="./game.js"></script>', '<script>' + bundle + '</script>', 1)
page = re.sub(r'(?<=src=")\./assets/[^\"]+', lambda m: data_url(m.group(0)), page)
assert '<script type="module"' not in page and './assets/' not in page
output = root / 'web' / 'floor-standalone.html'
output.write_bytes(page.encode('utf-8'))
print(f'Built {output.relative_to(root)} ({len(page):,} characters)')
