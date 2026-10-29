"""Bundle Potbreaker source files into the Cloudflare Worker artifact.

Editable UI, styles, translations, and information pages stay under web/.
The browser fetches /game.py from the same Worker origin.
"""
from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
html = (root / "web" / "index.html").read_text(encoding="utf-8")
python_source = (root / "web" / "game.py").read_text(encoding="utf-8")
html = html.replace("화면을 원하는 방향으로 밀기: 누르고 있으면 계속 이동", "방향 패드를 눌러 이동 · 누르고 있으면 계속 이동")
html = html.replace("♥ 회복 · 감 과장: ? 화분 4종 (하트 ±1 · 화분 풀충전 · 필드 리셋, 각 25%) · 기묘: 대시 3초 / 크다: 대시 5초 · 화면을 밀어 방향 조작 · 누르고 있으면 계속 이동", "감 과장 화분: 회복 · 피해 · 화분 충전 · 필드 초기화 중 하나 · 대시 재사용: 기묘 3초 / 크다 5초 · 방향 패드를 눌러 이동")
touch_block = (root / "web/touch-controls.js").read_text(encoding="utf-8").rstrip() + "\n"
touch_start = html.index("let touchPointerId=null")
touch_end = html.index("window.addEventListener('keyup'", touch_start)
if touch_start < 0 or touch_end < 0:
    raise SystemExit("Touch control block not found in web/index.html")
html = html[:touch_start] + touch_block + html[touch_end:]

dpad_markup = (root / "web" / "partials" / "dpad.html").read_text(encoding="utf-8")
touch_target = '<div class="touch-layer"><div class="actions">'
if touch_target not in html:
    raise SystemExit("Mobile action markup not found in web/index.html")
html = html.replace(touch_target, '<div class="touch-layer">' + dpad_markup + '<div class="actions">', 1)
html = html.replace("화면을 밀어 방향 조작", "원형 조작부를 눌러 방향 이동")


# v1.0.97: crawlable site metadata, visible game guidance, and safe publisher gates.
html = html.replace("POT BREAKER RE v1.0.97 · CBZP", "폿브레이커 RE | 기묘와 크다 부장의 미로 게임", 1)
seo_head = (root / "web/partials/seo-head.html").read_text(encoding="utf-8")
if "</head>" not in html:
    raise SystemExit("HTML head not found for SEO metadata")
html = html.replace("</head>", seo_head + "\n</head>", 1)
site_info = (root / "web/partials/site-footer.html").read_text(encoding="utf-8")
html = html.replace("POT BREAKER RE v1.0.89", "POT BREAKER RE v1.0.97")
html = html.replace("POT BREAKER RE v1.0.54", "POT BREAKER RE v1.0.97")
html = html.replace("<title>POT BREAKER RE v1.0.97 · CBZP</title>", "<title>폿브레이커 RE | 기묘와 크다 부장의 사무실 미로</title>")
screen_switch = "const show=id=>['title','intro','gamePanel','end'].forEach(n=>$(n).classList.toggle('hidden',n!==id));show('title');"
if screen_switch not in html:
    raise SystemExit("Screen switch function not found")
html = html.replace(screen_switch, "const show=id=>{const active=id==='gamePanel'||id==='end';document.body.classList.toggle('pb-game-active',id==='gamePanel');['title','intro','gamePanel','end'].forEach(n=>$(n).classList.toggle('hidden',n!==id));const f=document.getElementById('site-footer');if(f)f.style.setProperty('display',active?'none':'grid','important');if(active)document.documentElement.style.setProperty('--pb-footer-h','0px');else document.documentElement.style.removeProperty('--pb-footer-h')};show('title');", 1)
game_start = "async function start(){\n stop();paused=false;show('gamePanel');"
if game_start not in html:
    raise SystemExit("Game start function not found")
html = html.replace(game_start, "async function start(){\n stop();paused=false;show('gamePanel');document.getElementById('site-footer')?.style.setProperty('display','none','important');", 1)

footer_state_script = "<script>\n" + (root / "web" / "footer-state.js").read_text(encoding="utf-8") + "\n</script>"
html = html.replace("</body>", site_info + "\n" + footer_state_script + "\n</body>", 1)





language_picker = (root / "web/partials/language-picker.html").read_text(encoding="utf-8")
menu_anchor = '<button class="menu-ranking" id="openRanking">🏆 랭킹</button>'
if menu_anchor not in html:
    raise SystemExit("Menu insertion point for language selector not found")
html = html.replace(menu_anchor, menu_anchor + language_picker, 1)

# Source styles and localization are maintained separately from the Worker bundle.
html = html.replace("</style>", (root / "web" / "styles" / "potbreaker.css").read_text(encoding="utf-8") + "\n</style>", 1)
language_script = "<script>\n" + (root / "web" / "language.js").read_text(encoding="utf-8") + "\n</script>"
html = html.replace("</body>", language_script + "\n</body>", 1)


worker_template = (root / "cloudflare" / "worker.template.js").read_text(encoding="utf-8")
bundle_values = {
    "__PAGE__": html,
    "__GAME__": python_source,
    "__SITE_ABOUT__": (root / "web" / "pages" / "about.html").read_text(encoding="utf-8"),
    "__SITE_PRIVACY__": (root / "web" / "pages" / "privacy.html").read_text(encoding="utf-8"),
}
for placeholder, value in bundle_values.items():
    if worker_template.count(placeholder) != 1:
        raise SystemExit(f"Expected exactly one {placeholder} placeholder in worker.template.js")
    worker_template = worker_template.replace(placeholder, json.dumps(value, ensure_ascii=False), 1)
worker = worker_template

(root / "cloudflare" / "worker.js").write_text(worker, encoding="utf-8")
print("Built cloudflare/worker.js", len(worker.encode("utf-8")), "bytes")
