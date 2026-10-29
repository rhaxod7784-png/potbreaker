let touchDirection=[0,0],touchActive=false,dpadOrder=0;
const keyDirections={ArrowUp:'up',KeyW:'up',ArrowDown:'down',KeyS:'down',ArrowLeft:'left',KeyA:'left',ArrowRight:'right',KeyD:'right'};
const dpadDirections={up:[0,-1],down:[0,1],left:[-1,0],right:[1,0]};
const dpadPointers=new Map();
const dpad=document.getElementById('dpad');
for(const [direction,glyph] of [['up','▲'],['right','▶'],['down','▼'],['left','◀']]){const icon=document.createElement('span');icon.className='dpad-icon '+direction;icon.textContent=glyph;dpad.appendChild(icon)}
function refreshDpad(){
 let last=null;for(const p of dpadPointers.values())if(p.direction&&(!last||p.order>last.order))last=p;
 dpad.classList.remove('active-up','active-down','active-left','active-right');
 touchActive=!!last;touchDirection=last?dpadDirections[last.direction]:[0,0];
 if(last)dpad.classList.add('active-'+last.direction);
}
function directionAt(e){
 const rect=dpad.getBoundingClientRect(),dx=(e.clientX-(rect.left+rect.width/2))/(rect.width/2),dy=(e.clientY-(rect.top+rect.height/2))/(rect.height/2),radius=Math.hypot(dx,dy);
 if(radius>1.2||radius<.10)return null;
 const hit=document.elementFromPoint(e.clientX,e.clientY)?.closest?.('#dpad .dpad-button');
 if(hit?.dataset.direction)return hit.dataset.direction;
 return Math.abs(dx)>Math.abs(dy)?(dx<0?'left':'right'):(dy<0?'up':'down');
}
function setPointerDirection(e,p){
 const direction=directionAt(e);if(direction===p.direction)return;
 if(p.button)p.button.classList.remove('pressed');
 p.direction=direction;p.button=direction?dpad.querySelector('.dpad-button.'+direction):null;p.order=++dpadOrder;
 if(p.button)p.button.classList.add('pressed');refreshDpad();
}
function clearDpadPointer(id){
 const p=dpadPointers.get(id);if(!p)return;
 if(p.button)p.button.classList.remove('pressed');dpadPointers.delete(id);refreshDpad();
}
function moveDpadPointer(e){const p=dpadPointers.get(e.pointerId);if(p)setPointerDirection(e,p)}
dpad.addEventListener('pointerdown',e=>{
 if(!active||paused)return;e.preventDefault();
 const direction=directionAt(e);if(!direction)return;
 const prior=dpadPointers.get(e.pointerId);if(prior&&prior.button)prior.button.classList.remove('pressed');
 const p={button:null,direction:null,order:++dpadOrder};dpadPointers.set(e.pointerId,p);setPointerDirection(e,p);
 try{dpad.setPointerCapture(e.pointerId)}catch{}
});
window.addEventListener('pointermove',moveDpadPointer);
window.addEventListener('pointerup',e=>clearDpadPointer(e.pointerId));
window.addEventListener('pointercancel',e=>clearDpadPointer(e.pointerId));
function resetTouch(){for(const p of dpadPointers.values())if(p.button)p.button.classList.remove('pressed');dpadPointers.clear();touchActive=false;touchDirection=[0,0];dpad.classList.remove('active-up','active-down','active-left','active-right')}
