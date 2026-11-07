package com.neodash.neolink;

import android.Manifest;
import android.app.Activity;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.ServiceConnection;
import android.content.pm.PackageManager;
import android.content.pm.ResolveInfo;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.IBinder;
import android.os.Message;
import android.os.Messenger;
import android.os.RemoteException;
import android.view.Gravity;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.LinearLayout;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import com.neodash.neolink.service.NeoLinkService;

import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

public final class MainActivity extends Activity {
    private Messenger service;
    private final Messenger client = new Messenger(new Handler(msg -> {
        if (msg.what == NeoLinkService.MSG_STATE || msg.what == NeoLinkService.MSG_EVENT) {
            String json = msg.getData().getString(NeoLinkService.EXTRA_STATE_JSON, "{}");
            runOnUiThread(() -> renderState(json));
            return true;
        }
        return false;
    }));
    private TextView stateText;
    private Spinner iosSpinner, androidSpinner;
    private final List<String> packages = new ArrayList<>();
    private final List<String> labels = new ArrayList<>();

    private final ServiceConnection connection = new ServiceConnection() {
        @Override public void onServiceConnected(ComponentName name, IBinder binder) {
            service = new Messenger(binder);
            try { Message register = Message.obtain(null, NeoLinkService.MSG_REGISTER_CLIENT); register.replyTo = client; service.send(register); }
            catch (RemoteException ignored) { stateText.setText("Unable to subscribe to NeoLink events"); }
        }
        @Override public void onServiceDisconnected(ComponentName name) { service = null; stateText.setText("NeoLink service disconnected"); }
    };

    @Override protected void onCreate(Bundle saved) {
        super.onCreate(saved);
        buildUi();
        requestPermissionsIfNeeded();
    }

    private void requestPermissionsIfNeeded() {
        if (Build.VERSION.SDK_INT >= 31 && checkSelfPermission(Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.BLUETOOTH_CONNECT}, 10);
            return;
        }
        startManager();
        if (Build.VERSION.SDK_INT >= 33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, 11);
        }
    }

    private void startManager() {
        Intent manager = new Intent(this, NeoLinkService.class);
        try {
            if (Build.VERSION.SDK_INT >= 26) startForegroundService(manager); else startService(manager);
            bindService(manager, connection, Context.BIND_AUTO_CREATE);
        } catch (RuntimeException denied) {
            stateText.setText("NeoLink could not start. Check Bluetooth permission and Android background-start settings.");
        }
    }

    @Override public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == 10 && grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) startManager();
        else if (requestCode == 10) stateText.setText("Bluetooth permission is required for connection monitoring.");
    }

    private void buildUi() {
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(24, 24, 24, 24);
        root.setBackgroundColor(0xff080d16);
        setContentView(root);

        TextView title = label("NEOLINK", 28, 0xff53cfff);
        root.addView(title);
        TextView subtitle = label("CONNECTION MANAGER", 12, 0xff199bee);
        root.addView(subtitle);
        stateText = label("Waiting for service state…", 16, 0xffffffff);
        stateText.setPadding(0, 24, 0, 24);
        root.addView(stateText);

        root.addView(label("iOS / CarPlay receiver app", 14, 0xff53cfff));
        iosSpinner = new Spinner(this);
        root.addView(iosSpinner);
        root.addView(label("Android Auto receiver app", 14, 0xff53cfff));
        androidSpinner = new Spinner(this);
        root.addView(androidSpinner);

        TextView save = label("SAVE RECEIVER SELECTIONS", 14, 0xff080d16);
        save.setGravity(Gravity.CENTER);
        save.setBackgroundColor(0xff199bee);
        save.setPadding(12, 14, 12, 14);
        root.addView(save);
        save.setOnClickListener(v -> saveSelections());

        TextView note = label("Pairing is not projection. NeoLink waits for a supported session signal before any receiver launch.", 12, 0xffb7c8d8);
        note.setPadding(0, 24, 0, 0);
        root.addView(note);

        loadLaunchableApps();
    }

    private TextView label(String text, int size, int color) {
        TextView view = new TextView(this);
        view.setText(text);
        view.setTextSize(size);
        view.setTextColor(color);
        return view;
    }

    private void loadLaunchableApps() {
        Intent query = new Intent(Intent.ACTION_MAIN);
        query.addCategory(Intent.CATEGORY_LAUNCHER);
        List<ResolveInfo> apps = getPackageManager().queryIntentActivities(query, 0);
        packages.clear(); labels.clear();
        packages.add(""); labels.add("Select an installed app…");
        for (ResolveInfo info : apps) {
            String pkg = info.activityInfo.packageName;
            if (pkg.equals(getPackageName())) continue;
            packages.add(pkg);
            labels.add(info.loadLabel(getPackageManager()) + "  ·  " + pkg);
        }
        ArrayAdapter<String> adapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, labels);
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        iosSpinner.setAdapter(adapter);
        androidSpinner.setAdapter(adapter);
        String savedIos = getSharedPreferences("receivers", MODE_PRIVATE).getString("ios_package", "");
        String savedAndroid = getSharedPreferences("receivers", MODE_PRIVATE).getString("android_package", "");
        int iosIndex = packages.indexOf(savedIos);
        int androidIndex = packages.indexOf(savedAndroid);
        iosSpinner.setSelection(Math.max(0, iosIndex));
        androidSpinner.setSelection(Math.max(0, androidIndex));
    }

    private void saveSelections() {
        getSharedPreferences("receivers", MODE_PRIVATE).edit()
            .putString("ios_package", packages.get(iosSpinner.getSelectedItemPosition()))
            .putString("android_package", packages.get(androidSpinner.getSelectedItemPosition()))
            .apply();
        Toast.makeText(this, "Receiver selections saved", Toast.LENGTH_SHORT).show();
    }

    private void requestState() {
        if (service == null) return;
        try {
            Message request = Message.obtain(null, NeoLinkService.MSG_GET_STATE);
            request.replyTo = client;
            service.send(request);
        } catch (RemoteException ignored) { stateText.setText("Unable to read NeoLink state"); }
    }

    private void renderState(String json) {
        try {
            JSONObject root = new JSONObject(json);
            JSONObject connection = root.optJSONObject("connection");
            String transport = connection == null ? "unknown" : connection.optString("transport", "unknown");
            String link = connection == null ? "unknown" : connection.optString("link_state", "unknown");
            String platform = connection == null ? "unknown" : connection.optString("platform", "unknown");
            String projection = connection == null ? "unknown" : connection.optString("projection_state", "unknown");
            stateText.setText("SERVICE: " + root.optString("service_state", "unknown")
                + "\nTRANSPORT: " + transport
                + "\nDEVICE TYPE: " + platform
                + "\nLINK: " + link
                + "\nPROJECTION: " + projection);
        } catch (Exception ignored) { stateText.setText("NeoLink is running; state format not recognized"); }
    }

    @Override protected void onDestroy() {
        if (service != null) {
            try { Message unregister = Message.obtain(null, NeoLinkService.MSG_UNREGISTER_CLIENT); unregister.replyTo = client; service.send(unregister); }
            catch (RemoteException ignored) { }
        }
        try { unbindService(connection); } catch (IllegalArgumentException ignored) { }
        super.onDestroy();
    }
}
