# Current browser release — POT BREAKER RE v1.0.89

The current web game is the Korean-language Cloudflare Worker release at [potbreaker.com](https://potbreaker.com/). It runs the Python game engine in the browser with Pyodide and Canvas rendering.

- Search discovery: `/robots.txt`, `/sitemap.xml`, canonical page metadata, and accessible game guidance.
- Indexable pages: `/`, `/about`, and `/privacy`; `/game.py` is marked `noindex`.
- AdSense: publisher verification and `/ads.txt` are generated only when a valid `ADSENSE_PUBLISHER_ID` is configured. Ad script loading is gated by explicit flags and limited to `/about`; the game screen has no ad script.
- Setup requirements: [docs/SEO_ADSENSE.md](docs/SEO_ADSENSE.md).
- Release notes: [POT_BREAKER_RE_v1.0.89_CHANGELOG.md](POT_BREAKER_RE_v1.0.89_CHANGELOG.md).
- The Android WebView v0.16.0 package below is a separate legacy app and does not automatically receive web release updates.

---

# POT BREAKER Android v0.16.0

POT BREAKER 브라우저 게임을 **안드로이드 앱으로 설치할 수 있도록 WebView로 패키징한 프로젝트**입니다.

현재 정규 버전은 **v0.16.0**입니다.

## 프로젝트 정보

- 앱 이름: `POT BREAKER`
- 패키지명: `com.potbreaker.game`
- 버전명: `0.16.0`
- 버전 코드: `1600`
- 최소 Android SDK: 23
- Target / Compile SDK: 35
- 화면 방향: 가로모드
- 게임 본체: `app/src/main/assets/index.html`
- 인터넷 연결: 기본 플레이에는 필요 없음
- 진동: Android 네이티브 진동 브리지 사용

## 저장소를 클론하는 방법

```bash
git clone https://github.com/rhaxod7784-png/potbreaker.git
cd potbreaker
```

기본 브랜치인 `main`에 Android Studio 프로젝트 전체가 들어 있으므로 별도 브랜치 전환 없이 바로 열 수 있습니다.

## Android Studio에서 실행

1. Android Studio 실행
2. **Open** 선택
3. 클론한 `potbreaker` 폴더 선택
4. Gradle Sync 완료까지 대기
5. 에뮬레이터 또는 Android 기기 연결
6. 상단의 **Run ▶** 실행

## APK 만들기

Android Studio에서:

**Build → Build APK(s)**

Debug APK 경로:

```text
app/build/outputs/apk/debug/app-debug.apk
```

또는 Windows PowerShell에서:

```powershell
./build-apk.ps1
```

## 주요 폴더

```text
app/
├─ build.gradle
└─ src/main/
   ├─ AndroidManifest.xml
   ├─ assets/
   │  └─ index.html        # POT BREAKER 게임 본체
   ├─ java/com/potbreaker/game/
   │  └─ MainActivity.java # Android WebView 및 네이티브 연동
   └─ res/
      ├─ drawable/
      └─ values/
```

## 승리 기록 저장

Android 앱에서 생성된 승리 기록은 WebView의 `localStorage`에 저장됩니다.

브라우저에서 플레이한 기존 WIN 기록과 Android 앱의 WIN 기록은 서로 다른 저장소를 사용하므로 자동으로 이전되지 않습니다.

앱 데이터 삭제 또는 앱 제거 시 Android 앱 내부의 기록도 삭제될 수 있습니다.

## 버전 관리 기준

이 프로젝트는 `vMAJOR.MINOR.PATCH` 형식을 사용합니다.

- **MAJOR**: 기존 호환성을 깨는 전면 변경
- **MINOR**: 새 기능·새 시스템 추가
- **PATCH**: 버그 수정, 감도·수치·UI·BGM·밸런스 조정

모든 릴리스는 `CHANGELOG.md`에 다음 항목을 기록합니다.

- Release type
- Date
- Changed
- Fixed
- Code
- Reason
- Compatibility

## 현재 개발 기준

- 브라우저 게임 기준선: `v0.15.0`
- Android 설치 패키징 추가: `v0.16.0`

## 브라우저 게임 v1.0.25

- 웹 게임 소스: `web/index.html`, `web/game.py`
- Worker 생성: `python scripts/build_worker.py`
- 배포 설정: `wrangler.toml`
- Cloudflare D1 초기 스키마: `cloudflare/migrations/0001_init.sql`
- D1 바인딩 이름: `POTBREAKER_DB`

노멀은 기존 밸런스, 하드는 기묘의 화분 1개, 베리 하드는 기묘의 화분 1개와 크다 체력 10으로 플레이합니다. 익명 방문 및 게임 결과 이벤트를 D1에 기록하며, 승리로 끝난 게임만 닉네임·난이도·클리어 시간을 랭킹에 등록합니다. 랭킹은 베리 하드, 하드, 노멀 순으로 표시하고 난이도 안에서는 빠른 기록이 먼저 나옵니다.


Worker build status is generated from `scripts/build_worker.py` on each push to this branch.
