# POT BREAKER RE v1.0.5

Latest tested build. web/v105/release-template.html contains __ASSET_MAP__ as placeholder filled at deployment from the previous embedded CBZP sprite map. Python engine is game.py.

- Gimyo HP 3, Keuda HP 5
- All Keuda hits and collision damage 1 HP, with brief invulnerability
- Crow bombs inflict damage only; never turn into collectible pots
- Moving partitions move up to 5 per tick and have visual sliding interpolation
- Sweep speed is 2/3 of v1.0.4
- “쨍그랑!” and shards on damage
- Removed interactive and decorative game-board monitors
- Local Python unit tests 7/7 pass; browser/device testing pending
