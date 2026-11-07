package com.neodash.neolink.service;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.Service;
import android.bluetooth.BluetoothDevice;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.hardware.usb.UsbDevice;
import android.hardware.usb.UsbManager;
import android.os.Binder;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.os.Message;
import android.os.Messenger;
import android.os.RemoteException;
import android.net.ConnectivityManager;
import android.net.Network;
import android.net.NetworkCapabilities;
import android.net.NetworkRequest;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public final class NeoLinkService extends Service {
    public static final String ACTION_BIND = "com.neodash.neolink.action.BIND";
    public static final int MSG_GET_STATE = 1;
    public static final int MSG_STATE = 2;
    public static final int MSG_EVENT = 3;
    public static final int MSG_REGISTER_CLIENT = 4;
    public static final int MSG_UNREGISTER_CLIENT = 5;
    public static final String EXTRA_STATE_JSON = "state_json";

    private static final String CHANNEL_ID = "neolink_connection";
    private final List<Messenger> clients = new ArrayList<>();
    private final Handler handler = new Handler(Looper.getMainLooper(), this::handleMessage);
    private final Messenger messenger = new Messenger(handler);
    private final Object lock = new Object();

    private String transport = "none";
    private String deviceName = null;
    private String platform = "unknown";
    private String linkState = "disconnected";
    private String projectionState = "unknown";
    private String lastEvent = "service_started";
    private long updatedAt = System.currentTimeMillis();
    private boolean receiversRegistered;
    private ConnectivityManager connectivityManager;
    private ConnectivityManager.NetworkCallback wifiCallback;
    private final Set<Network> wifiNetworks = new HashSet<>();

    private final BroadcastReceiver deviceReceiver = new BroadcastReceiver() {
        @Override public void onReceive(Context context, Intent intent) {
            String action = intent.getAction();
            if (BluetoothDevice.ACTION_ACL_CONNECTED.equals(action)) {
                BluetoothDevice device = getBluetoothDevice(intent);
                synchronized (lock) {
                    transport = "bluetooth";
                    deviceName = safeDeviceName(device);
                    platform = "unknown";
                    linkState = "paired_candidate";
                    projectionState = "unknown";
                    lastEvent = "bluetooth_link_connected";
                }
                publish();
            } else if (BluetoothDevice.ACTION_ACL_DISCONNECTED.equals(action)) {
                synchronized (lock) {
                    transport = "none";
                    deviceName = null;
                    platform = "unknown";
                    linkState = "disconnected";
                    projectionState = "ended";
                    lastEvent = "bluetooth_link_disconnected";
                }
                publish();
            } else if (UsbManager.ACTION_USB_DEVICE_ATTACHED.equals(action)) {
                UsbDevice device = getUsbDevice(intent);
                synchronized (lock) {
                    transport = "usb";
                    deviceName = device == null ? "USB device" : "USB " + device.getVendorId() + ":" + device.getProductId();
                    platform = device != null && device.getVendorId() == 0x05AC ? "ios" : "unknown";
                    linkState = "connected";
                    projectionState = "unknown";
                    lastEvent = "usb_device_attached";
                }
                publish();
            } else if (UsbManager.ACTION_USB_DEVICE_DETACHED.equals(action)) {
                synchronized (lock) {
                    transport = "none";
                    deviceName = null;
                    platform = "unknown";
                    linkState = "disconnected";
                    projectionState = "ended";
                    lastEvent = "usb_device_detached";
                }
                publish();
            }
        }
    };

    @Override public void onCreate() {
        super.onCreate();
        createNotificationChannel();
        Notification notification = buildNotification();
        try {
            if (Build.VERSION.SDK_INT >= 29) {
                startForeground(41, notification, android.content.pm.ServiceInfo.FOREGROUND_SERVICE_TYPE_CONNECTED_DEVICE);
            } else {
                startForeground(41, notification);
            }
        } catch (SecurityException denied) {
            stopSelf();
            return;
        }
        registerDeviceReceivers();
        registerWifiCallback();
        publish();
    }

    private void registerDeviceReceivers() {
        if (receiversRegistered) return;
        IntentFilter filter = new IntentFilter();
        filter.addAction(BluetoothDevice.ACTION_ACL_CONNECTED);
        filter.addAction(BluetoothDevice.ACTION_ACL_DISCONNECTED);
        filter.addAction(UsbManager.ACTION_USB_DEVICE_ATTACHED);
        filter.addAction(UsbManager.ACTION_USB_DEVICE_DETACHED);
        if (Build.VERSION.SDK_INT >= 33) registerReceiver(deviceReceiver, filter, Context.RECEIVER_NOT_EXPORTED);
        else registerReceiver(deviceReceiver, filter);
        receiversRegistered = true;
    }

    private void registerWifiCallback() {
        connectivityManager = (ConnectivityManager) getSystemService(CONNECTIVITY_SERVICE);
        if (connectivityManager == null) return;
        wifiCallback = new ConnectivityManager.NetworkCallback() {
            @Override public void onAvailable(Network network) {
                synchronized (lock) { wifiNetworks.add(network); }
                publish();
            }
            @Override public void onCapabilitiesChanged(Network network, NetworkCapabilities caps) {
                synchronized (lock) {
                    if (caps.hasTransport(NetworkCapabilities.TRANSPORT_WIFI)) wifiNetworks.add(network);
                    else wifiNetworks.remove(network);
                }
                publish();
            }
            @Override public void onLost(Network network) {
                synchronized (lock) { wifiNetworks.remove(network); }
                publish();
            }
        };
        try {
            NetworkRequest request = new NetworkRequest.Builder()
                .addTransportType(NetworkCapabilities.TRANSPORT_WIFI)
                .build();
            connectivityManager.registerNetworkCallback(request, wifiCallback);
        } catch (RuntimeException ignored) { wifiCallback = null; }
    }

    private BluetoothDevice getBluetoothDevice(Intent intent) {
        if (Build.VERSION.SDK_INT >= 33) return intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE, BluetoothDevice.class);
        return intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE);
    }

    private UsbDevice getUsbDevice(Intent intent) {
        if (Build.VERSION.SDK_INT >= 33) return intent.getParcelableExtra(UsbManager.EXTRA_DEVICE, UsbDevice.class);
        return intent.getParcelableExtra(UsbManager.EXTRA_DEVICE);
    }

    private String safeDeviceName(BluetoothDevice device) {
        if (device == null) return "Bluetooth device";
        try { return device.getName(); } catch (SecurityException ignored) { return "Bluetooth device"; }
    }

    private boolean handleMessage(Message message) {
        if (message.what == MSG_REGISTER_CLIENT) {
            if (message.replyTo != null && !clients.contains(message.replyTo)) clients.add(message.replyTo);
            sendSnapshot(message.replyTo, MSG_STATE);
            return true;
        }
        if (message.what == MSG_UNREGISTER_CLIENT) {
            if (message.replyTo != null) clients.remove(message.replyTo);
            return true;
        }
        if (message.what == MSG_GET_STATE) {
            sendSnapshot(message.replyTo, MSG_STATE);
            return true;
        }
        return false;
    }

    private void sendSnapshot(Messenger target, int what) {
        if (target == null) return;
        try {
            Message reply = Message.obtain(null, what);
            Bundle data = new Bundle();
            data.putString(EXTRA_STATE_JSON, snapshot().toString());
            reply.setData(data);
            target.send(reply);
        } catch (RemoteException ignored) { }
    }

    private JSONObject snapshot() {
        synchronized (lock) {
            JSONObject root = new JSONObject();
            JSONObject connection = new JSONObject();
            JSONObject receiver = new JSONObject();
            try {
                root.put("schema_version", 1);
                root.put("manager", "neolink");
                root.put("service_state", "running");
                root.put("wifi_network_available", !wifiNetworks.isEmpty());
                connection.put("transport", transport);
                connection.put("device_name", deviceName == null ? JSONObject.NULL : deviceName);
                connection.put("platform", platform);
                connection.put("link_state", linkState);
                connection.put("projection_state", projectionState);
                receiver.put("ios_package", getSharedPreferences("receivers", MODE_PRIVATE).getString("ios_package", null));
                receiver.put("android_package", getSharedPreferences("receivers", MODE_PRIVATE).getString("android_package", null));
                receiver.put("selected_package", platform.equals("ios")
                    ? getSharedPreferences("receivers", MODE_PRIVATE).getString("ios_package", null)
                    : platform.equals("android") ? getSharedPreferences("receivers", MODE_PRIVATE).getString("android_package", null) : null);
                root.put("connection", connection);
                root.put("receiver", receiver);
                root.put("last_event", lastEvent);
                root.put("updated_at_epoch_ms", updatedAt);
            } catch (JSONException ignored) { }
            return root;
        }
    }

    private void publish() {
        synchronized (lock) {
            updatedAt = System.currentTimeMillis();
            getSharedPreferences("neolink_state", MODE_PRIVATE).edit().putString("last_state", snapshot().toString()).apply();
        }
        Bundle data = new Bundle();
        data.putString(EXTRA_STATE_JSON, snapshot().toString());
        for (Messenger client : new ArrayList<>(clients)) {
            try {
                Message event = Message.obtain(null, MSG_EVENT);
                event.setData(data);
                client.send(event);
            } catch (RemoteException dead) {
                clients.remove(client);
            }
        }
    }

    private boolean handleMessageCompat(Message message) { return false; }

    private Notification buildNotification() {
        if (Build.VERSION.SDK_INT >= 26) {
            return new Notification.Builder(this, CHANNEL_ID)
                .setContentTitle("NeoLink is running")
                .setContentText("Monitoring supported phone connection events")
                .setSmallIcon(android.R.drawable.stat_sys_data_bluetooth)
                .setOngoing(true)
                .build();
        }
        return new Notification.Builder(this)
            .setContentTitle("NeoLink is running")
            .setContentText("Monitoring supported phone connection events")
            .setSmallIcon(android.R.drawable.stat_sys_data_bluetooth)
            .setOngoing(true)
            .build();
    }

    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= 26) {
            NotificationChannel channel = new NotificationChannel(CHANNEL_ID, "NeoLink connection manager", NotificationManager.IMPORTANCE_LOW);
            getSystemService(NotificationManager.class).createNotificationChannel(channel);
        }
    }

    @Override public IBinder onBind(Intent intent) { return messenger.getBinder(); }

    @Override public int onStartCommand(Intent intent, int flags, int startId) { return START_STICKY; }

    @Override public void onDestroy() {
        if (receiversRegistered) {
            try { unregisterReceiver(deviceReceiver); } catch (IllegalArgumentException ignored) { }
        }
        if (connectivityManager != null && wifiCallback != null) {
            try { connectivityManager.unregisterNetworkCallback(wifiCallback); } catch (RuntimeException ignored) { }
        }
        synchronized (lock) { wifiNetworks.clear(); }
        clients.clear();
        super.onDestroy();
    }
}
