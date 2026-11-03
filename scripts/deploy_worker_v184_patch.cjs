#!/usr/bin/env node
"use strict";
/**
 * Deploy the audited v184 feature patch without rebuilding the stale GitHub
 * Python v1.0.0 source. Fetch v184 by immutable Cloudflare version ID.
 *
 * node scripts/deploy_worker_v184_patch.cjs           # verify only
 * node scripts/deploy_worker_v184_patch.cjs --deploy  # upload + 100% deployment
 *
 * Needs: CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_API_TOKEN (Workers Scripts Write).
 */
const assert = require("node:assert/strict");
const { spawnSync } = require("node:child_process");
const { patchWorkerBundle } = require("./patch_worker_v184.cjs");

const VERSION = "ec53a477-dcef-4b75-8142-8066aabf1fe6";
const WORKER = "potbreaker";
const ACCOUNT = process.env.CLOUDFLARE_ACCOUNT_ID;
const TOKEN = process.env.CLOUDFLARE_API_TOKEN;
const TICK = String.fromCharCode(96);

async function cf(path, options = {}) {
  assert(ACCOUNT && TOKEN, "Set CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN");
  const r = await fetch("https://api.cloudflare.com/client/v4/accounts/" + ACCOUNT + path, {
    ...options,
    headers: { Authorization: "Bearer " + TOKEN, ...options.headers },
  });
  const body = await r.json();
  if (!r.ok || !body.success) {
    throw Error("Cloudflare " + r.status + ": " + JSON.stringify(body.errors || body));
  }
  return body.result;
}
function fromTemplate(bundle, key, nextKey) {
  const marker = "var " + key + " = " + TICK;
  const start = bundle.indexOf(marker) + marker.length;
  assert(start >= marker.length, "Missing " + key);
  const end = bundle.indexOf(TICK + ";\nvar " + nextKey + " = ", start);
  assert(end >= 0, "Unclosed " + key);
  return bundle.slice(start, end);
}
function fromModule(bundle, path) {
  const key = JSON.stringify(path) + ": ";
  const index = bundle.indexOf(key);
  assert(index >= 0, "Missing browser module " + path);
  const start = index + key.length;
  let end = -1;
  for (let i = start + 1; i < bundle.length; i++) {
    if (bundle[i] === "\\") i++;
    else if (bundle[i] === '"') { end = i; break; }
  }
  assert(end > start, "Unclosed browser module " + path);
  const encoded = bundle.slice(start, end + 1)
    .replace(/\\x([0-9A-Fa-f]{2})/g, (_, x) => "\\u00" + x)
    .replace(/\\u\{([0-9a-fA-F]+)\}/g, (_, x) => String.fromCodePoint(parseInt(x, 16)));
  return JSON.parse(encoded);
}
function validate(bundle, applied) {
  assert.equal(applied.length, 25, "All 25 scoped fixes must apply");
  const python = fromTemplate(bundle, "GAME", "BROWSER_MODULES");
  const page = fromTemplate(bundle, "PAGE", "GAME");
  const input = fromModule(bundle, "/modules/potbreaker/input.js");
  const main = fromModule(bundle, "/modules/potbreaker/main.js");
  const renderer = fromModule(bundle, "/modules/potbreaker/renderer.js");
  assert(page.includes('id="home"') && page.includes('id="registerScore"'), "Buttons must exist");
  assert(page.includes("#end .end-panel{z-index:20!important"), "Result action CSS must be visible");
  assert(main.includes("if(win)$('registerScore').classList.remove('hidden');if(activeRunId)"), "Victory action must not wait for API");
  assert(main.includes("chargingNow"), "Charging input must reach Python engine");
  assert(input.includes("fireReleasePending"), "Quick taps must be preserved");
  assert(input.includes("this.onDashUp") && input.includes("this.dashButton.addEventListener(type, this.onDashUp)"), "Dash release must not trigger fire release");
  assert(renderer.includes("drawChargeSparks(s)"), "Spark effect hook missing");
  assert(renderer.includes("i * Math.PI * 2 / n"), "Need one visual per charged pot");
  assert(renderer.includes("(p.boss||p.charged)?.92:.52"), "Charged pot must match boss projectile size");
  const pythonQA = [
    "import ast, json, sys",
    "src=sys.stdin.read(); ast.parse(src)",
    "namespace={'__name__':'potbreaker_qa'}",
    "exec(compile(src,'v184-game.py','exec'),namespace)",
    "PotBreaker=namespace['PotBreaker']",
    "for difficulty in ('normal','hard','very_hard'):",
    "    g=PotBreaker(seed=7,difficulty=difficulty)",
    "    assert g.player_pot_cap==3, (difficulty,g.player_pot_cap)",
    "    g.player=[2,2]; g.boss=[14,2]; g.walls=set(); g.moving_walls=set()",
    "    g.boss_move_cd=999; g.partition_timer=999; g.crow_spawn_timer=999",
    "    g.ammo=3; boss_before=g.boss_hp",
    "    g.step(.04,charging=True)",
    "    assert json.loads(g.state())['charge_count']==3",
    "    g.step(.04,charging=False)",
    "    charged=[p for p in g.projectiles if p.get('charged')]",
    "    assert len(charged)==1 and charged[0]['power']==3, charged",
    "    assert g.ammo==0 and g.boss_hp==boss_before, 'Do not insta-hit boss'",
    "    g.reset(); g.player=[2,2]; g.boss=[14,2]",
    "    g.walls={(4,2),(5,2),(6,2)}; g.moving_walls=set()",
    "    g.boss_move_cd=999; g.partition_timer=999; g.crow_spawn_timer=999",
    "    g.ammo=3; g.step(.04,charging=True); g.step(.04,charging=False)",
    "    for _ in range(45):",
    "        if g.phase!='playing': break",
    "        g.step(.04)",
    "    assert not any(p.get('charged') for p in g.projectiles), 'Third wall must block shot'",
    "    assert g.boss_hp==g.boss_hp_cap, 'Obstacles must prevent direct boss damage'",
    "print('PASS: three difficulty caps; charging; 3-pot projectile; no instant-hit; two-wall limit')",
  ].join("\n");
  const check = spawnSync("python3", ["-c", pythonQA], { input: python, encoding: "utf8", maxBuffer: 1024 * 1024 });
  if (check.status !== 0) throw Error("Python engine QA failed:\n" + check.stderr + check.stdout);
  for (const [path, js] of [["input", input], ["main", main], ["renderer", renderer]]) {
    const parse = spawnSync(process.execPath, ["--input-type=module", "--check"], { input: js, encoding: "utf8" });
    if (parse.status !== 0) throw Error(path + " JS syntax check failed: " + parse.stderr);
  }
  return check.stdout.trim();
}
async function main() {
  const version = await cf("/workers/workers/" + WORKER + "/versions/" + VERSION + "?include=modules");
  assert.equal(version.id, VERSION);
  assert.equal(version.number, 184);
  assert.equal(version.modules.length, 1);
  const original = Buffer.from(version.modules[0].content_base64, "base64").toString("utf8");
  const { code, applied } = patchWorkerBundle(original);
  const qaResult = validate(code, applied);
  console.log(qaResult);
  console.log("Patch matches:", applied.length, "; original bytes:", Buffer.byteLength(original), "; new bytes:", Buffer.byteLength(code));
  if (!process.argv.includes("--deploy")) {
    console.log("Verified only; production not modified. Pass --deploy to upload.");
    return;
  }
  const boundary = "----potbreaker-v184-" + Date.now();
  const metadata = {
    main_module: "worker.js",
    compatibility_date: version.compatibility_date || "2026-10-27",
    bindings: [{ name: "POTBREAKER_DB", type: "d1", id: "bfc89eda-b76b-44f0-9653-bbda3b7c6806" }],
    annotations: { "workers/message": "v184 base: ranking/home actions, all 3-pot caps, charge 1-3 sparks" },
  };
  const multipart = Buffer.concat([
    Buffer.from("--" + boundary + "\r\nContent-Disposition: form-data; name=\"metadata\"\r\nContent-Type: application/json\r\n\r\n" + JSON.stringify(metadata) + "\r\n"),
    Buffer.from("--" + boundary + "\r\nContent-Disposition: form-data; name=\"worker.js\"; filename=\"worker.js\"\r\nContent-Type: application/javascript+module\r\n\r\n"),
    Buffer.from(code),
    Buffer.from("\r\n--" + boundary + "--\r\n"),
  ]);
  const uploaded = await cf("/workers/scripts/" + WORKER + "/versions", {
    method: "POST",
    headers: { "Content-Type": "multipart/form-data; boundary=" + boundary },
    body: multipart,
  });
  assert(uploaded.id, "Upload returned no version ID");
  console.log("Uploaded new Worker version:", uploaded.id);
  const deployment = await cf("/workers/scripts/" + WORKER + "/deployments", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ strategy: "percentage", versions: [{ version_id: uploaded.id, percentage: 100 }],
      annotations: { "workers/message": "Deploy tested v184 charge/ranking patch from GitHub branch" } }),
  });
  const live = await cf("/workers/scripts/" + WORKER + "/deployments?per_page=1");
  assert.equal(live.deployments[0].versions[0].version_id, uploaded.id, "Production mismatch");
  assert.equal(live.deployments[0].versions[0].percentage, 100);
  console.log("DEPLOYED 100%:", deployment.id, "version:", uploaded.id);
}
main().catch(e => { console.error(e); process.exitCode = 1; });
