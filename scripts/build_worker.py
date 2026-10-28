"""Build illustrated POT BREAKER RE v1.0.83 for Cloudflare Workers.

Inputs: web/index.html (images + UI bundled) and web/game.py (Python core).
Unlike the original v1.0.0 builder, this does not expect an inline Python script
inside HTML. The browser fetches /game.py from the same Worker origin.
"""
from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
html = (root / "web" / "index.html").read_text(encoding="utf-8")
python_source = (root / "web" / "game.py").read_text(encoding="utf-8")
touch_block = "let touchDirection=[0,0],touchActive=false,dpadOrder=0;\nconst keyDirections={ArrowUp:'up',KeyW:'up',ArrowDown:'down',KeyS:'down',ArrowLeft:'left',KeyA:'left',ArrowRight:'right',KeyD:'right'};\nconst dpadDirections={up:[0,-1],down:[0,1],left:[-1,0],right:[1,0]};\nconst dpadPointers=new Map();\nconst dpad=document.getElementById('dpad');\nfor(const [direction,glyph] of [['up','▲'],['right','▶'],['down','▼'],['left','◀']]){const icon=document.createElement('span');icon.className='dpad-icon '+direction;icon.textContent=glyph;dpad.appendChild(icon)}\nfunction refreshDpad(){\n let last=null;for(const p of dpadPointers.values())if(p.direction&&(!last||p.order>last.order))last=p;\n dpad.classList.remove('active-up','active-down','active-left','active-right');\n touchActive=!!last;touchDirection=last?dpadDirections[last.direction]:[0,0];\n if(last)dpad.classList.add('active-'+last.direction);\n}\nfunction directionAt(e){\n const rect=dpad.getBoundingClientRect(),dx=(e.clientX-(rect.left+rect.width/2))/(rect.width/2),dy=(e.clientY-(rect.top+rect.height/2))/(rect.height/2);\n if(Math.hypot(dx,dy)<.10)return null;\n const hit=document.elementFromPoint(e.clientX,e.clientY)?.closest?.('#dpad .dpad-button');\n if(hit?.dataset.direction)return hit.dataset.direction;\n return Math.abs(dx)>Math.abs(dy)?(dx<0?'left':'right'):(dy<0?'up':'down');\n}\nfunction setPointerDirection(e,p){\n const direction=directionAt(e);if(direction===p.direction)return;\n if(p.button)p.button.classList.remove('pressed');\n p.direction=direction;p.button=direction?dpad.querySelector('.dpad-button.'+direction):null;p.order=++dpadOrder;\n if(p.button)p.button.classList.add('pressed');refreshDpad();\n}\nfunction clearDpadPointer(id){\n const p=dpadPointers.get(id);if(!p)return;\n if(p.button)p.button.classList.remove('pressed');dpadPointers.delete(id);refreshDpad();\n}\nfunction moveDpadPointer(e){const p=dpadPointers.get(e.pointerId);if(p)setPointerDirection(e,p)}\ndpad.addEventListener('pointerdown',e=>{\n if(!active||paused)return;e.preventDefault();\n const direction=directionAt(e);if(!direction)return;\n const prior=dpadPointers.get(e.pointerId);if(prior&&prior.button)prior.button.classList.remove('pressed');\n const p={button:null,direction:null,order:++dpadOrder};dpadPointers.set(e.pointerId,p);setPointerDirection(e,p);\n try{dpad.setPointerCapture(e.pointerId)}catch{}\n});\nwindow.addEventListener('pointermove',moveDpadPointer);\nwindow.addEventListener('pointerup',e=>clearDpadPointer(e.pointerId));\nwindow.addEventListener('pointercancel',e=>clearDpadPointer(e.pointerId));\nfunction resetTouch(){for(const p of dpadPointers.values())if(p.button)p.button.classList.remove('pressed');dpadPointers.clear();touchActive=false;touchDirection=[0,0];dpad.classList.remove('active-up','active-down','active-left','active-right')}\n"
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
html = html.replace("</style>", ".dpad{position:absolute!important;left:0!important;bottom:2.5%!important;width:clamp(204px,27cqw,252px)!important;height:clamp(136px,18cqw,168px)!important;aspect-ratio:auto;display:grid!important;grid-template-columns:repeat(3,minmax(0,1fr));grid-template-rows:repeat(2,minmax(0,1fr));column-gap:4px;row-gap:0;padding:3px!important;box-sizing:border-box;border:0!important;border-radius:0!important;background:transparent!important;box-shadow:none!important;pointer-events:auto!important;touch-action:none!important;user-select:none;-webkit-user-select:none}\n.dpad-button{display:grid!important;place-items:center;width:auto!important;height:auto!important;min-width:0;min-height:0;aspect-ratio:auto;padding:0;border:2px solid #f8feffed!important;border-radius:12px!important;background:linear-gradient(145deg,#ffffffc9,#c9ddf3ad)!important;color:#344f83!important;font-size:clamp(25px,3.7cqw,39px)!important;font-weight:1000;line-height:1;box-shadow:inset 0 2px 2px #fff9,0 4px 0 #283f655c!important;pointer-events:auto!important;touch-action:none!important;user-select:none;-webkit-user-select:none}\n.dpad-button.up{grid-column:2;grid-row:1}.dpad-button.left{grid-column:1;grid-row:1 / 3}.dpad-button.right{grid-column:3;grid-row:1 / 3}.dpad-button.down{grid-column:2;grid-row:2}\n.dpad-button.pressed{background:linear-gradient(145deg,#ffe9a8dd,#ffd982c9)!important;transform:translateY(3px);box-shadow:inset 0 1px 2px #fff9,0 1px 0 #283f6570!important}\n.dpad-button.up,.dpad-button.down{width:166.666%!important;justify-self:center;position:relative;z-index:2}\n.action.fire{width:clamp(98px,11cqw,132px)!important;min-width:0;min-height:0}.action.fire .symbol{font-size:clamp(24px,3.7cqw,42px)!important}\n.dpad{background:linear-gradient(45deg,transparent 49.4%,#ffffffdc 49.7%,#ffffffdc 50.3%,transparent 50.6%),linear-gradient(-45deg,transparent 49.4%,#ffffffdc 49.7%,#ffffffdc 50.3%,transparent 50.6%),conic-gradient(from -45deg,#d9eafa 0deg 90deg,#c8def4 90deg 180deg,#d9eafa 180deg 270deg,#c8def4 270deg 360deg)!important}
.dpad-button{border:0!important;background:transparent!important;pointer-events:auto!important}
.dpad-button.pressed{background:#ffdc7a99!important;filter:none!important}
.dpad-arrow{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);pointer-events:none}
.dpad-arrow{display:none!important}\n.dpad-icon{position:absolute;z-index:7;display:block!important;left:50%;top:50%;transform:translate(-50%,-50%);pointer-events:none;color:#344f83;font-size:clamp(28px,4cqw,42px);font-weight:1000;line-height:1}\n.dpad-icon.up{top:18%}.dpad-icon.right{left:82%}.dpad-icon.down{top:82%}.dpad-icon.left{left:18%}\n@media (orientation:portrait) and (pointer:coarse){\n .stage{width:100dvh!important;height:100vw!important;top:50%!important;overflow:hidden!important}\n #gamePanel{overflow:hidden!important}\n .dpad{left:1.5%!important;right:auto!important;top:auto!important;bottom:1.5%!important;transform:none!important}\n}
.dpad{width:clamp(184px,24cqw,232px)!important;height:clamp(184px,24cqw,232px)!important;aspect-ratio:1;display:block!important;padding:0!important;overflow:hidden!important;border:3px solid #ffffffed!important;border-radius:50%!important;background:#d9eafaad!important;box-shadow:0 4px 12px #31486b55!important}
.dpad-button{position:absolute!important;inset:0!important;display:flex!important;align-items:center!important;justify-content:center!important;width:100%!important;height:100%!important;min-width:0;min-height:0;aspect-ratio:auto;padding:0!important;border:1px solid #ffffffa8!important;border-radius:0!important;background:linear-gradient(145deg,#ffffffa8,#b9d3ee9c)!important;color:#344f83!important;font-size:clamp(28px,4cqw,42px)!important;font-weight:1000;line-height:1;box-shadow:none!important;pointer-events:auto!important;touch-action:none!important;user-select:none;-webkit-user-select:none}
.dpad-button.up{clip-path:polygon(0 0,100% 0,50% 50%);align-items:flex-start!important;padding-top:12%!important}
.dpad-button.right{clip-path:polygon(100% 0,100% 100%,50% 50%);justify-content:flex-end!important;padding-right:12%!important}
.dpad-button.down{clip-path:polygon(0 100%,100% 100%,50% 50%);align-items:flex-end!important;padding-bottom:12%!important}
.dpad-button.left{clip-path:polygon(0 0,50% 50%,0 100%);justify-content:flex-start!important;padding-left:12%!important}
.dpad-button.pressed{filter:brightness(1.18) saturate(1.15)!important;transform:none!important}
.dpad:after{content:"";position:absolute;left:42%;top:42%;width:16%;height:16%;border:2px solid #ffffffd9;border-radius:50%;background:#dcecffb8;box-shadow:0 1px 4px #334a6c55;pointer-events:none;z-index:5}
.action.fire{width:clamp(98px,11cqw,132px)!important;min-width:0;min-height:0}.action.fire .symbol{font-size:clamp(24px,3.7cqw,42px)!important}" + "</style>", 1)
html = html.replace("1.0.54", "1.0.83")
python_source = python_source.replace("1.0.54", "1.0.83")
worker = (
    "// Generated by scripts/build_worker.py. POT BREAKER RE v1.0.83 illustrated\n"
    + "const PAGE=" + json.dumps(html, ensure_ascii=False) + ";\n"
    + "const GAME=" + json.dumps(python_source, ensure_ascii=False) + ";\n"
    + """const SCHEMA=`CREATE TABLE IF NOT EXISTS visits (visitor_id TEXT PRIMARY KEY, created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now')));
CREATE TABLE IF NOT EXISTS game_runs (run_id TEXT PRIMARY KEY, visitor_id TEXT, difficulty TEXT NOT NULL CHECK(difficulty IN ('normal','hard','very_hard')), status TEXT NOT NULL DEFAULT 'playing' CHECK(status IN ('playing','win','lose')), elapsed_ms INTEGER, started_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now')), finished_at TEXT);
CREATE TABLE IF NOT EXISTS game_events (id INTEGER PRIMARY KEY AUTOINCREMENT, visitor_id TEXT, run_id TEXT, event_type TEXT NOT NULL, difficulty TEXT, elapsed_ms INTEGER, created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now')));
CREATE INDEX IF NOT EXISTS game_events_created_at ON game_events(created_at);
CREATE TABLE IF NOT EXISTS rankings (id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL UNIQUE, nickname TEXT NOT NULL, difficulty TEXT NOT NULL CHECK(difficulty IN ('normal','hard','very_hard')), elapsed_ms INTEGER NOT NULL, created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now')), FOREIGN KEY(run_id) REFERENCES game_runs(run_id));
CREATE INDEX IF NOT EXISTS rankings_order ON rankings(difficulty,elapsed_ms);`;
const json=(data,status=200)=>new Response(JSON.stringify(data),{status,headers:{"content-type":"application/json; charset=utf-8","cache-control":"no-store","x-content-type-options":"nosniff"}});
const validDifficulty=value=>["normal","hard","very_hard"].includes(value);
export default {async fetch(request,env){
const path=new URL(request.url).pathname;
if(path==="/health")
  return json({ok:true,version:"1.0.83",visual:"illustrated",engine:"Python/Pyodide",database:!!env.POTBREAKER_DB});
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
const page=path==="/"||path==="/index.html";
if(!page&&path!=="/game.py")return new Response("Not Found",{status:404});
const headers={"content-type":page?"text/html; charset=utf-8":"text/plain; charset=utf-8","cache-control":"no-store","x-content-type-options":"nosniff"};
return new Response(request.method==="HEAD"?null:(page?PAGE:GAME),{status:200,headers});
}};"""
)
(root / "cloudflare" / "worker.js").write_text(worker, encoding="utf-8")
print("Built cloudflare/worker.js", len(worker.encode("utf-8")), "bytes")
