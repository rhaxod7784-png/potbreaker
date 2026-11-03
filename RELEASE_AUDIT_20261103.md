# POT BREAKER RE — 2026-11-03 previous-update preservation audit

## Scope and evidence

This document distinguishes the verified Git history, authored release requirements, automated tests, and the Cloudflare production state. A passing test is not proof that an unexamined production change survives.

### Version lineage
- `main` = `53663ff18e4d07743acc9cf8e51149f36a5c818c`, an older 2026-10-27 source revision, NOT the current production truth.
- `fix/potbreaker-i18n-layout-v1.0.97` = `a6da7be2829b5df19ba41f986353a504b5cc2bb7`.
- `feat/ginkgo-tree-breaker-v0-6-20261030` = `d4337e909ecd12a8748bb17235cb40ea5ea9edea` before adding charge, based on the preceding v1.0.97 branch. GitHub PR #9 remains separate and draft.
- `feat/potbreaker-charge-burst-20261103` = original charge commit `7736ef81fc77f7f03da3c24497c1d0f1415a0537`, 15 commits ahead of Ginkgo with no dropped parent commits.
- PR #12 merged correction `6db5a6c70999af2b2a517ec723018b4be6e29fe4` into the charge branch, maintaining the previous Ginkgo functionality while adding regression tests. PR #11 remains draft and should not be directly merged into the stale `main`.

### Previously specified functionality validated in source

| Area | Check |
| --- | --- |
| Core PotBreaker | 3 HP player, boss HP Normal 5 / Hard 7 / Very Hard 10, ordinary ammo caps Normal 3 / Hard 2 / Very Hard 2 |
| Movement | Player dash cooldown 3 seconds, boss dash cooldown 5 seconds |
| Projectiles | Boss projectiles stop at partitions; normal throws remain available |
| Pot floor items | 4 ordinary pickups plus 1 healing pickup (total 5); avoid runaway growth |
| Modular game modes | Field, Combat, Actor, Charge components preserved alongside Ginkgo game mode |
| Ginkgo Tree Breaker | Original planned progression intervals **Normal 1.0 s / Hard 0.7 s / Very Hard 0.5 s** |
| Ginkgo gameplay | Round duration 60 s, lock penalty 0.5 s, independent scoreboard/ranking pathway |
| New charge burst | Holding Space gathers existing ordinary ammo and pickups; releasing does one boss HP of damage per pot, charge caps **3/4/5** by Normal/Hard/Very Hard |

The Ginkgo UI/server/Python had drifted to 3/2/1 seconds. PR #12 restored the documented 1.0/0.7/0.5 s across `web/ginkgo_modules.py`, `cloudflare/ginkgo-api.js`, `web/ginkgo.html`, and localized SEO/description text in `scripts/build_worker.py`. Python and Node tests were updated.

### Automated verification

After PR #12, GitHub Actions for `feat/potbreaker-charge-burst-20261103` passed:
- QA PotBreaker Charge Burst (push and PR)
- Ginkgo Tree Breaker build and checks (PR)
- Build Cloudflare Worker (push)

Regression test sources: `tests/test_charge_burst.py`, `tests/test_game_engine.py`, `tests/test_ginkgo_rules.cjs`, `tests/test_potbreaker_engine_modules.py`, and `tests/test_preserved_previous_updates.py`.

### Production deployment: NOT equivalent to this newer source

Cloudflare `potbreaker` active production deployment since **2026-11-03 16:13 KST** is Worker **v185**, version ID `92618ece-0320-44f2-a5e3-ad7b7faef76f`, API deploy receiving 100% traffic. Previous **v184**, version ID `ec53a477-dcef-4b75-8142-8066aabf1fe6`, was Wrangler-deployed **2026-11-02 22:53 KST** and is recorded as a backup.

The source changes in PR #12 occurred AFTER v185 was deployed, so restored Ginkgo intervals and compatibility tests are **not yet shipped in the active Worker**. Neither old v184 Worker source nor a full source-level comparison of v184 versus v185 has been obtained from the accessible Cloudflare APIs. Therefore **it is not established** whether other changes introduced solely in v184 were overwritten.

**Hold further production re-deployment.** Retrieve or reconstruct v184's exact deployed source, compare its engine, frontend, modes, D1/ranking, localization, and SEO/AdSense routes with this combined branch, reconcile any changes, repeat automated and real-browser/mobile QA, then deploy a single verified artifact. Do not overwrite the old `main` or replace production using a stale branch. Preserve the v184 and v185 version IDs for rollback.

This report records code comparison and fixes; it does not claim full restoration or post-fix production deployment.
