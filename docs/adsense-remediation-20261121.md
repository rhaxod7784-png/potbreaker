# potbreaker.com AdSense 심사 대응 — 2026-11-21

## 배포 증거와 범위

- 사이트: https://potbreaker.com
- Cloudflare Worker: `potbreaker`
- 이전 운영 버전: `5893d6b9-8b6f-421e-af54-54829c983c71` (롤백용)
- 수정 및 배포 버전: `8e69221c-95db-414d-a268-297d27faa2f1` (100%)
- 배포 ID: `c36ecde1-3f27-4893-875f-cb98a3a23823`
- D1 바인딩: `POTBREAKER_DB` 보존
- 변경 범위: `/floor` 검색 제외 지시 제거, canonical 및 `google-adsense-account` 검증 메타 추가

## 현상과 확인된 원인

AdSense의 '가치가 별로 없는 콘텐츠' 사유는 화면에서 확인되었지만, 정확히 어떤 페이지가 거절 대상이었는지는 제공되지 않았다. Google 콘텐츠 품질 문제는 기술 패치만으로 해결되었다고 단정할 수 없다.

배포 Worker에서 `/floor` 및 `/floor/` 요청이 `X-Robots-Tag: noindex` 처리되는 것을 확인했다. 반면 sitemap에는 `/floor`를 포함하고 있었다. 이는 검색 색인에 대한 실제 충돌이다. AdSense 승인과 직접 인과관계가 입증된 것은 아니다.

기존 `/about` 페이지는 최종 Worker에서 세 게임 모두를 다루는 독자적 가이드로 교체되고 있었다. 초기에 생성된 두 게임용 HTML만 보고 진단하지 말 것.

AdSense 메타태그와 `ads.txt` 지원은 존재한다. 광고 스크립트는 개인정보/동의 준비 플래그를 만족할 때에만 삽입되게 되어 있어 해당 플래그를 검증 없이 강제로 활성화하지 않았다. Google은 광고 코드, 메타태그, ads.txt를 사이트 확인 수단으로 인정한다.

## 코드 변경 (이미 Cloudflare 운영 버전 반영)

1. 기존 SEO 래퍼의 `noindex` 대상 목록에서 `/floor`, `/floor/`만 제거했다. `/api/*` 등 내부 자원은 계속 `noindex`.
2. `FLOOR_PAGE` HTML의 `</head>` 직전에 다음 태그를 삽입한다.
   - `<meta name="robots" content="index,follow">`
   - `<link rel="canonical" href="https://potbreaker.com/floor">`
   - `<meta name="google-adsense-account" content="ca-pub-7687564326575687">`
3. 게임 코드, 랭킹, DB 데이터와 모바일 조작 관련 로직은 수정하지 않았다.

## 확인 완료

- Cloudflare 배포에서 새 버전 100% 활성화
- 실제 브라우저 페이지 `/floor`에서 색인 메타, canonical, 게시자 확인 태그 확인
- `/about`에서 세 게임 가이드 및 약 2,700자의 본문 확인
- `/` 첫 화면 및 `/ginkgo` 페이지 로딩 확인
- D1 설정이 새 Worker 버전에 유지되는지 API 확인

## 미확인 및 후속 점검

- Google Search Console에서 `/floor` 실제 크롤링/색인 결과
- AdSense 재심사 결과 (사용자 계정에서 별도 요청해야 함)
- Google이 '저가치 콘텐츠'로 판단한 정확한 페이지와 사유
- 전체 게임 플레이·랭킹 API의 end-to-end QA

## 소스 일치성 경고

GitHub `main`의 `cloudflare/worker.js`와 `web/index.html`은 오래된 `v1.0.0`에 근거하고 있고, 운영 Cloudflare Worker는 여러 게임을 포함하는 최신 번들이다. **GitHub main을 그대로 다시 배포하면 현재 게임과 최신 기능을 덮어쓸 위험이 있다.** 이 브랜치는 변경 기록 보존 목적이며 운영 코드 자동 재배포 용도로 직접 연결해서는 안 된다.

## 공식 출처
- https://support.google.com/adsense/answer/12131223
- https://support.google.com/adsense/answer/81904
- https://support.google.com/adsense/answer/7299563
