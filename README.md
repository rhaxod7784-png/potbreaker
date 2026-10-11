# POT BREAKER Android / Web v0.16.1

POT BREAKER 브라우저 게임을 **안드로이드 앱으로 설치할 수 있도록 WebView로 패키징한 프로젝트**입니다.

현재 정규 버전은 **v0.16.1**입니다.

동일한 게임 HTML을 Cloudflare Workers 정적 사이트로도 배포할 수 있습니다.

## 웹 실행 및 Cloudflare 배포

Node.js 22 이상을 설치한 뒤 저장소 루트에서 실행합니다.

```bash
npm ci
npm test
npm run dev
```

터미널에 표시되는 로컬 주소를 브라우저에서 엽니다.

Cloudflare Workers의 Git 저장소 연결 설정:

- 저장소: `rhaxod7784-png/potbreaker`
- 브랜치: 이 패치가 들어 있는 브랜치
- 루트 디렉터리: 저장소 루트
- 빌드 명령: `npm ci && npm test`
- 배포 명령: `npm run deploy`
- Worker 이름: `potbreaker` (다른 이름을 쓰면 `wrangler.jsonc`의 `name`도 변경)

CLI에서 직접 배포할 경우:

```bash
npx wrangler login
npm run check:deploy
npm run deploy
```

Cloudflare Pages를 사용하는 경우에는 프레임워크를 None으로 두고,
빌드 명령은 `npm ci && npm test`, 출력 디렉터리는
`app/src/main/assets`로 설정합니다.

웹 배포는 `app/src/main/assets`만 공개하므로 Android 소스나 보관 ZIP은 포함되지 않습니다.
게임 HTML을 별도 복사하지 않아 Android와 웹의 게임 코드가 동일합니다.

## 백그라운드 오디오

- Android 홈 이동·앱 전환·화면 잠금 시 네이티브 수명주기에서 게임에 중단을 전달합니다.
- 웹에서는 탭 숨김과 페이지 이탈 시 BGM 타이머와 WebAudio 컨텍스트를 종료합니다.
- 돌아오면 이전에 재생하던 BGM을 새 컨텍스트에서 재개합니다. 브라우저가 자동 재생을 막으면 게임 화면을 터치합니다.
- 백그라운드에서는 게임 업데이트도 멈춥니다.

기기 확인 항목: BGM 재생 후 홈 이동, 화면 잠금, 최근 앱 전환, 뒤로 종료,
웹 탭 전환을 각각 수행하여 소리가 멈추는지 확인하고, 복귀 후 BGM이 중복되지 않는지 확인합니다.

## 프로젝트 정보

- 앱 이름: `POT BREAKER`
- 패키지명: `com.potbreaker.game`
- 버전명: `0.16.1`
- 버전 코드: `1601`
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
- 백그라운드 오디오 수정 및 Cloudflare 웹 배포 설정: `v0.16.1`

