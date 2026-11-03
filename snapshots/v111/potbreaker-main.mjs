import {ActionButtonModule, GameViewportModule, ScreenLayoutModule} from '../shared/ui-components.js';
import {PotBreakerInputModule} from './input.js';
import {createPotBreakerRenderer} from './renderer.js';

(()=>{'use strict';
const $=id=>document.getElementById(id),canvas=$('board');
const dirs={up:[0,-1],down:[0,1],left:[-1,0],right:[1,0]};
let runtime=null,game=null,active=false,paused=false,raf=0,last=0,acc=0,world=null,tick=0,endTimer=0,controls=null;
const renderer=createPotBreakerRenderer({canvas,assets:window.POT_ASSETS});
const viewport = new GameViewportModule();
const screenLayout = new ScreenLayoutModule({
 screens:{title:$('title'),intro:$('intro'),gamePanel:$('gamePanel'),end:$('end')},
 bodyStates:{'is-playing':id=>id==='gamePanel'||id==='end','is-pot-subview':id=>id!=='title'}
});
const show=id=>screenLayout.show(id);show('title');
// Difficulty selection and anonymous play/event tracking.
let selectedDifficulty='normal',activeRunId=null,gameStartedAt=0,lastClearMs=0,visitorId=null;
const difficultyNames={normal:'노멀',hard:'하드',very_hard:'베리 하드'};
async function api(path,data){const response=await fetch(path,{method:data?'POST':'GET',headers:data?{'content-type':'application/json'}:undefined,body:data?JSON.stringify(data):undefined,cache:'no-store'});const payload=await response.json().catch(()=>({}));if(!response.ok)throw new Error(payload.error||'서버 연결에 실패했습니다.');return payload}
api('/api/visit',{}).then(result=>{visitorId=result.visitor_id}).catch(()=>{});
document.querySelectorAll('[data-difficulty]').forEach(button=>button.addEventListener('click',()=>{selectedDifficulty=button.dataset.difficulty;document.querySelectorAll('[data-difficulty]').forEach(item=>item.setAttribute('aria-pressed',String(item===button)))}));
function formatTime(ms){const seconds=Math.max(0,ms)/1000;return `${Math.floor(seconds/60)}:${(seconds%60).toFixed(2).padStart(5,'0')}`}
function openRanking(form=false){$('rankingPanel').classList.remove('hidden');$('rankForm').classList.toggle('hidden',!form);$('rankingMessage').textContent='';loadRankings();if(form){$('rankSummary').textContent=`${formatTime(lastClearMs)} · ${difficultyNames[selectedDifficulty]}`;$('rankNickname').focus()}}
async function loadRankings(){const list=$('rankingList');list.innerHTML='<li>랭킹을 불러오는 중…</li>';try{const result=await api('/api/rankings');list.replaceChildren();if(!result.rankings.length){list.innerHTML='<li>아직 등록된 클리어 기록이 없습니다.</li>';return}for(const row of result.rankings){const item=document.createElement('li');item.textContent=`${row.nickname}　${formatTime(row.elapsed_ms)}　`;const detail=document.createElement('span');detail.textContent=`${difficultyNames[row.difficulty]||row.difficulty} · ${row.created_at}`;item.append(detail);list.append(item)}}catch(error){list.innerHTML='<li>랭킹을 불러오지 못했습니다.</li>';$('rankingMessage').textContent=error.message}}
$('openRanking').onclick=()=>openRanking(false);$('closeRanking').onclick=()=>$('rankingPanel').classList.add('hidden');$('rankingPanel').addEventListener('click',event=>{if(event.target===$('rankingPanel'))$('rankingPanel').classList.add('hidden')});$('registerScore').onclick=()=>openRanking(true);$('rankForm').addEventListener('submit',async event=>{event.preventDefault();const nickname=$('rankNickname').value.trim();if(!nickname)return;if(!activeRunId){$('rankingMessage').textContent='랭킹 등록을 위한 게임 기록이 없습니다. 다시 시작해 주세요.';return;}try{await api('/api/rankings',{run_id:activeRunId,nickname});$('rankForm').classList.add('hidden');$('rankingMessage').textContent='랭킹에 등록했습니다.';await loadRankings()}catch(error){$('rankingMessage').textContent=error.message}});

new ActionButtonModule($('openIntro'),()=>{renderer.unlockGameAudio();show('intro')}).mount();new ActionButtonModule($('begin'),start).mount();new ActionButtonModule($('again'),start).mount();$('home').onclick=()=>{stop();viewport.releaseLandscape();show('title')};$('pauseHome').onclick=()=>{stop();viewport.releaseLandscape();$('pausePanel').classList.add('hidden');show('title')};$('pause').onclick=()=>{paused=true;$('pausePanel').classList.remove('hidden')};$('resume').onclick=()=>{paused=false;$('pausePanel').classList.add('hidden');last=performance.now()};$('retry').onclick=()=>{ $('loader').classList.add('hidden');start()};
controls=new PotBreakerInputModule({canvas,directionPad:$('directionPad'),fireButton:$('fire'),dashButton:$('dash'),isRunning:()=>active&&!paused,onPause:()=>$('pause').click(),width:19,height:11});
function updateHUD(s){
 $('catAmmo').textContent=s.ammo+'/'+s.ammo_cap;$('bossAmmo').textContent=s.boss_ammo;$('difficultyLabel').textContent=difficultyNames[s.difficulty]||'노멀';
 $('catHP').textContent='♥'.repeat(Math.max(0,s.player_hp))+'♡'.repeat(Math.max(0,3-s.player_hp));
 $('bossHP').textContent=s.boss_hp+'/'+s.boss_hp_cap;$('dashLabel').textContent=s.player_dash_cd>0?s.player_dash_cd.toFixed(1)+'s':'대시';
 $('dash').disabled=false;$('dash').classList.toggle('cooldown',s.player_dash_cd>0);$('fire').disabled=s.ammo<1;
 $('notice').textContent=s.notice;$('notice').classList.toggle('hidden',!s.notice);
}
function stop(){active=false;if(raf)cancelAnimationFrame(raf);raf=0;if(endTimer){clearTimeout(endTimer);endTimer=0}controls?.stop()}
async function start(){
 stop();paused=false;await viewport.requestLandscape();show('gamePanel');$('endTag').textContent='';$('endTitle').textContent='';$('endText').textContent='';activeRunId=null;lastClearMs=0;$('registerScore').classList.add('hidden');try{const run=await api('/api/runs',{difficulty:selectedDifficulty,visitor_id:visitorId});activeRunId=run.run_id}catch(error){console.warn('랭킹 세션 생성 실패:',error)}renderer.reset();$('damageFlash').style.opacity='0';$('pausePanel').classList.add('hidden');$('loader').classList.remove('hidden');$('retry').classList.add('hidden');$('loadStatus').textContent='게임 엔진을 불러오는 중…';
 try{
  if(!window.loadPyodide)throw new Error('Pyodide를 불러오지 못했습니다. 인터넷 연결을 확인해 주세요.');
  if(!runtime){runtime=await loadPyodide({indexURL:'https://cdn.jsdelivr.net/pyodide/v0.27.7/full/'});const engine=await fetch('/game.py',{cache:'no-store'});if(!engine.ok)throw new Error('게임 엔진을 불러오지 못했습니다.');await runtime.runPythonAsync(await engine.text())}
  if(game)game.destroy();game=runtime.runPython('PotBreaker(None, \"'+selectedDifficulty+'\")');world=JSON.parse(game.state());updateHUD(world);renderer.trackEffects(world,tick);show('gamePanel');$('loader').classList.add('hidden');active=true;last=performance.now();gameStartedAt=last;acc=0;raf=requestAnimationFrame(safeLoop)
 }catch(error){$('loadStatus').textContent='게임을 불러오지 못했습니다. '+(error?.message||error);$('retry').classList.remove('hidden')}
}
function safeLoop(now){try{loop(now)}catch(error){console.error('게임 화면 갱신 오류:',error);active=false;$('loadStatus').textContent='게임 화면 갱신 오류: '+(error?.message||error);$('loader').classList.remove('hidden');$('retry').classList.remove('hidden')}}
function loop(now){
 if(!active)return;
 if(!paused){
  const dt=Math.min(.12,(now-last)/1000||.03);tick+=dt;acc+=dt;renderer.step(dt,tick);
  $('damageFlash').style.opacity=String(renderer.damageFlashOpacity());
  let count=0;
  while(acc>=.04&&count++<3){
   const [mx,my]=controls.getMove(dirs); const {fire:fireNow,charging:chargingNow,dash:dashNow}=controls.consumeActions();
   world=JSON.parse(game.step(.04,mx,my,dashNow,fireNow,0,0,chargingNow));renderer.trackEffects(world,tick);acc-=.04;updateHUD(world);
   if(world.phase!=='playing')break;
  }
  renderer.draw(world,tick,dt);
  if(world.phase!=='playing'){
   active=false;endTimer=window.setTimeout(()=>{endTimer=0;if(world&&world.phase!=='playing')end(world.phase)},450);
   last=now;raf=requestAnimationFrame(safeLoop);return;
  }
 }
 last=now;raf=requestAnimationFrame(safeLoop);
}
async function end(outcome){if(endTimer){clearTimeout(endTimer);endTimer=0}show('end');void viewport.requestLandscape();let win=outcome==='win';lastClearMs=Math.max(0,Math.round(performance.now()-gameStartedAt));$('registerScore').classList.add('hidden');$('endingArt').src=window.POT_ASSETS[win?'victory':'defeat'];$('endTag').textContent=win?'★ WINNER ★':'GAME OVER';$('endTitle').textContent=win?'기묘 승리!':'크다 부장 승리!';$('endText').textContent=win?'화분 한 방! 크다 부장의 뚝배기를 깼습니다.':'기묘가 화분에 머리만 내놓고 심어졌습니다…';if(win)$('registerScore').classList.remove('hidden');if(activeRunId){try{await api('/api/runs/finish',{run_id:activeRunId,outcome,elapsed_ms:lastClearMs});}catch(error){$('rankingMessage').textContent=error.message}}}
window.__potBreakerVisualCheck=(state)=>{world=state;show('gamePanel');renderer.draw(state,tick,.016)};
window.addEventListener('pageshow',()=>{stop();viewport.releaseLandscape();paused=false;activeRunId=null;lastClearMs=0;$('registerScore').classList.add('hidden');$('pausePanel').classList.add('hidden');$('loader').classList.add('hidden');$('retry').classList.add('hidden');show('title')});window.addEventListener('pagehide',stop);
})();
