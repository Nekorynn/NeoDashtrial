# Diauto · Open Headunit base

Diauto is the Android Auto receiver build for the NeoDash suite. It is based on the maintained Open Headunit project, with a separate application ID and NeoDash-inspired yellow/cyan/magenta accents plus Diauto app naming.

The patch does not replace or rewrite the Android Auto protocol, USB/Wi-Fi transports, audio pipeline, services, connection management or projection renderer. Those remain upstream.

GitHub Actions fetches Open Headunit at pinned commit `ae74788d8312dd7a735775ddc21370f1741a7af1`, applies `tools/patch_diauto.py`, runs the unit tests and builds the GitHub debug flavor.

Upstream: https://github.com/andreknieriem/open-headunit
License: AGPL-3.0. Keep all upstream notices and provide corresponding source when distributing modified builds.

Compatibility note: Open Headunit documents that Android Auto 17.4+ can block legacy wireless startup triggers. Use supported Native Mode, USB, dongle or Headunit Server paths as appropriate; NeoLink cannot bypass Android Auto restrictions.
