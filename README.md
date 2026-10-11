# POT BREAKER Android v0.16.0

Android WebView package for the current POT BREAKER game.

## App settings
- App name: POT BREAKER
- Package: `com.potbreaker.game`
- Version name: `0.16.0`
- Version code: `1600`
- Min SDK: 23
- Target / Compile SDK: 35
- Orientation: sensor landscape
- Network permission: none required
- Game asset: `app/src/main/assets/index.html`

## Build on Windows
The easiest path is Android Studio:
1. Open this folder as a project.
2. Let Android Studio complete Gradle/SDK sync.
3. Select **Build > Build APK(s)**.
4. Debug APK is created under `app/build/outputs/apk/debug/app-debug.apk`.

Or run `build-apk.ps1` from PowerShell. The script can download Gradle and Android command-line SDK components if they are missing; Java 17+ or Android Studio's bundled JBR is still required.

## Install
Transfer the resulting APK to the Android phone and open it. Android may ask you to allow installation from the app/file manager used to open the APK.

## Storage note
The Android WebView has its own local storage. Browser-play WIN records will not automatically transfer into the installed app.
