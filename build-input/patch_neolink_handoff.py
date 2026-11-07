#!/usr/bin/env python3
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve()
candidates=[]
for p in root.rglob("MainActivity.java"):
    s=p.read_text(encoding="utf-8")
    if 'addTile(apps,"SETTINGS"' in s and "private void showMedia()" in s:
        candidates.append((p,s))
if not candidates:
    raise SystemExit("Could not find the expected NeoDash dashboard source anchors; no files changed.")
path,src=candidates[0]
anchor='addTile(apps,"SETTINGS","⚙",CYAN,()->showSettings());'
if 'launchNeoLink()' not in src:
    if anchor not in src: raise SystemExit("NeoDash quick-launch tile anchor changed; patch stopped.")
    src=src.replace(anchor,'addTile(apps,"MOBILE","⇄",YELLOW,()->launchNeoLink()); '+anchor,1)
    method='    private void launchNeoLink(){ Intent i=getPackageManager().getLaunchIntentForPackage("com.neodash.neolink"); if(i!=null) startActivity(i); else Toast.makeText(this,"NeoLink is not installed.",Toast.LENGTH_LONG).show(); }\n'
    marker='    private void showMedia(){'
    if marker not in src: raise SystemExit("NeoDash showMedia() anchor changed; patch stopped.")
    src=src.replace(marker,method+marker,1)
path.write_text(src,encoding="utf-8")

manifests=list(root.rglob("AndroidManifest.xml"))
patched=False
for p in manifests:
    s=p.read_text(encoding="utf-8")
    if 'android:label="NeoDash"' in s and "com.neodash.neolink" not in s:
        s=s.replace('<manifest xmlns:android="http://schemas.android.com/apk/res/android">','<manifest xmlns:android="http://schemas.android.com/apk/res/android">\n    <queries><package android:name="com.neodash.neolink" /></queries>',1)
        p.write_text(s,encoding="utf-8")
        patched=True
        break
if not patched:
    # Package visibility may already be declared by the upstream app; don't alter unrelated manifests.
    print("NeoDash package visibility already present or manifest label differs; continuing.")
print("Added MOBILE tile to launch NeoLink in",path)
