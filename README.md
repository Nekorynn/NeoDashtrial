# NeoDash 0.3.2 — Blue Chrome Cyberpunk

**The Future Is in Drive.**

A lightweight Android automotive launcher preview for landscape Android phones and head units.

## Download

[Download NeoDash 0.3.2 APK](https://github.com/Nekorynn/NeoDashtrial/releases/download/v0.3.2/NeoDash-0.3.2-Cyberpunk-Dashboard-debug.apk)

[View all releases](https://github.com/Nekorynn/NeoDashtrial/releases)

This is a debug-signed preview APK, not a Play Store release. The app uses a separate debug package suffix so it can be installed alongside the previous NeoDash preview builds.

## What's new in 0.3.2

- First-launch setup blocks entry to the dashboard until the selected core permissions are granted: Location/GPS, Nearby Devices/Bluetooth on Android 12+, and Notifications on Android 13+.
- Setup asks the user to choose installed defaults for the map app, iOS receiver app, Android Auto receiver app and local media player.
- Settings allows all app defaults and the last-used media source to be changed later.
- Home dashboard is split into two panes: clock and media on the left; four app shortcuts on the right with a permanent next-page arrow.
- Media sources: Local, Bluetooth and Spotify. NeoDash remembers the last source selected. Transport buttons send media-key events to the active Android media session.
- Map mode displays an embedded OpenStreetMap pane on the left and clock/media on the right. The selected installed map app opens for full navigation.
- Bottom navigation uses Mobile instead of CarPlay. A valid receiver-session event launches the configured DiPlay or DiAuto app without a confirmation prompt.
- Blue-chrome typography and graphite panels are primary, with restrained yellow, magenta and cyan accents.

## Map embedding note

Android does not provide a standard public API for embedding arbitrary third-party map app screens inside another app's panel. The embedded map surface therefore uses OpenStreetMap; the installed map app selected in setup is used when opening full navigation.

## Compatibility and permissions

- Landscape-first; minimum SDK 24 (Android 7.0).
- The setup wizard requests precise location, Nearby Devices permissions where applicable, and notifications where applicable.
- The Mobile auto-launch feature relies on a valid receiver-session signal from the selected DiPlay/DiAuto receiver. A generic Bluetooth pairing by itself does not identify a phone OS reliably.
- Bluetooth audio output is controlled by Android; the Bluetooth media source uses the selected media player and current system audio route.

## Build locally

Requires JDK 17, Android SDK 34, Gradle 8.7, Python 3.12 and Pillow.

The GitHub Actions workflow extracts the bundled NeoDash source archive, applies the Chrome + Neon icon pack, applies the 0.3.2 dashboard/setup patch and builds the assembleDebug variant.

## Palette

Graphite #070C13 · Blue chrome #199BEE · Ice cyan #53CFFF · Secondary accents: electric yellow, neon magenta and cyan.
