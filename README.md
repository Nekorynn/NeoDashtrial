# NeoLink
Lightweight receiver launcher for the NeoDash suite.

NeoLink lists already-paired Bluetooth devices and lets the user assign each device to DiPlay (iPhone) or Diauto (Android). It launches the selected receiver and does not run a permanent polling service, duplicate projection logic, or manage media playback. DiPlay and Diauto own their connection sessions.

Bluetooth names/pairing alone do not reliably reveal a phone's operating system, so device type is explicitly assigned by the user rather than guessed.

NeoDash can open NeoLink with action `com.neodash.neolink.action.OPEN_RECEIVER` and extra `receiver=diplay|diauto`.

Default receiver packages: DiPlay debug `com.shihab.diplay.hudtest`; Diauto `com.neodash.diauto`.
