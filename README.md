# NeoDash + NeoLink — Architecture Preview 0.4.0

**One public repository. Two independent Android applications and APKs.**

This branch implements the first architecture-separation stage approved for NeoDash.

## Projects and APKs

- **NeoDash 0.4.0** — dashboard and boot starter. It retains the existing dashboard, map, media, clock and system-status experience. CI expands the retained source archive and applies the 0.3.2 baseline plus the architecture patch.
- **NeoLink 0.1.0** — a separate Android project in `NeoLink/`, with its own package ID (`com.neodash.neolink`) and independently built APK.
- **DiPlay** — external iPhone CarPlay receiver; not included or modified.
- **OpenHeadunit** — external Android Auto receiver; not included or modified.

The private NeoDash repository is not touched. DiPlay and OpenHeadunit are not touched.

## Implemented in this architecture preview

### NeoDash
- Keeps dashboard, boot UI, map, media, clock/date, GPS permission and system-status responsibilities.
- Keeps Bluetooth/Wi-Fi system status and time synchronization; no phone discovery or USB phone monitoring.
- Removes receiver-app selection from its setup and Settings screens.
- Removes the old dashboard-side receiver-launch method.
- Opens NeoLink Settings from the phone-connection shortcut and Settings row.
- Binds to NeoLink's protected Messenger service while active and receives pushed state events. It does not poll.
- Continues to work if NeoLink is not installed or unavailable.

### NeoLink
- Separate app and receiver-selection screen; saved iOS and Android receiver package choices.
- Foreground connection-manager service with a boot-start attempt, subject to Android permission and OEM background-start rules.
- Bluetooth ACL event monitoring.
- USB attach/detach monitoring; Apple USB vendor ID identifies some iOS devices, while ambiguous devices remain unknown.
- Event-driven Wi-Fi network availability monitoring. This is network status, not proof that a phone is connected.
- Permission-protected Messenger service with versioned JSON state snapshots and pushed event delivery.

## Not yet implemented / not yet verified

- Reliable Android phone OS identification across different USB/Bluetooth/Wi-Fi devices.
- A validated phone-to-receiver handshake for wireless projection.
- Automatic launching of the configured receiver after a reliable platform/session signal.
- Multiple-phone arbitration, active-session locking, switch/disconnect confirmation, reconnect and timeout policy.
- Physical cold-boot, warm-boot, disconnect/reconnect and multi-phone tests on the target head unit.

These limitations are deliberate: Bluetooth pairing or a generic Wi-Fi network must not be mistaken for an active projection session, and the system must not launch the wrong receiver. The architecture now has one owner for receiver selection and one status interface; automatic receiver launch will be added only when the device/session signal is reliable.

## Build

GitHub Actions builds two independent debug APKs on this branch:
- `NeoDash-0.4.0-Architecture-Preview-debug.apk`
- `NeoLink-0.1.0-Architecture-Preview-debug.apk`

Open the [Actions page](https://github.com/Nekorynn/NeoDashtrial/actions) and select the latest successful run on this branch. Download both APK artifacts from that run. Debug-signed previews are for testing, not Play Store releases.

See [ARCHITECTURE.md](ARCHITECTURE.md) for service ownership, message IDs, state schema, migration order and Android platform constraints.
