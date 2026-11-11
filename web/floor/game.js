"use strict";
import './i18n.js';
import { ART, CLERIC_ART } from './art.js';

const CHAR={gimyo:'기묘',keuda:'크다부장',yi:'이 대리',ho:'호 사원',gam:'감 과장'};
const $=id=>document.getElementById(id);const show=id=>{for(const pane of ['cover','intro','choose','play'])$(pane).classList.toggle('hidden',pane!==id);window.scrollTo({top:0,behavior:'instant'})};
for(const im of document.querySelectorAll('[data-hero]')){im.src=ART[im.dataset.hero];im.alt=CHAR[im.dataset.hero]+' 체스 말';}
let chosen='gimyo',game=null,timerId=null,aiId=null;const COL=11,ROWS=11,TEAMS=4;
const pos=(x,y)=>y*COL+x;const xy=i=>[i%COL,Math.floor(i/COL)];const inside=(x,y)=>x>=0&&x<COL&&y>=0&&y<ROWS;
const chooseRandom=(arr)=>arr[Math.floor(Math.random()*arr.length)];const shuffle=a=>{for(let i=a.length-1;i>0;i--){let j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]]}return a};

let soundEnabled=true, audioEngine=null, cueTimer=null, endTimer=null, fxHold=0;
const nowPlaying=()=>!!game&&game.phase==='playing';
function setEvent(message,type=''){
 const box=$('eventToast');box.textContent=message;box.className='event-toast'+(type?' event-'+type:'');
}
function playSound(type){
 if(!soundEnabled||!window.AudioContext&&!window.webkitAudioContext)return;
 try{
  audioEngine=audioEngine||new (window.AudioContext||window.webkitAudioContext)();
  if(audioEngine.state==='suspended')audioEngine.resume();
  const specs={select:[620,.07,0.035],move:[420,.10,.05],attack:[170,.18,.12],trap:[115,.24,.11],turn:[460,.08,.035],win:[740,.26,.09],lose:[180,.25,.07],skill:[910,.16,.07]};
  const [freq,duration,gain]=specs[type]||specs.move;
  const osc=audioEngine.createOscillator(),vol=audioEngine.createGain(),t=audioEngine.currentTime;
  osc.type=type==='attack'||type==='trap'?'sawtooth':'sine';osc.frequency.setValueAtTime(freq,t);
  if(type==='win')osc.frequency.exponentialRampToValueAtTime(freq*1.5,t+duration);
  else osc.frequency.exponentialRampToValueAtTime(Math.max(60,freq*.78),t+duration);
  vol.gain.setValueAtTime(gain,t);vol.gain.exponentialRampToValueAtTime(.001,t+duration);
  osc.connect(vol);vol.connect(audioEngine.destination);osc.start(t);osc.stop(t+duration+.005);
 }catch(e){/* Audio is optional. The game must not fail if sound is unavailable. */}
}
function cue(text,duration=780){const node=$('turnCue');if(!node)return;if(cueTimer)clearTimeout(cueTimer);node.classList.remove('active');node.textContent=text;void node.offsetWidth;node.classList.add('active');cueTimer=setTimeout(()=>node.classList.remove('active'),duration)}
function burst(i,symbol='✦',danger=false){
 const cell=$('board').children[i];if(!cell)return;
 const rect=cell.getBoundingClientRect(),node=document.createElement('span');node.className='burst-symbol';node.textContent=symbol;
 node.style.left=(rect.left+rect.width/2-26)+'px';node.style.top=(rect.top+rect.height/2-26)+'px';$('effectLayer').append(node);
 const frames=[{transform:'translateY(7px) scale(.45)',opacity:0},{transform:'translateY(-9px) scale(1.3)',opacity:1,offset:.35},{transform:'translateY(-52px) scale(.9)',opacity:0}];
 if(node.animate){const a=node.animate(frames,{duration:750,easing:'ease-out'});a.onfinish=()=>node.remove()}else setTimeout(()=>node.remove(),750);
 if(danger){const arena=$('arena');arena.classList.remove('hit','trap');void arena.offsetWidth;arena.classList.add('trap');setTimeout(()=>arena.classList.remove('trap'),480)}
}
function travelFx(from,to,character,kind,alive=true){
 const a=$('board').children[from],b=$('board').children[to];if(!a||!b)return;
 const start=a.getBoundingClientRect(),end=b.getBoundingClientRect();
 if(start.width===0||end.width===0)return;
 const ghost=document.createElement('img');ghost.src=ART[character];ghost.className='flying-piece';ghost.alt='';ghost.style.left=start.left+'px';ghost.style.top=start.top+'px';ghost.style.width=start.width+'px';ghost.style.height=start.height+'px';$('effectLayer').append(ghost);
 const dx=(end.left+end.width/2)-(start.left+start.width/2),dy=(end.top+end.height/2)-(start.top+start.height/2);
 const cellEnd=b.querySelector('img');if(cellEnd&&alive)cellEnd.style.visibility='hidden';
 const frames=[{transform:'translate(0,0) scale(1)',opacity:1},{transform:`translate(${dx*.48}px,${dy*.48-12}px) scale(1.25)`,opacity:1,offset:.55},{transform:`translate(${dx}px,${dy}px) scale(${alive?'1.05':'.2'})`,opacity:alive?1:0}];
 const done=()=>{ghost.remove();if(cellEnd)cellEnd.style.visibility=''};
 const duration=game?.mode==='ai'&&game?.team===0?900:kind==='attack'?340:440;if(ghost.animate){const animation=ghost.animate(frames,{duration,easing:'cubic-bezier(.2,.75,.2,1)'});animation.onfinish=done;animation.oncancel=done}else{setTimeout(done,duration)}
}
function impact(i){const c=$('board').children[i];if(!c)return;const r=c.getBoundingClientRect(),v=document.createElement('div');v.className='impact-ring';v.style.left=(r.left+r.width/2-12)+'px';v.style.top=(r.top+r.height/2-12)+'px';v.style.width='24px';v.style.height='24px';$('effectLayer').append(v);if(v.animate){const a=v.animate([{transform:'scale(.3)',opacity:1},{transform:'scale(3.5)',opacity:0}],{duration:560,easing:'ease-out'});a.onfinish=()=>v.remove()}else setTimeout(()=>v.remove(),560)}
function blessingFx(i,buff){
 const cell=$('board').children[i];if(!cell)return;
 const r=cell.getBoundingClientRect(),node=document.createElement('div');node.className='blessing';
 const beam=document.createElement('div');beam.className='blessing-beam';beam.style.left=(r.left+r.width/2)+'px';beam.style.top=(r.top+r.height/2)+'px';$('effectLayer').append(beam);setTimeout(()=>beam.remove(),1850);
 const img=document.createElement('img');img.src=CLERIC_ART;img.alt='감 과장 클래릭';node.append(img);
 const label=document.createElement('span');label.textContent=buff==='extra'?'감 과장의 가호 · 한 턴 더!':'감 과장의 가호 · 폰 한 개 추가!';node.append(label);
 node.style.left=Math.max(8,Math.min(window.innerWidth-225,r.left-70))+'px';node.style.top=Math.max(8,r.top-85)+'px';$('effectLayer').append(node);
 if(node.animate)node.animate([{transform:'translateY(-65vh) scale(.55)',opacity:0},{transform:'translateY(-14px) scale(1.12)',opacity:1,offset:.42},{transform:'translateY(0) scale(1)',opacity:1,offset:.72},{transform:'translateY(35px) scale(.85)',opacity:0}],{duration:1800,easing:'cubic-bezier(.18,.75,.25,1)'});
 setTimeout(()=>node.remove(),1850);
}
function moveFeedback({from,to,character,team,captured,buff}){
 travelFx(from,to,character,captured?'attack':'move',true);
 const who=game.mode==='ai'&&team!==0?`${team+1}P 상대`:`플레이어 ${team+1}`;
 const coord=i=>`${Math.floor(i/COL)+1}행 ${i%COL+1}열`;
 if(game.mode==='ai'&&team!==0)cue(`${team+1}P 상대 이동 · ${coord(from)} → ${coord(to)}`,1300);
 if(buff){setTimeout(()=>blessingFx(to,buff),220);playSound('skill');setEvent(`${who} · ${buff==='extra'?'⏱ 한 턴 더':'♟ 폰 한 개 추가'}! 감 과장의 가호`, 'win')}
 else if(captured){burst(to,'⚔️',true);impact(to);playSound('attack');setEvent(`${who} · 상대 말 격파`, 'attack')}
 else{playSound('move');setEvent(`${who} 이동 ${coord(from)} → ${coord(to)}`)}
}
function showEndDialog(){
 const modal=$('endModal');if(!game||game.phase!=='finished')return;$('handoff').classList.add('hidden');
 const humanWon=game.winner===0,draw=game.winner===null;
 const title=draw?'무승부':game.mode==='ai'?(humanWon?'승리!':`AI ${game.winner+1}P 승리`):`플레이어 ${game.winner+1} 승리!`;
 $('endHeading').textContent=title;$('endReason').textContent=game.reason;
 $('endArt').src=ART[game.characters[draw?0:game.winner]];
 $('endArt').alt=CHAR[game.characters[draw?0:game.winner]]+' 체스말';
 $('endStats').textContent=`총 ${game.turn}턴 진행 · 남은 말 ${active(0).length} : ${active(1).length} : ${active(2).length} : ${active(3).length}`;
 modal.classList.remove('hidden');modal.focus();if(!draw){playSound(humanWon?'win':'lose');cue('🏆 '+title)}
 setEvent(title+' · '+game.reason,draw?'':'win');
}
function clearEnd(){if(endTimer)clearTimeout(endTimer);endTimer=null;$('endModal').classList.add('hidden');$('handoff').classList.add('hidden');$('arena').classList.remove('win');}

const FRONT=[[0,-1],[0,1],[1,0],[-1,0]];
function homeCells(team){
 const back=['special','special','queen','special'],cells=[];
 for(let n=0;n<6;n++){
  let front;
  if(team===0)front=pos(3+n,9);
  else if(team===1)front=pos(3+n,1);
  else if(team===2)front=pos(1,3+n);
  else front=pos(9,3+n);
  cells.push({front});
 }
 for(let n=0;n<4;n++){
  let rear;
  if(team===0)rear=pos(4+n,10);
  else if(team===1)rear=pos(4+n,0);
  else if(team===2)rear=pos(0,4+n);
  else rear=pos(10,4+n);
  cells.push({rear,role:back[n]});
 }
 return cells;
}
function newGame(character,mode){
 const characters=[character,...shuffle(['gimyo','keuda','yi','ho'].filter(c=>c!==character))],pieces=[];
 for(let team=0;team<TEAMS;team++)homeCells(team).forEach((cell,n)=>{
  pieces.push({id:team*10+n,team,at:cell.front??cell.rear,role:cell.front===undefined?cell.role:'basic'});
 });
 const crownAt=pos(5,5);
 pieces.push({id:-1,team:-1,at:crownAt,role:'king'});
 const cells=shuffle(Array.from({length:49},(_,i)=>pos(2+i%7,2+Math.floor(i/7))).filter(i=>i!==crownAt)).slice(0,6);
 const items=new Map(cells.map((cell,i)=>[cell,i<4?'extra':'pawn']));
 return {mode,characters,pieces,items,nextPieceId:40,alive:[true,true,true,true],aiRecent:[],selected:null,armed:false,abilityUsed:[false,false,false,false],gimyoUses:[0,0,0,0],comboRemaining:0,pendingExtra:false,turn:1,team:Math.floor(Math.random()*TEAMS),lastMove:null,graceUntil:0,handoff:false,remaining:10,timeouts:[0,0,0,0],phase:'playing',winner:null,reason:'',notice:'중앙 왕은 폰만 차지할 수 있습니다. 30바퀴 종료 때 왕을 지키세요.',crownHolder:null,crownOwner:null,crownAt,rounds:0,roundSteps:0,roundLimit:30};
}
const skillSpent=team=>game.characters[team]==='gimyo'?game.gimyoUses[team]>=2:game.abilityUsed[team];
const skillLeft=team=>game.characters[team]==='gimyo'?2-game.gimyoUses[team]:Number(!game.abilityUsed[team]);
const at=i=>game.pieces.find(p=>p.at===i);const active=t=>game.pieces.filter(p=>p.team===t);
const forwardVec=t=>FRONT[t];const blocked=i=>i<0||i>=COL*ROWS;
const crownPiece=()=>game.pieces.find(p=>p.id===game.crownHolder);
const crownCell=()=>crownPiece()?.at??game.crownAt;
const aliveTeams=()=>game.alive.map((alive,i)=>alive?i:null).filter(i=>i!==null);
function nextAlive(team){for(let n=1;n<=TEAMS;n++){const candidate=(team+n)%TEAMS;if(game.alive[candidate])return candidate}return team}
const roleOf=(piece,holderId=game.crownHolder)=>piece?.id===holderId?'king':piece?.role;
function attackKind(attacker,target,boost=false,holderId=game.crownHolder){
 if(!target||target.team===attacker.team)return null;
 const from=roleOf(attacker,holderId),to=roleOf(target,holderId);
 if(from==='king')return to==='special'||to==='queen'?'attack':null;
 if(from==='basic')return to==='special'?null:'attack';
 if(from==='special'){
  if(to==='basic'||to==='special')return 'attack';
  if(to==='king'&&boost&&game.characters[attacker.team]==='ho'&&!game.abilityUsed[attacker.team]&&game.pieces.some(p=>p.team===attacker.team&&p.role==='queen'))return 'attack';
  return null;
 }
 if(from==='queen')return to==='king'||to==='special'?'demote':null;
 return null;
}
function moveOptions(piece,boost=false,board=game.pieces,holderId=game.crownHolder){
 if(!piece||piece.team<0)return[];
 const [sx,sy]=xy(piece.at),out=[];
 const power=boost&&(piece.role==='special'||piece.role==='basic')&&game.characters[piece.team]==='gimyo';
 const occupant=i=>board.find(q=>q.at===i);
 const ray=(dx,dy,max)=>{for(let distance=1;distance<=max;distance++){
  const nx=sx+dx*distance,ny=sy+dy*distance;if(!inside(nx,ny))break;
  const i=pos(nx,ny),target=occupant(i);
  if(target){
   const kind=attackKind(piece,target,boost,holderId);
   if(kind&&(piece.role!=='basic'||distance===1))out.push({at:i,kind});
   if(target.team===piece.team||!power||roleOf(target,holderId)==='king')break;
  }else out.push({at:i,kind:'move'});
 }};
 if(piece.role==='queen'||piece.role==='special'||piece.role==='basic'&&power){
  const max=piece.role==='queen'?2:piece.role==='basic'?2:2*(power?2:1);
  for(const dx of [-1,0,1])for(const dy of [-1,0,1])if(dx||dy)ray(dx,dy,max);
 }else for(const dx of [-1,0,1])for(const dy of [-1,0,1])if(dx||dy){
  const nx=sx+dx,ny=sy+dy;if(!inside(nx,ny))continue;
  const i=pos(nx,ny),target=occupant(i);
  if(!target)out.push({at:i,kind:'move'});
  else{const kind=attackKind(piece,target,boost,holderId);if(kind)out.push({at:i,kind})}
 }
 return out;
}
function legalOptions(piece,boost=false,board=game.pieces,holderId=game.crownHolder){
 return moveOptions(piece,boost,board,holderId).filter(o=>o.at!==game.crownAt||holderId===null||piece.id===holderId||board.some(p=>p.at===o.at));
}
function teamHasLegalMove(team){
 return game.pieces.some(p=>p.team===team&&(legalOptions(p).length||!skillSpent(team)&&game.characters[team]==='gimyo'&&legalOptions(p,true).length));
}
function targets(){
 if(!game||game.phase!=='playing'||game.selected===null)return[];
 const piece=game.pieces.find(p=>p.id===game.selected);if(!piece)return[];
 const options=legalOptions(piece,game.armed);
 if(game.armed&&game.characters[game.team]==='yi')for(const pawn of active(game.team))
  if(pawn.role==='basic'&&pawn.id!==piece.id)options.push({at:pawn.at,kind:'swap'});
 return game.comboRemaining?options.filter(o=>o.kind==='attack'):options;
}
function eliminateTeam(team,reason){
 if(!game.alive[team])return;
 if(game.crownOwner===team){game.crownHolder=null;game.crownOwner=null;game.pieces.push({id:-1,team:-1,at:game.crownAt,role:'king'});}
 game.alive[team]=false;game.pieces=game.pieces.filter(p=>p.team!==team);
 game.notice=`${team+1}P ${CHAR[game.characters[team]]} 탈락 · ${reason}`;
 setEvent(game.notice,'danger');
}
function crownWinner(){
 if(game.rounds<game.roundLimit||game.crownOwner===null)return false;
 end('30바퀴 종료 · 왕 사수 성공',game.crownOwner);return true;
}
function assessAfterMove(){
 if(game.phase==='finished')return true;
 for(const opponent of aliveTeams())if(active(opponent).length===0)eliminateTeam(opponent,'남은 말 없음');
 return crownWinner();
}
function end(result,winner){
 if(!game||game.phase==='finished')return;
 game.phase='finished';game.winner=winner;game.reason=result;
 game.notice=winner===null?'무승부 · '+result:`${game.mode==='ai'?(winner===0?'승리!':'AI 승리 · '+(winner+1)+'P'):'플레이어 '+(winner+1)+' 승리!'} · ${result}`;
 if(timerId)clearInterval(timerId);timerId=null;if(aiId)clearTimeout(aiId);aiId=null;
 if(result.includes('왕'))$('arena').classList.add('win');
 render();if(endTimer)clearTimeout(endTimer);
 showEndDialog();
}
function assess(){
 if(!game||game.phase==='finished')return true;
 return crownWinner();
}
function nextTurn(acted,extra=false){
 if(!game||game.phase!=='playing')return;
 const actingTeam=game.team;
 if(acted)game.timeouts[actingTeam]=0;else game.timeouts[actingTeam]++;
 game.selected=null;game.armed=false;game.comboRemaining=0;game.pendingExtra=false;
 if(assess())return;
 game.turn++;
 const next=extra?actingTeam:nextAlive(actingTeam);
 if(!extra&&++game.roundSteps>=aliveTeams().length){game.roundSteps=0;game.rounds++;if(crownWinner())return;}
 game.team=next;game.remaining=10;
 game.notice=extra?'감 과장의 가호! 한 턴 더 움직이세요.':game.rounds>=game.roundLimit&&game.crownOwner===null?'연장전! 왕을 먼저 차지하면 승리합니다.':acted?'다음 플레이어의 차례입니다.':`시간 초과 · ${CHAR[game.characters[actingTeam]]} 턴 종료.`;
 render();cue(extra?'⏱ 한 턴 더!':`${game.team+1}P · ${CHAR[game.characters[game.team]]} 차례`);
 if(game.mode==='local'&&!extra){game.handoff=true;$('handoffHeading').textContent=`플레이어 ${game.team+1} 차례`;$('handoff').classList.remove('hidden');$('handoffBtn').focus()}
 if(!acted){setEvent(`${actingTeam+1}P 시간 초과 · 다음 차례`,'danger');playSound('turn')}
 queueAI();
}
function spawnPawn(team){
 const home=homeCells(team),front=home.map(c=>c.front).filter(i=>i!==undefined),rear=home.map(c=>c.rear).filter(i=>i!==undefined);
 const half=Array.from({length:COL*ROWS},(_,i)=>i).filter(i=>{
  const [x,y]=xy(i);return team===0?y>=5:team===1?y<5:team===2?x<5:x>=5;
 });
 const cell=[...front,...rear,...half].find(i=>!at(i)&&!game.items.has(i));
 if(cell===undefined)return false;
 game.pieces.push({id:game.nextPieceId++,team,at:cell,role:'basic'});return true;
}
function closestEmpty(origin,excluded=origin){
 const [ox,oy]=xy(origin);
 return Array.from({length:COL*ROWS},(_,i)=>i).filter(i=>i!==excluded&&i!==game.crownAt&&!at(i))
  .sort((a,b)=>{const [ax,ay]=xy(a),[bx,by]=xy(b);
   return Math.max(Math.abs(ax-ox),Math.abs(ay-oy))-Math.max(Math.abs(bx-ox),Math.abs(by-oy))
    ||Math.abs(ax-ox)+Math.abs(ay-oy)-Math.abs(bx-ox)-Math.abs(by-oy)||a-b})[0];
}
function openCrownCell(){
 const center=pos(Math.floor(COL/2),Math.floor(ROWS/2)),[cx,cy]=xy(center);
 return Array.from({length:COL*ROWS},(_,i)=>i).filter(i=>!at(i))
  .sort((a,b)=>{const [ax,ay]=xy(a),[bx,by]=xy(b);
   return Math.max(Math.abs(ax-cx),Math.abs(ay-cy))-Math.max(Math.abs(bx-cx),Math.abs(by-cy))
    ||Math.abs(ax-cx)+Math.abs(ay-cy)-Math.abs(bx-cx)-Math.abs(by-cy)||a-b})[0];
}
function act(destination,kind){
 if(!nowPlaying())return;
 const piece=game.pieces.find(x=>x.id===game.selected);if(!piece)return;
 if(!targets().some(o=>o.at===destination&&o.kind===kind))return;
 const from=piece.at,character=game.characters[piece.team],team=piece.team;
 if(kind==='swap'){
  const pawn=at(destination);if(!game.armed||character!=='yi'||pawn?.team!==team||pawn.role!=='basic')return;
  piece.at=destination;pawn.at=from;game.abilityUsed[team]=true;
  game.lastMove={from,to:destination,team,kind,captured:false,buff:null,swap:true};
  nextTurn(true);setEvent(`${team+1}P 이 대리 · 내 폰과 자리 교체`,'win');playSound('skill');return;
 }
 const target=kind==='move'?null:at(destination);
 if(kind!=='move'&&(!target||attackKind(piece,target,game.armed)!==kind))return;
 const gimyoPower=game.armed&&character==='gimyo';
 if(kind==='demote'){
  const oldRole=roleOf(target),newRole=oldRole==='king'?'special':'basic';
  const displaced=closestEmpty(destination);
  if(displaced===undefined)return;
  target.at=displaced;target.role=newRole;
  piece.at=destination;
  if(oldRole==='king'){
   game.crownHolder=null;game.crownOwner=null;
   game.crownAt=openCrownCell();
   game.pieces.push({id:-1,team:-1,at:game.crownAt,role:'king'});
  }
  if(gimyoPower)game.gimyoUses[team]++;
  game.lastMove={from,to:destination,team,kind,captured:false,buff:null,demoted:newRole,displaced};
  const finished=assessAfterMove();if(!finished)nextTurn(true);
  travelFx(from,destination,character,'attack',true);burst(destination,'⬇',true);playSound('attack');
  setEvent(`${team+1}P 퀸 이동 · ${oldRole==='king'?'왕→나이트 · 왕 중앙 복귀':'나이트→폰'} 강등`,'attack');return;
 }
 const hoPower=game.armed&&character==='ho'&&piece.role==='special'&&roleOf(target)==='king';
 const keudaFirst=game.armed&&character==='keuda'&&piece.role==='basic'&&kind==='attack';
 const comboSecond=game.comboRemaining>0;
 let captured=false,crownTaken=false;
 if(kind==='attack'){
  if(hoPower){const queen=active(team).find(p=>p.role==='queen');if(!queen)return;
   game.pieces=game.pieces.filter(p=>p!==queen);game.abilityUsed[team]=true;}
  if(roleOf(target)==='king'){
   game.crownHolder=piece.id;game.crownOwner=team;crownTaken=true;
  }
  game.pieces=game.pieces.filter(x=>x!==target);captured=true;
 }
 piece.at=destination;
 if(gimyoPower)game.gimyoUses[team]++;if(keudaFirst)game.abilityUsed[team]=true;
 const blockedBlessing=game.crownOwner===team&&game.items.has(destination);
 const buff=blockedBlessing?null:game.items.get(destination)||null;
 if(buff){game.items.delete(destination);if(buff==='pawn')spawnPawn(team)}
 if(buff==='extra')game.pendingExtra=true;
 game.lastMove={from,to:destination,team,kind,captured,buff,crownTaken,hoPower,ability:gimyoPower||keudaFirst||comboSecond};
 const finished=assessAfterMove();
 if(!finished&&keudaFirst&&!crownTaken){
  game.armed=false;game.comboRemaining=1;game.selected=piece.id;
  if(targets().length){game.remaining=10;game.notice='연속 공격! 같은 폰으로 인접한 적 한 말을 더 고르거나 폰을 다시 눌러 종료하세요.';render();cue('⚔ 두 번째 공격');setEvent(game.notice,'attack');if(game.mode==='ai')queueAI();moveFeedback({from,to:destination,character,team,captured,buff});return}
  game.comboRemaining=0;
 }
 if(!finished)nextTurn(true,game.pendingExtra);
 if(!finished&&game.mode==='ai'&&team!==0)game.graceUntil=performance.now()+900;
 moveFeedback({from,to:destination,character,team,captured,buff});
 if(crownTaken){cue('♛ '+(team+1)+'P 왕 차지!',1500);setEvent(`${team+1}P가 왕을 차지했습니다. 폰으로 탈환하세요!`,'win')}
 else if(hoPower)setEvent(`${team+1}P 호 사원 · 퀸을 제물로 나이트가 왕을 차지!`,'win');
 else if(blockedBlessing)setEvent('왕을 보유 중이라 가호가 발동하지 않았습니다.','danger');
}
function cellClick(i){
 if(!game||game.phase!=='playing'||game.mode==='ai'&&game.team!==0)return;
 const piece=at(i);
 if(game.comboRemaining){
  if(piece?.id===game.selected){nextTurn(true,game.pendingExtra);return}
  const option=targets().find(o=>o.at===i);if(option)act(i,option.kind);return;
 }
 if(piece&&piece.team===game.team&&!(game.armed&&game.characters[game.team]==='yi'&&targets().some(o=>o.at===i&&o.kind==='swap'))){game.selected=game.selected===piece.id?null:piece.id;game.armed=false;game.notice='빛나는 이동·공격 칸을 누르세요.';render();playSound('select');return}
 const option=targets().find(o=>o.at===i);if(option)act(i,option.kind);
}
function skill(){
 if(!game||game.phase!=='playing'||game.selected===null||skillSpent(game.team)||game.comboRemaining||game.mode==='ai'&&game.team!==0)return;
 const piece=game.pieces.find(p=>p.id===game.selected),character=game.characters[game.team];
 const canUse=character==='gimyo'?(piece.role==='special'||piece.role==='basic'):character==='keuda'?piece.role==='basic'&&legalOptions(piece).some(o=>o.kind==='attack'):character==='yi'?active(game.team).some(p=>p.role==='basic'&&p.id!==piece.id):character==='ho'?piece.role==='special'&&active(game.team).some(p=>p.role==='queen'):false;
 if(!canUse)return;
 game.armed=!game.armed;
 game.notice=game.armed?({gimyo:'기묘: 폰·나이트 2배 이동과 적 뛰어넘기',keuda:'크다: 폰으로 인접 적 연속 공격',yi:'이 대리: 교체할 내 폰을 고르세요',ho:'호 사원: 퀸을 제물로 나이트가 왕을 공격'})[character]:'능력을 취소했습니다.';
 render();if(game.armed){cue('✦ 특수능력 준비');playSound('skill')}
}
function aiScore(piece,option,power){
 const team=piece.team,target=at(option.at),role=target?roleOf(target):null;
 const crown=crownCell(),[cx,cy]=xy(crown),[px,py]=xy(piece.at),[tx,ty]=xy(option.at);
 const before=Math.max(Math.abs(px-cx),Math.abs(py-cy)),after=Math.max(Math.abs(tx-cx),Math.abs(ty-cy));
 let score=0;
 if(option.kind==='attack')score+=role==='king'?1200:role==='queen'?85:role==='special'?32:12;
 if(option.kind==='demote')score+=role==='king'?330:35;
 if(option.kind==='swap')score+=piece.role==='special'||piece.role==='queen'?(before-after)*10:0;
 if(game.crownOwner!==team){
  score+=(piece.role==='basic'||game.characters[team]==='ho'&&piece.role==='special'?25:6)*(before-after);
  if(piece.role==='basic')score+=Math.max(0,8-after)*2;
 }else if(piece.id===game.crownHolder)score+=after*3;
 else score+=Math.max(0,4-after)*3;
 if(power&&game.characters[team]==='ho'&&role==='king')score-=100;
 if(power&&game.characters[team]==='gimyo')score-=10;
 if(game.aiRecent.includes(piece.id))score-=5;
 if(option.kind==='move'||option.kind==='attack'){
  const board=game.pieces.filter(p=>p!==piece&&p!==target).concat({...piece,at:option.at});
  const holder=role==='king'&&option.kind==='attack'?piece.id:game.crownHolder;
  const ownHolder=board.find(p=>p.id===holder&&p.team===team);
  if(ownHolder){
   const danger=board.some(p=>p.team>=0&&p.team!==team&&moveOptions(p,false,board,holder).some(o=>o.at===ownHolder.at&&(o.kind==='attack'||o.kind==='demote')));
   score+=danger?-430:65;
  }
  const moved=board[board.length-1];
  const threatened=board.some(p=>p.team>=0&&p.team!==team&&moveOptions(p,false,board,holder).some(o=>o.at===moved.at&&(o.kind==='attack'||o.kind==='demote')));
  if(threatened)score-=piece.role==='queen'?55:piece.role==='special'?23:8;
 }
 return score+Math.random()*1.2;
}
function queueAI(){
 if(aiId)clearTimeout(aiId);
 if(!game||game.phase!=='playing'||game.team===0||game.mode!=='ai')return;
 aiId=setTimeout(()=>{
  if(!game||game.phase!=='playing'||game.team===0)return;
  const team=game.team,options=[];
  const pieces=game.comboRemaining?[game.pieces.find(p=>p.id===game.selected)]:active(team);
  for(const piece of pieces){if(!piece)continue;
   const normal=legalOptions(piece).filter(o=>!game.comboRemaining||o.kind==='attack');
   for(const option of normal){
    const keuda=game.characters[team]==='keuda'&&!game.abilityUsed[team]&&piece.role==='basic'&&option.kind==='attack'&&game.pieces.some(p=>p.team!==team&&p.team>=0&&p.at!==option.at&&Math.max(Math.abs(xy(p.at)[0]-xy(option.at)[0]),Math.abs(xy(p.at)[1]-xy(option.at)[1]))===1);
    options.push({piece,option,power:keuda,score:aiScore(piece,option,keuda)});
   }
   if(!game.comboRemaining&&!skillSpent(team)&&['gimyo','ho'].includes(game.characters[team]))
    for(const option of legalOptions(piece,true).filter(o=>!normal.some(n=>n.at===o.at&&n.kind===o.kind)))
     options.push({piece,option,power:true,score:aiScore(piece,option,true)});
   if(!game.comboRemaining&&!game.abilityUsed[team]&&game.characters[team]==='yi')
    for(const pawn of active(team))if(pawn.role==='basic'&&pawn.id!==piece.id){
     const option={at:pawn.at,kind:'swap'};options.push({piece,option,power:true,score:aiScore(piece,option,true)-4});
    }
  }
  if(!options.length){nextTurn(false);return}
  options.sort((a,b)=>b.score-a.score);const pick=options[0];
  game.aiRecent.push(pick.piece.id);if(game.aiRecent.length>4)game.aiRecent.shift();
  game.selected=pick.piece.id;game.armed=pick.power;act(pick.option.at,pick.option.kind);
 },650);
}
function render(){
 if(!game)return;
 const board=$('board');board.replaceChildren();const options=new Map(targets().map(o=>[o.at,o.kind]));
 const visibleTeam=game.mode==='ai'?0:game.team;
 for(let i=0;i<COL*ROWS;i++){
  const el=document.createElement('button'),[x,y]=xy(i),piece=at(i);
  el.type='button';el.className='cell '+((x+y)%2?'dark':'light');
  if(options.has(i))el.classList.add(options.get(i)==='attack'||options.get(i)==='demote'?'attack':options.get(i)==='swap'?'swap-hint':'hint');
  if(game.lastMove?.from===i)el.classList.add('last-from');if(game.lastMove?.to===i)el.classList.add('last-to');
  if(piece){
   el.classList.add(piece.team===visibleTeam?'owner':'enemy','team-'+piece.team);
   if(piece.role==='king')el.classList.add('neutral-king');if(piece.id===game.crownHolder)el.classList.add('crown-holder');
   if(piece.role==='special')el.classList.add('piece-special');if(piece.role==='queen')el.classList.add('piece-queen');
   if(piece.role==='king'){const emblem=document.createElement('span');emblem.className='crown-emblem';emblem.textContent='♛';el.append(emblem)}else{const img=document.createElement('img');img.src=ART[game.characters[piece.team]];img.alt=CHAR[game.characters[piece.team]];el.append(img);}
   if(piece.team>=0){const band=document.createElement('span');band.className='piece-band';el.append(band);const tag=document.createElement('span');tag.className='team-mark';tag.textContent='P'+(piece.team+1);el.append(tag);}if(game.selected===piece.id)el.classList.add('selected');
  }
  const role=piece?(piece.role==='king'?'중앙 왕 · 폰으로만 차지 가능':`${piece.team+1}P `+({queen:'퀸',special:'나이트',basic:'폰'})[piece.role]+(piece.id===game.crownHolder?' · 왕 보유':'')):'';
  el.disabled=game.phase!=='playing';el.setAttribute('aria-label',`${y+1}행 ${x+1}열 ${piece?(piece.team<0?'':CHAR[game.characters[piece.team]]+' ')+role:''} ${options.get(i)||''}`);
  el.onclick=()=>cellClick(i);board.append(el);
 }
 $('turnLabel').textContent=`턴 ${game.turn} · ${CHAR[game.characters[game.team]]} (${game.team+1}P)`;
 $('timer').textContent=game.remaining.toFixed(1)+'초';$('timer').classList.toggle('urgent',game.remaining<=3);
 $('timeBar').style.width=Math.max(0,game.remaining*10)+'%';$('timeBar').parentElement.classList.toggle('danger',game.remaining<=3);
 $('battleStatus').textContent='● '+(game.phase==='finished'?'게임 종료':(game.team+1)+'P '+CHAR[game.characters[game.team]]+' 차례'+(game.crownOwner===game.team?' · 왕 보유':''));
 $('battleStatus').className='battle-status'+(game.team!==0?' enemy':'')+(game.remaining<=3?' alert':'');$('battleTurn').textContent=game.rounds+'/30바퀴';$('turnsLeft').textContent=game.turn>=10?(game.rounds>=game.roundLimit?'연장전 · 왕 먼저 차지':`${game.roundLimit-game.rounds}바퀴 남음`):'';
 $('piecesLeft').textContent=`왕 ${game.crownOwner===null?'중앙':(game.crownOwner+1)+'P'} · 말 ${[0,1,2,3].map(team=>active(team).length).join(' : ')}`;
 $('selectedLabel').textContent=game.selected===null?'말을 선택하세요.':`선택: ${CHAR[game.characters[game.team]]} · ${({king:'왕',queen:'퀸',special:'나이트',basic:'폰'})[game.pieces.find(p=>p.id===game.selected)?.role]||'말'}`;
 const currentChar=game.characters[game.team];$('spotArt').src=ART[currentChar];$('spotName').textContent=CHAR[currentChar];
 $('spotSkill').textContent=skillLeft(game.team)?({gimyo:'폰·나이트 2배 이동 · 적 뛰어넘기',keuda:'폰 연속 공격',yi:'내 폰과 자리 교체',ho:'퀸을 제물로 나이트가 왕 공격'})[currentChar]:'능력 모두 사용';const selectedPiece=game.pieces.find(p=>p.id===game.selected);$('abilityBtn').disabled=game.phase!=='playing'||skillSpent(game.team)||!selectedPiece||game.comboRemaining>0||game.mode==='ai'&&game.team!==0||currentChar==='gimyo'&&selectedPiece.role!=='special'&&selectedPiece.role!=='basic'||currentChar==='keuda'&&(selectedPiece.role!=='basic'||!legalOptions(selectedPiece).some(o=>o.kind==='attack'))||currentChar==='yi'&&!active(game.team).some(p=>p.role==='basic'&&p.id!==selectedPiece.id)||currentChar==='ho'&&(selectedPiece.role!=='special'||!active(game.team).some(p=>p.role==='queen'));$('abilityBtn').textContent=game.armed?'✕ 능력 취소':`✦ 능력 사용 · ${skillLeft(game.team)}회 남음`;$('abilityBtn').classList.toggle('armed',game.armed);$('skillHint').textContent=skillSpent(game.team)?'능력 사용 완료':game.armed?'빛나는 칸을 누르세요.':selectedPiece?'능력 버튼 → 빛나는 칸':'말을 선택하세요.';$('notice').textContent=game.notice;
 $('lastMoveText').textContent=game.lastMove?`${game.lastMove.team+1}P: ${Math.floor(game.lastMove.from/COL)+1}·${game.lastMove.from%COL+1} → ${Math.floor(game.lastMove.to/COL)+1}·${game.lastMove.to%COL+1}${game.lastMove.crownTaken?' · 왕 차지':game.lastMove.demoted?' · 강등':game.lastMove.swap?' · 자리 교체':game.lastMove.captured?' · 공격':''}${game.lastMove.buff?' · '+(game.lastMove.buff==='extra'?'한 턴 더':'폰 추가'):''}`:'아직 이동 없음';
 $('result').textContent=game.phase==='finished'?(game.winner===null?'무승부':`플레이어 ${game.winner+1} 승리`)+` — ${game.reason}`:'';
}
function announceOpening(){
 game.notice=`${game.team+1}P 선공 · 중앙 왕을 차지하세요.`;
 render();cue(`${game.team+1}P 선공!`,1300);
 if(game.mode==='local'&&game.team!==0){
  game.handoff=true;$('handoffHeading').textContent=`플레이어 ${game.team+1} 선공`;
  $('handoff').classList.remove('hidden');$('handoffBtn').focus();
 }
}
function stop(){if(timerId)clearInterval(timerId);if(aiId)clearTimeout(aiId);timerId=aiId=null;}function begin(){stop();let last=performance.now();timerId=setInterval(()=>{if(!game||game.phase!=='playing')return;let now=performance.now(),dt=Math.min(0.3,(now-last)/1000);last=now;if(game.handoff||now<game.graceUntil)return;game.remaining=Math.max(0,game.remaining-dt);if(game.remaining<=0)nextTurn(false);else{$('timer').textContent=game.remaining.toFixed(1)+'초';$('timeBar').style.width=Math.max(0,game.remaining*10)+'%';$('timer').classList.toggle('urgent',game.remaining<=3);$('timeBar').parentElement.classList.toggle('danger',game.remaining<=3)}},100);queueAI();}
$('storyBtn').onclick=()=>show('intro');$('chooseBtn').onclick=()=>show('choose');$('introBack').onclick=()=>show('cover');$('pickBack').onclick=()=>show('intro');document.querySelectorAll('[data-choice]').forEach(b=>b.onclick=()=>{chosen=b.dataset.choice;document.querySelectorAll('[data-choice]').forEach(a=>a.classList.toggle('selected',a===b))});$('playBtn').onclick=()=>{try{clearEnd();$('effectLayer').replaceChildren();game=newGame(chosen,$('opponent').value);$('launchError').textContent='';$('modeBadge').textContent=game.mode==='ai'?'AI 3명과 대전':'로컬 4인';show('play');render();begin();announceOpening();setEvent('폰으로 왕을 차지해 지키세요.');cue('⚔️ 대전 시작!');playSound('turn')}catch(e){$('launchError').textContent='게임 시작 오류: '+String(e)}};$('abilityBtn').onclick=skill;$('soundBtn').onclick=()=>{soundEnabled=!soundEnabled;$('soundBtn').textContent=soundEnabled?'🔊 효과음 켜짐':'🔇 효과음 꺼짐';$('soundBtn').setAttribute('aria-pressed',String(soundEnabled));if(soundEnabled)playSound('select')};$('endAgain').onclick=()=>{stop();clearEnd();game=newGame(chosen,$('opponent').value);render();begin();announceOpening();setEvent('재대전! 폰으로 중앙 왕을 차지하세요.');cue('⚔️ 재대전!')};$('endChange').onclick=()=>{stop();clearEnd();show('choose')};$('restartBtn').onclick=()=>{stop();clearEnd();show('choose')};$('quitBtn').onclick=()=>{stop();clearEnd();show('cover')};$('handoffBtn').onclick=()=>{if(!game)return;game.handoff=false;game.remaining=10;$('handoff').classList.add('hidden');render();};$('handoffExit').onclick=()=>{stop();clearEnd();show('cover')};
