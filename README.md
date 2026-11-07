# NeoDash 0.3.1 — Chrome + Neon

**The Future Is in Drive.**

A lightweight Android automotive launcher preview for landscape Android head units.

## Included in this preview

- Chrome-frame artwork with combined electric yellow, magenta and cyan neon.
- DiPlay, DiAuto, Waze and Spotify shortcuts.
- Google and commonly used Android apps, including Google, Chrome, Maps, YouTube, Gmail, Drive, Photos, Calendar, Meet, Docs, Sheets, Slides, Keep, Translate, Play Store, Play Games, YouTube Music, Assistant, Files, Wallet, Contacts, Phone and Messages.
- Known apps receive NeoDash artwork in the dashboard, app drawer and launcher-managed recent-app switcher.
- Unknown apps keep their original Android icons. Standard appearance remains unchanged.

## Download

Go to **Actions → Build NeoDash 0.3.1 APK → Artifacts** and download the latest debug APK.

This is a debug-signed preview, not a Play Store release. The GitHub Actions build has passed. Real head-unit testing is still required.

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
- GPS, Bluetooth, Wi-Fi and physical vehicle button support depend on Android permissions, device firmware and hardware.
- Google artwork is illustrative; it does not replace or modify icons inside Google apps.

## Brand colors

- Obsidian `#101116`
- Electric yellow `#F5E342`
- Neon magenta `#FF2E88`
- Cyber cyan `#00D9FF`

