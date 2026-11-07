# DiPlay · NeoDash Edition

This branch builds the upstream DiPlay CarPlay receiver with a compact NeoDash-style home screen: graphite surfaces, electric-yellow primary actions, cyan/magenta status accents and reduced text.

The patch changes only `DiPlayActivity.home()` and the semantic palette. It keeps upstream wired/wireless connection, CarPlay projection, audio, phone selection, settings and session code.

GitHub Actions fetches upstream DiPlay at pinned commit `615b32ce0b40cd0b99ce94ba23a512001553684f`, applies the patch, runs tests/lint and builds `:mobile:assembleDebug`.

**Standalone connection limitation:** the CI debug APK is source-only and has no accessory identity. Upstream's build guide requires external `offline-mfi/identity.pk8` and `certificate.p7b` assets for standalone CarPlay. These are not committed or extracted from another APK. A valid, authorized local identity must be supplied before producing a standalone iPhone-connecting APK.

Upstream: https://github.com/shihabal3amri/DiPlay
