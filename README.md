# NeoDash 0.3.1 — Chrome + Neon

**The Future Is in Drive.**

A lightweight Android automotive launcher preview for landscape Android head units.

## Included

- Chrome-frame art with combined electric yellow, neon magenta and cyber cyan.
- DiPlay, DiAuto, Waze and Spotify.
- Google and popular Android apps, including Google, Chrome, Maps, YouTube, Gmail, Drive, Photos, Calendar, Meet, Docs, Sheets, Slides, Keep, Translate, Play Store, Play Games, YouTube Music, Assistant, Files, Wallet, Contacts, Phone and Messages.
- Recognized apps use NeoDash art in the dashboard, app drawer and launcher-managed recent-app switcher.
- Unknown apps keep their original icons. Standard appearance remains unchanged.

## Download

Go to **Actions → Build NeoDash 0.3.1 APK → Artifacts** and download the latest debug APK.

This is a debug-signed preview, not a Play Store release. The automated build has completed successfully. Real head-unit testing is still required.

## Build locally

Requires JDK 17, Android SDK 34, Gradle 8.7, Python 3.12 and Pillow.

```bash
python -m pip install Pillow
python build-input/patch_chrome_neon.py .
gradle --no-daemon clean assembleDebug
```

APK output: `app/build/outputs/apk/debug/app-debug.apk`

## Compatibility

- Landscape-first, minimum SDK 23 (Android 6.0).
- GPS, Bluetooth, Wi-Fi and physical buttons depend on Android permissions, device firmware and head-unit hardware.
- Google app artwork is illustrative; it does not alter icons inside the Google apps.

## Brand palette

- Obsidian `#101116`
- Electric yellow `#F5E342`
- Neon magenta `#FF2E88`
- Cyber cyan `#00D9FF`
