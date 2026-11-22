# potbreaker 운영 소스 기준

`cloudflare/worker.js`는 Cloudflare에서 실제로 100% 트래픽을 처리하는 `potbreaker` Worker의 보관본이다.

## 동기화 기준

- 운영 Worker: `potbreaker`
- 기준 날짜: 2026-11-22
- 운영 버전: `8e69221c-95db-414d-a268-297d27faa2f1`
- 배포 ID: `c36ecde1-3f27-4893-875f-cb98a3a23823`
- 트래픽: 100%
- D1 바인딩: `POTBREAKER_DB`

## 안전 규칙

1. 운영 변경은 항상 이 파일을 기준으로 만든다.
2. 이전 `scripts/build_worker.py`와 `web/`의 초기 게임 소스는 역사 보관물이다. 운영 Worker를 다시 생성하거나 배포하는 데 사용하지 않는다.
3. Cloudflare API의 `content/v2`에서 실제 Worker를 다시 내려받은 뒤 해시와 버전을 기록해 동기화 상태를 확인한다.
4. 배포 전에는 새 버전을 업로드만 하고, 게임·랭킹·D1 바인딩을 검증한 후 배포 비율을 변경한다.

