# NeoDash 0.3.1 — Chrome + Neon

**The Future Is in Drive.**

A lightweight Android automotive launcher preview for landscape Android head units.

## What's included

- Chrome-framed app art with combined electric yellow, neon magenta and cyber cyan.
- DiPlay, DiAuto, Waze and Spotify dashboard shortcuts.
- Google and common Android app icon pack.
- Chrome + Neon styling for recognized apps in the dashboard, app drawer and recent-app switcher.
- Unknown apps retain their original Android icons; Standard appearance remains unchanged.

## Download the APK

Open **Actions → Build NeoDash 0.3.1 APK → Artifacts** to download the latest debug APK.

This is a debug-signed preview build, not a Play Store release. It has compiled successfully in GitHub Actions but still needs testing on a real head unit.

## Build locally

Requires JDK 17, Android SDK 34, Gradle 8.7, Python 3.12 and Pillow.

```bash
python -m pip install Pillow
python build-input/patch_chrome_neon.py .
gradle --no-daemon clean assembleDebug
```

Output: `app/build/outputs/apk/debug/app-debug.apk`

## Compatibility notes

- Minimum SDK 23 (Android 6.0), landscape-first.
- GPS, Bluetooth, Wi-Fi and physical vehicle-button support depends on permissions, Android version and head-unit firmware.
- Google app artwork is illustrative and does not modify icons inside the original apps.

## Brand palette

- Obsidian `#101116`
- Electric yellow `#F5E342`
- Neon magenta `#FF2E88`
- Cyber cyan `#00D9FF`

