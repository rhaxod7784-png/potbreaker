// Standalone Node 20 tests for Ginkgo Tree Breaker game rules.
const fs=require("node:fs"),vm=require("node:vm"),assert=require("node:assert/strict");
const ctx={crypto:require("node:crypto").webcrypto,Date,Uint32Array,Response,URL,Math,JSON,console};
vm.createContext(ctx);
vm.runInContext(fs.readFileSync("cloudflare/ginkgo-api.js","utf8")+";globalThis.G={ginkgoInit,ginkgoAdvance,ginkgoScoreTap,GINKGO_TOTAL,GINKGO_INTERVAL};",ctx);
const G=ctx.G;
assert.equal(G.GINKGO_TOTAL,91);
assert.equal(G.GINKGO_INTERVAL.normal,3000);
assert.equal(G.GINKGO_INTERVAL.hard,2000);
assert.equal(G.GINKGO_INTERVAL.very_hard,1000);
const s=G.ginkgoInit();
assert.equal(s.cells.length,91);
for(let tick=1;tick<=120;tick++){
 G.ginkgoAdvance(s,tick);
 assert.equal(s.tick,tick);
 for(const cell of s.cells){
  assert.ok(cell.phase>=0&&cell.phase<=3);
  if(cell.sex===0)assert.ok(cell.phase<2,"male tree cannot have fruit");
 }
}
s.cells[0]={phase:2,sex:1};s.combo=3;s.score=6;s.max_combo=3;
assert.equal(G.ginkgoScoreTap(s,0,1000),true);assert.equal(s.score,10);assert.equal(s.combo,4);
s.cells[1]={phase:2,sex:1};
G.ginkgoScoreTap(s,1,1000);
assert.equal(s.score,15,"simultaneous taps earn +4 and +5");
assert.equal(s.max_combo,5);
s.cells[2]={phase:0,sex:0};G.ginkgoScoreTap(s,2,1100);
assert.equal(s.combo,0);assert.equal(s.score,15);assert.equal(s.max_combo,5);
s.cells[3]={phase:3,sex:1};G.ginkgoScoreTap(s,3,1500);
assert.equal(s.lock_until,2000);
s.cells[4]={phase:2,sex:1};
assert.equal(G.ginkgoScoreTap(s,4,1750),false);
assert.equal(s.score,15);
assert.equal(G.ginkgoScoreTap(s,4,2000),true);
assert.equal(s.score,16);
console.log("Ginkgo: deterministic state/sex, +4/+5 combo, penalty, lock, high streak checks passed.");
