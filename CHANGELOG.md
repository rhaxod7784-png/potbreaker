# POT BREAKER CHANGELOG

POT BREAKER의 정규 버전 기록입니다.

기존 작업 파일명 `v0.1 ~ v0.21`은 당시 작업 순서를 나타내는 역사적 파일명이며, 아래 CHANGELOG는 실제 변경 규모에 맞춰 정규화한 `vMAJOR.MINOR.PATCH`를 사용합니다.

---

## v0.16.1 — 백그라운드 오디오 수정·Cloudflare 웹 배포

**Release type:** PATCH  
**Date:** 2026-10-11

### Changed
- Android와 웹이 동일한 HTML을 사용하는 Cloudflare Workers 정적 배포 설정 추가.
- Wrangler 버전 고정, npm 실행·배포 명령 및 배포 설정 문서 추가.
- 앱·HTML·npm 버전 0.16.1, Android versionCode 1601로 갱신.

### Fixed
- 홈 이동·앱 전환·화면 잠금·웹 페이지 이탈 시 BGM 타이머와 WebAudio 컨텍스트 종료.
- Android 네이티브 백그라운드 상태를 확인해 지연된 효과음·BGM 콜백의 오디오 재시작 차단.
- 복귀 시 단일 BGM 타이머로 재개하고 사용자 입력으로 오디오 활성화 재시도.
- 백그라운드 게임 업데이트 중단 및 복귀 시 프레임 시간 초기화.
- APK 빌드 SDK 설정에서 조회되지 않는 기본 `tools` 패키지를 제외하고 `platform-tools`만 설치하도록 수정.

### Code
- MainActivity 수명주기·AndroidBridge
- 게임 HTML 오디오 수명주기
- wrangler.jsonc, package.json, package-lock.json
- tests/audio-lifecycle.test.cjs

### Reason
- 휴대폰에서 게임을 벗어난 뒤에도 음악이 계속 나오는 문제를 수정하고 웹 배포 경로를 추가.

### Compatibility
- 게임 규칙과 localStorage 키 유지.
- Android와 웹의 승리 기록은 서로 다른 저장소를 사용.

---

## v0.16.0 — Android 설치 패키징

**Release type:** MINOR  
**Date:** 2026-10-11

### Changed
- 기존 브라우저 게임을 Android WebView 앱으로 패키징.
- 게임 HTML을 APK 내부 오프라인 asset으로 포함.
- Android Activity를 가로모드·몰입형 전체화면으로 구성.
- Android 네이티브 진동 브리지 추가.
- 앱 표시 버전을 `v0.16.0`으로 통일.
- GitHub Actions Android APK 빌드 workflow 추가.

### Fixed
- 브라우저 주소창과 브라우저별 화면 회전 동작에 의존하던 실행 환경을 Android Activity로 분리.
- `navigator.vibrate()`가 제한되는 WebView 환경에서 네이티브 진동 fallback 제공.

### Code
- `app/src/main/java/com/potbreaker/game/MainActivity.java`
- `app/src/main/AndroidManifest.xml`
- `app/src/main/assets/index.html`
- `app/build.gradle`
- `.github/workflows/android-build.yml`
- 패키징 HTML의 Android 진동 호환 코드

### Reason
- 브라우저 탭을 열지 않고 Android 기기에 직접 설치하여 POT BREAKER를 실행할 수 있도록 배포 경로를 추가하기 위해 변경.

### Compatibility
- 핵심 게임 규칙은 `v0.15.0`에서 그대로 이어짐.
- 브라우저와 Android WebView의 localStorage는 서로 분리됨.
- 브라우저 WIN 기록은 Android 앱으로 자동 이전되지 않음.

---

## v0.15.0 — 누적 승리 기록

**Release type:** MINOR  
**Date:** 2026-08-13

### Changed
- YOU/BOT 상태창에 누적 WIN 기록 추가.
- 승리 기록을 localStorage에 저장.
- WILD POT 출현 빈도를 약 1.5배 증가.

### Fixed
- 반복 플레이 결과가 매 경기 종료 후 사라지는 문제 보완.
- WILD POT의 존재감이 낮던 밸런스 조정.

### Code
- `winRecord`
- `saveWinRecord()`
- `recordWin()`
- `WILD_POT_FREQUENCY`
- `nextWildPotDelay()`

### Reason
- 반복 플레이의 결과를 계속 확인할 수 있게 하고 중립 오브젝트 개입 빈도를 높이기 위해 변경.

### Compatibility
- 기존 게임 규칙 유지.
- 새 localStorage 키만 추가.

---

## v0.14.0 — BOOST 공격·BOT BOOST·WILD POT

**Release type:** MINOR  
**Date:** 2026-08-13

### Changed
- BOOST 상태로 상대 몸통 충돌 시 1 HIT.
- BOT BOOST 3회 및 랜덤 사용 추가.
- 중립 WILD POT 시스템 추가.
- YOU/BOT/중립 화분 색상 분리.
- WILD POT이 YOU를 맞히면 BOT +1, BOT을 맞히면 YOU +1.

### Fixed
- 결과 배너 터치 닫기 이벤트를 pointer/touch/click으로 보강.
- 양측 화분 소유자 식별 문제 개선.

### Code
- `awardHit()`
- `activateBoost()`
- `botUseBoost()`
- `neutralPots`
- `spawnNeutralPot()`
- `updateNeutralPots()`
- `drawNeutralPots()`
- `drawPot(..., owner)`

### Reason
- BOOST를 공격 수단으로 확장하고 경기 중 제3의 랜덤 변수를 추가하기 위해 변경.

### Compatibility
- 신규 득점 규칙과 중립 오브젝트가 추가된 MINOR.
- 이전 버전과 경기 결과가 동일하게 재현되지는 않음.

---

## v0.13.3 — BGM 고속화·결과 배너 QA

**Release type:** PATCH  
**Date:** 2026-08-13

### Changed
- BGM 음역 상승.
- BGM interval `112ms → 82ms`.
- 빠른 장식음 추가.
- 결과 배너 터치·Enter·Esc 닫기 기능 추가.

### Fixed
- 다음 게임 시작 시 결과 배너가 화면을 가리는 문제 수정 시도.

### Code
- `startMischiefBgm()`
- `dismissWinnerOverlay()`
- winner overlay event handler

### Reason
- BGM 속도감과 경기 종료 후 재시작 UX 개선.

### Compatibility
- 게임 규칙 변경 없음.

---

## v0.13.2 — BGM 톤·템포 조정

**Release type:** PATCH  
**Date:** 2026-08-13

### Changed
- BGM을 높은 음역의 toy-arcade 느낌으로 변경.
- interval `155ms → 112ms`.
- 짧은 staccato와 click 장식음 추가.

### Fixed
- 기존 BGM이 보스전처럼 무겁게 들리는 문제 조정.

### Code
- `startMischiefBgm()` melody/harmony 배열
- BGM interval

### Reason
- 게임의 가볍고 정신없는 분위기에 BGM 톤을 맞추기 위해 변경.

### Compatibility
- 게임 규칙·저장 구조 변경 없음.

---

## v0.13.1 — 모바일 회전·대기 BGM

**Release type:** PATCH  
**Date:** 2026-08-13

### Changed
- 첫 터치에서 fullscreen + landscape lock 시도.
- START 전 대기화면부터 BGM 재생.
- 결과 화면에서도 BGM 유지.

### Fixed
- 모바일에서 게임 화면만 CSS로 90도 돌아가 잘리는 문제 수정.

### Code
- portrait 강제 회전 CSS 제거
- `tryMobileLandscape()`
- `unlockMobileExperience()`

### Reason
- 실제 스마트폰 사용 테스트에서 확인된 화면 회전 오류를 해결하기 위해 변경.

### Compatibility
- v0.13.0 게임 구조 유지.

---

## v0.13.0 — 출시 전 폴리시 시스템

**Release type:** MINOR  
**Date:** 2026-08-13

### Changed
- WebAudio BGM 추가.
- 바운스 효과음 추가.
- 마지막 3초 카운트다운 강조.
- 중앙 승리 결과 배너.
- BOT 승리 문구 `졌쥬?ㅋ`.
- 화분-캐릭터 명중 진동.
- BOOST 강도·버튼 UI 개선.
- 화분 선택 쿨타임/잔류시간 표시.
- 좌우 HUD 확대.

### Fixed
- 남은 시간·승자·현재 상태가 작아 확인하기 어려운 문제 개선.

### Code
- `startMischiefBgm()`
- `playTone()`
- `playBoing()`
- winner overlay
- timer danger UI
- pot-info popup

### Reason
- 공개 가능한 수준으로 인게임 피드백과 UI 완성도를 높이기 위해 변경.

### Compatibility
- 기존 핵심 게임 규칙 유지.
- 오디오·결과 UI 시스템 추가.

---

## v0.12.2 — 명중 주체 가독성

**Release type:** PATCH  
**Date:** 2026-08-13

### Changed
- YOU/BOT 명중 주체 표시.
- 득점 HUD 순간 강조.

### Fixed
- 누가 맞혔는지 구분하기 어려운 사용 테스트 문제 해결.

### Code
- `showHitOwner()`
- `drawHitOwnerFlash()`
- score pulse state

### Reason
- 경기 중 점수 획득 주체를 즉시 인식할 수 있게 하기 위해 변경.

### Compatibility
- 게임 규칙 변경 없음.

---

## v0.12.1 — BOOST·쿨타임 밸런스

**Release type:** PATCH  
**Date:** 2026-08-11

### Changed
- BOOST를 랜덤 방향 고속 이동으로 조정.
- 쿨타임을 소 0.3 / 중 0.7 / 대 1.0 / 특대 1.5초로 조정.

### Fixed
- BOOST 체감이 약한 문제.
- 전투 템포가 느린 구간 조정.

### Code
- `useBoost()`
- `POT.cooldown`
- projectile `maxLife`

### Reason
- 기존 BOOST·화분 기능의 체감과 밸런스를 조정하기 위해 변경.

### Compatibility
- v0.12.0 기능 구조 유지.

---

## v0.12.0 — BOOST 시스템

**Release type:** MINOR  
**Date:** 2026-08-11

### Changed
- 플레이어 BOOST 3회 추가.
- BOOST 버튼 추가.
- 화분별 projectile speed 차등.
- 불필요한 life/reroll/manual emote UI 제거.

### Fixed
- 발사 이외에 순간적인 위치 변화를 만들 수단이 없던 문제 보완.

### Code
- `boostsLeft`
- `useBoost()`
- `PROJECTILE_SPEED`

### Reason
- 발사 타이밍 외에 회피·위치 변경용 능동 조작을 추가하기 위해 변경.

### Compatibility
- AUTO LOCK + FIRE 구조 유지.
- BOOST 입력 추가.

---

## v0.11.0 — 20초 제한전

**Release type:** MINOR  
**Date:** 2026-08-11

### Changed
- 10 HIT 선취제에서 20초 제한전으로 변경.
- HIT 동점 시 큰 화분 승리.
- 같은 화분이면 DRAW.
- 공중 상쇄 내구 규칙 수정.

### Fixed
- 고착 경기의 플레이 시간이 길어지는 문제.
- 큰 화분이 의도보다 한 발 빨리 깨지는 문제.

### Code
- `MATCH_DURATION`
- `finishTimedMatch()`
- `updateTimerHud()`
- projectile `hp < 0` 파괴 조건

### Reason
- 짧은 플레이 세션과 자동 종료 조건을 확립하기 위해 변경.

### Compatibility
- 이전 10 HIT 승리 규칙과 호환되지 않음.

---

## v0.10.0 — 피격 넉백·투사체 수명

**Release type:** MINOR  
**Date:** 2026-08-11

### Changed
- 피격 시 화분 진행 방향 넉백.
- 화분 잔류시간을 각 화분 cooldown과 연결.

### Fixed
- 피격 결과의 운동감이 약한 문제 개선.

### Code
- `applyHitKnockback()`
- projectile `maxLife`
- actor 반발력 관련 값

### Reason
- 피격 결과와 화분별 차이를 물리적으로 더 명확하게 표현하기 위해 변경.

### Compatibility
- AUTO LOCK + FIRE 구조 유지.

---

## v0.9.0 — AUTO LOCK + FIRE

**Release type:** MINOR  
**Date:** 2026-08-11

### Changed
- 수동 드래그 조준 제거.
- 자동 조준 추가.
- FIRE 버튼 중심 조작으로 변경.
- 화분 역할을 쿨타임·공중 상쇄 내구도로 재설계.

### Fixed
- 계속 튕기는 캐릭터를 직접 조준하기 어려운 문제 해결.

### Code
- `autoAimVelocity()`
- `playerFire()`
- `POT.cooldown`
- `POT.damage`
- `POT.durability`

### Reason
- 조준 자체보다 발사 타이밍에 집중하도록 핵심 조작을 재설계.

### Compatibility
- 이전 드래그 조작과 호환되지 않는 MINOR.

---

## v0.8.0 — 무한 바운스 난전

**Release type:** MINOR  
**Date:** 2026-08-11

### Changed
- 캐릭터 바운스 횟수 제한 제거.
- 정착 단계 삭제.
- 경기 종료까지 계속 이동.
- YOU/BOT 몸통 충돌 추가.

### Fixed
- 캐릭터가 멈추면 속도감이 사라지는 문제 제거.

### Code
- settled gating 제거
- 최소 운동량 유지
- `resolveActorCollision()`

### Reason
- 무한 바운스를 핵심 플레이 루프로 확정하기 위해 변경.

### Compatibility
- 캐릭터 이동 규칙이 크게 변경됨.

---

## v0.7.0 — 모바일 UI·BOT 랜덤샷

**Release type:** MINOR  
**Date:** 2026-08-11

### Changed
- 16:9 모바일 가로 UI.
- fullscreen/orientation 시도.
- BOT 10% 랜덤 투척.

### Fixed
- 모바일 UI 공간 문제 개선.
- BOT 반복 탄도 고착 완화.

### Code
- responsive CSS
- fullscreen/orientation 처리
- `botFire()` random branch

### Reason
- 스마트폰 플레이 환경과 BOT 전투 변수를 확장하기 위해 변경.

### Compatibility
- 데스크톱 기본 플레이 유지.

---

## v0.6.1 — 지형·겹침 QA

**Release type:** PATCH  
**Date:** 2026-08-11

### Changed
- 구름 지형 아래를 바닥까지 채움.
- 드래그 히트박스 가독성 개선.

### Fixed
- 공격 불가능 빈 공간.
- YOU/BOT 겹침으로 인한 입력 모호성.

### Code
- hill collision
- actor separation
- grab-zone UI

### Reason
- 신규 시스템이 아닌 기존 충돌·입력 문제를 수정하기 위한 PATCH.

### Compatibility
- v0.6.0 게임 규칙 유지.

---

## v0.6.0 — 전투 템포·티배깅 확장

**Release type:** MINOR  
**Date:** 2026-08-11

### Changed
- 화분 수 제한 제거.
- 10 HIT 승리.
- 플레이어 공격 실패 시 BOT 자동 티배깅.
- 화면 흔들림 강화.

### Fixed
- 탄약 제한으로 전투 리듬이 끊기는 문제 제거.

### Code
- ammo 제한 제거
- score rule
- BOT taunt path

### Reason
- 연속 난전과 BOT 성격을 강화하기 위해 변경.

### Compatibility
- 탄약·승리 규칙 변경.

---

## v0.5.0 — 구름 지형·바운스 물리

**Release type:** MINOR  
**Date:** 2026-08-11

### Changed
- 둥근 구름 언덕 지형.
- 캐릭터 벽·천장·바닥 반사.
- squash/stretch.
- BOT AIM 보정.

### Fixed
- 정적인 포격전의 운동감 부족 개선.

### Code
- `generateObstacles()`
- `hillSurfaceY()`
- `startSpawn()`
- `updateSpawnActor()`
- `squashActor()`

### Reason
- 캐릭터 자체를 지속적인 움직임 요소로 만들기 위해 변경.

### Compatibility
- 지형·이동 물리가 크게 변경됨.

---

## v0.4.0 — 파괴 피드백

**Release type:** MINOR  
**Date:** 2026-08-11

### Changed
- 실패 화분 지형화 제거.
- YOU/BOT 식별 강화.
- 와장창·파편·충격파·화면 흔들림.
- WebAudio 효과음·진동.

### Fixed
- 남은 화분이 공격을 막는 문제.
- 타격 피드백 부족.

### Code
- `breakFx()`
- `shatter()`
- screen shake
- vibration

### Reason
- 화분 파괴를 핵심 보상으로 강화하기 위해 변경.

### Compatibility
- 기본 공격 방식 유지.

---

## v0.3.0 — 탄수·승리조건·사거리

**Release type:** MINOR  
**Date:** 2026-08-11

### Changed
- 화분 20개 제한.
- 5 HIT 승리.
- 실패 화분 지형화 실험.
- 화분별 사거리 차등.

### Fixed
- 종료 조건이 없던 초기 구조에 승패 조건 추가.

### Code
- ammo state
- `targetScore`
- pot별 speed/range

### Reason
- 화분별 전략 차이와 경기 종료 조건을 검증하기 위해 변경.

### Compatibility
- 이전 승리 규칙과 동일하지 않음.

---

## v0.2.0 — 실시간 BOT·드래그 투척

**Release type:** MINOR  
**Date:** 2026-08-11

### Changed
- BOT 실시간 동시 공격.
- Pointer Events 드래그 투척.
- 예상 탄도.
- 복수 투사체.
- 랜덤 지형·시작 배치.

### Fixed
- 단독 투척 구조를 실시간 대전으로 확장.

### Code
- Pointer Events
- `botFire()`
- `updateProjectiles()`
- projectile collision

### Reason
- 턴제보다 동시에 일어나는 난전이 더 적합하다고 판단하여 변경.

### Compatibility
- 플레이 방식이 크게 변경됨.

---

## v0.1.0 — 최초 플레이어블

**Release type:** MINOR  
**Date:** 2026-08-11

### Changed
- 최초 브라우저 플레이어블.
- Canvas 캐릭터·화분·기본 투척·충돌.

### Fixed
- 해당 없음.

### Code
- 단일 HTML 구조
- Canvas 2D Context
- `startGame()`
- `update(dt)`
- `draw()`

### Reason
- POT BREAKER 아이디어를 실제 조작 가능한 형태로 검증하기 위해 최초 제작.

### Compatibility
- 최초 버전이므로 이전 버전 호환 대상 없음.

