#!/usr/bin/env python3
"""Move receiver ownership out of NeoDash and connect the dashboard to NeoLink."""
from pathlib import Path
import re

ROOT = Path("build-source/NeoDash-Sleek-v0.3.0")
JAVA = ROOT / "app/src/main/java/com/neodash/launcher"
MAIN = JAVA / "MainActivity.java"
MANIFEST = ROOT / "app/src/main/AndroidManifest.xml"
BOOT = JAVA / "NeoDashBootReceiver.java"
OLD_SERVICE = JAVA / "NeoDashConnectionManager.java"
NEW_SERVICE = JAVA / "NeoDashSystemStatusService.java"

def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)

def remove_regex(text: str, pattern: str, label: str) -> str:
    result, count = re.subn(pattern, "", text, count=1, flags=re.S)
    if count != 1:
        raise SystemExit(f"{label}: expected one block, found {count}")
    return result

# --- NeoDash system-status service: keep clock/GPS/radio status, remove phone ownership. ---
service = OLD_SERVICE.read_text(encoding="utf-8")
service = service.replace("NeoDashConnectionManager", "NeoDashSystemStatusService")
service = service.replace('    public static final String ACTION_RECEIVER_SESSION = "com.neodash.launcher.RECEIVER_SESSION";\n', "")
for line in [
    '    public static final String EXTRA_CONNECTED = "connected";\n',
    '    public static final String EXTRA_RECEIVER_RUNNING = "receiver_running";\n',
    '    public static final String EXTRA_DEVICE_OS = "device_os";\n',
    '    public static final String EXTRA_SESSION_ID = "session_id";\n',
    '    public static final String EXTRA_RECEIVER = "receiver";\n',
    '    private boolean usbRegistered;\n',
    '    private boolean receiverSessionActive;\n',
    '    private String receiverSessionId;\n',
    'import android.hardware.usb.UsbManager;\n',
    'import android.provider.Settings;\n',
]:
    service = service.replace(line, "")
service = service.replace('buildNotification("Monitoring device connections")',
                          'buildNotification("System status and clock synchronization")')
pattern = (
    r'    @Override public int onStartCommand\(Intent intent, int flags, int startId\) \{.*?'
    r'\n    \}\n\n    private boolean validSession\(Intent intent, String id\) \{.*?'
    r'\n    \}\n\n    private void registerEventSources\(\) \{'
)
replacement = (
    '    @Override public int onStartCommand(Intent intent, int flags, int startId) {\n'
    '        if (intent != null && ACTION_REFRESH_TIME.equals(intent.getAction()) && timeSyncManager != null) {\n'
    '            timeSyncManager.refreshIfNeeded();\n'
    '        }\n'
    '        publishStatus();\n'
    '        return START_STICKY;\n'
    '    }\n\n'
    '    private void registerEventSources() {'
)
service, count = re.subn(pattern, replacement, service, count=1, flags=re.S)
if count != 1:
    raise SystemExit("System status service: could not isolate receiver-session handling")
service = re.sub(
    r'        BluetoothAdapter adapter = BluetoothAdapter\.getDefaultAdapter\(\);\n'
    r'        if \(adapter != null && !adapter\.isEnabled\(\)\) \{\n'
    r'            try \{ adapter\.enable\(\); \} catch \(RuntimeException ignored\) \{ \}\n'
    r'        \}\n',
    "",
    service,
    count=1,
)
service = service.replace('        radios.addAction(BluetoothAdapter.ACTION_CONNECTION_STATE_CHANGED);\n', "")
service = service.replace('        radios.addAction(UsbManager.ACTION_USB_DEVICE_ATTACHED);\n', "")
service = service.replace('        radios.addAction(UsbManager.ACTION_USB_DEVICE_DETACHED);\n', "")
service = service.replace('        status.putExtra("receiver_active", receiverSessionActive);\n', "")
if "ACTION_RECEIVER_SESSION" in service or "receiverSessionActive" in service or "UsbManager" in service:
    raise SystemExit("System status service still contains receiver/device-discovery ownership")
NEW_SERVICE.write_text(service, encoding="utf-8")
OLD_SERVICE.unlink()

# --- NeoDash UI: receiver app setup and automatic launching move to NeoLink. ---
main = MAIN.read_text(encoding="utf-8")
# The dashboard clock must never wait for trusted/network time verification.
# Android's local wall clock is always the immediate display source; time sync is advisory.
main = replace_once(
    main,
    '        long trustedNow = getVerifiedDashboardTimeMillis();',
    '        long trustedNow = System.currentTimeMillis();',
    "Use Android system clock immediately",
)

# Replace launcher-shortcut-only discovery with a de-duplicated scan of installed
# applications that Android can actually launch. This includes launchable OEM/system apps.

# Full inventory for the All Apps screen, including enabled OEM/system packages
# that do not publish a launcher-category activity.
helper = r"""
    private List<ResolveInfo> allInstalledApps() {
        android.content.pm.PackageManager pm = getPackageManager();
        java.util.LinkedHashMap<String, ResolveInfo> byPackage = new java.util.LinkedHashMap<>();
        for (android.content.pm.ApplicationInfo app : pm.getInstalledApplications(0)) {
            if (!app.enabled || app.packageName == null || app.packageName.equals(getPackageName())) continue;
            ResolveInfo info = new ResolveInfo();
            android.content.pm.ActivityInfo activity = new android.content.pm.ActivityInfo();
            activity.applicationInfo = app;
            activity.packageName = app.packageName;
            activity.name = app.className;
            info.activityInfo = activity;
            byPackage.put(app.packageName, info);
        }
        ArrayList<ResolveInfo> apps = new ArrayList<>(byPackage.values());
        Collections.sort(apps, new Comparator<ResolveInfo>() {
            @Override public int compare(ResolveInfo a, ResolveInfo b) {
                return a.loadLabel(pm).toString().compareToIgnoreCase(b.loadLabel(pm).toString());
            }
        });
        return apps;
    }

"""
main = replace_once(
    main,
    '    private List<ResolveInfo> launchableApps() {',
    helper + '    private List<ResolveInfo> launchableApps() {',
    "Add full installed-app inventory",
)
main = replace_once(
    main,
    '        GridLayout grid = new GridLayout(this);\n        grid.setColumnCount(4);\n        grid.setUseDefaultMargins(false);\n        List<ResolveInfo> apps = launchableApps();',
    '        GridLayout grid = new GridLayout(this);\n        grid.setColumnCount(4);\n        grid.setUseDefaultMargins(false);\n        List<ResolveInfo> apps = allInstalledApps();',
    "Use full inventory in All Apps",
)
old_apps = r'''    private List<ResolveInfo> launchableApps\(\) \{.*?\n    \}\n\n    private void launchPackageOrFind'''
new_apps = r'''    private List<ResolveInfo> launchableApps() {
        if (cachedLaunchableApps != null) return cachedLaunchableApps;
        android.content.pm.PackageManager pm = getPackageManager();
        java.util.LinkedHashMap<String, ResolveInfo> byPackage = new java.util.LinkedHashMap<>();

        Intent launcherQuery = new Intent(Intent.ACTION_MAIN, null);
        launcherQuery.addCategory(Intent.CATEGORY_LAUNCHER);
        for (ResolveInfo info : pm.queryIntentActivities(launcherQuery, 0)) {
            if (info.activityInfo != null && info.activityInfo.enabled) {
                byPackage.put(info.activityInfo.packageName, info);
            }
        }

        // Some head-unit/OEM apps publish a Leanback entry rather than a phone launcher entry.
        Intent leanbackQuery = new Intent(Intent.ACTION_MAIN, null);
        leanbackQuery.addCategory("android.intent.category.LEANBACK_LAUNCHER");
        for (ResolveInfo info : pm.queryIntentActivities(leanbackQuery, 0)) {
            if (info.activityInfo != null && info.activityInfo.enabled) {
                byPackage.putIfAbsent(info.activityInfo.packageName, info);
            }
        }

        // Include enabled installed packages (including OEM system apps) when Android
        // exposes a safe package launch intent, even if they omitted CATEGORY_LAUNCHER.
        for (android.content.pm.ApplicationInfo app : pm.getInstalledApplications(0)) {
            if (!app.enabled || app.packageName == null || app.packageName.equals(getPackageName())
                    || byPackage.containsKey(app.packageName)) continue;
            Intent launch = pm.getLaunchIntentForPackage(app.packageName);
            if (launch == null) continue;

            ResolveInfo synthetic = new ResolveInfo();
            android.content.pm.ActivityInfo activity = new android.content.pm.ActivityInfo();
            activity.applicationInfo = app;
            activity.packageName = app.packageName;
            activity.name = launch.getComponent() != null
                    ? launch.getComponent().getClassName() : app.className;
            synthetic.activityInfo = activity;
            byPackage.put(app.packageName, synthetic);
        }

        ArrayList<ResolveInfo> apps = new ArrayList<>(byPackage.values());
        Collections.sort(apps, new Comparator<ResolveInfo>() {
            @Override public int compare(ResolveInfo a, ResolveInfo b) {
                return a.loadLabel(pm).toString().compareToIgnoreCase(b.loadLabel(pm).toString());
            }
        });
        cachedLaunchableApps = apps;
        return cachedLaunchableApps;
    }

    private void launchPackageOrFind'''
main, count = re.subn(old_apps, new_apps, main, count=1, flags=re.S)
if count != 1:
    raise SystemExit(f"Installed app scan replacement expected one method, found {count}")
# Refresh the cached package list whenever the user opens All Apps.
main = replace_once(
    main,
    '    private void showApps() {',
    '    private void showApps() {\n        cachedLaunchableApps = null;',
    "Refresh installed app list when opening All Apps",
)
main = main.replace("NeoDashConnectionManager", "NeoDashSystemStatusService")
main = main.replace("else if (index == 2) launchMobileForDetectedPhone();", "else if (index == 2) openNeoLinkSettings();")
main = main.replace('TextView serviceStatus = label(getSystemStatusText(), 11, MUTED, false);', 'TextView serviceStatus = label(getSystemStatusText() + "  |  " + neoLinkSummary, 11, MUTED, false);')
main = main.replace("import android.content.Context;\n",
                    "import android.content.Context;\nimport android.content.ComponentName;\nimport android.content.ServiceConnection;\n")
main = main.replace("import android.os.Handler;\n",
                    "import android.os.Handler;\nimport android.os.IBinder;\nimport android.os.Message;\nimport android.os.Messenger;\nimport android.os.RemoteException;\n")

main = replace_once(
    main,
    "    private BroadcastReceiver statusReceiver;\n",
    """    private BroadcastReceiver statusReceiver;
    private static final String NEOLINK_PACKAGE = "com.neodash.neolink";
    private static final String NEOLINK_BIND_ACTION = "com.neodash.neolink.action.BIND";
    private static final int NEOLINK_MSG_STATE = 2;
    private static final int NEOLINK_MSG_EVENT = 3;
    private static final int NEOLINK_MSG_REGISTER = 4;
    private static final int NEOLINK_MSG_UNREGISTER = 5;
    private Messenger neoLinkService;
    private boolean neoLinkBound;
    private String neoLinkSummary = "NEOLINK: CHECKING";
    private final Messenger neoLinkClient = new Messenger(new Handler(Looper.getMainLooper(), msg -> {
        if (msg.what == NEOLINK_MSG_STATE || msg.what == NEOLINK_MSG_EVENT) {
            String json = msg.getData().getString("state_json", "{}");
            runOnUiThread(() -> updateNeoLinkState(json));
            return true;
        }
        return false;
    }));
    private final ServiceConnection neoLinkConnection = new ServiceConnection() {
        @Override public void onServiceConnected(ComponentName name, IBinder binder) {
            neoLinkService = new Messenger(binder);
            neoLinkSummary = "NEOLINK: ONLINE";
            sendNeoLinkMessage(NEOLINK_MSG_REGISTER);
            updateNeoLinkSummaryView();
        }
        @Override public void onServiceDisconnected(ComponentName name) {
            neoLinkService = null;
            neoLinkSummary = "NEOLINK: OFFLINE";
            updateNeoLinkSummaryView();
        }
    };
""",
    "NeoDash Messenger client fields",
)

# Remove receiver selection from first-run dashboard setup.
main = main.replace('        addAppPreferenceRow(list, "iOS CARPLAY RECEIVER", "ios_app_package", "Choose the iOS receiver app", "ios");\n', "")
main = main.replace('        addAppPreferenceRow(list, "ANDROID AUTO RECEIVER", "android_app_package", "Choose the Android receiver app", "android");\n', "")
main = replace_once(
    main,
    '        addAppPreferenceRow(list, "DEFAULT MAP APPLICATION", "map_package", "Choose an installed map app", "map");\n',
    '        addAppPreferenceRow(list, "DEFAULT MAP APPLICATION", "map_package", "Choose an installed map app", "map");\n'
    '        addNeoLinkPreferenceRow(list);\n',
    "NeoLink setup row",
)
main = main.replace(
    'TextView hint = label("Choose the installed apps NeoDash should use. These choices can be changed later in Settings.", 11, MUTED, false);',
    'TextView hint = label("Choose map and media apps here. NeoLink manages phone connections and receiver app choices separately.", 11, MUTED, false);'
)
main = replace_once(
    main,
    'String[] keys = {"map_package", "ios_app_package", "android_app_package", "local_media_package"};',
    'String[] keys = {"map_package", "local_media_package"};',
    "Wizard required app defaults",
)

# Replace the two receiver rows in Settings with one NeoLink entry.
main = main.replace('        addAppPreferenceRow(body, "iOS CARPLAY RECEIVER", "ios_app_package", "Not selected", "ios");\n', "")
main = main.replace('        addAppPreferenceRow(body, "ANDROID AUTO RECEIVER", "android_app_package", "Not selected", "android");\n', "")
main = replace_once(
    main,
    '        addAppPreferenceRow(body, "DEFAULT MAP APPLICATION", "map_package", "Not selected", "map");\n',
    '        addAppPreferenceRow(body, "DEFAULT MAP APPLICATION", "map_package", "Not selected", "map");\n'
    '        addNeoLinkPreferenceRow(body);\n',
    "Settings NeoLink row",
)

# Remove receiver-specific selection filters from the generic app picker.
main = main.replace('            else if ("ios".equals(type)) match = containsAny(label + " " + pkg, new String[]{"diplay", "carplay", "airplay"});\n', "")
main = main.replace('            else if ("android".equals(type)) match = containsAny(label + " " + pkg, new String[]{"diauto", "android auto", "gearhead"});\n', "")

# Delete the old dashboard-side receiver launch path.
main = remove_regex(
    main,
    r'    private void launchMobileForDetectedPhone\(\) \{.*?\n    \}\n',
    "Legacy receiver launch method",
)
main = remove_regex(
    main,
    r'    private void showPendingReceiverPrompt\(\) \{.*?\n    \}\n',
    "Legacy receiver prompt method",
)
main = main.replace('                    if (NeoDashSystemStatusService.ACTION_RECEIVER_SESSION.equals(intent.getAction())) showPendingReceiverPrompt();\n', "")
main = main.replace('            statusFilter.addAction(NeoDashSystemStatusService.ACTION_RECEIVER_SESSION);\n', "")
main = main.replace('        showPendingReceiverPrompt();\n', "")

# Bind once while the dashboard is active; service events are pushed, never polled.
main = replace_once(
    main,
    '        if (prefs != null && !hasAllRequiredPermissions()) { showPermissionSetup(); return; }\n        if (timeReceiver == null) {',
    '        if (prefs != null && !hasAllRequiredPermissions()) { showPermissionSetup(); return; }\n'
    '        bindNeoLink();\n'
    '        if (timeReceiver == null) {',
    "Bind NeoLink during dashboard resume",
)
main = replace_once(
    main,
    '                    if (status instanceof TextView) ((TextView) status).setText(getSystemStatusText());',
    '                    if (status instanceof TextView) ((TextView) status).setText(getSystemStatusText() + "  |  " + neoLinkSummary);',
    "Append NeoLink status to dashboard system status",
)
main = replace_once(
    main,
    '        super.onPause();',
    '        unbindNeoLink();\n        super.onPause();',
    "Unbind NeoLink on dashboard pause",
)

# Add the client and the settings deep-link helpers before the existing app finder.
helper_anchor = '    private String findInstalledPackage(String hint) {'
helpers = r'''
    private void addNeoLinkPreferenceRow(LinearLayout parent) {
        LinearLayout item = column();
        item.setPadding(dp(3), dp(9), dp(3), dp(9));
        item.addView(label("PHONE CONNECTIONS / RECEIVER APPS", 10, CYAN, true));
        TextView action = label("OPEN NEOLINK SETTINGS  ›", 11, WHITE, true);
        action.setPadding(0, dp(8), 0, dp(4));
        item.addView(action);
        item.addView(label("NeoLink owns device detection, receiver selection and receiver launch.", 10, MUTED, false));
        item.setOnClickListener(v -> openNeoLinkSettings());
        parent.addView(item);
        View divider = new View(this);
        divider.setBackgroundColor(LINE);
        parent.addView(divider, new LinearLayout.LayoutParams(-1, dp(1)));
    }

    private void openNeoLinkSettings() {
        Intent launch = getPackageManager().getLaunchIntentForPackage(NEOLINK_PACKAGE);
        if (launch == null) {
            Toast.makeText(this, "Install the separate NeoLink companion app to configure phone receivers.", Toast.LENGTH_LONG).show();
            return;
        }
        try { startActivity(launch); }
        catch (RuntimeException ex) { Toast.makeText(this, "NeoLink could not be opened", Toast.LENGTH_SHORT).show(); }
    }

    private void bindNeoLink() {
        if (neoLinkBound) return;
        Intent service = new Intent(NEOLINK_BIND_ACTION);
        service.setPackage(NEOLINK_PACKAGE);
        try {
            if (android.os.Build.VERSION.SDK_INT >= 26) startForegroundService(service);
            else startService(service);
            neoLinkBound = bindService(service, neoLinkConnection, Context.BIND_AUTO_CREATE);
            if (!neoLinkBound) {
                neoLinkSummary = "NEOLINK: NOT AVAILABLE";
                updateNeoLinkSummaryView();
            }
        } catch (RuntimeException unavailable) {
            neoLinkSummary = "NEOLINK: NOT INSTALLED / UNAVAILABLE";
            updateNeoLinkSummaryView();
        }
    }

    private void sendNeoLinkMessage(int what) {
        if (neoLinkService == null) return;
        try {
            Message message = Message.obtain(null, what);
            if (what == NEOLINK_MSG_REGISTER || what == NEOLINK_MSG_UNREGISTER) message.replyTo = neoLinkClient;
            neoLinkService.send(message);
        } catch (RemoteException ignored) { }
    }

    private void unbindNeoLink() {
        if (neoLinkService != null) sendNeoLinkMessage(NEOLINK_MSG_UNREGISTER);
        if (neoLinkBound) {
            try { unbindService(neoLinkConnection); } catch (IllegalArgumentException ignored) { }
        }
        neoLinkBound = false;
        neoLinkService = null;
    }

    private void updateNeoLinkState(String json) {
        try {
            org.json.JSONObject root = new org.json.JSONObject(json);
            org.json.JSONObject connection = root.optJSONObject("connection");
            if (connection == null) {
                neoLinkSummary = "NEOLINK: STATE UNKNOWN";
            } else {
                String link = connection.optString("link_state", "unknown").toUpperCase(Locale.ROOT);
                String platform = connection.optString("platform", "unknown").toUpperCase(Locale.ROOT);
                String transport = connection.optString("transport", "none").toUpperCase(Locale.ROOT);
                boolean wifi = root.optBoolean("wifi_network_available", false);
                neoLinkSummary = "NEOLINK: " + link + " / " + platform + " / " + transport + " / WIFI " + (wifi ? "ON" : "OFF");
            }
        } catch (Exception ignored) {
            neoLinkSummary = "NEOLINK: STATE UNAVAILABLE";
        }
        updateNeoLinkSummaryView();
    }

    private void updateNeoLinkSummaryView() {
        View status = findViewWithTag("system_service_status");
        if (status instanceof TextView) {
            ((TextView) status).setText(getSystemStatusText() + "  |  " + neoLinkSummary);
        }
    }

'''
main = replace_once(main, helper_anchor, helpers + helper_anchor, "NeoLink client and settings helpers")

# Bluetooth scan/discovery permissions belong to NeoLink, not the dashboard.
main = main.replace('            if (!permissionGranted(Manifest.permission.BLUETOOTH_SCAN)) missing.add(Manifest.permission.BLUETOOTH_SCAN);\n', "")
main = main.replace('            addPermissionStatusRow(body, "BLUETOOTH SCAN", Manifest.permission.BLUETOOTH_SCAN);\n', "")
MAIN.write_text(main, encoding="utf-8")

# --- Keep only system status/time sync ownership in the renamed NeoDash service. ---
# Ensure all references in boot receiver and manifest use the renamed class.
boot = BOOT.read_text(encoding="utf-8")
boot = boot.replace('            if (context.checkSelfPermission(Manifest.permission.BLUETOOTH_SCAN) != PackageManager.PERMISSION_GRANTED) return;\n', "")
boot = boot.replace("Starts the connection monitor only after onboarding and required permissions are complete.",
                    "Checks dashboard setup prerequisites; NeoLink owns phone connection monitoring.")
BOOT.write_text(boot, encoding="utf-8")

manifest = MANIFEST.read_text(encoding="utf-8")
manifest = manifest.replace('    <uses-permission android:name="android.permission.BLUETOOTH_SCAN" android:usesPermissionFlags="neverForLocation" />\n', "")
manifest = manifest.replace('            android:name=".NeoDashConnectionManager"', '            android:name=".NeoDashSystemStatusService"')
manifest = manifest.replace(
    '<manifest xmlns:android="http://schemas.android.com/apk/res/android">\n',
    '<manifest xmlns:android="http://schemas.android.com/apk/res/android">\n'
    '    <uses-permission android:name="android.permission.QUERY_ALL_PACKAGES" />\n'
    '    <uses-permission android:name="com.neodash.neolink.permission.BIND_SERVICE" />\n'
    '    <queries><package android:name="com.neodash.neolink" /><intent><action android:name="android.intent.action.MAIN" /><category android:name="android.intent.category.LAUNCHER" /></intent></queries>\n',
    1,
)
if manifest.count("<queries>") != 1 or "android.intent.category.LAUNCHER" not in manifest:
    raise SystemExit("NeoDash package visibility query is missing or duplicated")
if manifest.count('android.permission.QUERY_ALL_PACKAGES') != 1:
    raise SystemExit("NeoDash installed-app visibility permission is missing or duplicated")
MANIFEST.write_text(manifest, encoding="utf-8")

# Mark the architecture build distinctly from the retained 0.3.2 baseline.
gradle_file = ROOT / "app/build.gradle"
gradle_text = gradle_file.read_text(encoding="utf-8")
gradle_text, code_count = re.subn(r'(versionCode\s*=?\s*)\d+', r'\g<1>40', gradle_text, count=1)
gradle_text, name_count = re.subn(r'(versionName\s*=?\s*)["\']([^"\']+)["\']', r'\g<1>"0.4.0"', gradle_text, count=1)
if code_count != 1 or name_count != 1:
    raise SystemExit("Could not set NeoDash 0.4.0 versionCode/versionName")
gradle_file.write_text(gradle_text, encoding="utf-8")

print("NeoDash/NeoLink architecture patch applied.")



# Map rendering is intentionally not part of NeoDash; navigation launches the selected external app.

# --- Media artwork/session support. Read Android's active MediaSession metadata. ---
main = replace_once(
    main,
    "    private LinearLayout root;\n",
    "    private LinearLayout root;\n"
    "    private android.widget.ImageView albumArtView;\n"
    "    private android.widget.TextView mediaTitleView, mediaArtistView;\n"
    "    private android.media.session.MediaController activeMediaController;\n"
    "    private final android.os.Handler mediaHandler = new android.os.Handler(android.os.Looper.getMainLooper());\n"
    "    private final Runnable mediaRefreshRunnable = new Runnable() {\n"
    "        @Override public void run() {\n"
    "            updateActiveMediaSession();\n"
    "            mediaHandler.postDelayed(this, 1500L);\n"
    "        }\n"
    "    };\n",
    "add media session fields",
)

main = replace_once(
    main,
    "        hub.addView(active, new LinearLayout.LayoutParams(-1, dp(22)));\n\n"
    "        LinearLayout controls = row();",
    "        hub.addView(active, new LinearLayout.LayoutParams(-1, dp(22)));\n\n"
    "        LinearLayout mediaInfo = row();\n"
    "        mediaInfo.setGravity(Gravity.CENTER_VERTICAL);\n"
    "        mediaInfo.setPadding(dp(2), dp(5), dp(2), dp(5));\n"
    "        albumArtView = new android.widget.ImageView(this);\n"
    "        albumArtView.setScaleType(android.widget.ImageView.ScaleType.CENTER_CROP);\n"
    "        albumArtView.setBackground(panel(Color.rgb(9, 23, 35), LINE, 8));\n"
    "        albumArtView.setImageResource(android.R.drawable.ic_media_play);\n"
    "        LinearLayout.LayoutParams artParams = new LinearLayout.LayoutParams(dp(54), dp(54));\n"
    "        artParams.rightMargin = dp(10);\n"
    "        mediaInfo.addView(albumArtView, artParams);\n"
    "        LinearLayout trackText = column();\n"
    "        mediaTitleView = label(\"No active player\", 11, WHITE, true);\n"
    "        mediaArtistView = label(\"Start music on your connected device\", 9, MUTED, false);\n"
    "        trackText.addView(mediaTitleView);\n"
    "        LinearLayout.LayoutParams artistParams = new LinearLayout.LayoutParams(-1, -2);\n"
    "        artistParams.topMargin = dp(4);\n"
    "        trackText.addView(mediaArtistView, artistParams);\n"
    "        mediaInfo.addView(trackText, new LinearLayout.LayoutParams(0, -2, 1));\n"
    "        hub.addView(mediaInfo, new LinearLayout.LayoutParams(-1, dp(62)));\n"
    "        mediaTitleView.setOnClickListener(v -> openMediaNotificationAccess());\n"
    "        mediaArtistView.setOnClickListener(v -> openMediaNotificationAccess());\n"
    "        mediaHandler.removeCallbacks(mediaRefreshRunnable);\n"
    "        mediaHandler.post(mediaRefreshRunnable);\n\n"
    "        LinearLayout controls = row();",
    "add live media artwork row",
)

main = replace_once(
    main,
    "    private void addMediaSource(LinearLayout parent, String title, String key, String selected) {",
    "    private void openMediaNotificationAccess() {\n"
    "        try {\n"
    "            startActivity(new android.content.Intent(android.provider.Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS));\n"
    "        } catch (RuntimeException ex) {\n"
    "            Toast.makeText(this, \"Enable NeoDash media access in Android Settings\", Toast.LENGTH_LONG).show();\n"
    "        }\n"
    "    }\n\n"
    "    private void updateActiveMediaSession() {\n"
    "        if (albumArtView == null || mediaTitleView == null || mediaArtistView == null) return;\n"
    "        try {\n"
    "            android.media.session.MediaSessionManager manager = (android.media.session.MediaSessionManager) getSystemService(android.content.Context.MEDIA_SESSION_SERVICE);\n"
    "            if (manager == null) return;\n"
    "            android.content.ComponentName listener = new android.content.ComponentName(this, NeoDashMediaNotificationListener.class);\n"
    "            java.util.List<android.media.session.MediaController> sessions = manager.getActiveSessions(listener);\n"
    "            activeMediaController = null;\n"
    "            if (sessions != null) {\n"
    "                for (android.media.session.MediaController candidate : sessions) {\n"
    "                    android.media.session.PlaybackState state = candidate.getPlaybackState();\n"
    "                    if (activeMediaController == null) activeMediaController = candidate;\n"
    "                    if (state != null && (state.getState() == android.media.session.PlaybackState.STATE_PLAYING\n"
    "                            || state.getState() == android.media.session.PlaybackState.STATE_BUFFERING)) {\n"
    "                        activeMediaController = candidate;\n"
    "                        break;\n"
    "                    }\n"
    "                }\n"
    "            }\n"
    "            if (activeMediaController == null) {\n"
    "                mediaTitleView.setText(\"No active player\");\n"
    "                mediaArtistView.setText(\"Tap here to enable media access\");\n"
    "                albumArtView.setImageResource(android.R.drawable.ic_media_play);\n"
    "                albumArtView.setTag(null);\n"
    "                return;\n"
    "            }\n"
    "            android.media.MediaMetadata metadata = activeMediaController.getMetadata();\n"
    "            if (metadata == null) {\n"
    "                mediaTitleView.setText(activeMediaController.getPackageName());\n"
    "                mediaArtistView.setText(\"Waiting for track information\");\n"
    "                return;\n"
    "            }\n"
    "            String title = metadata.getString(android.media.MediaMetadata.METADATA_KEY_TITLE);\n"
    "            String artist = metadata.getString(android.media.MediaMetadata.METADATA_KEY_ARTIST);\n"
    "            if (title == null || title.trim().isEmpty()) title = metadata.getString(android.media.MediaMetadata.METADATA_KEY_DISPLAY_TITLE);\n"
    "            if (artist == null || artist.trim().isEmpty()) artist = metadata.getString(android.media.MediaMetadata.METADATA_KEY_ALBUM);\n"
    "            mediaTitleView.setText(title == null || title.trim().isEmpty() ? activeMediaController.getPackageName() : title);\n"
    "            mediaArtistView.setText(artist == null ? \"Now playing\" : artist);\n"
    "            android.graphics.Bitmap art = metadata.getBitmap(android.media.MediaMetadata.METADATA_KEY_ART);\n"
    "            if (art == null) art = metadata.getBitmap(android.media.MediaMetadata.METADATA_KEY_ALBUM_ART);\n"
    "            if (art == null) art = metadata.getBitmap(android.media.MediaMetadata.METADATA_KEY_DISPLAY_ICON);\n"
    "            if (art != null) {\n"
    "                albumArtView.setImageBitmap(art);\n"
    "                albumArtView.setTag(\"bitmap:\" + title);\n"
    "            } else {\n"
    "                String artUri = metadata.getString(android.media.MediaMetadata.METADATA_KEY_ART_URI);\n"
    "                if (artUri == null) artUri = metadata.getString(android.media.MediaMetadata.METADATA_KEY_ALBUM_ART_URI);\n"
    "                if (artUri == null) artUri = metadata.getString(android.media.MediaMetadata.METADATA_KEY_DISPLAY_ICON_URI);\n"
    "                if (artUri != null && !artUri.equals(String.valueOf(albumArtView.getTag()))) {\n"
    "                    albumArtView.setTag(artUri);\n"
    "                    final String requestedUri = artUri;\n"
    "                    new Thread(() -> {\n"
    "                        android.graphics.Bitmap decoded = null;\n"
    "                        try (java.io.InputStream input = getContentResolver().openInputStream(android.net.Uri.parse(requestedUri))) {\n"
    "                            if (input != null) decoded = android.graphics.BitmapFactory.decodeStream(input);\n"
    "                        } catch (Exception ignored) { }\n"
    "                        final android.graphics.Bitmap result = decoded;\n"
    "                        runOnUiThread(() -> {\n"
    "                            if (albumArtView != null && requestedUri.equals(albumArtView.getTag())) {\n"
    "                                if (result != null) albumArtView.setImageBitmap(result);\n"
    "                                else albumArtView.setImageResource(android.R.drawable.ic_media_play);\n"
    "                            }\n"
    "                        });\n"
    "                    }).start();\n"
    "                } else if (artUri == null) {\n"
    "                    albumArtView.setImageResource(android.R.drawable.ic_media_play);\n"
    "                    albumArtView.setTag(null);\n"
    "                }\n"
    "            }\n"
    "        } catch (SecurityException denied) {\n"
    "            activeMediaController = null;\n"
    "            mediaTitleView.setText(\"Media access not enabled\");\n"
    "            mediaArtistView.setText(\"Tap here to enable media access\");\n"
    "            albumArtView.setImageResource(android.R.drawable.ic_media_play);\n"
    "            albumArtView.setTag(null);\n"
    "        } catch (RuntimeException ignored) {\n"
    "            activeMediaController = null;\n"
    "        }\n"
    "    }\n\n"
    "    private void addMediaSource(LinearLayout parent, String title, String key, String selected) {",
    "add active media session reader",
)

main = replace_once(
    main,
    "    private void addTransportButton(LinearLayout parent, String title, int keyCode) {\n"
    "        TextView button = label(title, 9, WHITE, true);\n"
    "        button.setGravity(Gravity.CENTER);\n"
    "        button.setPadding(dp(7), 0, dp(7), 0);\n"
    "        button.setBackground(panel(Color.rgb(12, 26, 38), LINE, 9));\n"
    "        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(0, dp(38), title.equals(\"PLAY / PAUSE\") ? 1.35f : 0.8f);\n"
    "        p.setMargins(dp(2), 0, dp(2), 0);\n"
    "        parent.addView(button, p);\n"
    "        button.setOnClickListener(v -> dispatchMediaKey(keyCode));\n"
    "    }",
    "    private void addTransportButton(LinearLayout parent, String title, int keyCode) {\n"
    "        String glyph = keyCode == android.view.KeyEvent.KEYCODE_MEDIA_PREVIOUS ? \"⏮\"\n"
    "                : keyCode == android.view.KeyEvent.KEYCODE_MEDIA_NEXT ? \"⏭\" : \"⏯\";\n"
    "        TextView button = label(glyph, 21, CYAN, true);\n"
    "        button.setGravity(Gravity.CENTER);\n"
    "        button.setContentDescription(title);\n"
    "        button.setBackground(panel(Color.rgb(12, 26, 38), LINE, 9));\n"
    "        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(0, dp(42), title.equals(\"PLAY / PAUSE\") ? 1.2f : 1f);\n"
    "        p.setMargins(dp(2), 0, dp(2), 0);\n"
    "        parent.addView(button, p);\n"
    "        button.setOnClickListener(v -> dispatchMediaKey(keyCode));\n"
    "    }",
    "replace transport text with icons",
)

main = replace_once(
    main,
    "    private void dispatchMediaKey(int keyCode) {\n"
    "        try {\n"
    "            AudioManager audio = (AudioManager) getSystemService(AUDIO_SERVICE);",
    "    private void dispatchMediaKey(int keyCode) {\n"
    "        try {\n"
    "            if (activeMediaController != null) {\n"
    "                android.media.session.MediaController.TransportControls transport = activeMediaController.getTransportControls();\n"
    "                if (keyCode == android.view.KeyEvent.KEYCODE_MEDIA_PREVIOUS) transport.skipToPrevious();\n"
    "                else if (keyCode == android.view.KeyEvent.KEYCODE_MEDIA_NEXT) transport.skipToNext();\n"
    "                else {\n"
    "                    android.media.session.PlaybackState state = activeMediaController.getPlaybackState();\n"
    "                    if (state != null && state.getState() == android.media.session.PlaybackState.STATE_PLAYING) transport.pause();\n"
    "                    else transport.play();\n"
    "                }\n"
    "                return;\n"
    "            }\n"
    "            AudioManager audio = (AudioManager) getSystemService(AUDIO_SERVICE);",
    "send controls to active media session",
)

MAIN.write_text(main, encoding="utf-8")

# Notification-listener access is the supported third-party route to active media sessions.
listener_java = JAVA / "NeoDashMediaNotificationListener.java"
listener_java.write_text(
    "package com.neodash.launcher;\n\n"
    "public class NeoDashMediaNotificationListener extends android.service.notification.NotificationListenerService {\n"
    "    @Override public void onNotificationPosted(android.service.notification.StatusBarNotification sbn) { }\n"
    "    @Override public void onNotificationRemoved(android.service.notification.StatusBarNotification sbn) { }\n"
    "}\n",
    encoding="utf-8",
)
manifest = MANIFEST.read_text(encoding="utf-8")
service_entry = (
    '        <service android:name=".NeoDashMediaNotificationListener" '
    'android:label="NeoDash media access" '
    'android:permission="android.permission.BIND_NOTIFICATION_LISTENER_SERVICE" '
    'android:exported="true">'
    '<intent-filter><action android:name="android.service.notification.NotificationListenerService" /></intent-filter>'
    '</service>\n'
)
if "NeoDashMediaNotificationListener" not in manifest:
    manifest = manifest.replace("</application>", service_entry + "    </application>", 1)
    MANIFEST.write_text(manifest, encoding="utf-8")

print("Map WebView renderer enabled; active media metadata/artwork and icon transport controls installed.")


# --- Quick-launch tiles: let the app artwork use the full tile body. ---
main = MAIN.read_text(encoding="utf-8")
shortcut_start = main.index("private void addShortcut(")
shortcut_end = main.find("\n    private ", shortcut_start + 1)
if shortcut_start < 0 or shortcut_end < 0:
    raise SystemExit("Could not locate addShortcut method")
shortcut_block = main[shortcut_start:shortcut_end]
if "tile.setPadding(dp(7), dp(8), dp(7), dp(8));" not in shortcut_block:
    raise SystemExit("Could not locate addShortcut tile padding")
shortcut_block = shortcut_block.replace(
    "tile.setPadding(dp(7), dp(8), dp(7), dp(8));",
    "tile.setPadding(dp(1), dp(1), dp(1), dp(1));",
    1,
)
main = main[:shortcut_start] + shortcut_block + main[shortcut_end:]
custom_icon_old = (
    "            int iconWidth = iconScale == 0 ? 44 : (iconScale == 2 ? 58 : 52);\n"
    "            LinearLayout.LayoutParams iconParams = new LinearLayout.LayoutParams(dp(iconWidth), 0, 1);\n"
    "            iconParams.gravity = Gravity.CENTER;\n"
    "            tile.addView(icon, iconParams);"
)
custom_icon_new = (
    "            LinearLayout.LayoutParams iconParams = new LinearLayout.LayoutParams(-1, 0, 1);\n"
    "            tile.addView(icon, iconParams);"
)
if custom_icon_old not in shortcut_block:
    raise SystemExit("Could not locate custom app artwork layout in addShortcut")
shortcut_block = shortcut_block.replace(custom_icon_old, custom_icon_new)

installed_icon_old = (
    "            icon.setScaleType(ImageView.ScaleType.FIT_CENTER);\n"
    "            int iconDp = iconScale == 0 ? 34 : (iconScale == 2 ? 52 : 43);\n"
    "            LinearLayout.LayoutParams imageParams = new LinearLayout.LayoutParams(dp(iconDp), 0, 1);\n"
    "            imageParams.gravity = Gravity.CENTER;\n"
    "            tile.addView(icon, imageParams);"
)
installed_icon_new = (
    "            icon.setScaleType(ImageView.ScaleType.FIT_CENTER);\n"
    "            LinearLayout.LayoutParams imageParams = new LinearLayout.LayoutParams(-1, 0, 1);\n"
    "            tile.addView(icon, imageParams);"
)
if installed_icon_old not in shortcut_block:
    raise SystemExit("Could not locate installed app icon layout in addShortcut")
shortcut_block = shortcut_block.replace(installed_icon_old, installed_icon_new)
main = main[:shortcut_start] + shortcut_block + main[shortcut_end:]

# --- Remove embedded map rendering and all OSM URL/location-preview code. ---
# Remove every remaining WebView-backed map-pane implementation detail. The
# navigation shortcut still launches the selected external navigation package.
main = MAIN.read_text(encoding="utf-8")
main = re.sub(r"(?m)^\s*private WebView mapWebView;\s*\n", "", main)
main = re.sub(r"(?m)^\s*private double mapLatitude = Double\.NaN;\s*\n", "", main)
main = re.sub(r"(?m)^\s*private double mapLongitude = Double\.NaN;\s*\n", "", main)
main = re.sub(
    r"(?ms)^\s*mapWebView = new WebView\(this\);.*?mapPane\.addView\(mapWebView, new LinearLayout\.LayoutParams\(-1, 0, 1\)\);\s*",
    '            TextView navigationInfo = label("NAVIGATION OPENS IN YOUR SELECTED APP", 10, MUTED, true);\n'
    '            navigationInfo.setGravity(Gravity.CENTER);\n'
    '            mapPane.addView(navigationInfo, new LinearLayout.LayoutParams(-1, 0, 1));\n',
    main,
    count=1,
)
main = re.sub(r'(?m)^\s*mapPane\.addView\(mapNote, mn\);\s*\n?', "", main)
main = re.sub(r'(?m)^\s*TextView mapNote = label\([^\n]*\);\s*\n?', "", main)
main = re.sub(
    r"(?ms)^\s*if \(Double\.isNaN\(mapLatitude\).*?^\s*}\s*\n",
    "",
    main,
    count=1,
)

# Final defensive sweep: remove map-specific methods/calls regardless of indentation
# or surrounding layout changes made by the baseline patch.
main = re.sub(r"(?s)    private String buildEmbeddedMapUrl\\(\\) \\{.*?\\n    \\}\\n", "", main, count=1)
main = re.sub(r"(?s)    private void requestFreshMapLocation\\(\\) \\{.*?\\n    \\}\\n", "", main, count=1)
main = re.sub(r"(?m)^.*mapWebView\\.loadUrl\\([^\\n]*\\);\\s*\\n?", "", main)
main = re.sub(r"(?m)^.*requestFreshMapLocation\\(\\);\\s*\\n?", "", main)
main = re.sub(r"(?m)^.*buildEmbeddedMapUrl\\(\\);\\s*\\n?", "", main)
main = re.sub(r"(?m)^\\s*private WebView mapWebView;\\s*\\n?", "", main)
main = re.sub(r"(?m)^\\s*private double mapLatitude = Double\\.NaN;\\s*\\n?", "", main)
main = re.sub(r"(?m)^\\s*private double mapLongitude = Double\\.NaN;\\s*\\n?", "", main)
main = re.sub(r"(?m)^.*mapWebView\\.setBackgroundColor\\([^\\n]*\\);\\s*\\n?", "", main)
main = re.sub(r"(?m)^.*mapWebView\\.getSettings\\(\\);\\s*\\n?", "", main)
main = re.sub(r"(?m)^.*mapWebView\\.setWebViewClient\\([^\\n]*\\);\\s*\\n?", "", main)
main = re.sub(r"(?m)^.*mapPane\\.addView\\(mapWebView[^\\n]*\\);\\s*\\n?", "", main)
main = re.sub(r"(?m)^.*TextView mapNote = label\\([^\\n]*\\);\\s*\\n?", "", main)
main = re.sub(r"(?m)^.*mapPane\\.addView\\(mapNote[^\\n]*\\);\\s*\\n?", "", main)

remaining_map_refs = [(i + 1, line) for i, line in enumerate(main.splitlines())
                     if re.search(r"openstreetmap|buildEmbeddedMapUrl|mapWebView|mapNote|mapLatitude|mapLongitude", line, re.I)]
if remaining_map_refs:
    print("MAP/OSM REFERENCES AFTER CLEANUP:")
    for line_no, line in remaining_map_refs:
        print(f"{line_no}: {line}")
    raise SystemExit("Embedded map cleanup incomplete; inspect references above")
MAIN.write_text(main, encoding="utf-8")
print("Removed all embedded map WebView code; navigation remains external-app only.")

main = MAIN.read_text(encoding="utf-8")
main = re.sub(
    r"    private String buildEmbeddedMapUrl\(\) \{.*?\n    \}\n\n",
    "",
    main,
    count=1,
    flags=re.S,
)
main = re.sub(
    r"    private void requestFreshMapLocation\(\) \{.*?\n    \}\n\n",
    "",
    main,
    count=1,
    flags=re.S,
)
main = main.replace("            mapWebView.loadUrl(buildEmbeddedMapUrl());\n", "")
main = main.replace("            requestFreshMapLocation();\n", "")
main = main.replace('        TextView mapNote = label("MAP PANEL: OpenStreetMap  ·  NAVIGATION: YOUR SELECTED APP", 8, MUTED, false);\n', "")
remaining_map_refs = [(i + 1, line) for i, line in enumerate(main.splitlines())
                     if re.search(r"openstreetmap|buildEmbeddedMapUrl|mapWebView|mapNote|mapLatitude|mapLongitude", line, re.I)]
if remaining_map_refs:
    print("MAP/OSM REFERENCES AFTER CLEANUP:")
    for line_no, line in remaining_map_refs:
        print(f"{line_no}: {line}")
    raise SystemExit("Embedded map cleanup incomplete; inspect references above")
MAIN.write_text(main, encoding="utf-8")
print("Removed embedded map URL builder, OSM references and map-specific location refresh code.")
 
# --- Notification access: deep-link to NeoDash and make the grant state explicit. ---
main = replace_once(
    main,
    "    private android.widget.TextView mediaTitleView, mediaArtistView;\n",
    "    private android.widget.TextView mediaTitleView, mediaArtistView, mediaAccessButton;\n",
    "add media access action view",
)
main = replace_once(
    main,
    "        hub.addView(mediaInfo, new LinearLayout.LayoutParams(-1, dp(62)));\n",
    "        hub.addView(mediaInfo, new LinearLayout.LayoutParams(-1, dp(62)));\n"
    "        mediaAccessButton = label(\"ENABLE MEDIA ACCESS  ↗\", 10, BG, true);\n"
    "        mediaAccessButton.setGravity(Gravity.CENTER);\n"
    "        mediaAccessButton.setBackground(panel(CYAN, CYAN, 9));\n"
    "        LinearLayout.LayoutParams accessParams = new LinearLayout.LayoutParams(-1, dp(32));\n"
    "        accessParams.topMargin = dp(5);\n"
    "        hub.addView(mediaAccessButton, accessParams);\n"
    "        mediaAccessButton.setOnClickListener(v -> openMediaNotificationAccess());\n"
    "        mediaAccessButton.setVisibility(hasMediaNotificationAccess() ? View.GONE : View.VISIBLE);\n",
    "add explicit media access grant button",
)
main = replace_once(
    main,
    "    private void openMediaNotificationAccess() {\n"
    "        try {\n"
    "            startActivity(new android.content.Intent(android.provider.Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS));\n"
    "        } catch (RuntimeException ex) {\n"
    "            Toast.makeText(this, \"Enable NeoDash media access in Android Settings\", Toast.LENGTH_LONG).show();\n"
    "        }\n"
    "    }",
    "    private boolean hasMediaNotificationAccess() {\n"
    "        android.content.ComponentName listener = new android.content.ComponentName(this, NeoDashMediaNotificationListener.class);\n"
    "        try {\n"
    "            if (android.os.Build.VERSION.SDK_INT >= 27) {\n"
    "                android.app.NotificationManager nm = (android.app.NotificationManager) getSystemService(NOTIFICATION_SERVICE);\n"
    "                return nm != null && nm.isNotificationListenerAccessGranted(listener);\n"
    "            }\n"
    "            String enabled = android.provider.Settings.Secure.getString(getContentResolver(), \"enabled_notification_listeners\");\n"
    "            return enabled != null && enabled.contains(listener.flattenToString());\n"
    "        } catch (RuntimeException ignored) { return false; }\n"
    "    }\n\n"
    "    private void openMediaNotificationAccess() {\n"
    "        android.content.ComponentName listener = new android.content.ComponentName(this, NeoDashMediaNotificationListener.class);\n"
    "        try {\n"
    "            android.content.Intent intent;\n"
    "            if (android.os.Build.VERSION.SDK_INT >= 30) {\n"
    "                intent = new android.content.Intent(\"android.settings.NOTIFICATION_LISTENER_DETAIL_SETTINGS\");\n"
    "                intent.putExtra(\"android.provider.extra.NOTIFICATION_LISTENER_COMPONENT_NAME\", listener);\n"
    "            } else {\n"
    "                intent = new android.content.Intent(android.provider.Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS);\n"
    "                new AlertDialog.Builder(this).setTitle(\"Enable NeoDash media access\")\n"
    "                    .setMessage(\"On the next screen, find NeoDash and turn on Allow notification access. Then return to NeoDash.\")\n"
    "                    .setPositiveButton(\"OPEN SETTINGS\", (dialog, which) -> { try { startActivity(intent); } catch (RuntimeException ignored) { } })\n"
    "                    .setNegativeButton(\"CANCEL\", null).show();\n"
    "                return;\n"
    "            }\n"
    "            startActivity(intent);\n"
    "        } catch (RuntimeException ex) {\n"
    "            try { startActivity(new android.content.Intent(android.provider.Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS)); }\n"
    "            catch (RuntimeException ignored) { Toast.makeText(this, \"Open Android Settings → Notification access → NeoDash\", Toast.LENGTH_LONG).show(); }\n"
    "        }\n"
    "    }",
    "deep-link to NeoDash notification access",
)
main = replace_once(
    main,
    "        if (albumArtView == null || mediaTitleView == null || mediaArtistView == null) return;\n"
    "        try {",
    "        if (albumArtView == null || mediaTitleView == null || mediaArtistView == null) return;\n"
    "        boolean mediaGranted = hasMediaNotificationAccess();\n"
    "        if (mediaAccessButton != null) mediaAccessButton.setVisibility(mediaGranted ? View.GONE : View.VISIBLE);\n"
    "        if (!mediaGranted) {\n"
    "            activeMediaController = null;\n"
    "            mediaTitleView.setText(\"Media access required\");\n"
    "            mediaArtistView.setText(\"Enable NeoDash in Android notification access\");\n"
    "            albumArtView.setImageResource(android.R.drawable.ic_media_play);\n"
    "            albumArtView.setTag(null);\n"
    "            return;\n"
    "        }\n"
    "        try {",
    "check media access before querying sessions",
)
# Add an immediate refresh after returning from Android Settings.
main = replace_once(
    main,
    "    @Override protected void onResume() {\n"
    "        super.onResume();\n",
    "    @Override protected void onResume() {\n"
    "        super.onResume();\n"
    "        if (mediaHandler != null) { mediaHandler.removeCallbacks(mediaRefreshRunnable); mediaHandler.post(mediaRefreshRunnable); }\n",
    "refresh media permission and metadata on resume",
)
MAIN.write_text(main, encoding="utf-8")
print("Full-tile app icons, fresh GPS-only map centering, selected nav app labeling, and direct media-access setup applied.")


# --- NeoDash UI 0.4.1: readable typography and refined touch-first surfaces. ---
main = MAIN.read_text(encoding="utf-8")
label_match = re.search(
    r"    private TextView label\([^)]*\) \{.*?\n    \}",
    main,
    flags=re.S,
)
if not label_match:
    raise SystemExit("UI typography: could not locate label helper")
label_block = label_match.group(0)
if "NEODASH_UI_041_TYPOGRAPHY" not in label_block:
    return_line = re.search(r"(?m)^\s*return v;\s*$", label_block)
    if not return_line:
        raise SystemExit("UI typography: could not locate label return")
    typography = (
        "        // NEODASH_UI_041_TYPOGRAPHY: readable on older 7-inch head-unit displays.\n"
        "        float readableSp = size <= 9 ? 10.5f : (size <= 12 ? 12.0f : size);\n"
        "        v.setTextSize(android.util.TypedValue.COMPLEX_UNIT_SP, readableSp);\n"
        "        v.setTypeface(Typeface.create(size >= 30 ? \"sans-serif-light\" : (bold ? \"sans-serif-medium\" : \"sans-serif\"), Typeface.NORMAL));\n"
        "        v.setLetterSpacing(size >= 30 ? -0.012f : 0.012f);\n"
    )
    label_block = label_block[:return_line.start()] + typography + label_block[return_line.start():]
    main = main[:label_match.start()] + label_block + main[label_match.end():]

# Give the dashboard clock a little more presence without crowding the pane.
main = replace_once(
    main,
    'clockView = label("--:--", 56, WHITE, true);',
    'clockView = label("--:--", 60, WHITE, true);',
    "refine dashboard clock hierarchy",
)

# Increase the visual breathing room in the media strip and make its metadata easier to scan.
main = replace_once(
    main,
    'mediaTitleView = label("No active player", 11, WHITE, true);',
    'mediaTitleView = label("No active player", 13, WHITE, true);',
    "improve media title legibility",
)
main = replace_once(
    main,
    'mediaArtistView = label("Start music on your connected device", 9, MUTED, false);',
    'mediaArtistView = label("Start music on your connected device", 11, MUTED, false);',
    "improve media subtitle legibility",
)
main = replace_once(
    main,
    'TextView caption = label(name.toUpperCase(Locale.getDefault()), iconScale == 0 ? 9 : 10, WHITE, true);',
    'TextView caption = label(name.toUpperCase(Locale.getDefault()), iconScale == 0 ? 10 : 11, WHITE, true);',
    "improve shortcut caption legibility",
)
main = replace_once(
    main,
    'TextView pageLabel = label((shortcutPage + 1) + " / " + pageCount, 8, MUTED, true);',
    'TextView pageLabel = label((shortcutPage + 1) + " / " + pageCount, 10, MUTED, true);',
    "improve shortcut page indicator legibility",
)

# Slightly stronger visual separation while preserving the existing NeoDash palette.
main = main.replace(
    "left.setBackground(panel(PANEL, LINE, 18));",
    "left.setBackground(panel(PANEL, Color.rgb(49, 101, 135), 20));",
)
main = main.replace(
    "tile.setBackground(panel(featured ? Color.rgb(13, 33, 51) : PANEL_HI, stroke, 17));",
    "tile.setBackground(panel(featured ? Color.rgb(15, 38, 57) : PANEL_HI, stroke, 19));",
)
MAIN.write_text(main, encoding="utf-8")
print("NeoDash 0.4.1 typography and touch-first UI polish applied.")
