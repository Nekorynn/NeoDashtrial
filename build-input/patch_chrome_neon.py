#!/usr/bin/env python3
"""Patch NeoDash 0.3.0 source with the Chrome + Neon icon pack."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import math, sys

project = Path(sys.argv[1])
main_path = project / "app/src/main/java/com/neodash/launcher/MainActivity.java"
gradle_path = project / "app/build.gradle"
readme_path = project / "README.md"
res = project / "app/src/main/res/drawable-nodpi"
res.mkdir(parents=True, exist_ok=True)

def replace_once(source, old, new, label):
    if old not in source:
        raise SystemExit("Patch target not found: " + label)
    return source.replace(old, new, 1)

java = main_path.read_text(encoding="utf-8")
old_shortcut = '''        int iconColor = neon ? (featured ? CYAN : BLUE) : WHITE;
        if (neon) {
            NeonAppIconView icon = new NeonAppIconView(shortcutIconKind(name, packageName), iconColor);
            int iconWidth = iconScale == 0 ? 44 : (iconScale == 2 ? 58 : 52);
            LinearLayout.LayoutParams iconParams = new LinearLayout.LayoutParams(dp(iconWidth), 0, 1);
            iconParams.gravity = Gravity.CENTER;
            tile.addView(icon, iconParams);
        } else {
            ImageView icon = new ImageView(this);
            Drawable appIcon = null;
            try { appIcon = getPackageManager().getApplicationIcon(packageName); }
            catch (Exception ignored) {
                for (ResolveInfo info : launchableApps()) {
                    String candidate = info.activityInfo.packageName.toLowerCase(Locale.ROOT);
                    if (candidate.contains(fallback.toLowerCase(Locale.ROOT))) {
                        appIcon = info.loadIcon(getPackageManager());
                        break;
                    }
                }
            }
            if (appIcon != null) icon.setImageDrawable(appIcon);
            else icon.setImageDrawable(getDrawable(android.R.drawable.sym_def_app_icon));
            icon.setScaleType(ImageView.ScaleType.FIT_CENTER);
            int iconDp = iconScale == 0 ? 34 : (iconScale == 2 ? 52 : 43);
            LinearLayout.LayoutParams imageParams = new LinearLayout.LayoutParams(dp(iconDp), 0, 1);
            imageParams.gravity = Gravity.CENTER;
            tile.addView(icon, imageParams);
        }
'''
new_shortcut = '''        int iconColor = neon ? (featured ? CYAN : BLUE) : WHITE;
        Drawable neonArtwork = neon ? getNeonAppIcon(packageName, name) : null;
        if (neonArtwork != null) {
            ImageView icon = new ImageView(this);
            icon.setImageDrawable(neonArtwork);
            icon.setScaleType(ImageView.ScaleType.FIT_CENTER);
            int iconWidth = iconScale == 0 ? 44 : (iconScale == 2 ? 58 : 52);
            LinearLayout.LayoutParams iconParams = new LinearLayout.LayoutParams(dp(iconWidth), 0, 1);
            iconParams.gravity = Gravity.CENTER;
            tile.addView(icon, iconParams);
        } else if (neon) {
            NeonAppIconView icon = new NeonAppIconView(shortcutIconKind(name, packageName), iconColor);
            int iconWidth = iconScale == 0 ? 44 : (iconScale == 2 ? 58 : 52);
            LinearLayout.LayoutParams iconParams = new LinearLayout.LayoutParams(dp(iconWidth), 0, 1);
            iconParams.gravity = Gravity.CENTER;
            tile.addView(icon, iconParams);
        } else {
            ImageView icon = new ImageView(this);
            Drawable appIcon = null;
            try { appIcon = getPackageManager().getApplicationIcon(packageName); }
            catch (Exception ignored) {
                for (ResolveInfo info : launchableApps()) {
                    String candidate = info.activityInfo.packageName.toLowerCase(Locale.ROOT);
                    if (candidate.contains(fallback.toLowerCase(Locale.ROOT))) {
                        appIcon = info.loadIcon(getPackageManager());
                        break;
                    }
                }
            }
            if (appIcon != null) icon.setImageDrawable(appIcon);
            else icon.setImageDrawable(getDrawable(android.R.drawable.sym_def_app_icon));
            icon.setScaleType(ImageView.ScaleType.FIT_CENTER);
            int iconDp = iconScale == 0 ? 34 : (iconScale == 2 ? 52 : 43);
            LinearLayout.LayoutParams imageParams = new LinearLayout.LayoutParams(dp(iconDp), 0, 1);
            imageParams.gravity = Gravity.CENTER;
            tile.addView(icon, imageParams);
        }
'''
java = replace_once(java, old_shortcut, new_shortcut, "dashboard shortcut image selection")

helper = '''    /** Bundled Chrome + Neon art for known apps; unknown apps keep Android's original icon. */
    private Drawable getNeonAppIcon(String packageName, String appName) {
        String pkg = packageName == null ? "" : packageName.toLowerCase(Locale.ROOT);
        String name = appName == null ? "" : appName.toLowerCase(Locale.ROOT);
        String asset = null;
        if (pkg.contains("diplay") || name.contains("diplay") || name.contains("carplay")) asset = "icon_diplay";
        else if (pkg.contains("diauto") || pkg.contains("gearhead") || name.contains("diauto") || name.contains("android auto")) asset = "icon_diauto";
        else if (pkg.contains("waze") || name.contains("waze")) asset = "icon_waze";
        else if (pkg.contains("spotify") || name.contains("spotify")) asset = "icon_spotify";
        else if (pkg.equals("com.android.chrome") || pkg.contains("chrome") || name.equals("chrome")) asset = "icon_chrome";
        else if (pkg.contains("google.android.apps.maps") || name.contains("maps")) asset = "icon_maps";
        else if (pkg.contains("google.android.youtube.music") || name.contains("youtube music") || name.contains("play music")) asset = "icon_play_music";
        else if (pkg.contains("google.android.youtube") || name.equals("youtube") || name.equals("youtube tv")) asset = "icon_youtube";
        else if (pkg.contains("google.android.gm") || name.contains("gmail")) asset = "icon_gmail";
        else if (pkg.contains("google.android.apps.photos") || name.contains("photos")) asset = "icon_photos";
        else if (pkg.contains("google.android.apps.tachyon") || name.equals("meet")) asset = "icon_meet";
        else if (pkg.contains("google.android.calendar") || name.contains("calendar")) asset = "icon_calendar";
        else if (pkg.contains("google.android.keep") || name.equals("keep") || name.contains("keep notes")) asset = "icon_keep";
        else if (pkg.contains("google.android.apps.translate") || name.contains("translate")) asset = "icon_translate";
        else if (pkg.equals("com.android.vending") || name.contains("play store")) asset = "icon_play_store";
        else if (pkg.contains("google.android.play.games") || name.contains("play games")) asset = "icon_play_games";
        else if (pkg.contains("google.android.videos") || name.contains("google tv") || name.contains("play movies")) asset = "icon_play_movies";
        else if (pkg.contains("google.android.apps.docs.editors.sheets") || name.equals("sheets") || name.contains("google sheets")) asset = "icon_sheets";
        else if (pkg.contains("google.android.apps.docs.editors.slides") || name.equals("slides") || name.contains("google slides")) asset = "icon_slides";
        else if (pkg.contains("google.android.apps.docs.editors.docs") || name.equals("docs") || name.contains("google docs")) asset = "icon_docs";
        else if (pkg.contains("google.android.apps.docs") || name.equals("drive") || name.contains("google drive")) asset = "icon_drive";
        else if (pkg.contains("google.android.apps.walletnfcrel") || name.contains("wallet")) asset = "icon_wallet";
        else if (pkg.contains("google.earth") || name.equals("earth") || name.contains("google earth")) asset = "icon_earth";
        else if (pkg.contains("google.android.apps.fitness") || name.equals("fit") || name.equals("google fit")) asset = "icon_fit";
        else if (pkg.contains("google.android.apps.magazines") || name.contains("news")) asset = "icon_news";
        else if (pkg.contains("google.android.apps.chromecast.app") || name.contains("home")) asset = "icon_home";
        else if (pkg.contains("google.android.apps.nbu.files") || pkg.contains("google.android.documentsui") || name.equals("files") || name.contains("file manager")) asset = "icon_files";
        else if (pkg.contains("google.android.contacts") || name.contains("contacts")) asset = "icon_contacts";
        else if (pkg.contains("google.android.dialer") || name.contains("phone")) asset = "icon_phone";
        else if (pkg.contains("google.android.apps.messaging") || name.contains("messages")) asset = "icon_messages";
        else if (pkg.contains("google.android.deskclock") || name.equals("clock")) asset = "icon_clock";
        else if (pkg.contains("google.android.calculator") || name.contains("calculator")) asset = "icon_calculator";
        else if (pkg.contains("google.android.apps.bard") || name.contains("gemini") || name.contains("assistant")) asset = "icon_assistant";
        else if (pkg.contains("googlequicksearchbox") || name.equals("google") || name.equals("google app")) asset = "icon_google";
        else if (pkg.equals("com.android.settings") || name.equals("settings")) asset = "icon_settings";
        if (asset == null) return null;
        int id = getResources().getIdentifier(asset, "drawable", getPackageName());
        return id == 0 ? null : getDrawable(id);
    }

'''
java = replace_once(java, '    private static final int ICON_GENERIC = 0;\n', helper + '    private static final int ICON_GENERIC = 0;\n', "known-app asset resolver")
java = replace_once(java,
'''                appIcon = getPackageManager().getApplicationIcon(packageName);
            } catch (Exception ex) { appName = packageName; appIcon = getDrawable(android.R.drawable.sym_def_app_icon); }
''',
'''                appIcon = getPackageManager().getApplicationIcon(packageName);
                Drawable themed = neon ? getNeonAppIcon(packageName, appName) : null;
                if (themed != null) appIcon = themed;
            } catch (Exception ex) { appName = packageName; appIcon = getDrawable(android.R.drawable.sym_def_app_icon); }
''', "recent-app icons")
java = replace_once(java,
'''            ImageView icon = new ImageView(this);
            try { icon.setImageDrawable(info.loadIcon(getPackageManager())); }
            catch (Exception ignored) { }
            icon.setScaleType(ImageView.ScaleType.FIT_CENTER);
            item.addView(icon, new LinearLayout.LayoutParams(dp(39), dp(39)));
            TextView name = label(info.loadLabel(getPackageManager()).toString(), 10, WHITE, true);
''',
'''            String appLabel = info.loadLabel(getPackageManager()).toString();
            ImageView icon = new ImageView(this);
            Drawable themed = neon ? getNeonAppIcon(info.activityInfo.packageName, appLabel) : null;
            if (themed != null) icon.setImageDrawable(themed);
            else {
                try { icon.setImageDrawable(info.loadIcon(getPackageManager())); }
                catch (Exception ignored) { }
            }
            icon.setScaleType(ImageView.ScaleType.FIT_CENTER);
            item.addView(icon, new LinearLayout.LayoutParams(dp(39), dp(39)));
            TextView name = label(appLabel, 10, WHITE, true);
''', "installed-app drawer icons")
java = java.replace("Choose how NeoDash shortcut icons are presented.", "Chrome + Neon uses the combined yellow, magenta and cyan icon pack for Google apps and supported shortcuts. Standard keeps original Android icons.")
java = java.replace('addSettingChoice(styles, "NEON", neon,', 'addSettingChoice(styles, "NEON CHROME", neon,')
java = java.replace("Version 0.3.0 · Lightweight launcher · DiPlay stays a separate app. Custom third-party icon packs can be added in a later update.", "Version 0.3.1 · Chrome + Neon app icons · DiPlay and DiAuto stay separate apps. Unknown apps keep their original Android icons.")
main_path.write_text(java, encoding="utf-8")

# Draw crisp Android-sized artwork with a shared chrome bezel and all three neon colors.
Y=(255,222,35,255); M=(255,40,210,255); C=(0,232,255,255); S=(240,246,252,255)
def icon_art(key):
    im=Image.new("RGBA",(128,128),(4,7,13,255))
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((8,8,120,120),radius=25,fill=(8,13,22,255))
    for x in range(18,116,16):
        for y in range(22,112,18):
            d.line((x,y,x+5,y-3,x+10,y,x+10,y+6,x+5,y+9,x,y+6,x,y),fill=(25,42,54,110),width=1)
    logo=Image.new("RGBA",(128,128),(0,0,0,0)); a=ImageDraw.Draw(logo)
    if key=="icon_google":
        a.arc((30,25,98,95),35,315,fill=(66,133,244,255),width=13); a.line((65,60,100,60),fill=(52,168,83,255),width=12); a.arc((30,25,98,95),-45,80,fill=(251,188,5,255),width=12)
    elif key=="icon_chrome":
        a.pieslice((25,25,103,103),210,330,fill=(52,168,83,255)); a.pieslice((25,25,103,103),330,90,fill=(234,67,53,255)); a.pieslice((25,25,103,103),90,210,fill=(251,188,5,255)); a.ellipse((48,48,80,80),fill=(66,133,244,255),outline=S,width=3)
    elif key=="icon_maps":
        a.ellipse((36,22,92,78),fill=(66,133,244,255),outline=S,width=3); a.polygon([(42,66),(86,66),(64,111)],fill=(52,168,83,255)); a.ellipse((52,38,76,62),fill=(251,188,5,255))
    elif key=="icon_youtube":
        a.rounded_rectangle((20,34,108,94),radius=18,fill=(235,40,65,255),outline=C,width=3); a.polygon([(53,47),(82,64),(53,81)],fill=S)
    elif key=="icon_drive":
        a.line([(47,25),(79,25),(108,81),(91,103),(60,50),(35,95)],fill=(52,168,83,255),width=14,joint="curve"); a.line([(47,25),(21,76),(38,104),(67,53)],fill=(66,133,244,255),width=13,joint="curve"); a.line([(38,104),(93,104),(108,81)],fill=(251,188,5,255),width=13,joint="curve")
    elif key=="icon_gmail":
        a.line([(23,93),(23,37),(64,67),(105,37),(105,93)],fill=(234,67,53,255),width=13,joint="curve"); a.line((23,38,43,53),fill=(66,133,244,255),width=8); a.line((105,38,85,53),fill=(52,168,83,255),width=8)
    elif key=="icon_photos":
        a.pieslice((50,24,88,66),0,300,fill=(66,133,244,255)); a.pieslice((66,50,108,90),0,300,fill=(234,67,53,255)); a.pieslice((39,65,81,108),0,300,fill=(52,168,83,255)); a.pieslice((24,39,66,81),0,300,fill=(251,188,5,255))
    elif key=="icon_calendar":
        a.rounded_rectangle((27,25,101,104),radius=11,fill=(21,130,230,255),outline=M,width=4); a.rectangle((27,25,101,48),fill=(234,67,53,255)); a.text((42,51),"31",fill=S)
    elif key=="icon_meet":
        a.rounded_rectangle((24,35,83,91),radius=10,fill=(66,133,244,255),outline=C,width=4); a.polygon([(82,48),(109,34),(109,92),(82,78)],fill=(52,168,83,255))
    elif key in ("icon_docs","icon_sheets","icon_slides","icon_files","icon_news"):
        col={"icon_docs":(66,133,244,255),"icon_sheets":(52,168,83,255),"icon_slides":(251,188,5,255),"icon_files":(66,133,244,255),"icon_news":(66,133,244,255)}[key]
        a.polygon([(34,20),(82,20),(99,37),(99,107),(34,107)],fill=col,outline=S); a.polygon([(82,20),(82,38),(99,38)],fill=(255,255,255,100))
        if key=="icon_sheets":
            for x in (49,66,83): a.line((x,55,x,90),fill=S,width=3)
            for y in (55,72,90): a.line((45,y,89,y),fill=S,width=3)
        elif key=="icon_slides": a.rectangle((47,53,87,82),outline=S,width=4)
        else:
            for y in (54,68,82): a.line((47,y,84,y),fill=S,width=4)
    elif key=="icon_keep":
        a.rounded_rectangle((31,23,97,91),radius=13,fill=(255,195,25,255),outline=S,width=3); a.ellipse((49,37,79,70),outline=S,width=6); a.line((64,70,64,87),fill=S,width=6); a.line((53,91,75,91),fill=S,width=5)
    elif key=="icon_translate":
        a.rounded_rectangle((20,27,74,89),radius=7,fill=(66,133,244,255),outline=S,width=3); a.rounded_rectangle((58,43,108,101),radius=7,fill=(240,244,248,255),outline=M,width=3); a.text((32,39),"G",fill=S); a.text((72,59),"T",fill=(23,55,90,255))
    elif key=="icon_play_store":
        a.polygon([(34,22),(98,64),(34,106)],fill=(52,168,83,255),outline=S); a.polygon([(34,22),(73,50),(55,64)],fill=(66,133,244,255)); a.polygon([(73,50),(98,64),(73,80),(55,64)],fill=(251,188,5,255)); a.polygon([(34,106),(55,64),(73,80)],fill=(234,67,53,255))
    elif key=="icon_play_games":
        a.rounded_rectangle((23,40,105,89),radius=23,fill=(43,180,101,255),outline=S,width=4); a.line((43,55,43,76),fill=S,width=5); a.line((32,65,54,65),fill=S,width=5); a.ellipse((76,55,84,63),fill=Y); a.ellipse((89,70,97,78),fill=M)
    elif key=="icon_play_movies":
        a.rounded_rectangle((24,27,104,101),radius=10,fill=(240,52,126,255),outline=S,width=4)
        for y in (40,62,84): a.rectangle((31,y,38,y+8),fill=S); a.rectangle((90,y,97,y+8),fill=S)
    elif key=="icon_play_music":
        a.line((68,25,68,82),fill=M,width=9); a.line((68,25,97,18),fill=Y,width=8); a.ellipse((40,75,70,102),fill=C); a.ellipse((70,63,100,90),fill=M)
    elif key=="icon_assistant":
        for x,y,r,col in [(43,45,17,(66,133,244,255)),(82,73,13,(234,67,53,255)),(59,96,17,(251,188,5,255)),(93,37,8,(52,168,83,255))]: a.ellipse((x-r,y-r,x+r,y+r),fill=col,outline=S,width=2)
    elif key=="icon_home":
        a.polygon([(19,60),(64,22),(109,60),(101,69),(64,39),(27,69)],fill=M); a.polygon([(32,60),(96,60),(96,105),(32,105)],fill=(12,25,38,255),outline=C); a.rectangle((55,75,73,105),fill=Y)
    elif key=="icon_wallet":
        a.rounded_rectangle((23,34,105,98),radius=12,fill=(23,105,190,255),outline=S,width=4); a.rounded_rectangle((23,23,105,50),radius=10,fill=(52,168,83,255),outline=Y,width=3); a.line((26,61,103,61),fill=M,width=5); a.rounded_rectangle((72,61,108,84),radius=7,fill=(12,19,30,255),outline=C,width=3)
    elif key=="icon_earth":
        a.ellipse((22,22,106,106),fill=(22,118,200,255),outline=S,width=4); a.arc((38,22,90,106),70,290,fill=C,width=5); a.arc((22,44,106,84),0,180,fill=C,width=5); a.arc((22,44,106,84),180,360,fill=C,width=5)
    elif key=="icon_fit":
        a.polygon([(64,104),(24,64),(24,46),(39,31),(54,31),(64,43),(74,31),(90,31),(104,46),(104,64)],fill=(52,168,83,255),outline=S); a.line((31,48,51,68,64,54,81,74,99,50),fill=Y,width=6)
    elif key=="icon_contacts":
        a.ellipse((45,22,83,60),fill=(66,133,244,255),outline=S,width=3); a.rounded_rectangle((28,64,100,108),radius=24,fill=(66,133,244,255),outline=C,width=3)
    elif key=="icon_phone":
        a.arc((27,21,101,105),30,300,fill=(52,168,83,255),width=19); a.rounded_rectangle((23,24,49,51),radius=7,fill=M); a.rounded_rectangle((80,78,106,104),radius=7,fill=C)
    elif key=="icon_messages":
        a.rounded_rectangle((20,25,108,88),radius=20,fill=(66,133,244,255),outline=S,width=4); a.polygon([(42,82),(34,109),(69,84)],fill=C)
        for x in (45,64,83): a.ellipse((x-4,53,x+4,61),fill=S)
    elif key=="icon_clock":
        a.ellipse((22,22,106,106),outline=C,width=7); a.ellipse((30,30,98,98),outline=M,width=2); a.line((64,64,64,39),fill=S,width=5); a.line((64,64,88,75),fill=Y,width=5); a.ellipse((59,59,69,69),fill=S)
    elif key=="icon_calculator":
        a.rounded_rectangle((27,20,101,108),radius=12,fill=(18,24,37,255),outline=S,width=4); a.rounded_rectangle((39,31,89,50),radius=4,fill=(66,133,244,255),outline=C,width=2)
        for x in (44,64,84):
            for y in (65,84): a.rounded_rectangle((x-5,y-5,x+5,y+5),radius=2,fill=(Y,M,C)[(x//20+y//20)%3])
    elif key=="icon_settings":
        a.ellipse((30,30,98,98),fill=(80,100,116,255),outline=S,width=4); a.ellipse((49,49,79,79),fill=(7,12,19,255),outline=C,width=4)
        for angle in range(0,360,45):
            cx=64+39*math.cos(math.radians(angle)); cy=64+39*math.sin(math.radians(angle)); a.rounded_rectangle((cx-6,cy-6,cx+6,cy+6),radius=3,fill=S)
    elif key=="icon_all_apps":
        for x in (26,70):
            for y in (26,70): a.rounded_rectangle((x,y,x+31,y+31),radius=6,fill=(15,25,38,255),outline=(Y,M,C,S)[(x+y)//40%4],width=5)
    elif key=="icon_diplay":
        a.arc((15,24,73,100),105,255,fill=C,width=6); a.arc((27,34,70,90),105,255,fill=M,width=5); a.rounded_rectangle((48,30,111,88),radius=12,fill=(10,18,30,255),outline=S,width=5); a.polygon([(70,43),(94,59),(70,75)],fill=Y)
    elif key=="icon_diauto":
        a.polygon([(64,15),(109,87),(91,87),(64,46),(37,87),(19,87)],fill=S,outline=Y); a.polygon([(64,64),(92,107),(75,107),(64,90),(53,107),(36,107)],fill=M,outline=C)
    elif key=="icon_waze":
        a.ellipse((27,22,101,91),fill=(180,204,214,255),outline=C,width=5); a.ellipse((43,47,52,56),fill=(5,10,16,255)); a.ellipse((75,47,84,56),fill=(5,10,16,255)); a.arc((48,53,81,78),10,170,fill=(5,10,16,255),width=5); a.ellipse((34,84,55,105),fill=Y); a.ellipse((73,84,94,105),fill=Y)
    elif key=="icon_spotify":
        a.ellipse((19,19,109,109),fill=(18,23,34,255),outline=M,width=6)
        for box,col in [((32,39,96,65),Y),((36,55,92,80),C),((42,71,86,93),M)]: a.arc(box,200,340,fill=col,width=6)
    halo=Image.new("RGBA",(128,128),(0,0,0,0)); halo.alpha_composite(logo); halo=halo.filter(ImageFilter.GaussianBlur(7))
    im=Image.alpha_composite(im,halo); im=Image.alpha_composite(im,logo)
    glow=Image.new("RGBA",(128,128),(0,0,0,0)); gd=ImageDraw.Draw(glow)
    gd.rounded_rectangle((3,3,125,125),radius=29,outline=Y,width=5); gd.arc((3,3,125,125),20,165,fill=M,width=6); gd.arc((3,3,125,125),190,340,fill=C,width=6)
    im=Image.alpha_composite(im,glow.filter(ImageFilter.GaussianBlur(7)))
    d=ImageDraw.Draw(im); d.rounded_rectangle((4,4,124,124),radius=28,outline=S,width=4); d.rounded_rectangle((9,9,119,119),radius=23,outline=(116,151,172,235),width=1)
    d.line((16,19,38,19,51,10),fill=Y,width=3); d.line((88,119,105,119,118,106),fill=M,width=4); d.line((105,119,119,105),fill=C,width=3); d.line((22,119,62,119),fill=Y,width=2); d.arc((8,8,120,120),205,325,fill=(255,255,255,180),width=2)
    im.convert("RGB").save(res/(key+".png"),optimize=True)

asset_names = [
"icon_diplay","icon_diauto","icon_waze","icon_spotify","icon_google","icon_chrome","icon_maps","icon_youtube",
"icon_drive","icon_gmail","icon_photos","icon_calendar","icon_meet","icon_docs","icon_sheets","icon_slides",
"icon_keep","icon_translate","icon_play_store","icon_play_games","icon_play_movies","icon_play_music","icon_assistant","icon_files",
"icon_news","icon_home","icon_wallet","icon_earth","icon_fit","icon_contacts","icon_phone","icon_messages",
"icon_clock","icon_calculator","icon_settings","icon_all_apps"]
for name in asset_names:
    icon_art(name)

gradle=gradle_path.read_text(encoding="utf-8")
gradle=gradle.replace("versionCode 4","versionCode 5").replace("versionName '0.3.0-time-input-foundation'","versionName '0.3.1-chrome-neon-icons'").replace("applicationIdSuffix '.debug'","applicationIdSuffix '.debug31'")
gradle_path.write_text(gradle,encoding="utf-8")
readme=readme_path.read_text(encoding="utf-8")
readme=readme.replace("# NeoDash 0.3.0 — Time Sync + Physical Input Foundation","# NeoDash 0.3.1 — Chrome + Neon Icon Pack")
feature="""## What's new in 0.3.1 — Chrome + Neon icons

- Added 36 bundled app icons with a unified chrome frame and combined yellow, magenta and cyan neon trim.
- Includes DiPlay, DiAuto, Waze, Spotify and common Google / Android apps: Google, Chrome, Maps, YouTube, Drive, Gmail, Photos, Calendar, Meet, Docs, Sheets, Slides, Keep, Translate, Play Store, Play Games, Google TV / Movies, YouTube Music, Assistant, Files, News, Home, Wallet, Earth, Fit, Contacts, Phone, Messages, Clock and Calculator, plus Settings and All Apps artwork.
- The Neon Chrome appearance uses the bundled artwork in dashboard shortcuts, the installed-app drawer and launcher-managed recent-app switcher where a known app package is recognized.
- Apps not covered by the pack continue using their installed Android icons; Standard appearance always uses original Android icons.
- The pack is local to NeoDash and does not replace or modify icons inside the other installed apps.

"""
if "What's new in 0.3.1" not in readme:
    readme=readme.replace("## Retained dashboard functionality",feature+"## Retained dashboard functionality",1)
readme_path.write_text(readme,encoding="utf-8")
print("Generated",len(asset_names),"Chrome + Neon icon assets")
