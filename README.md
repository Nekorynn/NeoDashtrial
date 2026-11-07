# NeoDash 0.3.1 — Chrome + Neon

**The Future Is in Drive.**

A lightweight Android automotive launcher preview for landscape Android head units.

## Included
- Chrome-frame art with combined electric yellow, magenta and cyan neon.
- DiPlay, DiAuto, Waze, Spotify and common Google / Android apps.
- Recognized apps use NeoDash art in dashboard shortcuts, app drawer and launcher-managed recent-app switcher.
- Unknown apps retain their original Android icons; Standard appearance remains unchanged.

## Download
Open **Actions → Build NeoDash 0.3.1 APK → Artifacts** to download the debug APK.
This is a debug-signed preview, not a Play Store release. The GitHub Actions build has compiled successfully; testing on a real head unit is still required.

## Build locally
Requires JDK 17, Android SDK 34, Gradle 8.7, Python 3.12 and Pillow.

```bash
python -m pip install Pillow
python build-input/patch_chrome_neon.py .
gradle --no-daemon clean assembleDebug
```

Output: `app/build/outputs/apk/debug/app-debug.apk`

## Compatibility
- Landscape-first, minimum SDK 23 (Android 6.0).
- GPS, Bluetooth, Wi-Fi and physical buttons depend on Android permissions, hardware and head-unit firmware.
- Google app artwork is illustrative; it does not modify icons inside Google apps.

## Palette
Obsidian `#101116` · Electric yellow `#F5E342` · Neon magenta `#FF2E88` · Cyber cyan `#00D9FF`
