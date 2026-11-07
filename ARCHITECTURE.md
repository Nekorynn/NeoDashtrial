# NeoDash / NeoLink Architecture

## Repository layout

This repository is a monorepo containing independent Android applications:

- NeoDash source — currently retained in `build-input/NeoDash-Sleek-v0.3.0-GitHub-Build-Source.zip` and expanded into a temporary Gradle project by CI.
- `NeoLink/` — independent lightweight connection-manager application (receiver launch orchestration is a later migration stage).
- `build-input/` — retained NeoDash source archive and deterministic patch scripts.
- `.github/workflows/` — builds each APK independently.

DiPlay and OpenHeadunit are external receiver applications. They are not copied, forked, bundled, or modified here.

## Responsibility ownership

| Capability | Owner | Notes |
|---|---|---|
| Dashboard, clock, widgets, map and media UI | NeoDash | Remains usable if NeoLink is unavailable |
| Dashboard boot experience | NeoDash | Android/OEM boot restrictions still apply |
| Bluetooth/Wi-Fi/USB phone connection events | NeoLink | One connection manager only |
| Device platform identification | NeoLink | Unknown is a valid state; Bluetooth pairing alone is not OS identification |
| Receiver app selection and saved defaults | NeoLink | DiPlay-compatible and OpenHeadunit-compatible apps are user selected |
| Receiver launch / reconnect / active-session lifecycle | NeoLink | Launch request is not proof of projection |
| CarPlay rendering | DiPlay | External app; no duplicated receiver implementation |
| Android Auto rendering | OpenHeadunit | External app; no duplicated receiver implementation |
| Connection status display | NeoDash | Consumes NeoLink state; must not discover or launch receivers |

## NeoLink service contract v1

NeoLink exposes an explicit, permission-protected Android bound service:

- Component: `com.neodash.neolink/.service.NeoLinkService`
- Action: `com.neodash.neolink.action.BIND`
- Permission: `com.neodash.neolink.permission.BIND_SERVICE` (signature)
- Transport: Android `Messenger` with `Bundle` messages.
- `MSG_GET_STATE = 1`: request a complete state snapshot.
- `MSG_STATE = 2`: full state snapshot reply.
- `MSG_EVENT = 3`: state-change event.
- `MSG_REGISTER_CLIENT = 4`: subscribe to pushed state events.
- `MSG_UNREGISTER_CLIENT = 5`: remove the client subscription.
- Bundle field `state_json`: versioned JSON object.

The service sends a complete snapshot immediately after client registration and subsequent events when state changes, including Bluetooth, USB and Wi-Fi network availability changes. Consumers should bind once and react to events, not poll. Wi-Fi network availability is not proof of a phone or projection session.

State schema v1:

```json
{
  "schema_version": 1,
  "manager": "neolink",
  "service_state": "running",
  "wifi_network_available": false,
  "connection": {
    "transport": "none|bluetooth|usb|wifi|unknown",
    "device_name": null,
    "platform": "unknown|ios|android",
    "link_state": "disconnected|paired_candidate|connected|session_active|reconnecting",
    "projection_state": "unknown|launch_requested|active|ended"
  },
  "receiver": {
    "ios_package": null,
    "android_package": null,
    "selected_package": null
  },
  "last_event": "service_started",
  "updated_at_epoch_ms": 0
}
```

A Bluetooth ACL connection is only a `paired_candidate`; it must never be represented as an active CarPlay/Android Auto session. A receiver launch is `launch_requested`; only a receiver-provided callback/API can establish `active`.

## Migration status and safety

The source archive is expanded in CI, where the architecture patch now:
1. Renames the old NeoDash connection service to a system-status/time-sync service.
2. Removes USB phone events, Bluetooth connection-state events and receiver-session handling from that NeoDash service, while retaining general Bluetooth/Wi-Fi/GPS/time status.
3. Removes receiver-app selection and automatic receiver-launch methods from NeoDash.
4. Adds a NeoDash Messenger client that binds to NeoLink, subscribes to pushed state events and displays NeoLink status in the system-status panel.
5. Adds a NeoLink settings entry point from the dashboard.

The NeoDash and NeoLink APKs are built independently. The old 0.3.2 baseline on `main` is not modified by this architecture branch. The current implementation does not claim end-to-end phone projection or automatic receiver launching.

Next stage:
1. Add reliable phone platform/session identification for USB, Bluetooth and wireless projection.
2. Implement receiver launching and active-session reporting in NeoLink only after a trusted platform/session signal is available.
3. Add multiple-phone arbitration, active-session lock, switch/disconnect confirmation, reconnect and timeout handling.
4. Verify cold boot, warm boot, NeoLink unavailable, service restart, disconnect/reconnect and multiple-phone scenarios on the target head unit.

## Android platform constraints

- Bluetooth pairing is not proof of an active projection session.
- Android versions/OEMs may require user approval for Bluetooth/Wi-Fi controls, background activity launches and boot startup.
- The app displays Manila time (`Asia/Manila`) without changing the Android system clock. Changing system time requires privileged/device-owner access.
- USB vendor IDs can identify some Apple devices, but a generic USB/Bluetooth connection does not always identify the phone OS. Ambiguous devices remain `unknown` until a supported handshake or explicit user configuration is available.
- Wi-Fi connection state alone is not phone discovery. A supported receiver handshake is required before classifying a Wi-Fi peer as a projection session.
