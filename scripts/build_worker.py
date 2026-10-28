"""Build illustrated POT BREAKER RE v1.0.91 for Cloudflare Workers.

Inputs: web/index.html (images + UI bundled) and web/game.py (Python core).
Unlike the original v1.0.0 builder, this does not expect an inline Python script
inside HTML. The browser fetches /game.py from the same Worker origin.
"""
from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
html = (root / "web" / "index.html").read_text(encoding="utf-8")
python_source = (root / "web" / "game.py").read_text(encoding="utf-8")
touch_block = "let touchDirection=[0,0],touchActive=false,dpadOrder=0;\nconst keyDirections={ArrowUp:'up',KeyW:'up',ArrowDown:'down',KeyS:'down',ArrowLeft:'left',KeyA:'left',ArrowRight:'right',KeyD:'right'};\nconst dpadDirections={up:[0,-1],down:[0,1],left:[-1,0],right:[1,0]};\nconst dpadPointers=new Map();\nconst dpad=document.getElementById('dpad');\nfor(const [direction,glyph] of [['up','▲'],['right','▶'],['down','▼'],['left','◀']]){const icon=document.createElement('span');icon.className='dpad-icon '+direction;icon.textContent=glyph;dpad.appendChild(icon)}\nfunction refreshDpad(){\n let last=null;for(const p of dpadPointers.values())if(p.direction&&(!last||p.order>last.order))last=p;\n dpad.classList.remove('active-up','active-down','active-left','active-right');\n touchActive=!!last;touchDirection=last?dpadDirections[last.direction]:[0,0];\n if(last)dpad.classList.add('active-'+last.direction);\n}\nfunction directionAt(e){\n const rect=dpad.getBoundingClientRect(),dx=(e.clientX-(rect.left+rect.width/2))/(rect.width/2),dy=(e.clientY-(rect.top+rect.height/2))/(rect.height/2),radius=Math.hypot(dx,dy);\n if(radius>1.2||radius<.10)return null;\n const hit=document.elementFromPoint(e.clientX,e.clientY)?.closest?.('#dpad .dpad-button');\n if(hit?.dataset.direction)return hit.dataset.direction;\n return Math.abs(dx)>Math.abs(dy)?(dx<0?'left':'right'):(dy<0?'up':'down');\n}\nfunction setPointerDirection(e,p){\n const direction=directionAt(e);if(direction===p.direction)return;\n if(p.button)p.button.classList.remove('pressed');\n p.direction=direction;p.button=direction?dpad.querySelector('.dpad-button.'+direction):null;p.order=++dpadOrder;\n if(p.button)p.button.classList.add('pressed');refreshDpad();\n}\nfunction clearDpadPointer(id){\n const p=dpadPointers.get(id);if(!p)return;\n if(p.button)p.button.classList.remove('pressed');dpadPointers.delete(id);refreshDpad();\n}\nfunction moveDpadPointer(e){const p=dpadPointers.get(e.pointerId);if(p)setPointerDirection(e,p)}\ndpad.addEventListener('pointerdown',e=>{\n if(!active||paused)return;e.preventDefault();\n const direction=directionAt(e);if(!direction)return;\n const prior=dpadPointers.get(e.pointerId);if(prior&&prior.button)prior.button.classList.remove('pressed');\n const p={button:null,direction:null,order:++dpadOrder};dpadPointers.set(e.pointerId,p);setPointerDirection(e,p);\n try{dpad.setPointerCapture(e.pointerId)}catch{}\n});\nwindow.addEventListener('pointermove',moveDpadPointer);\nwindow.addEventListener('pointerup',e=>clearDpadPointer(e.pointerId));\nwindow.addEventListener('pointercancel',e=>clearDpadPointer(e.pointerId));\nfunction resetTouch(){for(const p of dpadPointers.values())if(p.button)p.button.classList.remove('pressed');dpadPointers.clear();touchActive=false;touchDirection=[0,0];dpad.classList.remove('active-up','active-down','active-left','active-right')}\n"
touch_start = html.index("let touchPointerId=null")
touch_end = html.index("window.addEventListener('keyup'", touch_start)
if touch_start < 0 or touch_end < 0:
    raise SystemExit("Touch control block not found in web/index.html")
html = html[:touch_start] + touch_block + html[touch_end:]

dpad_markup = "<div class=\"dpad\" id=\"dpad\" role=\"group\" aria-label=\"방향 이동\"><button class=\"dpad-button up\" data-direction=\"up\" aria-label=\"위로 이동\"><span class=\"dpad-arrow\">▲</span></button><button class=\"dpad-button left\" data-direction=\"left\" aria-label=\"왼쪽 이동\"><span class=\"dpad-arrow\">◀</span></button><button class=\"dpad-button right\" data-direction=\"right\" aria-label=\"오른쪽 이동\"><span class=\"dpad-arrow\">▶</span></button><button class=\"dpad-button down\" data-direction=\"down\" aria-label=\"아래로 이동\"><span class=\"dpad-arrow\">▼</span></button></div>"
touch_target = '<div class="touch-layer"><div class="actions">'
if touch_target not in html:
    raise SystemExit("Mobile action markup not found in web/index.html")
html = html.replace(touch_target, '<div class="touch-layer">' + dpad_markup + '<div class="actions">', 1)
html = html.replace("화면을 밀어 방향 조작", "원형 조작부를 눌러 방향 이동")
dpad_css = """
#dpad{position:absolute!important;left:1.5%!important;bottom:1.5%!important;top:auto!important;right:auto!important;width:clamp(184px,24cqw,232px)!important;height:clamp(184px,24cqw,232px)!important;aspect-ratio:1;display:block!important;padding:0!important;overflow:visible!important;border:3px solid #ffffffed!important;border-radius:50%!important;background:linear-gradient(45deg,transparent 49.4%,#ffffffdc 49.7%,#ffffffdc 50.3%,transparent 50.6%),linear-gradient(-45deg,transparent 49.4%,#ffffffdc 49.7%,#ffffffdc 50.3%,transparent 50.6%),conic-gradient(from -45deg,#d9eafa88 0deg 90deg,#c8def488 90deg 180deg,#d9eafa88 180deg 270deg,#c8def488 270deg 360deg)!important;box-shadow:0 4px 12px #31486b55!important;touch-action:none!important;user-select:none;-webkit-user-select:none}
#dpad>.dpad-button{position:absolute!important;inset:0!important;display:flex!important;align-items:center!important;justify-content:center!important;width:100%!important;height:100%!important;padding:0!important;border:1px solid #ffffffa8!important;border-radius:0!important;background:transparent!important;color:#344f83!important;font-size:clamp(28px,4cqw,42px)!important;font-weight:1000;box-shadow:none!important;pointer-events:auto!important;touch-action:none!important;clip-path:none!important}
#dpad>.dpad-button.up{clip-path:polygon(0 0,100% 0,50% 50%)!important;align-items:flex-start!important;padding-top:12%!important}
#dpad>.dpad-button.right{clip-path:polygon(100% 0,100% 100%,50% 50%)!important;justify-content:flex-end!important;padding-right:12%!important}
#dpad>.dpad-button.down{clip-path:polygon(0 100%,100% 100%,50% 50%)!important;align-items:flex-end!important;padding-bottom:12%!important}
#dpad>.dpad-button.left{clip-path:polygon(0 0,50% 50%,0 100%)!important;justify-content:flex-start!important;padding-left:12%!important}
#dpad>.dpad-button.pressed{filter:brightness(1.18) saturate(1.15)!important;transform:none!important;background:#ffdc7a66!important}
#dpad:after{content:"";position:absolute;left:42%;top:42%;width:16%;height:16%;border:2px solid #ffffffd9;border-radius:50%;background:#dcecff70;box-shadow:0 1px 4px #334a6c55;pointer-events:none;z-index:5}
.action.fire{width:clamp(110px,13cqw,148px)!important;min-width:0;min-height:0}.action.fire .symbol{font-size:clamp(28px,4cqw,46px)!important}
@media (orientation:portrait) and (pointer:coarse){#dpad{left:1.5%!important;bottom:1.5%!important;top:auto!important;right:auto!important}}
"""
html = html.replace("</style>", dpad_css + "\n</style>", 1)


# v1.0.91: crawlable site metadata, visible game guidance, and safe publisher gates.
html = html.replace("POT BREAKER RE v1.0.91 · CBZP", "폿브레이커 RE | 기묘와 크다 부장의 미로 게임", 1)
seo_head = """
<meta name="description" content="기묘를 조작해 CBZP 사무실 미로에서 크다 부장과 대결하는 무료 브라우저 게임. 게임 소개, 조작법, 개인정보 및 광고 안내를 확인하세요.">
<link rel="canonical" href="https://potbreaker.com/">
<link rel="alternate" hreflang="ko" href="https://potbreaker.com/">
<link rel="alternate" hreflang="en" href="https://potbreaker.com/en">
<link rel="alternate" hreflang="zh" href="https://potbreaker.com/zh">
<link rel="alternate" hreflang="ja" href="https://potbreaker.com/ja">
<meta property="og:type" content="website">
<meta property="og:locale" content="ko_KR">
<meta property="og:site_name" content="POT BREAKER RE">
<meta property="og:title" content="폿브레이커 RE | 기묘와 크다 부장의 사무실 미로">
<meta property="og:description" content="고양이 인턴 기묘와 악어 부장 크다의 CBZP 사무실 미로 추격전.">
<meta property="og:url" content="https://potbreaker.com/">
<meta name="twitter:card" content="summary">
"""
if "</head>" not in html:
    raise SystemExit("HTML head not found for SEO metadata")
html = html.replace("</head>", seo_head + "\n</head>", 1)
site_info = """<footer class="site-footer" id="site-footer">
<section class="site-guide" aria-labelledby="seo-heading">
<div class="site-guide-copy">
<h1 id="seo-heading">기묘와 크다 부장의 사무실 미로 추격전</h1>
<p>CBZP 인턴 고양이 기묘가 이동 파티션으로 이루어진 사무실에서 크다 부장을 피해 화분을 던지는 1인용 브라우저 게임입니다.</p>
</div>
<details class="site-guide-howto"><summary>게임 방법</summary><p>방향 패드로 이동하고, 대시로 위험을 피하며, 투척 버튼으로 화분을 던지세요. 기묘와 크다 부장의 체력 중 먼저 0이 되면 경기가 끝납니다.</p></details>
<nav aria-label="게임 안내"><a href="/about">게임 소개와 조작법</a><a href="/privacy">개인정보 및 광고 안내</a></nav>
</section>
</footer>"""
seo_css = """
:root{--pb-footer-h:clamp(72px,9vh,104px)}
.viewport{display:flex!important;align-items:center!important;justify-content:center!important;overflow:hidden!important;background:linear-gradient(135deg,#c8e8ff,#9acaf6)!important}
.stage{flex:0 0 auto!important}
html,body{height:auto!important;min-height:100%!important;overflow-x:hidden!important;overflow-y:auto!important}
body{min-height:100dvh!important}
.viewport{height:calc(100dvh - var(--pb-footer-h))!important;min-height:280px;box-sizing:border-box}
.stage{width:min(100vw,calc((100dvh - var(--pb-footer-h))*1.77778))!important;height:min(calc(100dvh - var(--pb-footer-h)),56.25vw)!important}
.site-footer{position:relative;z-index:50;width:100%;min-height:var(--pb-footer-h);box-sizing:border-box;display:grid;place-items:center;padding:8px clamp(12px,2vw,28px);background:linear-gradient(100deg,#dff5ff,#b9e0fa 55%,#99cdf2);border-top:1px solid #ffffffc7;color:#293b60}
.site-guide{width:min(100%,1280px);display:grid;grid-template-columns:minmax(0,1fr) auto auto;align-items:center;gap:clamp(8px,1.6vw,22px)}
.site-guide-copy h1{margin:0 0 3px;font-size:clamp(11px,1.15vw,16px);line-height:1.2}.site-guide-copy p{margin:0;font-size:clamp(9px,.9vw,12px);line-height:1.35}
.site-guide-howto{position:relative;font-size:clamp(9px,.9vw,12px)}.site-guide-howto summary{cursor:pointer;font-weight:800;white-space:nowrap}.site-guide-howto p{max-width:min(55vw,520px);margin:6px 0 0}
.site-guide nav{display:flex;gap:clamp(6px,1vw,14px);flex-wrap:wrap;justify-content:flex-end;font-size:clamp(9px,.9vw,12px)}.site-guide a{color:#244e70;text-underline-offset:2px}
#title .start-art-button{display:grid!important;place-items:center!important;box-sizing:border-box;background:linear-gradient(180deg,#ffe475,#ffc83f)!important;border:3px solid #5c4222!important;color:#24324c!important;font-size:clamp(15px,2cqw,25px)!important;font-weight:1000;line-height:1;box-shadow:0 4px 0 #8e5d24!important;text-shadow:0 1px 0 #fff8}

.comic-cover-wrap{position:relative;width:100%;height:100%;min-width:0;min-height:0;max-height:100%;overflow:hidden}
.comic-cover-wrap>.comic-cover{display:block;width:100%;height:100%;min-width:0;min-height:0;max-height:100%;object-fit:contain}
.comic-translation-layer{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:3}
@media(max-width:700px){:root{--pb-footer-h:clamp(78px,11vh,116px)}.site-guide{grid-template-columns:minmax(0,1fr) auto;gap:4px 10px}.site-guide-copy{grid-column:1/-1}.site-guide nav{justify-content:flex-start}.site-guide-howto p{max-width:80vw}}
@media(orientation:portrait) and (pointer:coarse){
 .viewport{position:relative!important;inset:auto!important;height:calc(100dvh - var(--pb-footer-h))!important;min-height:220px!important;width:100vw!important;display:block!important;overflow:hidden!important}
 .stage{position:absolute!important;left:50%!important;top:50%!important;width:min(calc(100dvh - var(--pb-footer-h)),177.778vw)!important;height:min(100vw,calc((100dvh - var(--pb-footer-h))*0.5625))!important;transform:translate(-50%,-50%) rotate(90deg)!important;transform-origin:center center!important}
}
@media(orientation:landscape){.viewport{height:calc(100dvh - var(--pb-footer-h))!important}}
"""
html = html.replace("</style>", seo_css + "\n</style>", 1)
html = html.replace("POT BREAKER RE v1.0.89", "POT BREAKER RE v1.0.91")
html = html.replace("POT BREAKER RE v1.0.54", "POT BREAKER RE v1.0.91")
html = html.replace("<title>POT BREAKER RE v1.0.91 · CBZP</title>", "<title>폿브레이커 RE | 기묘와 크다 부장의 사무실 미로</title>")
html = html.replace("</body>", site_info + "\n</body>", 1)


language_css = """
.legend{pointer-events:auto!important;display:flex;align-items:center;justify-content:center;gap:8px;width:min(94%,900px);max-width:94%;box-sizing:border-box;white-space:normal;flex-wrap:wrap}
.locale-control{display:inline-flex;align-items:center;pointer-events:auto;position:relative;z-index:20}
.locale-control select{pointer-events:auto;appearance:auto;max-width:104px;padding:4px 20px 4px 9px;border:1px solid #ffffffed;border-radius:999px;background:#fffef4;color:#293b60;font:700 clamp(9px,1cqw,12px)/1.2 system-ui,sans-serif;box-shadow:0 2px 7px #34486b36;touch-action:manipulation}
.locale-control select:focus-visible{outline:3px solid #f0bd48;outline-offset:2px}
.locale-control .sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
@media(max-width:700px){.legend{width:96%;max-width:96%;gap:5px}.locale-control select{max-width:90px;padding:4px 16px 4px 7px}}
"""
language_css += "\n.menu .locale-control{position:absolute;right:4%;bottom:4%;z-index:6}\n"
html = html.replace("</style>", language_css + "\n</style>", 1)
language_picker = """<label class="locale-control"><span class="sr-only">언어 선택</span><select id="pb-locale" aria-label="언어 변경"><option value="ko">한국어</option><option value="en">English</option><option value="zh">中文</option><option value="ja">日本語</option></select></label>"""
menu_anchor = '<button class="menu-ranking" id="openRanking">🏆 랭킹</button>'
if menu_anchor not in html:
    raise SystemExit("Menu insertion point for language selector not found")
html = html.replace(menu_anchor, menu_anchor + language_picker, 1)

language_script = r"""<script>
(()=> {
const dictionaries = {
en: {
"폿브레이커 RE | 기묘와 크다 부장의 사무실 미로":"POT BREAKER RE | Gimyo vs. Manager Keuda",
"POT BREAKER RE v1.0.91":"POT BREAKER RE v1.0.91",
"기묘가 CBZP에 출근하고, 이상한 사무실에서 화분을 피하고 크다 부장에게 쫓기는 4컷 만화":"A four-panel comic: Gimyo starts at CBZP, dodges flying pots, and is chased by Manager Keuda.",
"기묘와 크다 부장의 사무실 미로 추격전":"Office Maze Chase: Gimyo vs. Manager Keuda",
"CBZP 인턴 고양이 기묘가 이동 파티션으로 이루어진 사무실에서 크다 부장을 피해 화분을 던지는 1인용 브라우저 게임입니다.":"Play as Gimyo, a CBZP cat intern. Dodge Manager Keuda and throw pots in this browser maze game.",
"기묘를 조작해 CBZP 사무실 미로에서 크다 부장과 대결하는 무료 브라우저 게임. 게임 소개, 조작법, 개인정보 및 광고 안내를 확인하세요.":"A free browser maze game: guide Gimyo through the CBZP office. Read the game guide, controls, privacy and advertising information.",
"고양이 인턴 기묘와 악어 부장 크다의 CBZP 사무실 미로 추격전.":"A CBZP office maze chase starring cat intern Gimyo and crocodile manager Keuda.",
"게임 시작":"Start Game","🏆 랭킹":"🏆 Rankings","게임 방법":"How to Play",
"방향 패드로 이동하고, 대시로 위험을 피하며, 투척 버튼으로 화분을 던지세요. 기묘와 크다 부장의 체력 중 먼저 0이 되면 경기가 끝납니다.":"Move with the directional pad, dash to dodge, and throw pots. The match ends when either character runs out of HP.",
"게임 소개와 조작법":"Game Guide & Controls","개인정보 및 광고 안내":"Privacy & Ads",
"이상한 회사의":"A Strange","인턴 생활":"Company Internship","정말... 이 회사에서":"Can I really survive","살아남을 수 있을까?":"at this company?",
"난이도":"Difficulty","노멀":"Normal","하드":"Hard","베리 하드":"Very Hard","베리 하드":"Very Hard","베리 하드":"Very Hard",
"사무실로 입장 ▶":"Enter the Office ▶","기묘 / PLAYER":"Gimyo / PLAYER","크다 부장 / NPC":"Manager Keuda / NPC",
"대시":"Dash","던지기":"Throw","↻ 다시 도전":"↻ Play Again","처음으로":"Home","랭킹 등록":"Submit Score",
"🏆 POT BREAKER 랭킹":"🏆 POT BREAKER Rankings","닉네임":"Nickname","최대 16자":"Up to 16 characters",
"랭킹을 불러오는 중…":"Loading rankings…","사무실 문을 열고 있습니다":"Opening the office door","Python 게임 엔진을 준비하고 있습니다.":"Preparing the Python game engine.",
"다시 시도하기":"Try Again","잠깐 휴식!":"Take a Break!","계속하기":"Resume","아직 등록된 클리어 기록이 없습니다.":"No completed runs have been recorded yet.",
"랭킹을 불러오지 못했습니다.":"Could not load rankings.","서버 연결에 실패했습니다.":"Could not connect to the server.",
"랭킹에 등록했습니다.":"Score submitted.","Pyodide를 불러오지 못했습니다. 인터넷 연결을 확인해 주세요.":"Could not load Pyodide. Check your internet connection.",
"게임 엔진을 불러오지 못했습니다.":"Could not load the game engine.","게임을 불러오지 못했습니다.":"Could not load the game.",
"게임 화면 갱신 오류:":"Game screen update error:","기묘 승리!":"Gimyo Wins!","크다 부장 승리!":"Manager Keuda Wins!",
"화분 한 방! 크다 부장의 뚝배기를 깼습니다.":"One pot hit! Manager Keuda is down.","기묘가 화분에 머리만 내놓고 심어졌습니다…":"Gimyo got planted with only their head above the pot…",
"쨍그랑!":"Crash!","감 과장":"Manager Gam","랭킹 닫기":"Close rankings",
"♥ 회복 · 감 과장: ? 화분 4종 (하트 ±1 · 화분 풀충전 · 필드 리셋, 각 25%) · 기묘: 대시 3초 / 크다: 대시 5초 · 원형 조작부를 눌러 방향 이동 · 누르고 있으면 계속 이동":"♥ Heal · Manager Gam: 4 random pot effects (±1 heart, refill pots, reset field; 25% each) · Gimyo dash: 3s / Keuda dash: 5s · Use the circular pad to move; hold to keep moving",
"원형 조작부를 눌러 방향 이동 · 누르고 있으면 계속 이동":"Use the circular pad to move · Hold to keep moving",
"화분: 공격 · 대시 버튼: 3칸 돌진 (3초 재사용)":"Pots: attack · Dash: 3 tiles (3s cooldown)",
"PC: 방향키 / WASD · Space(공격) · Shift(대시)":"PC: Arrows / WASD · Space (throw) · Shift (dash)",
"언어 변경":"Change language","언어 선택":"Select language","게임 안내":"Game Guide"
"대시 버튼: 3칸 돌진 · 3초 재사용 대기":"Dash: move 3 tiles · 3-second cooldown",
"감 과장 출동!":"Manager Gam is here!",
"화분 투하!":"Pots incoming!",
"크다":"Keuda",
"기묘":"Gimyo",
"회복 화분! HP +1":"Healing pot! HP +1",
"회복 화분을 찾았지만 HP가 가득 찼습니다.":"You found a healing pot, but your HP is already full.",
"화분 폭발!":"Pot exploded!",
"화분 회복!":"Healing pot!",
"화분 풀충전!":"Pots refilled!",
"필드 화분 리셋!":"Field pots reset!",
"감 과장 명중!":"Manager Gam hit!"
},
zh: {
"폿브레이커 RE | 기묘와 크다 부장의 사무실 미로":"POT BREAKER RE｜奇妙与克达部长",
"기묘와 크다 부장의 사무실 미로 추격전":"奇妙与克达部长的办公室迷宫追逐战",
"CBZP 인턴 고양이 기묘가 이동 파티션으로 이루어진 사무실에서 크다 부장을 피해 화분을 던지는 1인용 브라우저 게임입니다.":"扮演 CBZP 实习猫奇妙，在办公室迷宫中躲避克达部长并投掷花盆的单人网页游戏。",
"기묘를 조작해 CBZP 사무실 미로에서 크다 부장과 대결하는 무료 브라우저 게임. 게임 소개, 조작법, 개인정보 및 광고 안내를 확인하세요.":"免费浏览器迷宫游戏：操控奇妙在 CBZP 办公室中挑战克达部长。查看游戏介绍、操作、隐私与广告说明。",
"고양이 인턴 기묘와 악어 부장 크다의 CBZP 사무실 미로 추격전.":"猫咪实习生奇妙与鳄鱼部长克达在 CBZP 办公室迷宫展开追逐。",
"게임 시작":"开始游戏","🏆 랭킹":"🏆 排行榜","게임 방법":"游戏方法",
"방향 패드로 이동하고, 대시로 위험을 피하며, 투척 버튼으로 화분을 던지세요. 기묘와 크다 부장의 체력 중 먼저 0이 되면 경기가 끝납니다.":"使用方向键移动、冲刺躲避，并投掷花盆。奇妙或克达部长任一方生命值归零时，比赛结束。",
"게임 소개와 조작법":"游戏介绍与操作","개인정보 및 광고 안내":"隐私与广告",
"이상한 회사의":"奇怪公司的","인턴 생활":"实习生活","정말... 이 회사에서":"真的……我能在这家公司","살아남을 수 있을까?":"活下来吗？",
"난이도":"难度","노멀":"普通","하드":"困难","베리 하드":"极难","사무실로 입장 ▶":"进入办公室 ▶",
"기묘 / PLAYER":"奇妙 / 玩家","크다 부장 / NPC":"克达部长 / NPC","대시":"冲刺","던지기":"投掷",
"↻ 다시 도전":"↻ 再试一次","처음으로":"返回首页","랭킹 등록":"提交排行","🏆 POT BREAKER 랭킹":"🏆 POT BREAKER 排行榜",
"닉네임":"昵称","최대 16자":"最多16个字符","랭킹을 불러오는 중…":"正在加载排行榜…","사무실 문을 열고 있습니다":"正在打开办公室的门",
"Python 게임 엔진을 준비하고 있습니다.":"正在准备 Python 游戏引擎。","다시 시도하기":"重试","잠깐 휴식!":"休息一下！","계속하기":"继续",
"아직 등록된 클리어 기록이 없습니다.":"暂无通关记录。","랭킹을 불러오지 못했습니다.":"无法加载排行榜。",
"서버 연결에 실패했습니다.":"连接服务器失败。","랭킹에 등록했습니다.":"已提交排行。","Pyodide를 불러오지 못했습니다. 인터넷 연결을 확인해 주세요.":"无法加载 Pyodide，请检查网络连接。",
"게임 엔진을 불러오지 못했습니다.":"无法加载游戏引擎。","게임을 불러오지 못했습니다.":"无法加载游戏。","게임 화면 갱신 오류:":"游戏画面更新错误：",
"기묘 승리!":"奇妙获胜！","크다 부장 승리!":"克达部长获胜！","화분 한 방! 크다 부장의 뚝배기를 깼습니다.":"花盆一击！克达部长被击倒了。",
"기묘가 화분에 머리만 내놓고 심어졌습니다…":"奇妙被种进花盆，只露出了脑袋……","쨍그랑!":"哐当！","감 과장":"甘科长",
"랭킹 닫기":"关闭排行榜",
"♥ 회복 · 감 과장: ? 화분 4종 (하트 ±1 · 화분 풀충전 · 필드 리셋, 각 25%) · 기묘: 대시 3초 / 크다: 대시 5초 · 원형 조작부를 눌러 방향 이동 · 누르고 있으면 계속 이동":"♥ 回复 · 甘科长：4种随机花盆效果（心值±1、花盆补满、重置场地，各25%）· 奇妙冲刺：3秒 / 克达冲刺：5秒 · 使用圆形方向键移动，按住可持续移动",
"원형 조작부를 눌러 방향 이동 · 누르고 있으면 계속 이동":"使用圆形方向键移动 · 按住可持续移动","화분: 공격 · 대시 버튼: 3칸 돌진 (3초 재사용)":"花盆：攻击 · 冲刺：移动3格（冷却3秒）",
"PC: 방향키 / WASD · Space(공격) · Shift(대시)":"电脑：方向键 / WASD · 空格（投掷）· Shift（冲刺）",
"언어 변경":"切换语言","언어 선택":"选择语言","게임 안내":"游戏说明","기묘가 CBZP에 출근하고, 이상한 사무실에서 화분을 피하고 크다 부장에게 쫓기는 4컷 만화":"四格漫画：奇妙来到 CBZP 实习，在办公室躲避花盆并被克达部长追赶。"
"대시 버튼: 3칸 돌진 · 3초 재사용 대기":"冲刺：移动3格 · 冷却3秒",
"감 과장 출동!":"甘科长登场！",
"화분 투하!":"花盆来袭！",
"크다":"克达",
"기묘":"奇妙",
"회복 화분! HP +1":"恢复花盆！HP +1",
"회복 화분을 찾았지만 HP가 가득 찼습니다.":"找到了恢复花盆，但生命值已满。",
"화분 폭발!":"花盆爆炸！",
"화분 회복!":"花盆恢复！",
"화분 풀충전!":"花盆补满！",
"필드 화분 리셋!":"场地花盆已重置！",
"감 과장 명중!":"甘科长命中！"
},
ja: {
"폿브레이커 RE | 기묘와 크다 부장의 사무실 미로":"POT BREAKER RE｜キミョとクダ部長",
"기묘와 크다 부장의 사무실 미로 추격전":"キミョとクダ部長のオフィス迷路チェイス",
"CBZP 인턴 고양이 기묘가 이동 파티션으로 이루어진 사무실에서 크다 부장을 피해 화분을 던지는 1인용 브라우저 게임입니다.":"CBZPの猫インターン、キミョを操作して、オフィス迷路でクダ部長を避けながら植木鉢を投げるブラウザーゲームです。",
"기묘를 조작해 CBZP 사무실 미로에서 크다 부장과 대결하는 무료 브라우저 게임. 게임 소개, 조작법, 개인정보 및 광고 안내를 확인하세요.":"キミョを操作してCBZPのオフィス迷路でクダ部長と対決する無料ブラウザーゲーム。遊び方、操作方法、プライバシーと広告の案内はこちら。",
"고양이 인턴 기묘와 악어 부장 크다의 CBZP 사무실 미로 추격전.":"猫のインターン、キミョとワニのクダ部長がCBZPのオフィス迷路で追いかけっこ。",
"게임 시작":"ゲーム開始","🏆 랭킹":"🏆 ランキング","게임 방법":"遊び方",
"방향 패드로 이동하고, 대시로 위험을 피하며, 투척 버튼으로 화분을 던지세요. 기묘와 크다 부장의 체력 중 먼저 0이 되면 경기가 끝납니다.":"方向パッドで移動し、ダッシュで攻撃を避け、投げるボタンで植木鉢を投げます。どちらかの体力が0になると試合終了です。",
"게임 소개와 조작법":"ゲーム紹介・操作方法","개인정보 및 광고 안내":"プライバシー・広告について",
"이상한 회사의":"不思議な会社の","인턴 생활":"インターン生活","정말... 이 회사에서":"本当に…この会社で","살아남을 수 있을까?":"生き残れるのかな？",
"난이도":"難易度","노멀":"ノーマル","하드":"ハード","베리 하드":"ベリーハード","사무실로 입장 ▶":"オフィスへ ▶",
"기묘 / PLAYER":"キミョ / PLAYER","크다 부장 / NPC":"クダ部長 / NPC","대시":"ダッシュ","던지기":"投げる",
"↻ 다시 도전":"↻ もう一度挑戦","처음으로":"タイトルへ","랭킹 등록":"ランキング登録","🏆 POT BREAKER 랭킹":"🏆 POT BREAKER ランキング",
"닉네임":"ニックネーム","최대 16자":"16文字まで","랭킹을 불러오는 중…":"ランキングを読み込み中…","사무실 문을 열고 있습니다":"オフィスのドアを開いています",
"Python 게임 엔진을 준비하고 있습니다.":"Pythonゲームエンジンを準備しています。","다시 시도하기":"再試行","잠깐 휴식!":"ちょっと休憩！","계속하기":"続ける",
"아직 등록된 클리어 기록이 없습니다.":"クリア記録はまだありません。","랭킹을 불러오지 못했습니다.":"ランキングを読み込めませんでした。",
"서버 연결에 실패했습니다.":"サーバーに接続できませんでした。","랭킹에 등록했습니다.":"ランキングに登録しました。","Pyodide를 불러오지 못했습니다. 인터넷 연결을 확인해 주세요.":"Pyodideを読み込めませんでした。ネット接続を確認してください。",
"게임 엔진을 불러오지 못했습니다.":"ゲームエンジンを読み込めませんでした。","게임을 불러오지 못했습니다.":"ゲームを読み込めませんでした。","게임 화면 갱신 오류:":"画面更新エラー：",
"기묘 승리!":"キミョの勝利！","크다 부장 승리!":"クダ部長の勝利！","화분 한 방! 크다 부장의 뚝배기를 깼습니다.":"植木鉢の一撃！クダ部長を倒しました。",
"기묘가 화분에 머리만 내놓고 심어졌습니다…":"キミョは植木鉢に植えられ、頭だけ出ています…","쨍그랑!":"ガシャーン！","감 과장":"カム課長",
"랭킹 닫기":"ランキングを閉じる",
"♥ 회복 · 감 과장: ? 화분 4종 (하트 ±1 · 화분 풀충전 · 필드 리셋, 각 25%) · 기묘: 대시 3초 / 크다: 대시 5초 · 원형 조작부를 눌러 방향 이동 · 누르고 있으면 계속 이동":"♥ 回復 · カム課長：植木鉢の効果4種（ハート±1、植木鉢補充、フィールドリセット・各25%）· キミョのダッシュ：3秒 / クダのダッシュ：5秒 · 円形パッドで移動、長押しで連続移動",
"원형 조작부를 눌러 방향 이동 · 누르고 있으면 계속 이동":"円形パッドで移動 · 長押しで連続移動","화분: 공격 · 대시 버튼: 3칸 돌진 (3초 재사용)":"植木鉢：攻撃 · ダッシュ：3マス移動（クールダウン3秒）",
"PC: 방향키 / WASD · Space(공격) · Shift(대시)":"PC：矢印キー / WASD · Space（投げる）· Shift（ダッシュ）",
"언어 변경":"言語を変更","언어 선택":"言語を選択","게임 안내":"ゲームガイド","기묘가 CBZP에 출근하고, 이상한 사무실에서 화분을 피하고 크다 부장에게 쫓기는 4컷 만화":"4コマ漫画：キミョがCBZPに出勤し、植木鉢を避けながらクダ部長に追われます。"
"대시 버튼: 3칸 돌진 · 3초 재사용 대기":"ダッシュ：3マス移動 · クールダウン3秒",
"감 과장 출동!":"カム課長が登場！",
"화분 투하!":"植木鉢が降ってくる！",
"크다":"クダ",
"기묘":"キミョ",
"회복 화분! HP +1":"回復の植木鉢！HP +1",
"회복 화분을 찾았지만 HP가 가득 찼습니다.":"回復の植木鉢を見つけましたが、HPは満タンです。",
"화분 폭발!":"植木鉢が爆発！",
"화분 회복!":"植木鉢で回復！",
"화분 풀충전!":"植木鉢を補充！",
"필드 화분 리셋!":"フィールドの植木鉢をリセット！",
"감 과장 명중!":"カム課長に命中！"
}
};
const selectors=[...document.querySelectorAll(".locale-control select")];
if(!selectors.length)return;
const textOriginal=new WeakMap(),textRendered=new WeakMap(),attrOriginal=new WeakMap(),attrRendered=new WeakMap();
const routeLocale=location.pathname.match(/^\/(en|zh|ja)\/?$/)?.[1];
let locale=routeLocale||"ko",busy=false;
if(!routeLocale){try{const saved=localStorage.getItem("potbreaker-locale");if(["ko","en","zh","ja"].includes(saved))locale=saved}catch{}}
const translate=value=>{
 if(locale==="ko")return value;
 const dictionary=dictionaries[locale]||{};
 if(Object.prototype.hasOwnProperty.call(dictionary,value))return dictionary[value];
 let result=value;
 for(const key of Object.keys(dictionary).sort((a,b)=>b.length-a.length)){
  if(result.includes(key))result=result.split(key).join(dictionary[key]);
 }
 return result;
};
function visit(root=document.documentElement){
 if(!root)return;
 const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT,{acceptNode:n=>n.parentElement?.closest("script,style,select,option,textarea")?NodeFilter.FILTER_REJECT:NodeFilter.FILTER_ACCEPT});
 let n;while(n=walker.nextNode()){
  const current=n.nodeValue;
  if(!textOriginal.has(n)||(textRendered.has(n)&&textRendered.get(n)!==current))textOriginal.set(n,current);
  const next=translate(textOriginal.get(n));textRendered.set(n,next);
  if(next!==current)n.nodeValue=next;
 }
 const elements=root.nodeType===Node.ELEMENT_NODE?[root,...root.querySelectorAll("*")]:[];
 const attrs=["aria-label","title","placeholder","content"];
 for(const el of elements){
  let saved=attrOriginal.get(el);if(!saved){saved={};attrOriginal.set(el,saved)}
  for(const attr of attrs){if(!el.hasAttribute(attr))continue;
   const current=el.getAttribute(attr),key=attr+":"+el.tagName,rendered=attrRendered.get(el)||{};
   if(!Object.prototype.hasOwnProperty.call(saved,key)||(Object.prototype.hasOwnProperty.call(rendered,key)&&rendered[key]!==current))saved[key]=current;
   const next=translate(saved[key]);rendered[key]=next;attrRendered.set(el,rendered);
   if(next!==current)el.setAttribute(attr,next)
  }
 }
}
const comicCaptions={
en:["Gimyo starts as a CBZP intern!","But… something feels strange about the office.","Flowerpots suddenly come flying from somewhere!","Manager Keuda throws another pot at Gimyo!"],
zh:["奇妙来到 CBZP，开始实习了！","但是……公司的气氛有点奇怪。","突然，不知从哪儿飞来了花盆！","克达部长又朝奇妙扔花盆了！"],
ja:["キミョ、CBZPでインターン開始！","でも…会社の雰囲気がなんだか変。","突然どこからか植木鉢が飛んできた！","クダ部長がキミョにまた植木鉢を投げた！"]
};
function drawComicTranslations(){
 const img=document.querySelector(".comic-cover");if(!img)return;
 let wrap=img.parentElement;
 if(!wrap?.classList.contains("comic-cover-wrap")){
  wrap=document.createElement("div");wrap.className="comic-cover-wrap";
  img.parentNode.insertBefore(wrap,img);wrap.appendChild(img);
 }
 let canvas=wrap.querySelector(".comic-translation-layer");
 if(!canvas){canvas=document.createElement("canvas");canvas.className="comic-translation-layer";canvas.setAttribute("aria-hidden","true");wrap.appendChild(canvas)}
 const draw=()=>{
  const wr=wrap.getBoundingClientRect(),ir=img.getBoundingClientRect(),dpr=window.devicePixelRatio||1;
  if(!wr.width||!wr.height||!ir.width||!ir.height)return;
  canvas.width=Math.round(wr.width*dpr);canvas.height=Math.round(wr.height*dpr);
  const ctx=canvas.getContext("2d");ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,wr.width,wr.height);
  if(locale==="ko")return;
  const captions=comicCaptions[locale];if(!captions)return;
  const boxes=[
   {x:.09,y:.155,w:.397,h:.073},{x:.585,y:.155,w:.385,h:.073},
   {x:.09,y:.545,w:.397,h:.073},{x:.585,y:.545,w:.385,h:.073}
  ];
  const ox=ir.left-wr.left,oy=ir.top-wr.top;
  boxes.forEach((box,index)=>{
   const x=ox+ir.width*box.x,y=oy+ir.height*box.y,w=ir.width*box.w,h=ir.height*box.h,r=Math.min(5,h*.16);
   ctx.beginPath();if(ctx.roundRect)ctx.roundRect(x,y,w,h,r);else ctx.rect(x,y,w,h);
   ctx.fillStyle="#fffdf5";ctx.fill();ctx.strokeStyle="#d4d0c8";ctx.lineWidth=Math.max(1,h*.025);ctx.stroke();
   let size=h*.48;ctx.font="800 "+size+"px system-ui,'Noto Sans CJK KR',sans-serif";
   while(ctx.measureText(captions[index]).width>w-10&&size>h*.25){size-=.5;ctx.font="800 "+size+"px system-ui,'Noto Sans CJK KR',sans-serif"}
   ctx.fillStyle="#203451";ctx.textAlign="left";ctx.textBaseline="middle";
   ctx.fillText(captions[index],x+5,y+h*.52,w-10);
  });
 };
 if(img.complete)draw();else img.addEventListener("load",draw,{once:true});
 if(!canvas.__pbResizeObserver){canvas.__pbResizeObserver=new ResizeObserver(draw);canvas.__pbResizeObserver.observe(wrap)}
}
function apply(next){
 locale=["ko","en","zh","ja"].includes(next)?next:"ko";
 try{localStorage.setItem("potbreaker-locale",locale)}catch{}
 document.documentElement.lang=locale;
 const localePath=locale==="ko"?"/":"/"+locale;
 if(location.pathname!==localePath)history.replaceState(null,"",localePath+location.search+location.hash);
 const canonical=document.querySelector('link[rel="canonical"]');if(canonical)canonical.href=location.origin+localePath;
 const ogLocale=document.querySelector('meta[property="og:locale"]');if(ogLocale)ogLocale.content=locale==="ko"?"ko_KR":locale==="en"?"en_US":locale==="zh"?"zh_CN":"ja_JP";
 busy=true;selectors.forEach(selector=>selector.value=locale);visit();drawComicTranslations();busy=false;
}
selectors.forEach(selector=>selector.addEventListener("change",()=>apply(selector.value)));
window.addEventListener("popstate",()=>apply(location.pathname.match(/^\/(en|zh|ja)\/?$/)?.[1]||"ko"));
if(window.CanvasRenderingContext2D&&!CanvasRenderingContext2D.prototype.__pbTranslated){
 for(const method of ["fillText","strokeText"]){
  const original=CanvasRenderingContext2D.prototype[method];
  CanvasRenderingContext2D.prototype[method]=function(text,...args){return original.call(this,translate(String(text)),...args)};
 }
 CanvasRenderingContext2D.prototype.__pbTranslated=true;
}
apply(locale);
new MutationObserver(records=>{if(busy)return;for(const r of records){if(r.type==="characterData"){visit(r.target.parentElement)}else if(r.type==="childList"){for(const node of r.addedNodes){if(node.nodeType===Node.ELEMENT_NODE||node.nodeType===Node.TEXT_NODE)visit(node)}}else if(r.type==="attributes"){visit(r.target)}}}).observe(document.body,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:["aria-label","title","placeholder","content"]});
})();
</script>"""
html = html.replace("</body>", language_script + "\n</body>", 1)

worker = (
    "// Generated by scripts/build_worker.py. POT BREAKER RE v1.0.91 SEO/AdSense-ready\n"
    + "const PAGE=" + json.dumps(html, ensure_ascii=False) + ";\n"
    + "const GAME=" + json.dumps(python_source, ensure_ascii=False) + ";\n"
    + """const SCHEMA=`CREATE TABLE IF NOT EXISTS visits (visitor_id TEXT PRIMARY KEY, created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now')));
CREATE TABLE IF NOT EXISTS game_runs (run_id TEXT PRIMARY KEY, visitor_id TEXT, difficulty TEXT NOT NULL CHECK(difficulty IN ('normal','hard','very_hard')), status TEXT NOT NULL DEFAULT 'playing' CHECK(status IN ('playing','win','lose')), elapsed_ms INTEGER, started_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now')), finished_at TEXT);
CREATE TABLE IF NOT EXISTS game_events (id INTEGER PRIMARY KEY AUTOINCREMENT, visitor_id TEXT, run_id TEXT, event_type TEXT NOT NULL, difficulty TEXT, elapsed_ms INTEGER, created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now')));
CREATE INDEX IF NOT EXISTS game_events_created_at ON game_events(created_at);
CREATE TABLE IF NOT EXISTS rankings (id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL UNIQUE, nickname TEXT NOT NULL, difficulty TEXT NOT NULL CHECK(difficulty IN ('normal','hard','very_hard')), elapsed_ms INTEGER NOT NULL, created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now')), FOREIGN KEY(run_id) REFERENCES game_runs(run_id));
CREATE INDEX IF NOT EXISTS rankings_order ON rankings(difficulty,elapsed_ms);`;
const SITE_ABOUT="<!doctype html><html lang=\"ko\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>게임 소개와 조작법 | 폿브레이커 RE</title><meta name=\"description\" content=\"CBZP 사무실 미로에서 기묘와 크다 부장이 대결하는 폿브레이커 RE의 게임 방법, 난이도, 등장인물을 소개합니다.\"><link rel=\"canonical\" href=\"https://potbreaker.com/about\"><meta property=\"og:type\" content=\"website\"><meta property=\"og:locale\" content=\"ko_KR\"><meta property=\"og:title\" content=\"게임 소개와 조작법 | 폿브레이커 RE\"><meta property=\"og:description\" content=\"기묘와 크다 부장의 사무실 미로 추격전 게임 소개와 조작법.\"><meta property=\"og:url\" content=\"https://potbreaker.com/about\"><style>body{margin:0;background:#f7f2e9;color:#293754;font:18px/1.7 system-ui,'Malgun Gothic',sans-serif}main{max-width:820px;margin:auto;padding:clamp(22px,5vw,64px)}h1,h2{line-height:1.25}a{color:#285c91}nav{display:flex;gap:1em;flex-wrap:wrap}section{margin:2rem 0;padding:1rem 1.3rem;background:#fff;border-radius:16px}li{margin:.35rem 0}</style></head><body><main><header><nav aria-label=\"사이트\"><a href=\"/\">게임으로 돌아가기</a><a href=\"/privacy\">개인정보 및 광고 안내</a></nav></header><article><h1>폿브레이커 RE: 사무실 미로 추격전</h1><p>CBZP(Cloud Bear Zoo Park)의 인턴 고양이 기묘가 사무실 미로를 이동하며 크다 부장과 화분 대결을 펼치는 1인용 브라우저 게임입니다. 이동 파티션 사이에서 위치를 잡고, 화분을 모으고, 상대의 공격을 피하세요.</p><section><h2>게임 방법</h2><ol><li>시작 화면에서 난이도를 선택하고 게임을 시작합니다.</li><li>모바일에서는 화면의 원형 방향 조작부를 눌러 이동하고 대시·투척 버튼으로 행동합니다. 컴퓨터에서는 방향키 또는 WASD로 이동하고 Shift로 대시, Space로 화분을 던집니다.</li><li>기묘의 체력이 0이 되기 전에 크다 부장의 체력을 0으로 만들면 승리합니다.</li></ol><p>방향 조작은 상·하·좌·우로 입력되며, 대시는 재사용 대기시간이 있습니다. 이동 중 파티션과 화분 위치를 살피세요.</p></section><section><h2>등장인물</h2><ul><li><strong>기묘</strong> — 플레이어가 조작하는 CBZP 인턴 고양이.</li><li><strong>크다 부장</strong> — 기묘를 추적하며 화분을 던지는 악어 보스.</li><li><strong>감 과장</strong> — 무작위 효과의 화분을 떨어뜨리는 까마귀.</li></ul></section><section><h2>난이도</h2><p>크다 부장의 체력은 노멀 5, 하드 7, 베리하드 10입니다. 감 과장 화분은 하트 회복, 하트 감소, 화분 충전, 필드 화분 초기화 효과 중 하나를 제공합니다.</p></section><p><a href=\"/\">폿브레이커 RE 플레이하기</a></p></article></main></body></html>";
const SITE_PRIVACY="<!doctype html><html lang=\"ko\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>개인정보 및 광고 안내 | 폿브레이커 RE</title><meta name=\"description\" content=\"폿브레이커 RE의 게임 기록 처리와 Google 광고 쿠키 사용 안내입니다.\"><link rel=\"canonical\" href=\"https://potbreaker.com/privacy\"><meta property=\"og:type\" content=\"website\"><meta property=\"og:locale\" content=\"ko_KR\"><meta property=\"og:title\" content=\"개인정보 및 광고 안내 | 폿브레이커 RE\"><meta property=\"og:description\" content=\"게임 기록과 광고 기술 사용에 관한 안내.\"><meta property=\"og:url\" content=\"https://potbreaker.com/privacy\"><style>body{margin:0;background:#f7f2e9;color:#293754;font:17px/1.7 system-ui,'Malgun Gothic',sans-serif}main{max-width:820px;margin:auto;padding:clamp(22px,5vw,64px)}h1,h2{line-height:1.25}a{color:#285c91}section{margin:1.5rem 0;padding:1rem 1.3rem;background:#fff;border-radius:16px}</style></head><body><main><nav aria-label=\"사이트\"><a href=\"/\">게임으로 돌아가기</a> · <a href=\"/about\">게임 소개</a></nav><article><h1>개인정보 및 광고 안내</h1><p>이 안내는 POT BREAKER RE에서 처리하는 게임 기록과 광고 기술을 설명합니다.</p><section><h2>게임 기록</h2><p>게임 기록 기능은 무작위 방문자/경기 식별자, 선택 난이도, 승패, 경기 시간과 랭킹 등록 시 사용자가 입력한 닉네임(최대 16자)을 Cloudflare D1에 저장합니다. 기록은 방문 통계, 경기 검증과 랭킹 제공에 사용됩니다. 실명·이메일·전화번호 입력은 게임 기능에 필요하지 않습니다. 현재 데이터베이스에는 기록 자동 만료 기능이 설정되어 있지 않습니다.</p></section><section><h2>광고 쿠키</h2><p>AdSense 게시자 ID와 운영 설정이 등록되기 전에는 Google 광고 스크립트를 불러오지 않습니다. 광고가 활성화되면 Google 및 광고 파트너가 쿠키, 광고 식별자, IP 주소 또는 웹 비콘을 사용해 광고를 제공·측정할 수 있습니다. Google 광고 설정에서 맞춤 광고를 관리할 수 있으며, <a href=\"https://www.aboutads.info/choices/\">aboutads.info 선택 페이지</a>에서도 일부 맞춤 광고를 거부할 수 있습니다.</p><p>EEA, 영국 또는 스위스 사용자에게 맞춤 광고를 제공하려면 Google 인증 CMP 및 해당 동의 요건을 먼저 갖춰야 합니다. 운영 설정은 이를 확인한 뒤에만 활성화해야 합니다.</p></section><section><h2>외부 서비스</h2><p>게임 페이지와 게임 기록 API는 Cloudflare Workers 및 D1을 사용합니다. Google 광고 기능을 활성화하면 Google의 <a href=\"https://policies.google.com/technologies/partner-sites\">파트너 사이트 데이터 사용 안내</a>와 개인정보처리방침이 적용될 수 있습니다.</p></section><p>최종 갱신: 2026-10-28</p></article></main></body></html>";
const json=(data,status=200)=>new Response(JSON.stringify(data),{status,headers:{"content-type":"application/json; charset=utf-8","cache-control":"no-store","x-content-type-options":"nosniff"}});
const validDifficulty=value=>["normal","hard","very_hard"].includes(value);
export default {async fetch(request,env){
const path=new URL(request.url).pathname;
if(path==="/health")
  return json({ok:true,version:"1.0.91",visual:"illustrated",engine:"Python/Pyodide",database:!!env.POTBREAKER_DB});
if(path.startsWith("/api/")){
  if(!env.POTBREAKER_DB)return json({error:"랭킹 데이터베이스가 연결되지 않았습니다."},503);
  try{
    await env.POTBREAKER_DB.exec(SCHEMA);
    if(request.method==="GET"&&path==="/api/rankings"){
      const result=await env.POTBREAKER_DB.prepare("SELECT nickname,difficulty,elapsed_ms,created_at FROM rankings ORDER BY CASE difficulty WHEN 'very_hard' THEN 3 WHEN 'hard' THEN 2 ELSE 1 END DESC, elapsed_ms ASC, created_at ASC LIMIT 100").all();
      return json({rankings:result.results||[]});
    }
    if(request.method!=="POST")return json({error:"지원하지 않는 요청입니다."},405);
    const body=await request.json();
    if(path==="/api/visit"){
      const visitorId=crypto.randomUUID();
      await env.POTBREAKER_DB.batch([
        env.POTBREAKER_DB.prepare("INSERT INTO visits(visitor_id) VALUES (?)").bind(visitorId),
        env.POTBREAKER_DB.prepare("INSERT INTO game_events(visitor_id,event_type) VALUES (?,'visit')").bind(visitorId)
      ]);
      return json({visitor_id:visitorId});
    }
    if(path==="/api/runs"){
      if(!validDifficulty(body.difficulty))return json({error:"난이도가 올바르지 않습니다."},400);
      const visitorId=typeof body.visitor_id==="string"?body.visitor_id:null,runId=crypto.randomUUID();
      await env.POTBREAKER_DB.batch([
        env.POTBREAKER_DB.prepare("INSERT INTO game_runs(run_id,visitor_id,difficulty) VALUES (?,?,?)").bind(runId,visitorId,body.difficulty),
        env.POTBREAKER_DB.prepare("INSERT INTO game_events(visitor_id,run_id,event_type,difficulty) VALUES (?,?,'start',?)").bind(visitorId,runId,body.difficulty)
      ]);
      return json({run_id:runId});
    }
    if(path==="/api/runs/finish"){
      const runId=typeof body.run_id==="string"?body.run_id:"",outcome=body.outcome,elapsed=Math.floor(Number(body.elapsed_ms));
      if(!runId||!["win","lose"].includes(outcome)||!Number.isFinite(elapsed)||elapsed<1000||elapsed>3600000)return json({error:"게임 결과가 올바르지 않습니다."},400);
      const run=await env.POTBREAKER_DB.prepare("SELECT visitor_id,difficulty,status FROM game_runs WHERE run_id=?").bind(runId).first();
      if(!run||run.status!=="playing")return json({error:"유효한 게임 기록을 찾지 못했습니다."},409);
      if(outcome==="win"&&elapsed<(run.difficulty==="very_hard"?6000:3000))return json({error:"클리어 시간이 너무 짧습니다."},400);
      await env.POTBREAKER_DB.batch([
        env.POTBREAKER_DB.prepare("UPDATE game_runs SET status=?,elapsed_ms=?,finished_at=strftime('%Y-%m-%d %H:%M:%S','now') WHERE run_id=? AND status='playing'").bind(outcome,elapsed,runId),
        env.POTBREAKER_DB.prepare("INSERT INTO game_events(visitor_id,run_id,event_type,difficulty,elapsed_ms) VALUES (?, ?, ?, ?, ?)").bind(run.visitor_id,runId,outcome,run.difficulty,elapsed)
      ]);
      return json({ok:true});
    }
    if(path==="/api/rankings"){
      const runId=typeof body.run_id==="string"?body.run_id:"",nickname=typeof body.nickname==="string"?body.nickname.trim().slice(0,16):"";
      if(!runId||!nickname)return json({error:"닉네임을 입력해 주세요."},400);
      const run=await env.POTBREAKER_DB.prepare("SELECT difficulty,elapsed_ms,status FROM game_runs WHERE run_id=?").bind(runId).first();
      if(!run||run.status!=="win"||!run.elapsed_ms)return json({error:"승리한 게임만 랭킹에 등록할 수 있습니다."},403);
      const existing=await env.POTBREAKER_DB.prepare("SELECT id FROM rankings WHERE run_id=?").bind(runId).first();
      if(existing)return json({error:"이 게임 기록은 이미 등록됐습니다."},409);
      await env.POTBREAKER_DB.prepare("INSERT INTO rankings(run_id,nickname,difficulty,elapsed_ms) VALUES (?,?,?,?)").bind(runId,nickname,run.difficulty,run.elapsed_ms).run();
      return json({ok:true});
    }
    return json({error:"요청한 API를 찾지 못했습니다."},404);
  }catch(error){return json({error:"랭킹 서버 처리 중 오류가 발생했습니다."},500)}
}
if(!["GET","HEAD"].includes(request.method))return new Response("Method Not Allowed",{status:405,headers:{Allow:"GET, HEAD"}});
const headers={"cache-control":"public, max-age=300","x-content-type-options":"nosniff"};
const publisherId=typeof env.ADSENSE_PUBLISHER_ID==="string"&&/^ca-pub-\d{16}$/.test(env.ADSENSE_PUBLISHER_ID)?env.ADSENSE_PUBLISHER_ID:"";
const text=(body,type="text/plain; charset=utf-8",status=200,extra={})=>new Response(request.method==="HEAD"?null:body,{status,headers:{"content-type":type,...headers,...extra}});
if(path==="/robots.txt")return text("User-agent: *\nAllow: /\nSitemap: https://potbreaker.com/sitemap.xml\n");
if(path==="/sitemap.xml"){
 const variants=[["ko","/"],["en","/en"],["zh","/zh"],["ja","/ja"]];
 const alternates=variants.map(([lang,url])=>`<xhtml:link rel="alternate" hreflang="${lang}" href="https://potbreaker.com${url}"/>`).join("");
 const urls=variants.map(([lang,url])=>`<url><loc>https://potbreaker.com${url}</loc>${alternates}</url>`).join("");
 return text('<?xml version="1.0" encoding="UTF-8"?>'+
  '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'+urls+
  '<url><loc>https://potbreaker.com/about</loc></url><url><loc>https://potbreaker.com/privacy</loc></url></urlset>',
  "application/xml; charset=utf-8");
}
if(path==="/ads.txt"){
 if(!publisherId)return text("AdSense publisher ID is not configured.\n","text/plain; charset=utf-8",404);
 return text("google.com, "+publisherId.replace("ca-pub-","pub-")+", DIRECT, f08c47fec0942fa0\n");
}
if(path==="/about"||path==="/privacy"){
 const isAbout=path==="/about",doc=isAbout?SITE_ABOUT:SITE_PRIVACY;
 const adsReady=path==="/about"&&publisherId&&env.ADSENSE_ENABLED==="true"&&env.ADSENSE_PRIVACY_READY==="true"&&env.ADSENSE_CONSENT_READY==="true";
 const adLoader=adsReady?'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client='+publisherId+'" crossorigin="anonymous"></script>':"";
 const verification=publisherId?'<meta name="google-adsense-account" content="'+publisherId+'">':"";
 const html=doc.replace("</head>",verification+adLoader+"</head>");
 return text(html,"text/html; charset=utf-8",200,{"cache-control":"public, max-age=300"});
}
const localeMatch=path.match(/^\/(en|zh|ja)\/?$/);
const page=path==="/"||path==="/index.html"||!!localeMatch;
if(!page&&path!=="/game.py")return new Response("Not Found",{status:404});
const responseHeaders={"content-type":page?"text/html; charset=utf-8":"text/plain; charset=utf-8","cache-control":"no-store","x-content-type-options":"nosniff"};
if(path==="/game.py")responseHeaders["x-robots-tag"]="noindex";
const verification=publisherId?'<meta name="google-adsense-account" content="'+publisherId+'">':"";
const adsReady=path==="/about"&&publisherId&&env.ADSENSE_ENABLED==="true"&&env.ADSENSE_PRIVACY_READY==="true"&&env.ADSENSE_CONSENT_READY==="true";
const adLoader=adsReady?'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client='+publisherId+'" crossorigin="anonymous"></script>':"";
const pageLocale=localeMatch?.[1]||"ko";
const localePath=pageLocale==="ko"?"/":"/"+pageLocale;
const ogLocale=pageLocale==="ko"?"ko_KR":pageLocale==="en"?"en_US":pageLocale==="zh"?"zh_CN":"ja_JP";
const localizedPage=PAGE.replace('<html lang="ko">',`<html lang="${pageLocale}">`)
 .replace('<link rel="canonical" href="https://potbreaker.com/">',`<link rel="canonical" href="https://potbreaker.com${localePath}">`)
 .replace('<meta property="og:locale" content="ko_KR">',`<meta property="og:locale" content="${ogLocale}">`);
const body=page?localizedPage.replace("</head>",verification+"</head>"):GAME;
return new Response(request.method==="HEAD"?null:body,{status:200,headers:responseHeaders});
}};"""
)
(root / "cloudflare" / "worker.js").write_text(worker, encoding="utf-8")
print("Built cloudflare/worker.js", len(worker.encode("utf-8")), "bytes")
