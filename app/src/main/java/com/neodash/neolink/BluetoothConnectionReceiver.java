package com.neodash.neolink;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.bluetooth.BluetoothDevice;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Build;

public final class BluetoothConnectionReceiver extends BroadcastReceiver {
    private static final String CHANNEL = "neolink-phone-connections";
    private static final String DIPLAY = "com.shihab.diplay.hudtest";
    private static final String DIAUTO = "com.neodash.diauto";

    @Override public void onReceive(Context context, Intent intent) {
        if (intent == null || !BluetoothDevice.ACTION_ACL_CONNECTED.equals(intent.getAction())) return;
        BluetoothDevice device;
        if (Build.VERSION.SDK_INT >= 33) device = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE, BluetoothDevice.class);
        else device = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE);
        if (device == null) return;
        try {
            String address = device.getAddress();
            SharedPreferences prefs = context.getSharedPreferences("neolink", Context.MODE_PRIVATE);
            String type = prefs.getString("type_" + address, "");
            if (type.isEmpty()) return;
            String pkg = "iPhone".equals(type) ? DIPLAY : DIAUTO;
            Intent launch = context.getPackageManager().getLaunchIntentForPackage(pkg);
            if (launch == null) return;
            launch.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            PendingIntent pending = PendingIntent.getActivity(context, address.hashCode(), launch,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
            NotificationManager manager = (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);
            if (manager == null) return;
            if (Build.VERSION.SDK_INT >= 26) {
                manager.createNotificationChannel(new NotificationChannel(CHANNEL, "Phone connections", NotificationManager.IMPORTANCE_DEFAULT));
            }
            String name = device.getName();
            if (name == null || name.trim().isEmpty()) name = "Paired phone";
            String receiver = "iPhone".equals(type) ? "DiPlay" : "Diauto";
            Notification.Builder builder = Build.VERSION.SDK_INT >= 26
                ? new Notification.Builder(context, CHANNEL) : new Notification.Builder(context);
            Notification notification = builder
                .setSmallIcon(android.R.drawable.stat_sys_data_bluetooth)
                .setContentTitle(name + " connected")
                .setContentText("Tap to open " + receiver)
                .setContentIntent(pending)
                .setAutoCancel(true)
                .build();
            manager.notify(address.hashCode(), notification);
        } catch (SecurityException ignored) {
            // The user can still open and launch a receiver manually from NeoLink.
        }
    }
}
