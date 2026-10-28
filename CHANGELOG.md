## v1.0.61 — 방향 튐 추가 완화

**Release type:** PATCH  
**Date:** 2026-10-28

### Changed
- 방향 전환 확정량을 0.12칸에서 0.13칸으로 소폭 올려 순간적인 흔들림에 덜 반응하도록 조정.
- 새 축 방향 우세 기준을 1.3배에서 1.32배로 미세 조정.
- 한 칸 이동 속도와 이동 간격은 유지.

### QA
- 직진 흔들림 억제, 의도된 코너 전환 시뮬레이션 및 엔진 회귀 테스트 8개 확인.
- 실기기 QA는 미실시.

## v1.0.60 — 터치 방향 튐 미세 억제

**Release type:** PATCH  
**Date:** 2026-10-28

### Changed
- 방향 전환 확정 누적량을 0.10칸에서 0.12칸으로 조금 올려 간헐적인 옆 방향 튐을 줄임.
- 새 축 방향이 기존 축의 흔들림보다 분명해야 하는 기준을 1.25배에서 1.3배로 조정.
- 이동 간격, 직진 감도, 터치 해제 동작은 유지.

### QA
- 직진 중 옆 흔들림 억제와 의도적 코너 전환 시뮬레이션.
- 엔진 회귀 테스트 8개 확인.
- 휴대폰 실기기 QA는 미실시.

## v1.0.59 — 직진 중 방향 튐 억제

**Release type:** PATCH  
**Date:** 2026-10-28

### Changed
- 현재 방향을 유지하는 동안 미세한 직진 흔들림만으로 다른 축으로 바뀌지 않도록 수정.
- 새 방향 또는 반대 방향은 같은 방향 입력이 누적 기준에 도달할 때 확정.
- 큰 입력은 바로 방향을 바꾸고, 한 칸 이동 주기와 터치 해제 동작은 유지.

### QA
- 직진 중 작은 수직 흔들림 유지, 지속적인 코너 전환, 가로·세로 좌표 및 해제 정지 시뮬레이션.
- 엔진 회귀 테스트 8개 검증.
- 실기기 QA는 미실시.

## v1.0.58 — 방향 흔들림 보정

**Release type:** PATCH  
**Date:** 2026-10-28

### Changed
- 작은 대각선 흔들림을 새 방향으로 오인하지 않도록 축 우세 판정을 1.0에서 1.06으로 조정.
- 방향 입력 임계값은 0.05칸으로 맞춰 빠른 전환 감도와 안정성을 절충.
- 이동 간격과 한 번에 한 칸 이동하는 동작은 유지.

### QA
- 축 흔들림 억제와 실제 코너 전환 시뮬레이션, 엔진 회귀 테스트 8개 검증.
- 실제 휴대폰 촉감 QA는 미실시.

## v1.0.57 — 방향 전환 감도 미세 조정

**Release type:** PATCH  
**Date:** 2026-10-28

### Changed
- 방향 입력 임계값을 0.055칸에서 0.045칸으로 낮춰 작은 드래그에도 방향 전환이 조금 더 빨리 반영되도록 조정.
- 축 우세 기준을 1.03에서 1.0으로 낮춰 기존 방향을 고집하는 구간을 줄임.
- 격자 이동 간격과 한 번에 한 칸 이동하는 동작은 유지.

### QA
- 작은 연속 입력과 축 전환 시뮬레이션, 엔진 회귀 테스트 8개 검증.
- 실제 휴대폰 촉감 QA는 미실시.

## v1.0.56 — 방향 전환 반응 미세 조정

**Release type:** PATCH  
**Date:** 2026-10-28

### Changed
- 방향 입력 최소 누적량을 0.07칸에서 0.055칸으로 낮춰 천천히 드래그할 때 전환 반응을 조금 앞당김.
- 축 우세 기준을 1.05에서 1.03으로 완화해 방향 전환을 약간 더 쉽게 조정.
- 한 칸 이동 간격과 터치 해제 동작은 유지.

### QA
- 방향 전환, 가로·세로 좌표 변환, 해제 정지 시뮬레이션 및 엔진 테스트 8개 재검증.
- 실제 휴대폰 촉감 QA는 미실시.

## v1.0.55 — 느린 드래그 방향 전환 보정

**Release type:** PATCH  
**Date:** 2026-10-28

### Changed
- 포인터 이벤트마다 버리던 미세 이동량을 방향 판정용으로 짧게 누적해 천천히 드래그해도 전환 입력을 받도록 수정.
- 방향을 판정하면 누적량을 초기화해 이전 축의 잔량이 다음 코너에 섞이지 않도록 함.
- 이동은 고정된 격자 간격으로 유지하고, 한 번의 긴 드래그가 여러 칸의 대기 이동을 만들지 않도록 함.
- 터치 해제 시 이동을 즉시 정지.

### QA
- 작은 연속 입력, 가로·세로 화면 회전, 축 전환 및 터치 해제 시뮬레이션 통과.
- 엔진 회귀 테스트 8개 통과.
- 실제 휴대폰 촉감 QA는 미실시.

## v1.0.54 — 이동 속도와 방향 전환 단순화

**Release type:** PATCH  
**Date:** 2026-10-28

### Changed
- 터치 이동 거리로 여러 칸을 예약하던 경로 큐를 제거.
- 터치 중에는 최근 드래그 방향만 반영하고, 캐릭터는 고정된 격자 이동 간격으로 한 칸씩 이동.
- 방향 전환 시 이전 경로 잔여량이 재생되지 않으며, 터치 해제 즉시 이동 중단.
- 작은 좌표 흔들림만 무시하고 방향 우세도 기준을 완화해 축 전환을 빠르게 처리.

### QA
- 스크립트 문법, 터치 방향 갱신, 해제 중단 정적/동작 검증 필요.
- 실제 휴대폰에서 감도 확인 필요.

## v1.0.53 — 터치 경로 튐 및 끝방향 보정

**Release type:** PATCH  
**Date:** 2026-10-28

### Changed
- 드래그 방향 축이 바뀔 때 이전 축에 남은 분수 이동량을 버려 코너에서 이전 방향으로 추가 이동하지 않도록 수정.
- 터치가 끝나면 처리되지 않은 입력 대기열을 비워 접촉이 끝난 뒤 뒤늦게 움직이지 않도록 변경.
- 축 전환에는 최소 이동량과 우세도 기준을 적용해 작은 터치 흔들림으로 방향이 튀는 현상을 줄임.

### QA
- 4칸 네모 입력, 코너 전환, 손가락 떼기 후 이동 중단 시뮬레이션 필요.

## v1.0.52 — 터치 방향 반전 수정

**Release type:** PATCH  
**Date:** 2026-10-28

### Changed
- 이전 수정에서 추가한 전체 방향 반전을 되돌림. 화면 좌표를 게임 격자 좌표로 변환한 원래 방향을 사용.

### QA
- 가로·세로 회전 화면에서 4칸 경로 방향 테스트 및 엔진 회귀 테스트 8개 통과.
- 실기기 QA 필요.

## v1.0.51 — 터치 이동 방향 반전 보정

**Release type:** PATCH  
**Date:** 2026-10-28

### Changed
- 터치 드래그 벡터의 부호를 반전해 보고된 반대 방향 이동을 보정.
- 화면 회전 보정과 4칸 경로 입력은 유지.

### QA
- 4칸 사각형 경로 방향과 터치 해제 후 경로 완료를 검증.
- 엔진 회귀 테스트 8개 통과, 스크립트 문법 확인.
- 실기기에서 방향 체감은 추가 확인 필요.

## v1.0.50 — 드래그 경로 입력 완료 보장

**Release type:** PATCH  
**Date:** 2026-10-28

### Changed
- 손가락을 놓아도 이미 그린 격자 경로는 끝까지 반영하고, 경로 대기열이 끝나면 이동을 멈춤.
- 빠르게 그린 네 칸 정사각형의 코너와 각 변이 손을 뗀 뒤에도 누락되지 않도록 처리.
- 새 터치, 창 포커스 해제, 게임 종료 시에는 남은 경로를 초기화.

### QA
- 4칸씩 그린 정사각형 경로 순서와 터치 해제 후 경로 완료를 동작 검증.
- 엔진 회귀 테스트 8개 통과, 스크립트 문법 및 플래시/조작 UI 정적 확인.
- 실제 휴대폰에서의 촉감 및 드래그 속도 검증은 미실시.

## v1.0.49 — 드래그 경로 기반 격자 이동

**Release type:** PATCH  
**Date:** 2026-10-28

### Changed
- 손가락의 드래그 경로를 캔버스 좌표에 맞춰 격자 단위로 누적하고, 각 칸을 상하좌우 이동 단계로 큐에 보존.
- 네 칸 변과 코너 회전이 입력에서 사라지지 않도록 방향 스무딩/연속 판정 대신 경로 자체를 처리.
- 터치가 끝나면 남은 이동 단계를 초기화해 접촉 없이 움직임이 이어지지 않도록 함.
- 막힌 칸에서 대기열이 멈추지 않도록 짧은 시간 후 해당 단계를 건너뜀.

### QA
- 엔진 회귀 테스트 8개 및 터치 경로 정적 검증 통과.
- 실제 휴대폰 기기에서의 손가락 드래그 검증은 미실시.

## v1.0.48 — 게임 전체 피격 플래시 적용

**Release type:** PATCH  
**Date:** 2026-10-28

### Changed
- 캔버스 안쪽 플래시를 HUD와 조작 버튼까지 덮는 게임 화면 전체 오버레이로 변경.
- 화분 파괴 시 0.24초 동안 최대 24%의 붉은 투명도 효과 적용. 화면 흔들림은 없음.

### Code
- `web/index.html`, `cloudflare/worker.js`, `scripts/build_worker.py`, `tests/test_potbreaker_re.py`

---

## v1.0.47 — 화분 피격 화면 효과 교체

**Release type:** PATCH  
**Date:** 2026-10-28

### Changed
- 화분 파괴 때 화면을 무작위로 흔드는 효과를 제거.
- 같은 이벤트에 최대 24% 불투명도의 붉은 화면 플래시를 0.24초간 표시.

### Code
- `web/index.html`, `cloudflare/worker.js`, `scripts/build_worker.py`, `tests/test_potbreaker_re.py`

---

## v1.0.46 — 연속 드래그 방향 보정

**Release type:** PATCH  
**Date:** 2026-10-28

### Changed
- 고정 거리 문턱 대신 연속 드래그 벡터를 짧게 평균내고, 새 축 방향이 이어질 때 전환하도록 수정.
- 명확한 입력은 빠르게 반영하고, 단발성 흔들림은 걸러 방향 전환이 덜 딱딱하고 덜 튀게 조정.

### Preserved
- 실제 표시 캔버스 축 변환, 0.18초/칸 이동 속도, 확대된 발사 버튼.

### Code
- `web/index.html`, `cloudflare/worker.js`, `scripts/build_worker.py`, `tests/test_potbreaker_re.py`

---

## v1.0.45 — 드래그 방향 전환 안정화

**Release type:** PATCH  
**Date:** 2026-10-28

### Changed
- 마지막 감도 조정 이후 잦아진 방향 전환을 줄이도록 전환 거리를 0.21칸, 축 우세도 1.25로 조정.
- 초기 방향 판정도 작은 손가락 흔들림에 덜 민감하도록 기준을 소폭 높임.

### Preserved
- 실제 표시 캔버스 축 기반 방향 변환, 기묘 이동 0.18초/칸, 확대된 발사 버튼.

### Code
- `web/index.html`, `cloudflare/worker.js`, `scripts/build_worker.py`, `tests/test_potbreaker_re.py`

---

## v1.0.44 — 화면 축 기준 터치 방향 보정

**Release type:** PATCH  
**Date:** 2026-10-28

### Fixed
- 손가락 드래그를 실제 표시된 캔버스 축에 투영해 화면 회전 상태에서도 위·아래 방향이 격자와 일치하도록 보정.
- 방향 감지 거리를 소폭 낮춰 짧은 아래 방향 드래그도 더 잘 인식하고, 드래그 축 판정 완충값도 줄임.

### Preserved
- 기묘 이동 속도 0.18초/칸, 확대된 휴대폰 발사 버튼.

### Code
- `web/index.html`, `cloudflare/worker.js`, `scripts/build_worker.py`, `tests/test_potbreaker_re.py`

---

## v1.0.43 — 이동 속도·터치 반응·발사 버튼 보정

**Release type:** PATCH  
**Date:** 2026-10-28

### Changed
- 기묘의 한 칸 이동 간격을 0.24초에서 0.18초로 줄여 이동 속도를 약 33% 높임.
- 방향 전환 누적 거리와 축 판정 여유를 낮춰 드래그 방향을 더 쉽게 바꾸도록 조정.
- 휴대폰 발사 버튼 크기를 82–108px 범위로 확대.

### Code
- `web/game.py`, `web/index.html`, `cloudflare/worker.js`, `scripts/build_worker.py`, `tests/test_potbreaker_re.py`

---

## v1.0.42 — 방향 전환 완충값 조정

**Release type:** PATCH  
**Date:** 2026-10-28

### Changed
- 방향 전환 거리를 0.286칸에서 0.235칸으로 낮춰 방향 변경 반응을 부드럽게 조정.
- 첫 방향 입력과 축 판정 기준은 유지.

### Code
- `web/index.html`, `cloudflare/worker.js`, `scripts/build_worker.py`, `tests/test_potbreaker_re.py`

---

## v1.0.41 — 방향 흔들림 억제 30% 추가

**Release type:** PATCH  
**Date:** 2026-10-28

### Changed
- 최초 드래그 반응은 유지하고, 이미 이동 중일 때 방향을 다시 판정하는 누적 거리를 0.22칸에서 0.286칸으로 30% 높여 미세한 손가락 흔들림을 줄임.

### Code
- `web/index.html`, `cloudflare/worker.js`, `scripts/build_worker.py`, `tests/test_potbreaker_re.py`

---

## v1.0.40 — 미세한 방향 튐 추가 보정

**Release type:** PATCH  
**Date:** 2026-10-28

### Changed
- 방향이 이미 정해진 상태에서 비슷한 크기의 가로·세로 드래그가 들어오면 기존 축을 조금 더 유지하도록 보정.
- 이동 간격과 터치 전환 임계값은 유지.

### Code
- `web/index.html`, `cloudflare/worker.js`, `scripts/build_worker.py`, `tests/test_potbreaker_re.py`

---

## v1.0.39 — 드래그 방향 흔들림 완화

**Release type:** PATCH  
**Date:** 2026-10-28

### Changed
- 방향이 정해진 뒤 반대 방향 전환은 조금 더 분명한 손가락 이동이 있어야 반영하도록 완충 구간 추가.
- 대각선에 가까운 미세 흔들림은 기존 방향을 유지하고, 명확한 가로·세로 드래그는 한 칸 이동 방향으로 반영.

### Code
- `web/index.html`, `cloudflare/worker.js`, `scripts/build_worker.py`, `tests/test_potbreaker_re.py`

---

## v1.0.38 — 터치 드래그 방향 계산 통일

**Release type:** PATCH  
**Date:** 2026-10-28

### Changed
- 초기 터치 위치와 드래그 입력을 섞던 처리를 제거하고, 손가락 드래그 벡터만으로 방향을 결정하도록 통일.
- CSS 회전 행렬을 역변환해 화면상 손가락 움직임을 게임 격자 방향에 맞춤. 누르는 동안 반복 이동하고, 손가락을 떼면 즉시 정지.

### Code
- `web/index.html`, `cloudflare/worker.js`, `scripts/build_worker.py`, `tests/test_potbreaker_re.py`

---

## v1.0.37 — 드래그 방향 전환 반응 개선

**Release type:** PATCH  
**Date:** 2026-10-28

### Changed
- 드래그 중 방향 전환 감지 임계값을 낮춰 손가락 이동에 더 빠르게 반응하도록 조정.

### Code
- `web/index.html`, `cloudflare/worker.js`, `scripts/build_worker.py`, `tests/test_potbreaker_re.py`

---

## v1.0.36 — 누르는 동안 연속 이동·해제 즉시 정지

**Release type:** PATCH  
**Date:** 2026-10-28

### Changed
- 손가락을 누르고 있는 동안 반복 이동하며, 드래그 방향에 맞춰 방향 전환.
- 손가락을 떼면 이동 입력과 방향 상태를 즉시 초기화해 터치가 없을 때 움직이지 않도록 수정.

### Code
- `web/index.html`, `cloudflare/worker.js`, `scripts/build_worker.py`, `tests/test_potbreaker_re.py`

---

## v1.0.35 — 연속 터치 이동·방향 전환

**Release type:** PATCH  
**Date:** 2026-10-28

### Changed
- 손가락을 누르고 있는 동안 한 칸씩 반복 이동하고, 드래그하면 손가락의 방향에 맞춰 이동 방향 전환.
- 손가락을 떼면 반복 이동은 즉시 멈춤. 짧은 터치 입력은 최대 한 칸 이동으로 처리.

### Preserved
- 터치 방향 버튼 없이 플레이 화면을 직접 조작. 감 과장 화분 효과 4종 각 25%.

### Code
- `web/index.html`, `cloudflare/worker.js`, `scripts/build_worker.py`, `tests/test_potbreaker_re.py`

---

## v1.0.34 — 터치 입력·결과 전환·감 과장 아이템 수정

**Release type:** PATCH  
**Date:** 2026-10-28

### Fixed
- 종료 화면에서 서버 기록 응답을 기다리지 않고 해당 승리·패배 그림과 문구를 즉시 갱신해 이전 결과가 보이지 않도록 수정.
- 화면 터치는 한 번에 한 칸만 입력하고, 드래그는 손가락 이동 방향으로 한 칸 입력. 회전된 화면은 실제 캔버스 방향을 기준으로 좌표 보정.
- 감 과장 화분 효과를 하트 +1, 하트 -1, 화분 풀충전, 필드 화분 리셋으로 균등 추첨하도록 수정.

### Preserved
- 크다 부장 체력: 노멀 5, 하드 7, 베리 하드 10.

### Code
- `web/index.html`, `web/game.py`, `cloudflare/worker.js`, `scripts/build_worker.py`, `tests/test_potbreaker_re.py`

---

## v1.0.33 — 터치 방향 이동·화면 복귀 초기화

**Release type:** PATCH  
**Date:** 2026-10-28

### Fixed
- 방향 버튼을 제거하고, 플레이 화면 터치·드래그 방향으로 기묘가 한 칸씩 이동하도록 변경. 세로 화면 회전 좌표도 반영하며 빠른 터치 입력은 한 칸 이동으로 처리.
- 페이지 새로고침·복귀와 새 게임 시작 때 이전 승리 화면이 남지 않도록 종료 화면 상태를 초기화하고, 대기 중인 종료 전환을 취소.

### Preserved
- 크다 부장 체력: 노멀 5, 하드 7, 베리 하드 10.

### Code
- `web/index.html`, `web/game.py`, `cloudflare/worker.js`, `scripts/build_worker.py`, `tests/test_potbreaker_re.py`

---

## v1.0.32 — 크다 부장 체력·방향 버튼 이동

**Release type:** PATCH  
**Date:** 2026-10-28

### Changed
- 크다 부장 체력: 노멀 5, 하드 7, 베리 하드 10.
- 원형 조이스틱을 상·하·좌·우 터치 버튼으로 교체하고, 이동 입력은 한 번에 한 방향 한 칸씩 처리. 대각선 이동은 끔.
- 버튼을 누르고 있으면 한 칸씩 반복 이동하며, 최대 이동 간격은 0.24초.

### Code
- `web/game.py`, `web/index.html`, `cloudflare/worker.js`, `scripts/build_worker.py`, `tests/test_potbreaker_re.py`

---

## v1.0.31 — 격자 이동·세로 화면 조이스틱 QA

**Release type:** PATCH  
**Date:** 2026-10-28

### Fixed
- 기묘의 자유 연속 이동을 격자 기준 8방향 한 칸 이동으로 변경하고, 최대 이동 속도를 약 10.5칸/초에서 약 4.2칸/초로 낮춤.
- 세로 화면에서 게임 무대가 90도 회전할 때 조이스틱 입력 벡터를 같은 회전 방향으로 보정해 손가락 방향과 캐릭터 이동 방향을 일치시킴.

### Code
- `web/game.py`, `web/index.html`, `cloudflare/worker.js`, `scripts/build_worker.py`, `tests/test_potbreaker_re.py`

---

## v1.0.24 — 세로 휴대폰 시작 화면 정렬 보정

**Release type:** PATCH  
**Date:** 2026-10-28

### Changed
- 세로 휴대폰에서 가로 게임 스테이지를 뷰포트 가운데에 고정 배치해 시작 안내와 버튼이 잘리지 않도록 수정.
- 화면, Worker, 안내 문서 버전을 v1.0.24로 통일.

### Verified
- Worker 스크립트 문법 검사 통과.


## v1.0.23 — 감 과장 물음표 화분 아이템

**Release type:** PATCH  
**Date:** 2026-10-28

### Changed
- 감 과장이 떨어뜨리는 폭탄을 획득형 물음표 화분으로 변경. 착지한 물음표 화분을 기묘나 크다가 주우면 동일한 확률로 HP 1 감소 또는 1 회복.
- 한 번 투하할 때 물음표 화분 2개를 생성하고, 투하 간격은 기존 0.6초에서 1.2초로 늘림.
- 물음표 화분을 보라색 화분과 `?` 표시로 구분.

### Verified
- 두 캐릭터 모두 피해/회복 효과와 무적 시간 중 피해 적용 확인.
- 투하당 2개 생성, 1.2초 간격 및 50:50 효과 분기 확인.


## v1.0.22 — 세로 휴대폰 자동 회전 화면과 연속 발사

**Release type:** PATCH  
**Date:** 2026-10-28

### Changed
- 휴대폰을 직접 가로로 돌리지 않아도 세로 기기 안에서 게임 화면을 가로 방향으로 자동 회전.
- 기묘의 발사 버튼을 누르고 있는 동안 화분을 연속 발사하고, 손을 떼면 중단.
- 십자 키의 터치 영역을 216–264px로 확대.
- 화면, Worker, 문서 버전을 v1.0.22로 통일.

### Verified
- 화면 회전, 발사 버튼 누름/해제, 대형 십자 키 동작 검증.


# POT BREAKER CHANGELOG


## v1.0.21 — 조준선 제거 및 자동 조준

**Release type:** PATCH  
**Date:** 2026-10-28

### Changed
- 화면의 조준 부채꼴과 캐릭터 조준선을 제거.
- 화분 발사 방향을 상대 캐릭터 위치에 직접 맞추도록 자동 조준 개선.

### Verified
- 자동 조준 벡터와 조준선 제거 테스트 통과.



## v1.0.20 — 벽 충돌 이펙트와 휴대폰 가로 전환

**Release type:** PATCH  
**Date:** 2026-10-28

### Changed
- 벽 충돌은 투사체를 멈추고 화분을 다시 놓되, 파손 모션·사운드·흔들림은 발생하지 않도록 수정.
- 캐릭터 피격에만 타격 판정과 파손 이펙트를 적용하고 투사체 간 충돌 판정을 제거.
- 휴대폰 시작 동작에서 전체화면과 가로 방향 잠금을 사용자 탭 안에서 동시에 요청.

### Verified
- 벽 충돌은 파손 이벤트를 만들지 않고, 캐릭터 피격은 파손 이벤트를 만드는 테스트 통과.



## v1.0.19 — 휴대폰 조작 및 타격 이펙트 복구

**Release type:** PATCH  
**Date:** 2026-10-28

### Changed
- 모바일 십자패드를 156–184px로 키우고 방향키 터치 영역과 대비를 높임.
- 게임이 Worker의 최신 /game.py를 불러오도록 통일해 보유량·피격 이벤트 누락을 방지.
- 화분 파손 시 `쨍그랑!` 글자와 파편 애니메이션을 별도로 표시하고 지속시간을 늘림.
- 재시작할 때 이펙트 이벤트 ID와 파편 상태를 초기화.
- 버전을 v1.0.19로 통일.

### Verified
- Worker 및 화면 스크립트 문법 검사, 엔진 단위 테스트 통과.



## v1.0.18 — 기묘 시작 화분 3개 지급

**Release type:** PATCH  
**Date:** 2026-10-28

### Changed
- 기묘가 게임 시작 시 화분 3개를 들고 시작하도록 수정.
- 화면과 Worker 버전을 v1.0.18로 통일.

### Verified
- 초기 보유량 3개, 최대 보유량 3개 테스트 통과.

## v1.0.17 — 휴대폰 조작 및 화면 QA 보완

**Release type:** PATCH  
**Date:** 2026-10-28

### Changed
- 기묘의 화분 보유 한도를 1개에서 3개로 늘리고 HUD에 현재 보유량과 한도를 표시.
- 화면 모서리의 터치 조작 버튼을 작게 조정하고 투명도를 높임.
- 시작 위치를 안쪽으로 옮겨 버튼이 기묘를 가리는 상황을 줄임.
- 세로 화면 안내를 명확히 하고, 휴대폰에서 가로 플레이 화면을 우선하도록 정리.
- 화면·Worker·문서 버전을 v1.0.17로 통일.

### Verified
- 십자패드 이동, 캐릭터별 화분 색 구분, 화분 파손 시 화면 흔들림과 파손음.
- 플레이어 화분으로 감 과장을 맞히면 기묘 HP가 1 회복되며 크다 부장은 회복되지 않음.
- 기묘의 이동 속도는 기존 v1.0.15 값 대비 약 10% 높음.

### Code
- `web/game.py`, `web/index.html`, `cloudflare/worker.js`, `scripts/build_worker.py`, `tests/test_potbreaker_re.py`

---

## v1.0.14 — 모바일 조이스틱 터치 입력 보강

**Release type:** PATCH  
**Date:** 2026-10-28

### Changed
- 포인터 이벤트에 터치 이벤트 처리를 추가해 모바일에서 조이스틱 입력이 끊기지 않게 보강.
- 세로 화면 회전 대체 모드에서 화면 좌표를 게임 방향에 맞게 변환.

### Code
- `web/index.html`, `cloudflare/worker.js`, `scripts/build_worker.py`, `tests/test_potbreaker_re.py`

---

## v1.0.13 — 조이스틱 응답성과 화분 파손음

**Release type:** PATCH  
**Date:** 2026-10-27

### Changed
- 조이스틱 입력을 8방향 양자화에서 힘 조절이 되는 방향 입력으로 바꾸고, 이동 간격에 입력 세기를 반영.
- 포인터 캡처가 실패해도 창 전체에서 손가락 이동과 해제를 추적하도록 보강하고 입력 데드존을 낮춤.
- 화분이 벽/캐릭터/다른 화분과 충돌해 깨질 때 짧은 쨍그랑 효과음 재생. 모바일 오디오 정책을 고려해 첫 터치에서 오디오를 활성화.

### Code
- `web/game.py`, `web/index.html`, `cloudflare/worker.js`, `scripts/build_worker.py`, `tests/test_potbreaker_re.py`

---

## v1.0.12 — 모바일 조이스틱 대각선과 터치 영역 개선

**Release type:** PATCH  
**Date:** 2026-10-27

### Changed
- 모바일 조이스틱으로 8방향 이동을 지원하고, 대각선 이동 때 모서리 벽을 통과하지 않도록 처리.
- 대각선 이동 간격을 보정해 기존 이동 속도를 유지.
- 모바일 던지기 버튼의 터치 영역을 최소 112×112 CSS px로 확대.

### Code
- `web/game.py`, `web/index.html`, `cloudflare/worker.js`, `scripts/build_worker.py`, `tests/test_potbreaker_re.py`

---

## v1.0.11 — 모바일 첫 화면 잘림 수정

**Release type:** PATCH  
**Date:** 2026-10-27

### Fixed
- 모바일에서 설명 문구가 화면 폭 기준으로 커져 4컷 소개 화면과 입장 버튼이 아래로 잘리던 문제.
- 4컷과 설명 영역을 게임 무대 높이 안에 맞추고 글자와 여백을 무대 크기에 따라 조정.

### Code
- `web/index.html`, `cloudflare/worker.js`, `scripts/build_worker.py`, `tests/test_potbreaker_re.py`

---

## v1.0.10 — 기묘 이동 속도 소폭 상향

**Release type:** PATCH  
**Date:** 2026-10-27

### Changed
- 기묘의 일반 이동 간격을 0.115초에서 0.105초로, 돌진 후 이동 간격을 0.095초에서 0.09초로 줄여 이동 속도를 약 10% 높임.

### Code
- `web/game.py`, `web/index.html`, `cloudflare/worker.js`, `scripts/build_worker.py`, `tests/test_potbreaker_re.py`

---

## v1.0.9 — 모바일 화면 회전과 조작 UI 조정

**Release type:** PATCH  
**Date:** 2026-10-27

### Changed
- 모바일에서 게임 시작 시 전체 화면과 가로 방향 잠금을 요청하고, 잠금이 지원되지 않으면 게임 화면을 자동으로 가로 배치.
- 게임 무대 크기에 맞춰 HUD와 터치 조작 크기를 계산하도록 조정.
- 모바일 인트로에서 4컷 만화를 크게 보여주고, 설명 패널을 숨겨 패널이 잘리지 않게 조정.
- 작은 화면에서 하단 안내 문구를 감춰 캐릭터와 맵 가림을 줄임.

### Fixed
- 모바일 브라우저의 넓은 viewport 기준으로 조작 버튼이 커져 캐릭터를 가리던 문제.
- 세로 화면에서 고정 16:9 무대가 작게 축소되던 문제.

### Code
- `web/index.html`, `cloudflare/worker.js`, `scripts/build_worker.py`, `tests/test_potbreaker_re.py`

### Reason
- 휴대폰에서 게임을 가로 화면으로 크게 표시하고, 주요 캐릭터와 전장을 쉽게 볼 수 있도록 개선.

---
## v1.0.8 — RE 전투 밸런스 및 파티션 충돌

**Release type:** PATCH  
**Date:** 2026-10-27

### Changed
- 크다 부장 화분 크기를 키우고 이동 속도를 7.2에서 6.4 격자 단위/초로 낮춤.
- 감 과장 재등장 간격을 9초에서 14초로 늘리고 폭격 간격을 1.05초에서 0.6초로 줄임.
- 크다 부장 돌진과 양쪽 화분 투사체가 파티션을 통과하지 않도록 충돌 판정 추가.
- 오프닝 4컷을 동일한 672×409 크기로 유지하고 3번 패널 크롭 검증을 추가.

### Fixed
- 보스 돌진이 파티션 너머의 빈 칸을 목적지로 선택해 벽을 통과하던 문제.
- 크다 부장 화분이 파티션을 무시하고 플레이어에게 도달하던 문제.

### Code
- `web/game.py`, `web/index.html`, `cloudflare/worker.js`, `scripts/build_worker.py`, `tests/test_potbreaker_re.py`

### Reason
- 기존 추격·화분·컷신 규칙을 유지하면서 요청된 벽 충돌, 감 과장 폭격 빈도, 보스 화분 밸런스를 반영.

---

POT BREAKER의 정규 버전 기록입니다.

기존 작업 파일명 `v0.1 ~ v0.21`은 당시 작업 순서를 나타내는 역사적 파일명이며, 아래 CHANGELOG는 실제 변경 규모에 맞춰 정규화한 `vMAJOR.MINOR.PATCH`를 사용합니다.

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

## v1.0.25

- 난이도 선택: 노멀(기존 밸런스), 하드(기묘 화분 1개), 베리 하드(기묘 화분 1개·크다 체력 10).
- 메인 화면에서 누구나 볼 수 있는 랭킹 버튼 추가.
- Cloudflare D1에 익명 방문, 게임 시작, 승리·패배 이벤트 기록.
- 승리 화면에서 닉네임을 입력해 클리어 시간과 난이도를 등록.
- 랭킹은 베리 하드, 하드, 노멀 순으로 묶고 각 난이도 안에서 빠른 기록을 우선 표시.
- Cloudflare D1 `POTBREAKER_DB` 바인딩 및 초기 마이그레이션 추가.

## v1.0.30

- Replace eight-way joystick snapping with continuous analog direction and radial speed.
- Move Kimyo continuously between grid cells with wall sliding and diagonal normalization.
- Keep the joystick direction aligned with the finger to prevent unexpected directional jumps.

## v1.0.29

- Remove the special bomb pot while keeping the healing pot and Gamgwajang’s random mystery pots.
- Add a rounded-rectangle canvas fallback for mobile WebViews that lack `CanvasRenderingContext2D.roundRect`.
- Catch draw-loop errors and show a retryable error panel instead of silently freezing the game screen.

## v1.0.28

- Fix the missing mobile direction reader that stopped the game loop after the intro.
- Start Kimyo and Keuda with no loaded pots; set Kimyo capacity to 3 on Normal and 2 on Hard/Very Hard.
- Set Keuda HP to 3/5/7 for Normal/Hard/Very Hard.
- Keep one clearly marked healing pot and one bomb pot in the arena, distinct from Gamgwajang’s purple mystery pots.

## v1.0.27

- Restore `getMove()` after replacing the mobile direction pad with the round joystick. The missing function caused the first animation frame to throw and stop the game.
- Keep keyboard movement and 8-way joystick movement routed through the same game loop.
- Version the Worker as v1.0.27.

## v1.0.26

- 휴대폰 이동 패드를 원형 조이스틱으로 복구하고 8방향 입력으로 대각선 이동을 지원.
- 대시 버튼은 재사용 대기 중에도 터치 가능 상태를 유지하고, 입력 방향이 없으면 바라보는 방향으로 대시.
- 화분 충돌을 이동 선분 전체에서 검사해 빠른 투사체가 캐릭터를 통과하는 문제 수정.

## v1.0.62
- Mobile touch turns respond slightly sooner while retaining cardinal movement and the existing drift filter.

## v1.0.63
- Lower the mobile touch turn confirmation slightly to make direction changes more responsive.

## v1.0.64
- Make mobile touch direction changes slightly easier to register.

## v1.0.65
- Slightly lower the mobile touch direction change threshold again.
