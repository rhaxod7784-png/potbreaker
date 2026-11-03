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
- Production release status must be checked separately against Cloudflare active Worker version and live `/health` endpoint.

## Repository
`feat/potbreaker-charge-burst-20261103` → v1.1.0 release.
