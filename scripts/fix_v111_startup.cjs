"use strict";

/**
 * Strictly scoped release patch for already-deployed POT BREAKER Worker v188.
 * Fix a JS SyntaxError in the Pot Breaker browser module and stamp v1.1.1.
 * Source of truth: Cloudflare Worker version 188; never rebuild from stale main.
 */
function fixV111Startup(source) {
  const applied=[];
  function replace(expected,replacement,label,requiredCount=1) {
    const count=source.split(expected).length-1;
    if(count!==requiredCount)throw Error(label+": expected "+requiredCount+" matches but found "+count);
    source=source.replaceAll(expected,replacement);
    applied.push(label);
  }

  // This is a SyntaxError: a second 'const' is illegal after a comma in
  // the same declaration. The full module fails to parse, so Start cannot run.
  replace(
    "const [mx,my]=controls.getMove(dirs),const {fire:fireNow,charging:chargingNow,dash:dashNow}=controls.consumeActions();",
    "const [mx,my]=controls.getMove(dirs); const {fire:fireNow,charging:chargingNow,dash:dashNow}=controls.consumeActions();",
    "fix duplicate const in game loop"
  );
  replace("POT BREAKER RE v1.0.92","POT BREAKER RE v1.1.1","set game title and on-screen version",2);
  replace('version: "1.0.92", visual:', 'version: "1.1.1", visual:',"set health version");

  // The former production bundle ran a 2,500-tick standalone stress test
  // unconditionally in Pyodide (__name__='__main__'), delaying game startup.
  // Keep that test in repository CI, not in the browser-served Python module.
  const startMarker = "var GAME = `";
  const endMarker = "`;
var BROWSER_MODULES = ";
  const begin=source.indexOf(startMarker),from=begin+startMarker.length;
  const end=source.indexOf(endMarker,from);
  if(begin<0||end<0)throw Error("v188 Python bundle marker missing");
  const python=source.slice(from,end);
  const guard="if __name__ == '__main__':
    g = PotBreaker(42)";
  const guardIndex=python.lastIndexOf(guard);
  if(guardIndex<0 || python.slice(guardIndex).indexOf("print('OK: 2500 deterministic engine ticks')")<0) {
    throw Error("Unexpected Python standalone test; no modification");
  }
  if(python.slice(guardIndex+guard.length).includes("class "))throw Error("Unexpected code after standalone test");
  const cleaned=python.slice(0,guardIndex).trimEnd()+"
";
  source=source.slice(0,from)+cleaned+source.slice(end);
  applied.push("exclude standalone Python stress test from Pyodide startup");
  if(source.includes("),const {fire:fireNow"))throw Error("Startup SyntaxError still present");
  if(!source.includes("def _advance_charge_projectiles")||!source.includes("drawChargeSparks(s)"))throw Error("Charge or spark regression");
  if(!source.includes("if(win)$('registerScore').classList.remove('hidden')"))throw Error("Ranking button regression");
  return {code:source,applied};
}

module.exports={fixV111Startup};
