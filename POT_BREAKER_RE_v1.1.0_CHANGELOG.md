# POT BREAKER RE v1.1.0 — 2026-11-03

## Release type
MINOR — optional charge-burst mechanic on the modular PotBreaker engine.

## Added
- Hold Space to gather currently owned ordinary pots into a charged attack. Field pots collected while holding Space join the charge.
- Release Space to apply one HP of damage per collected pot to Keuda, clamped at zero HP.
- Normal: at most 3 charged pots; Hard: at most 4; Very Hard: at most 5.
- Independent `ChargeModule` composed with `FieldModule`, `CombatModule`, and `ActorModule`.
- In-game charged-pot counter and regression tests.

## Preserved
- Ginkgo Tree Breaker mode and shared `GameEngine`.
- Existing touch throw control and ordinary pot throw input (the Space keyboard control is reassigned to hold/release).
- Cloudflare D1 binding, cron, game ranking API, and existing other gameplay logic.

## Verification
- GitHub Actions: QA PotBreaker Charge Burst, Ginkgo Tree Breaker build and checks, Build Cloudflare Worker.
- Cloudflare v185 was deployed via API on 2026-11-03 16:13 KST at 100% traffic. Earlier Worker v184 remains recorded for rollback, but its source has not been fully compared with the deployed v185 code. Deployment does not prove previous features were preserved.
- 2026-11-03: merged PR #12 (commit `6db5a6c70999af2b2a517ec723018b4be6e29fe4`) to add preexisting-gameplay regression checks, but it also mistakenly reverted Ginkgo 3/2/1-second timing to an older 1/0.7/0.5-second specification. This was corrected by restoring the explicitly later 2026-10-31 commit `1b74c755c9` timing (Normal 3s, Hard 2s, Very Hard 1s) across game engine, server, UI, translations, and regression tests. This source correction is **not** included in the currently deployed v185 Worker.

## Repository
`feat/potbreaker-charge-burst-20261103` → v1.1.0 release.
