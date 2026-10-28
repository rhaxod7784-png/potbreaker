"""Build illustrated POT BREAKER RE v1.0.88 for Cloudflare Workers.

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
html = html.replace("</style>", dpad_css + "\\n</style>", 1)


# v1.0.89: crawlable site metadata, visible game guidance, and safe publisher gates.
html = html.replace("POT BREAKER RE v1.0.89 · CBZP", "폿브레이커 RE | 기묘와 크다 부장의 미로 게임", 1)
seo_head = """
<meta name="description" content="기묘를 조작해 CBZP 사무실 미로에서 크다 부장과 대결하는 무료 브라우저 게임. 게임 소개, 조작법, 개인정보 및 광고 안내를 확인하세요.">
<link rel="canonical" href="https://potbreaker.com/">
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
title_end = '<button class="menu-ranking" id="openRanking">🏆 랭킹</button></section>'
site_info = """<section class="seo-info" aria-labelledby="seo-heading">
<h1 id="seo-heading">기묘와 크다 부장의 사무실 미로 추격전</h1>
<p>CBZP 인턴 고양이 기묘가 이동 파티션으로 이루어진 사무실에서 크다 부장을 피해 화분을 던지는 1인용 브라우저 게임입니다.</p>
<details><summary>게임 방법</summary><p>방향 패드로 이동하고, 대시로 위험을 피하며, 투척 버튼으로 화분을 던지세요. 기묘와 크다 부장의 체력 중 먼저 0이 되면 경기가 끝납니다.</p></details>
<nav aria-label="게임 안내"><a href="/about">게임 소개와 조작법</a><a href="/privacy">개인정보 및 광고 안내</a></nav>
</section>"""
if title_end not in html:
    raise SystemExit("Title screen marker not found for visible game information")
html = html.replace(title_end, '<button class="menu-ranking" id="openRanking">🏆 랭킹</button>' + site_info + '</section>', 1)
seo_css = """
.seo-info{position:absolute;left:2%;bottom:1.5%;z-index:5;width:min(43%,520px);max-height:40%;overflow:auto;padding:clamp(6px,1.1cqw,14px);border:1px solid #ffffffbd;border-radius:14px;background:#fffaf0e8;box-shadow:0 3px 14px #31415b35;color:#303d67;font-size:clamp(8px,1.03cqw,13px);line-height:1.35;text-align:left}
.seo-info h1{margin:0 0 .35em;font-size:1.18em;line-height:1.2}.seo-info p{margin:.25em 0}.seo-info details{margin-top:.25em}.seo-info summary{cursor:pointer;font-weight:900}.seo-info nav{display:flex;gap:.8em;flex-wrap:wrap;margin-top:.35em}.seo-info a{color:#244e70;text-decoration:underline;text-underline-offset:2px}
@media(max-width:700px){.seo-info{width:48%;max-height:36%;font-size:clamp(7px,1.2cqw,11px)}}
"""
html = html.replace("</style>", seo_css + "\n</style>", 1)

worker = (
    "// Generated by scripts/build_worker.py. POT BREAKER RE v1.0.89 SEO/AdSense-ready\n"
    + "const PAGE=" + json.dumps(html, ensure_ascii=False) + ";\n"
    + "const GAME=" + json.dumps(python_source, ensure_ascii=False) + ";\n"
    + """const SCHEMA=`CREATE TABLE IF NOT EXISTS visits (visitor_id TEXT PRIMARY KEY, created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now')));
CREATE TABLE IF NOT EXISTS game_runs (run_id TEXT PRIMARY KEY, visitor_id TEXT, difficulty TEXT NOT NULL CHECK(difficulty IN ('normal','hard','very_hard')), status TEXT NOT NULL DEFAULT 'playing' CHECK(status IN ('playing','win','lose')), elapsed_ms INTEGER, started_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now')), finished_at TEXT);
CREATE TABLE IF NOT EXISTS game_events (id INTEGER PRIMARY KEY AUTOINCREMENT, visitor_id TEXT, run_id TEXT, event_type TEXT NOT NULL, difficulty TEXT, elapsed_ms INTEGER, created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now')));
CREATE INDEX IF NOT EXISTS game_events_created_at ON game_events(created_at);
CREATE TABLE IF NOT EXISTS rankings (id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL UNIQUE, nickname TEXT NOT NULL, difficulty TEXT NOT NULL CHECK(difficulty IN ('normal','hard','very_hard')), elapsed_ms INTEGER NOT NULL, created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now')), FOREIGN KEY(run_id) REFERENCES game_runs(run_id));
CREATE INDEX IF NOT EXISTS rankings_order ON rankings(difficulty,elapsed_ms);`;
const SITE_ABOUT="<!doctype html><html lang=\"ko\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>게임 소개와 조작법 | 폿브레이커 RE</title><meta name=\"description\" content=\"CBZP 사무실 미로에서 기묘와 크다 부장이 대결하는 폿브레이커 RE의 게임 방법, 난이도, 등장인물을 소개합니다.\"><link rel=\"canonical\" href=\"https://potbreaker.com/about\"><meta property=\"og:type\" content=\"website\"><meta property=\"og:locale\" content=\"ko_KR\"><meta property=\"og:title\" content=\"게임 소개와 조작법 | 폿브레이커 RE\"><meta property=\"og:description\" content=\"기묘와 크다 부장의 사무실 미로 추격전 게임 소개와 조작법.\"><meta property=\"og:url\" content=\"https://potbreaker.com/about\"><style>body{margin:0;background:#f7f2e9;color:#293754;font:18px/1.7 system-ui,'Malgun Gothic',sans-serif}main{max-width:820px;margin:auto;padding:clamp(22px,5vw,64px)}h1,h2{line-height:1.25}a{color:#285c91}nav{display:flex;gap:1em;flex-wrap:wrap}section{margin:2rem 0;padding:1rem 1.3rem;background:#fff;border-radius:16px}li{margin:.35rem 0}</style></head><body><main><header><nav aria-label=\"사이트\"><a href=\"/\">게임으로 돌아가기</a><a href=\"/privacy\">개인정보 및 광고 안내</a></nav></header><article><h1>폿브레이커 RE: 사무실 미로 추격전</h1><p>CBZP(Cloud Bear Zoo Park)의 인턴 고양이 기묘가 사무실 미로를 이동하며 크다 부장과 화분 대결을 펼치는 1인용 브라우저 게임입니다. 이동 파티션 사이에서 위치를 잡고, 화분을 모으고, 상대의 공격을 피하세요.</p><section><h2>게임 방법</h2><ol><li>시작 화면에서 난이도를 선택하고 게임을 시작합니다.</li><li>모바일에서는 화면의 원형 방향 조작부를 눌러 이동하고 대시·투척 버튼으로 행동합니다. 컴퓨터에서는 방향키 또는 WASD로 이동하고 Shift로 대시, Space로 화분을 던집니다.</li><li>기묘의 체력이 0이 되기 전에 크다 부장의 체력을 0으로 만들면 승리합니다.</li></ol><p>방향 조작은 상·하·좌·우로 입력되며, 대시는 재사용 대기시간이 있습니다. 이동 중 파티션과 화분 위치를 살피세요.</p></section><section><h2>등장인물</h2><ul><li><strong>기묘</strong> — 플레이어가 조작하는 CBZP 인턴 고양이.</li><li><strong>크다 부장</strong> — 기묘를 추적하며 화분을 던지는 악어 보스.</li><li><strong>감 과장</strong> — 무작위 효과의 화분을 떨어뜨리는 까마귀.</li></ul></section><section><h2>난이도</h2><p>크다 부장의 체력은 노멀 5, 하드 7, 베리하드 10입니다. 감 과장 화분은 하트 회복, 하트 감소, 화분 충전, 필드 화분 초기화 효과 중 하나를 제공합니다.</p></section><p><a href=\"/\">폿브레이커 RE 플레이하기</a></p></article></main></body></html>";
const SITE_PRIVACY="<!doctype html><html lang=\"ko\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>개인정보 및 광고 안내 | 폿브레이커 RE</title><meta name=\"description\" content=\"폿브레이커 RE의 게임 기록 처리와 Google 광고 쿠키 사용 안내입니다.\"><link rel=\"canonical\" href=\"https://potbreaker.com/privacy\"><meta property=\"og:type\" content=\"website\"><meta property=\"og:locale\" content=\"ko_KR\"><meta property=\"og:title\" content=\"개인정보 및 광고 안내 | 폿브레이커 RE\"><meta property=\"og:description\" content=\"게임 기록과 광고 기술 사용에 관한 안내.\"><meta property=\"og:url\" content=\"https://potbreaker.com/privacy\"><style>body{margin:0;background:#f7f2e9;color:#293754;font:17px/1.7 system-ui,'Malgun Gothic',sans-serif}main{max-width:820px;margin:auto;padding:clamp(22px,5vw,64px)}h1,h2{line-height:1.25}a{color:#285c91}section{margin:1.5rem 0;padding:1rem 1.3rem;background:#fff;border-radius:16px}</style></head><body><main><nav aria-label=\"사이트\"><a href=\"/\">게임으로 돌아가기</a> · <a href=\"/about\">게임 소개</a></nav><article><h1>개인정보 및 광고 안내</h1><p>이 안내는 POT BREAKER RE에서 처리하는 게임 기록과 광고 기술을 설명합니다.</p><section><h2>게임 기록</h2><p>게임 기록 기능은 무작위 방문자/경기 식별자, 선택 난이도, 승패, 경기 시간과 랭킹 등록 시 사용자가 입력한 닉네임(최대 16자)을 Cloudflare D1에 저장합니다. 기록은 방문 통계, 경기 검증과 랭킹 제공에 사용됩니다. 실명·이메일·전화번호 입력은 게임 기능에 필요하지 않습니다. 현재 데이터베이스에는 기록 자동 만료 기능이 설정되어 있지 않습니다.</p></section><section><h2>광고 쿠키</h2><p>AdSense 게시자 ID와 운영 설정이 등록되기 전에는 Google 광고 스크립트를 불러오지 않습니다. 광고가 활성화되면 Google 및 광고 파트너가 쿠키, 광고 식별자, IP 주소 또는 웹 비콘을 사용해 광고를 제공·측정할 수 있습니다. Google 광고 설정에서 맞춤 광고를 관리할 수 있으며, <a href=\"https://www.aboutads.info/choices/\">aboutads.info 선택 페이지</a>에서도 일부 맞춤 광고를 거부할 수 있습니다.</p><p>EEA, 영국 또는 스위스 사용자에게 맞춤 광고를 제공하려면 Google 인증 CMP 및 해당 동의 요건을 먼저 갖춰야 합니다. 운영 설정은 이를 확인한 뒤에만 활성화해야 합니다.</p></section><section><h2>외부 서비스</h2><p>게임 페이지와 게임 기록 API는 Cloudflare Workers 및 D1을 사용합니다. Google 광고 기능을 활성화하면 Google의 <a href=\"https://policies.google.com/technologies/partner-sites\">파트너 사이트 데이터 사용 안내</a>와 개인정보처리방침이 적용될 수 있습니다.</p></section><p>최종 갱신: 2026-10-29</p></article></main></body></html>";
const json=(data,status=200)=>new Response(JSON.stringify(data),{status,headers:{"content-type":"application/json; charset=utf-8","cache-control":"no-store","x-content-type-options":"nosniff"}});
const validDifficulty=value=>["normal","hard","very_hard"].includes(value);
export default {async fetch(request,env){
const path=new URL(request.url).pathname;
if(path==="/health")
  return json({ok:true,version:"1.0.89",visual:"illustrated",engine:"Python/Pyodide",database:!!env.POTBREAKER_DB});
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
if(path==="/sitemap.xml")return text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://potbreaker.com/</loc></url><url><loc>https://potbreaker.com/about</loc></url><url><loc>https://potbreaker.com/privacy</loc></url></urlset>',"application/xml; charset=utf-8");
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
const page=path==="/"||path==="/index.html";
if(!page&&path!=="/game.py")return new Response("Not Found",{status:404});
const responseHeaders={"content-type":page?"text/html; charset=utf-8":"text/plain; charset=utf-8","cache-control":"no-store","x-content-type-options":"nosniff"};
if(path==="/game.py")responseHeaders["x-robots-tag"]="noindex";
const verification=publisherId?'<meta name="google-adsense-account" content="'+publisherId+'">':"";
const adsReady=path==="/about"&&publisherId&&env.ADSENSE_ENABLED==="true"&&env.ADSENSE_PRIVACY_READY==="true"&&env.ADSENSE_CONSENT_READY==="true";
const adLoader=adsReady?'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client='+publisherId+'" crossorigin="anonymous"></script>':"";
const body=page?PAGE.replace("</head>",verification+"</head>"):GAME;
return new Response(request.method==="HEAD"?null:body,{status:200,headers:responseHeaders});
}};"""
)
(root / "cloudflare" / "worker.js").write_text(worker, encoding="utf-8")
print("Built cloudflare/worker.js", len(worker.encode("utf-8")), "bytes")
