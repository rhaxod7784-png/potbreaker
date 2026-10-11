# POT BREAKER CHANGELOG

## v0.16.0 — Android installable packaging
Release type: MINOR  
Date: 2026-08-19

### Changed
- Added an installable Android application target around the existing browser game.
- Bundled the game HTML inside the APK as an offline asset.
- Locked the native Activity to sensor landscape and immersive fullscreen.
- Added a native Android vibration bridge for character-hit vibration.
- Set the packaged game display version to `v0.16.0`.

### Fixed
- Removed dependence on browser address bars and browser-level landscape behavior when playing the Android package.
- Added a native vibration fallback for Android WebView environments where `navigator.vibrate()` is unavailable.

### Code
- `app/src/main/java/com/potbreaker/game/MainActivity.java`
- `app/src/main/AndroidManifest.xml`
- `app/src/main/assets/index.html`
- `app/build.gradle`
- Added `appVibrate(pattern)` compatibility wrapper in packaged HTML.

### Reason
- Make POT BREAKER directly installable and playable as an Android app instead of requiring a browser tab.

### Compatibility
- Core game rules are inherited from normalized `v0.15.0`.
- Android app storage is isolated from browser storage; existing browser WIN records do not migrate automatically.
- WIN records created inside the Android app persist in its WebView storage until app data is cleared or the app is uninstalled.
