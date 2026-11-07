# NeoDash + NeoLink — Architecture Preview 0.4.0

**One public repository. Two independent Android applications.**

This branch introduces the separation of responsibilities approved for NeoDash.

## Projects and APKs

- **NeoDash** — dashboard and boot starter. The existing 0.3.2 dashboard source is currently assembled from the retained source archive and patch pipeline in CI.
- **NeoLink** — a separate Android project in `NeoLink/`, with its own package ID (`com.neodash.neolink`) and independently built APK.
- **DiPlay** — external iPhone CarPlay receiver; not included or modified.
- **OpenHeadunit** — external Android Auto receiver; not included or modified.

The two APKs are built separately by GitHub Actions. NeoLink is currently an architecture preview, not yet an end-to-end projection manager.

## NeoLink preview currently implements

- Separate app and receiver-selection screen.
- Saved iOS and Android receiver package choices.
- Foreground connection-manager service with a boot-start attempt, subject to Android permission and OEM background-start rules.
- Bluetooth ACL and USB attach/detach event capture.
- A permission-protected Messenger service contract with versioned JSON state snapshots and event delivery.
- Conservative classification: Bluetooth is shown as a paired candidate, not as an active projection session. Apple USB vendor ID may identify some iPhones; ambiguous devices remain unknown.

## Not yet implemented / not yet verified

- NeoDash's Messenger client and connection-status UI.
- Full Wi-Fi peer discovery and receiver-specific session handshakes.
- Automatic receiver launching, reconnect/timeout policy, multi-phone arbitration and active-session lock.
- Removing the legacy receiver-selection/launch path from the existing NeoDash 0.3.2 source.
- Physical testing on the target head unit.

These items are intentionally staged. The existing NeoDash receiver code remains in place until the new service interface is integrated and verified, avoiding a regression where neither app can launch the receiver.

## Build

GitHub Actions builds:
- `NeoDash-0.3.2-Cyberpunk-Dashboard-debug.apk`
- `NeoLink-0.1.0-Architecture-Preview-debug.apk`

Open the [Actions page](https://github.com/Nekorynn/NeoDashtrial/actions) and select the latest run on this branch. Artifacts are debug-signed previews for testing, not Play Store releases.

See [ARCHITECTURE.md](ARCHITECTURE.md) for service ownership, message IDs, state schema, migration order and Android platform constraints.
