// Ginkgo Tree Breaker v0.6: authoritative game state and ranking (Cloudflare Workers/D1).
const GINKGO_COLS=13,GINKGO_ROWS=7,GINKGO_TOTAL=GINKGO_COLS*GINKGO_ROWS;
const GINKGO_INTERVAL={normal:3000,hard:2000,very_hard:1000};
const GINKGO_SCHEMA=`
CREATE TABLE IF NOT EXISTS ginkgo_runs (
 run_id TEXT PRIMARY KEY,
 difficulty TEXT NOT NULL,
 started_ms INTEGER NOT NULL,
 deadline_ms INTEGER NOT NULL,
 state_json TEXT NOT NULL,
 version INTEGER NOT NULL DEFAULT 0,
 finished INTEGER NOT NULL DEFAULT 0,
 created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS ginkgo_rankings (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 run_id TEXT NOT NULL UNIQUE,
 nickname TEXT NOT NULL,
 difficulty TEXT NOT NULL,
 score INTEGER NOT NULL,
 max_combo INTEGER NOT NULL,
 created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS ginkgo_rankings_order ON ginkgo_rankings(difficulty,score DESC,max_combo DESC);
CREATE TABLE IF NOT EXISTS ginkgo_cleanup (
 month TEXT PRIMARY KEY
);
`;
const ginkgoJSON=(payload,status=200)=>new Response(JSON.stringify(payload),{status,headers:{"content-type":"application/json; charset=utf-8","cache-control":"no-store","x-content-type-options":"nosniff","access-control-allow-origin":"https://potbreaker.com"}});
function ginkgoRand() {const x=new Uint32Array(1);crypto.getRandomValues(x);return x[0]>>>0;}
function ginkgoNext(s){let x=s.rng>>>0;x^=(x<<13);x^=x>>>17;x^=(x<<5);s.rng=x>>>0;return (s.rng>>>0)/4294967296;}
function ginkgoSex(s){return ginkgoNext(s)<.5?0:1;} // 0 male / 1 female
function ginkgoInit(){
 const s={rng:ginkgoRand()||987654321,tick:0,score:0,combo:0,max_combo:0,lock_until:0,cells:[]};
 for(let i=0;i<GINKGO_TOTAL;i++){
  const phase=Math.floor(ginkgoNext(s)*4);
  s.cells.push({phase,sex:phase>=2?1:ginkgoSex(s)});
 }
 return s;
}
function ginkgoAdvance(s,tick){
 const target=Math.max(s.tick,Math.min(121,Math.floor(tick)));
 while(s.tick<target) {
  s.tick++;
  for(const cell of s.cells){
   if(cell.phase===0)cell.phase=1;
   else if(cell.phase===1){
    if(cell.sex===1)cell.phase=2;
    else {cell.phase=0;cell.sex=ginkgoSex(s);}
   } else if(cell.phase===2)cell.phase=3;
   else {cell.phase=0;cell.sex=ginkgoSex(s);}
  }
 }
 return s;
}
function ginkgoScoreTap(s,index,now){
 if(now<s.lock_until)return false;
 const cell=s.cells[index];
 if(cell.phase===2){
  s.combo++;s.score+=s.combo;s.max_combo=Math.max(s.max_combo,s.combo);
  cell.phase=0;cell.sex=ginkgoSex(s);
 }else{
  s.combo=0;
  if(cell.phase===3)s.lock_until=now+500;
 }
 return true;
}
function ginkgoSnapshot(run,now){
 const state=JSON.parse(run.state_json),interval=GINKGO_INTERVAL[run.difficulty];
 ginkgoAdvance(state,Math.floor(Math.min(Math.max(0,now-run.started_ms),60000)/interval));
 return {run_id:run.run_id,difficulty:run.difficulty,score:state.score,combo:state.combo,max_combo:state.max_combo,cells:state.cells.map(c=>c.phase),locked_until:state.lock_until,remaining_ms:Math.max(0,run.deadline_ms-now),done:now>=run.deadline_ms,version:run.version,state};
}
async function ginkgoMonthlyCleanup(db,now=Date.now()){
 const seoul=new Date(now+9*3600000);
 const month=seoul.toISOString().slice(0,7);
 // Month rollover is performed at the first request on/after the 1st; a cron trigger
 // is also supplied so inactive sites do not retain out-of-rank rows indefinitely.
 const prior=await db.prepare("SELECT month FROM ginkgo_cleanup ORDER BY month DESC LIMIT 1").first();
 if(prior?.month===month)return;
 await db.prepare(`DELETE FROM ginkgo_rankings WHERE id IN (
   SELECT id FROM (
    SELECT id, RANK() OVER (PARTITION BY difficulty ORDER BY score DESC,max_combo DESC) as place
    FROM ginkgo_rankings
   ) WHERE place > 3
 )`).run();
 await db.prepare("INSERT OR IGNORE INTO ginkgo_cleanup(month) VALUES (?)").bind(month).run();
}
async function ginkgoAPI(request,env){
 if(!env.POTBREAKER_DB)return ginkgoJSON({error:"ranking_database_unavailable"},503);
 const url=new URL(request.url),path=url.pathname,method=request.method,db=env.POTBREAKER_DB,now=Date.now();
 try {
  await db.exec(GINKGO_SCHEMA);
  if(path==="/api/ginkgo/rankings"&&method==="GET"){
   await ginkgoMonthlyCleanup(db,now);
   const difficulty=url.searchParams.get("difficulty")||"normal";
   if(!(difficulty in GINKGO_INTERVAL))return ginkgoJSON({error:"invalid_difficulty"},400);
   const result=await db.prepare("SELECT nickname,difficulty,score,max_combo,created_at FROM ginkgo_rankings WHERE difficulty=? ORDER BY score DESC,max_combo DESC,created_at ASC LIMIT 100").bind(difficulty).all();
   return ginkgoJSON({rankings:result.results||[]});
  }
  let body={};
  if(method==="POST"){
   if(Number(request.headers.get("content-length")||"0")>16384)return ginkgoJSON({error:"payload_too_large"},413);
   try{body=await request.json()}catch{return ginkgoJSON({error:"invalid_json"},400)}
  }
  if(path==="/api/ginkgo/start"&&method==="POST"){
   const difficulty=body.difficulty;
   if(!(difficulty in GINKGO_INTERVAL))return ginkgoJSON({error:"invalid_difficulty"},400);
   const run_id=crypto.randomUUID(),deadline_ms=now+60000;
   const state=ginkgoInit();
   await db.prepare("INSERT INTO ginkgo_runs(run_id,difficulty,started_ms,deadline_ms,state_json) VALUES(?,?,?,?,?)").bind(run_id,difficulty,now,deadline_ms,JSON.stringify(state)).run();
   return ginkgoJSON({run_id,difficulty,remaining_ms:60000,score:0,combo:0,max_combo:0,cells:state.cells.map(c=>c.phase),done:false,version:0});
  }
  if(path==="/api/ginkgo/state"&&method==="GET"){
   const id=url.searchParams.get("run");
   if(!id||!/^[a-f0-9-]{36}$/i.test(id))return ginkgoJSON({error:"invalid_run"},400);
   const run=await db.prepare("SELECT * FROM ginkgo_runs WHERE run_id=?").bind(id).first();
   if(!run)return ginkgoJSON({error:"run_not_found"},404);
   const {state,...publicState}=ginkgoSnapshot(run,now);
   return ginkgoJSON(publicState);
  }
  if(path==="/api/ginkgo/tap"&&method==="POST"){
   const id=typeof body.run_id==="string"?body.run_id:"",index=body.index;
   if(!/^[a-f0-9-]{36}$/i.test(id)||!Number.isInteger(index)||index<0||index>=GINKGO_TOTAL)return ginkgoJSON({error:"invalid_tap"},400);
   const run=await db.prepare("SELECT * FROM ginkgo_runs WHERE run_id=?").bind(id).first();
   if(!run)return ginkgoJSON({error:"run_not_found"},404);
   if(now>=run.deadline_ms||run.finished)return ginkgoJSON({error:"game_ended"},409);
   const snapshot=ginkgoSnapshot(run,now),s=snapshot.state;
   if(now<s.lock_until)return ginkgoJSON({error:"temporarily_locked",locked_until:s.lock_until,remaining_ms:snapshot.remaining_ms},409);
   ginkgoScoreTap(s,index,now);
   const changed=await db.prepare("UPDATE ginkgo_runs SET state_json=?,version=version+1 WHERE run_id=? AND version=? AND finished=0 AND deadline_ms>?").bind(JSON.stringify(s),id,run.version,now).run();
   if(!changed.meta?.changes)return ginkgoJSON({error:"state_conflict"},409);
   return ginkgoJSON({score:s.score,combo:s.combo,max_combo:s.max_combo,cells:s.cells.map(c=>c.phase),locked_until:s.lock_until,remaining_ms:snapshot.remaining_ms,version:run.version+1});
  }
  if(path==="/api/ginkgo/finish"&&method==="POST"){
   const id=typeof body.run_id==="string"?body.run_id:"",nickname=typeof body.nickname==="string"?body.nickname.trim():"";
   if(!/^[a-f0-9-]{36}$/i.test(id)||nickname.length<1||nickname.length>16||/[\x00-\x1F\x7F<>]/.test(nickname))return ginkgoJSON({error:"invalid_result"},400);
   const run=await db.prepare("SELECT * FROM ginkgo_runs WHERE run_id=?").bind(id).first();
   if(!run)return ginkgoJSON({error:"run_not_found"},404);
   if(now<run.deadline_ms)return ginkgoJSON({error:"still_playing"},409);
   const s=JSON.parse(run.state_json);
   const updated=await db.prepare("UPDATE ginkgo_runs SET finished=1 WHERE run_id=? AND finished=0").bind(id).run();
   if(!updated.meta?.changes)return ginkgoJSON({error:"already_submitted"},409);
   await db.prepare("INSERT INTO ginkgo_rankings(run_id,nickname,difficulty,score,max_combo) VALUES (?,?,?,?,?)").bind(id,nickname,run.difficulty,s.score,s.max_combo).run();
   await ginkgoMonthlyCleanup(db,now);
   return ginkgoJSON({ok:true,score:s.score,max_combo:s.max_combo});
  }
  return ginkgoJSON({error:"not_found"},404);
 }catch(e){return ginkgoJSON({error:"server_error"},500);}
}
async function ginkgoCronCleanup(env,at=Date.now()){
 if(!env.POTBREAKER_DB)return;
 const seoul=new Date(at+9*3600000);
 if(seoul.getUTCDate()!==1)return;
 await env.POTBREAKER_DB.exec(GINKGO_SCHEMA);
 await ginkgoMonthlyCleanup(env.POTBREAKER_DB,at);
}
