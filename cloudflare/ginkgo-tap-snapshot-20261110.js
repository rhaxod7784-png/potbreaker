/* POTBREAKER_GINKGO_TAP_SNAPSHOT_20261110
 * Add after the production v219 bundle, before the final export.
 * Keep the 60-second round, difficulty multipliers, combo, and 500ms rotten lock.
 * The browser captures the displayed phase/tick at pointerdown; D1 remains authoritative.
 */
(() => {
  const localPath = "/modules/ginkgo/local-engine.js";
  const mainPath = "/modules/ginkgo/main.js";
  const localOriginal = BROWSER_MODULES[localPath];
  const mainOriginal = BROWSER_MODULES[mainPath];
  const localNeedle = "const now = Date.now(); this.advance(now);";
  const tapNeedle = " if(!localEngine.tap(index)){renderLocalState();return;}";
  const payloadNeedle = "JSON.stringify({run_id:tappedRun,index})";
  const matchCount = (source, needle) => typeof source === "string" ? source.split(needle).length - 1 : 0;
  if (matchCount(localOriginal, localNeedle) === 1 &&
      matchCount(mainOriginal, tapNeedle) === 1 &&
      matchCount(mainOriginal, payloadNeedle) === 2) {
    BROWSER_MODULES[localPath] = localOriginal.replace(
      localNeedle, "const now = Date.now(); /* Judge the last rendered board, not a later tick. */");
    BROWSER_MODULES[mainPath] = mainOriginal.replace(
      tapNeedle,
      " const tapTick=localEngine.clock.tick,tapPhase=localEngine.board.cells[index]?.phase;\n" + tapNeedle
    ).replaceAll(
      payloadNeedle, "JSON.stringify({run_id:tappedRun,index,tap_tick:tapTick,tap_phase:tapPhase})"
    );
  } else {
    console.error("[ginkgo-tap-fix] unexpected bundled browser module shape; refusing partial patch");
  }

  const previousAPI = ginkgoAPI;
  ginkgoAPI = async function(request, env) {
    if (request.method !== "POST" || new URL(request.url).pathname !== "/api/ginkgo/tap" ||
        !env.POTBREAKER_DB) return previousAPI(request, env);
    let body;
    try { body = await request.clone().json(); } catch { return previousAPI(request, env); }
    const tapTick = body?.tap_tick, tapPhase = body?.tap_phase;
    // Old clients retain the preexisting API contract; never trust a client-provided score.
    if (!Number.isInteger(tapTick) || tapTick < 0 || tapTick > 120 ||
        !Number.isInteger(tapPhase) || tapPhase < 0 || tapPhase > 3) {
      return previousAPI(request, env);
    }
    if (Number(request.headers.get("content-length") || "0") > 16384) return ginkgoJSON({error:"payload_too_large"},413);
    const id = typeof body.run_id === "string" ? body.run_id : "";
    const index = body.index;
    if (!/^[a-f0-9-]{36}$/i.test(id) || !Number.isInteger(index) ||
        index < 0 || index >= GINKGO_TOTAL) return ginkgoJSON({error:"invalid_tap"},400);
    const now = Date.now(), db = env.POTBREAKER_DB;
    try {
      const run = await db.prepare("SELECT * FROM ginkgo_runs WHERE run_id=?").bind(id).first();
      if (!run) return ginkgoJSON({error:"run_not_found"},404);
      if (now >= run.deadline_ms || run.finished) return ginkgoJSON({error:"game_ended"},409);
      const snapshot = ginkgoSnapshot(run, now), state = snapshot.state;
      if (now < state.lock_until) return ginkgoJSON({
        error:"temporarily_locked",locked_until:state.lock_until,remaining_ms:snapshot.remaining_ms
      },409);
      // Only reconcile one tick of latency, and only for 850ms after that tick.
      // The phase must be a valid predecessor of the authoritative current phase.
      const currentPhase = state.cells[index].phase;
      const elapsedSinceTick = now - (run.started_ms + state.tick * GINKGO_INTERVAL[run.difficulty]);
      const nextPhaseMatches =
        (tapPhase === 0 && currentPhase === 1) ||
        (tapPhase === 1 && (currentPhase === 0 || currentPhase === 2)) ||
        (tapPhase === 2 && currentPhase === 3) ||
        (tapPhase === 3 && currentPhase === 0);
      const useDisplayedPhase = state.tick === tapTick + 1 &&
        elapsedSinceTick >= 0 && elapsedSinceTick <= 850 && nextPhaseMatches;
      if (useDisplayedPhase) state.cells[index].phase = tapPhase;
      ginkgoScoreTap(state, index, now, run.difficulty);
      // A missed tap must not revert the board's natural timer progression.
      if (useDisplayedPhase && tapPhase !== 2) state.cells[index].phase = currentPhase;
      const changed = await db.prepare(
        "UPDATE ginkgo_runs SET state_json=?,version=version+1 WHERE run_id=? AND version=? AND finished=0 AND deadline_ms>?"
      ).bind(JSON.stringify(state), id, run.version, now).run();
      if (!changed.meta?.changes) return ginkgoJSON({error:"state_conflict"},409);
      return ginkgoJSON({
        score:state.score,combo:state.combo,max_combo:state.max_combo,state,
        cells:state.cells.map(cell=>cell.phase),locked_until:state.lock_until,
        remaining_ms:snapshot.remaining_ms,version:run.version+1
      });
    } catch (error) {
      console.error("[ginkgo-tap-fix] tap error", error?.stack || String(error));
      return ginkgoJSON({error:"server_error"},500);
    }
  };

  // Override just the module cache policy: existing mobile browsers must fetch the corrected input handling.
  const previousFetch = worker_default.fetch;
  worker_default.fetch = async function(request, env, ctx) {
    const response = await previousFetch.call(worker_default, request, env, ctx);
    const path = new URL(request.url).pathname;
    if ((path !== localPath && path !== mainPath) || response.status !== 200) return response;
    const headers = new Headers(response.headers);
    headers.set("cache-control","no-store, max-age=0");
    return new Response(response.body,{status:response.status,statusText:response.statusText,headers});
  };
})();
