# NeoLink

NeoLink is the lightweight phone handoff manager for NeoDash.

- Shows paired Bluetooth devices and lets the user assign each as iPhone/DiPlay or Android/Diauto.
- Uses the system Bluetooth ACL-connected broadcast for event-driven detection; no polling loop or permanent service.
- When an assigned phone connects, posts a notification asking the user to open the matching receiver. It does not force an unexpected foreground launch.
- Launches the selected receiver on request and can be opened by NeoDash with action `com.neodash.neolink.action.OPEN_RECEIVER` and extra `receiver=diplay|diauto`.
- Does not implement CarPlay/Android Auto, duplicate projection logic, or manage media playback.

Bluetooth names and generic pairing do not reliably reveal a phone OS, so type assignment is explicit rather than guessed. Android may suppress notifications until the user grants notification permission.

Default packages: DiPlay debug `com.shihab.diplay.hudtest`; Diauto `com.neodash.diauto`.
