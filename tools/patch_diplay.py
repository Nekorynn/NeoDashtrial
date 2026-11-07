#!/usr/bin/env python3
from pathlib import Path
import sys
root=Path(sys.argv[1])
a=root/"common/src/main/java/com/shilapi/xcertplay/DiPlayActivity.kt"
p=root/"common/src/main/java/com/shilapi/xcertplay/DiPlayPalette.kt"
if not a.is_file() or not p.is_file(): raise SystemExit("DiPlay source layout changed; patch stopped.")
s=a.read_text()
i=s.find("    private fun home(content: LinearLayout) {")
j=s.find("    // Only the category scrolls",i)
if i<0 or j<0: raise SystemExit("home() anchors changed; patch stopped.")
h='''    private fun home(content: LinearLayout) {
        val compact = isCompactLayout
        val body = column()
        val panel = card()
        homeCardTitle = label("CARPLAY", 12, ACCENT, true).apply { letterSpacing = .18f }
        panel.addView(homeCardTitle)
        status = label(getString(R.string.ready_when_you_are), 24, TEXT, true).apply { setPadding(0, dp(10), 0, dp(16)) }
        panel.addView(status)
        connectButton = button(getString(R.string.connect_phone), true) {
            if (CarPlayBackgroundSession.hasSession()) openProjection() else connect(true)
        }
        panel.addView(connectButton, matchButton(height = if (compact) 56 else 64))
        homeConnectionHint = null
        homeLastProblem = label("", 14, MUTED).apply { setPadding(0, dp(8), 0, 0) }
        panel.addView(homeLastProblem)
        panel.addView(button(getString(R.string.choose_iphone), false) { choosePhone() }, matchButton(CONTROL_GAP_DP, 48))
        disconnectButton = button(getString(R.string.disconnect), false) {
            disconnectButton?.isEnabled = false
            CarPlayBackgroundSession.stop { runOnUiThread { refreshStatus() } }
        }.apply { visibility = View.GONE }
        panel.addView(disconnectButton, matchButton(CONTROL_GAP_DP, 48))
        body.addView(panel)
        body.addView(space(14))
        body.addView(button(getString(R.string.connect_with_usb), false) { connect(false) }, matchButton(height = if (compact) 54 else 58))
        body.addView(space(10))
        body.addView(button(getString(R.string.settings), false) { page = "settings"; render() }, matchButton(height = if (compact) 54 else 58))
        setupError?.let { body.addView(label(it, 14, WARNING).apply { setPadding(0, dp(12), 0, 0) }) }
        content.addView(body)
    }

'''
a.write_text(s[:i]+h+s[j:])
s=p.read_text()
d0=s.find("        val DARK = DiPlayPalette("); l0=s.find("        val LIGHT = DiPlayPalette(",d0)
if d0<0 or l0<0: raise SystemExit("Dark/light palette anchors changed.")
dark="""        val DARK = DiPlayPalette(
            background = Color.rgb(7, 12, 19), surface = Color.rgb(17, 25, 35),
            button = Color.rgb(27, 38, 50), outline = Color.rgb(43, 57, 70),
            railSelected = Color.rgb(54, 63, 0), railSelectedOutline = Color.rgb(223, 255, 0),
            primaryText = Color.rgb(240, 245, 250), secondaryText = Color.rgb(165, 180, 194),
            accent = Color.rgb(223, 255, 0), onAccent = Color.rgb(7, 12, 19),
            accentTrack = Color.rgb(170, 205, 0), trackOff = Color.rgb(43, 57, 70),
            warning = Color.rgb(255, 65, 165), success = Color.rgb(83, 207, 255),
            danger = Color.rgb(190, 45, 45), ripple = 0x337F9F00,
            focusRing = Color.rgb(223, 255, 0), systemBar = Color.rgb(7, 12, 19),
            systemBarIconsAreDark = false, overlayBackground = Color.rgb(7, 12, 19),
            overlayPrimaryText = Color.WHITE, overlaySecondaryText = Color.rgb(165, 180, 194),
            overlayAccent = Color.rgb(223, 255, 0), overlayOnAccent = Color.rgb(7, 12, 19),
            overlayAccentTrack = Color.rgb(170, 205, 0), overlayTrackOff = Color.rgb(43, 57, 70),
            overlayDanger = Color.rgb(190, 45, 45),
        )

"""
s=s[:d0]+dark+s[l0:]
l0=s.find("        val LIGHT = DiPlayPalette("); e=s.find("\n    }\n}",l0)
if l0<0 or e<0: raise SystemExit("Light palette end changed.")
light="""        val LIGHT = DiPlayPalette(
            background = Color.rgb(242, 245, 248), surface = Color.rgb(255, 255, 255),
            button = Color.rgb(229, 235, 240), outline = Color.rgb(175, 188, 200),
            railSelected = Color.rgb(245, 250, 205), railSelectedOutline = Color.rgb(150, 180, 0),
            primaryText = Color.rgb(20, 28, 36), secondaryText = Color.rgb(85, 100, 112),
            accent = Color.rgb(130, 160, 0), onAccent = Color.WHITE,
            accentTrack = Color.rgb(130, 160, 0), trackOff = Color.rgb(175, 188, 200),
            warning = Color.rgb(190, 30, 105), success = Color.rgb(0, 130, 165),
            danger = Color.rgb(155, 48, 48), ripple = 0x33245A9C,
            focusRing = Color.rgb(130, 160, 0), systemBar = Color.rgb(242, 245, 248),
            systemBarIconsAreDark = true, overlayBackground = Color.rgb(244, 247, 250),
            overlayPrimaryText = Color.rgb(20, 28, 36), overlaySecondaryText = Color.rgb(75, 86, 101),
            overlayAccent = Color.rgb(95, 125, 0), overlayOnAccent = Color.WHITE,
            overlayAccentTrack = Color.rgb(95, 125, 0), overlayTrackOff = Color.rgb(168, 180, 190),
            overlayDanger = Color.rgb(155, 48, 48),
        )"""
p.write_text(s[:l0]+light+s[e:])
print("NeoDash home/palette patch applied; receiver transport untouched.")
