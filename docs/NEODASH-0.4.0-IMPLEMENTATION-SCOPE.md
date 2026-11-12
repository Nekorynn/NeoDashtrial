# NeoDash 0.4.0 — Implementation Scope

Target device: Android 8.1 Go (API 27), 1024×600 head unit.

Working branch: `architecture/0.4.0-neolink-separation`

This document records the agreed scope for the next architecture preview. It does not authorize changes to the private NeoDash repository, DiPlay, OpenHeadunit, or stable `main`.

## Product architecture

- NeoDash and NeoLink remain separate applications and APKs.
- NeoDash is a launcher and dashboard, not an application container.
- External apps own their functions. NeoDash launches them and displays information exposed through supported Android APIs.
- Preserve existing working features and avoid unrelated rewrites.
- Do not merge this branch into `main` without explicit approval.

## Navigation

- Remove the OpenStreetMap implementation, OSM tiles, embedded WebView map, map SDKs, static map images, and simulated map previews from NeoDash.
- Do not load or initialize a navigation app or map during normal Home startup.
- The bottom Map button launches the user's selected installed navigation app (initial targets: Google Maps and Waze) using supported Android intents.
- On Android 8.1, use full-screen external navigation. General-purpose embedding of another app's live UI into NeoDash is not a supported implementation path on this device.
- The physical Home button returns to NeoDash's normal Home layout.
- Remember which navigation app was opened and update navigation state when supported detection is available.
- Distinguish "navigation app opened/foreground" from "route actively navigating." Do not claim route-active status without reliable evidence.
- After returning Home, show the normal Home layout; optionally show a navigation status indicator only when the detected state is supported and reliable.
- Preserve music playback and dashboard state where Android permits.

## Media and external music apps

- NeoDash does not decode or play audio and does not implement codecs, playlists, a music library, or a separate folder browser.
- The selected external player handles folder browsing, song selection, playlists, decoding, and playback.
- Launch the selected/last-used player from the Music shortcut; a maximize control opens the active player full-screen.
- Use Android MediaSession/MediaController APIs and Notification Access to display available metadata and send supported transport commands.
- Display available album artwork, title, artist, album/player name, playback state and progress.
- Provide Previous, Play/Pause and Next controls; disable or hide controls the active session does not support.
- Detect/switch to another active player when possible.
- Initial compatibility targets: Spotify, a folder-based local music player, Bluetooth media sessions, and other compatible Android players.
- Evaluate local player options (including SicMu Player and SicMu Neo) for Android 8.1, folder navigation, USB/microSD/internal storage, artwork and MediaSession compatibility. Do not bundle or mandate a player before verification.

## Permissions Center and first-run setup

- Provide one central Permissions/Device Setup screen.
- Present all permissions relevant to features actually included in this release, with clear purpose and status.
- Request compatible runtime permissions together where Android allows.
- Open Android system settings for special access such as Notification Access; re-check grant state when returning.
- Show Granted, Action Required and Not Applicable states; provide retry/open-settings actions.
- Require permissions needed by implemented core features before entering the dashboard if that remains the user's chosen policy.
- Remember completed setup and avoid repeated prompts.
- Do not request hypothetical future microphone/camera permissions unless those features are implemented.
- Respect Android 8.1 permission rules; do not request Android 12+ Bluetooth runtime permissions on API 27.
- NeoLink owns Bluetooth discovery/phone-detection permissions and services; NeoDash owns its own location/media-related permissions. Avoid duplicate ownership.

## NeoLink

- Separate lightweight companion app for wired/wireless phone detection and receiver selection.
- NeoLink handles Bluetooth discovery, connection state, receiver choice and receiver launching.
- Support DiPlay for iPhone/CarPlay and OpenHeadunit for Android/Android Auto without modifying those projects.
- Ask for receiver choice on first connection, remember it, and allow later changes.
- Report connection status to NeoDash.
- Avoid duplicate services and unnecessary background/battery use.

## Dashboard and launcher

- Keep the normal Home layout as the default startup screen. No map app is loaded until the bottom Map button is pressed.
- Preserve the existing dual-pane design intent and right-side clock/media panel where compatible with the actual app-launching architecture. Do not claim a live external map is embedded in the left pane on Android 8.1.
- Keep the physical Home button as the return mechanism; no floating Home overlay.
- Fix shortcut artwork so icons fill their tiles without unwanted padding; preserve readable labels and standard app icon colours.
- Preserve customizable shortcuts (rearrange, remove, replace), grid app drawer and page navigation.
- Keep app shortcuts resilient to apps being uninstalled or unavailable.

## Clock, device status, startup and appearance

Preserve the previously selected requirements where present in the source:
- Configurable boot startup; GMT+8 default; display system clock immediately; retry time synchronization quietly and show sync status.
- GPS/location, Wi-Fi, Bluetooth and phone-connection status.
- Keep screen awake while the car is running where supported.
- Existing visual direction: pure black, blue-chrome/neon-blue primary, magenta/cyan/yellow accents with more blue and less yellow; readable 7-inch typography; animated neon clock; configurable sound effects; short logo boot animation; simple and advanced settings.

## Build and verification

1. Repair the existing architecture-branch build/patch failure before feature work.
2. Make patch scripts deterministic and fail clearly; remove duplicate/ambiguous string replacements.
3. Verify no OSM/WebView map code remains in generated NeoDash source or APK.
4. Verify no map is initialized on Home startup.
5. Verify Map button launches the configured app full-screen and physical Home restores normal Home.
6. Verify permission onboarding and Notification Access on API 27.
7. Verify MediaSession metadata/artwork/transport controls with actual supported players.
8. Verify NeoLink Bluetooth ownership, connection reporting and receiver choice.
9. Build both APKs, inspect logs/artifacts, and test compatibility before calling the preview successful.
10. Keep stable `main` untouched until the user approves a merge.

## Decisions still awaiting user selection

- Default music player policy: remember last active / fixed default / ask each time.
- Music shortcut policy: last-used / chooser / fixed default.
- Permission gate: require all permissions needed by implemented features / allow dashboard with warnings.
- Home left area: shortcuts / system information and shortcuts / customizable widgets and shortcuts.
- Startup: automatic by default / configurable by user.
- Navigation shortcuts: both Google Maps and Waze / selected app only / customizable.
- Initial media targets: Spotify, local player, Bluetooth media, other compatible players (confirm final subset).
