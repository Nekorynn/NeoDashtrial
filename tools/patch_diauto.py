#!/usr/bin/env python3
from pathlib import Path
import sys, xml.etree.ElementTree as ET
root=Path(sys.argv[1])
gradle=root/"app/build.gradle.kts"
strings=root/"app/src/main/res/values/strings.xml"
if not gradle.is_file() or not strings.is_file(): raise SystemExit("Open Headunit source layout changed.")
g=gradle.read_text()
g=g.replace('applicationId = "com.andrerinas.headunitrevived"','applicationId = "com.neodash.diauto"')
g=g.replace('versionName = "4.0.0-beta2"','versionName = "4.0.0-beta2-neodash"')
gradle.write_text(g)
s=strings.read_text()
s=s.replace('<string name="app_name">Open Headunit</string>','<string name="app_name">Diauto</string>')
s=s.replace('Welcome to Open Headunit','Welcome to Diauto')
s=s.replace('or "Open Headunit"','or "Diauto"')
strings.write_text(s)
ns='{http://schemas.android.com/apk/res/android}'
# Resource files use unnamespaced <color name="..."> elements.
def set_colors(path, values):
    if not path.exists(): return
    tree=ET.parse(path); r=tree.getroot()
    for el in r.findall("color"):
        name=el.attrib.get("name")
        if name in values: el.text=values[name]
    ET.indent(tree, space="    ")
    tree.write(path, encoding="utf-8", xml_declaration=True)
day={
 "brand_primary":"#DFFF00","color_projection_blue":"#DFFF00",
 "home_usb":"#FF41A5","home_wifi":"#53CFFF","home_self":"#DFFF00",
 "md_primary":"#DFFF00","md_on_primary":"#07100A",
 "md_secondary_container":"#394000","md_on_secondary_container":"#F0F5FA",
 "home_hint_button":"#DFFF00","home_hint_button_focused":"#B5D600",
}
night={
 "md_primary":"#DFFF00","md_on_primary":"#07100A",
 "md_secondary_container":"#394000","md_on_secondary_container":"#F0F5FA",
 "home_usb":"#FF41A5","home_wifi":"#53CFFF","home_self":"#DFFF00",
}
set_colors(root/"app/src/main/res/values/colors.xml",day)
set_colors(root/"app/src/main/res/values-night/colors.xml",night)
print("Diauto branding applied; Android Auto protocol, transport, services and connection code unchanged.")
