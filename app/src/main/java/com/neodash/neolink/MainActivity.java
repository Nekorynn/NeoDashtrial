package com.neodash.neolink;

import android.Manifest;
import android.app.*;
import android.bluetooth.*;
import android.content.*;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.graphics.Typeface;
import android.os.*;
import android.view.Gravity;
import android.widget.*;
import java.util.*;

public final class MainActivity extends Activity {
 private static final int REQ_BT=71;
 private static final String ACTION_OPEN="com.neodash.neolink.action.OPEN_RECEIVER";
 private static final String DIPLAY="com.shihab.diplay.hudtest", DIAUTO="com.neodash.diauto";
 private static final int BG=Color.rgb(7,12,19), PANEL=Color.rgb(17,25,35), YELLOW=Color.rgb(223,255,0), CYAN=Color.rgb(83,207,255), MAGENTA=Color.rgb(255,65,165), WHITE=Color.rgb(240,245,250);
 private SharedPreferences prefs; private LinearLayout list;

 @Override public void onCreate(Bundle b) {
  super.onCreate(b); prefs=getSharedPreferences("neolink",MODE_PRIVATE);
  if(ACTION_OPEN.equals(getIntent().getAction())) { String r=getIntent().getStringExtra("receiver"); if("diplay".equalsIgnoreCase(r)){launch(DIPLAY);finish();return;} if("diauto".equalsIgnoreCase(r)){launch(DIAUTO);finish();return;} }
  buildUi(); refresh();
 }
 private void buildUi(){
  LinearLayout root=new LinearLayout(this); root.setOrientation(1); root.setPadding(dp(22),dp(16),dp(22),dp(16)); root.setBackgroundColor(BG);
  TextView title=text("NEOLINK",25,YELLOW,true); root.addView(title);
  TextView sub=text("PHONE CONNECTIONS",11,CYAN,true); sub.setLetterSpacing(.18f); root.addView(sub);
  LinearLayout actions=new LinearLayout(this);
  Button a=button("OPEN DIPLAY",YELLOW,BG); a.setOnClickListener(v->launch(DIPLAY));
  Button d=button("OPEN DIAUTO",MAGENTA,WHITE); d.setOnClickListener(v->launch(DIAUTO));
  actions.addView(a,new LinearLayout.LayoutParams(0,dp(54),1)); LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(0,dp(54),1);p.leftMargin=dp(10);actions.addView(d,p); root.addView(actions);
  TextView heading=text("PAIRED DEVICES",14,WHITE,true); heading.setPadding(0,dp(20),0,dp(8));root.addView(heading);
  ScrollView scroll=new ScrollView(this);list=new LinearLayout(this);list.setOrientation(1);scroll.addView(list);root.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
  Button refresh=button("REFRESH DEVICES",CYAN,BG);refresh.setOnClickListener(v->refresh());root.addView(refresh,new LinearLayout.LayoutParams(-1,dp(46)));
  TextView note=text("NeoLink launches receivers. DiPlay and Diauto handle the connection.",10,0xFF91A0AE,false);note.setGravity(Gravity.CENTER);root.addView(note);
  setContentView(root);
 }
 private void refresh(){
  if(list==null)return;list.removeAllViews();BluetoothAdapter bt=BluetoothAdapter.getDefaultAdapter();
  if(bt==null){info("Bluetooth unavailable");return;}
  if(Build.VERSION.SDK_INT>=31&&checkSelfPermission(Manifest.permission.BLUETOOTH_CONNECT)!=PackageManager.PERMISSION_GRANTED){requestPermissions(new String[]{Manifest.permission.BLUETOOTH_CONNECT},REQ_BT);info("Allow Nearby Devices to list paired phones.");return;}
  try {List<BluetoothDevice> ds=new ArrayList<>(bt.getBondedDevices());ds.sort((x,y)->name(x).compareToIgnoreCase(name(y)));if(ds.isEmpty()){info("No paired devices yet.");return;}for(BluetoothDevice x:ds)addDevice(x);}catch(SecurityException e){info("Bluetooth permission required.");}
 }
 private void addDevice(BluetoothDevice dev){
  String address=dev.getAddress(), type=prefs.getString("type_"+address,"");
  LinearLayout row=new LinearLayout(this);row.setOrientation(1);row.setPadding(dp(12),dp(9),dp(12),dp(9));row.setBackgroundColor(PANEL);
  row.addView(text(name(dev),15,WHITE,true));row.addView(text(type.isEmpty()?"Tap to assign receiver":("iPhone".equals(type)?"DiPlay · iPhone":"Diauto · Android"),11,"iPhone".equals(type)?YELLOW:CYAN,false));
  row.setOnClickListener(v->new AlertDialog.Builder(this).setTitle(name(dev)).setItems(new String[]{"iPhone · DiPlay","Android · Diauto","Clear assignment"},(dlg,n)->{String k="type_"+address;if(n==2)prefs.edit().remove(k).apply();else prefs.edit().putString(k,n==0?"iPhone":"Android").apply();refresh();if(n!=2)launch(n==0?DIPLAY:DIAUTO);}).show());
  LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);p.bottomMargin=dp(8);list.addView(row,p);
 }
 private void launch(String pkg){Intent i=getPackageManager().getLaunchIntentForPackage(pkg);if(i==null){Toast.makeText(this,"Receiver not installed: "+pkg,Toast.LENGTH_LONG).show();return;}i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);startActivity(i);}
 private void info(String s){TextView t=text(s,13,0xFF91A0AE,false);t.setPadding(dp(8),dp(14),dp(8),dp(14));list.addView(t);}
 private String name(BluetoothDevice d){try{String n=d.getName();return n==null||n.trim().isEmpty()?d.getAddress():n;}catch(SecurityException e){return "Paired device";}}
 private TextView text(String s,int size,int color,boolean bold){TextView t=new TextView(this);t.setText(s);t.setTextSize(size);t.setTextColor(color);if(bold)t.setTypeface(Typeface.DEFAULT,Typeface.BOLD);return t;}
 private Button button(String s,int bg,int fg){Button b=new Button(this);b.setText(s);b.setTextSize(12);b.setTextColor(fg);b.setTypeface(Typeface.DEFAULT,Typeface.BOLD);b.setBackgroundTintList(android.content.res.ColorStateList.valueOf(bg));return b;}
 private int dp(int n){return Math.round(n*getResources().getDisplayMetrics().density);}
 @Override public void onRequestPermissionsResult(int r,String[] p,int[] g){super.onRequestPermissionsResult(r,p,g);if(r==REQ_BT)refresh();}
}
