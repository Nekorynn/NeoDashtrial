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
main = main.replace("NeoDashConnectionManager", "NeoDashSystemStatusService")
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
                neoLinkSummary = "NEOLINK: " + link + " / " + platform + " / " + transport;
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
    '    <uses-permission android:name="com.neodash.neolink.permission.BIND_SERVICE" />\n'
    '    <queries><package android:name="com.neodash.neolink" /></queries>\n',
    1,
)
MANIFEST.write_text(manifest, encoding="utf-8")

print("NeoDash/NeoLink architecture patch applied.")
