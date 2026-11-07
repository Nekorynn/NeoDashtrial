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

The service sends a complete snapshot immediately after binding and subsequent events when state changes. Consumers should bind once and react to events, not poll.

State schema v1:

```json
{
  "schema_version": 1,
  "manager": "neolink",
  "service_state": "running",
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

## Migration safety

The existing NeoDash 0.3.2 build pipeline currently applies its dashboard patch to a bundled source archive. The source archive is not expanded in the repository, so removing its old receiver-selection/launch code safely requires inspecting the expanded source in CI first. Until that inspection and the Messenger client integration are verified, the legacy launch path is retained rather than risking a broken dashboard or silently removing working functionality.

This branch adds the independent NeoLink application and service contract as the first migration stage. It does not yet claim end-to-end phone projection or automatic receiver launching. The next stage must:
1. Integrate a NeoDash Messenger client and visible connection state.
2. Verify cold boot, warm boot, NeoLink unavailable, service restart and reconnect.
3. Move receiver selection and launch ownership to NeoLink.
4. Remove NeoDash's legacy receiver-launch code only after the above checks pass.

## Android platform constraints

- Bluetooth pairing is not proof of an active projection session.
- Android versions/OEMs may require user approval for Bluetooth/Wi-Fi controls, background activity launches and boot startup.
- The app displays Manila time (`Asia/Manila`) without changing the Android system clock. Changing system time requires privileged/device-owner access.
- USB vendor IDs can identify some Apple devices, but a generic USB/Bluetooth connection does not always identify the phone OS. Ambiguous devices remain `unknown` until a supported handshake or explicit user configuration is available.
- Wi-Fi connection state alone is not phone discovery. A supported receiver handshake is required before classifying a Wi-Fi peer as a projection session.
