package com.neodash.launcher;

import android.app.*;
import android.os.*;
import android.content.*;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.view.*;
import android.widget.*;
import java.text.SimpleDateFormat;
import java.util.*;

public class MainActivity extends Activity {
    private final int BG = Color.rgb(8,10,16), PANEL = Color.rgb(17,22,34), BLUE = Color.rgb(22,139,255), CYAN = Color.rgb(0,217,255), PINK = Color.rgb(255,46,136), YELLOW = Color.rgb(245,227,66);
    private LinearLayout root, content, dock;
    private boolean neon = true;
    private TextView clock, date, status;
    private Handler handler = new Handler();
    private Runnable ticker;
    @Override public void onCreate(Bundle b) { super.onCreate(b); getWindow().getDecorView().setSystemUiVisibility(5894|1024|512); getWindow().setStatusBarColor(BG); getWindow().setNavigationBarColor(BG); buildHome(); startClock(); }
    private GradientDrawable shape(int color, int stroke) { GradientDrawable d=new GradientDrawable(); d.setColor(color); d.setCornerRadius(22); if(stroke!=0)d.setStroke(2,stroke); return d; }
    private TextView text(String s,int size,int color,boolean bold) { TextView t=new TextView(this); t.setText(s); t.setTextColor(color); t.setTextSize(size); t.setGravity(Gravity.CENTER_VERTICAL); if(bold)t.setTypeface(Typeface.DEFAULT,Typeface.BOLD); return t; }
    private LinearLayout column(){ LinearLayout l=new LinearLayout(this); l.setOrientation(1); return l; }
    private LinearLayout row(){ LinearLayout l=new LinearLayout(this); l.setOrientation(0); l.setGravity(Gravity.CENTER_VERTICAL); return l; }
    private void buildHome(){
        root=column(); root.setPadding(22,14,22,10); root.setBackgroundColor(BG); setContentView(root);
        LinearLayout header=row(); TextView brand=text("NEO",27,Color.WHITE,true); TextView dash=text("DASH",27,CYAN,true); header.addView(brand); header.addView(dash); View spacer=new View(this); header.addView(spacer,new LinearLayout.LayoutParams(0,1,1)); status=text("● SYSTEM READY   •   GPS STATUS NOT VERIFIED",11,CYAN,true); header.addView(status); root.addView(header,new LinearLayout.LayoutParams(-1,52));
        LinearLayout hero=column(); hero.setPadding(20,8,20,8); hero.setBackground(shape(PANEL,BLUE)); clock=text("--:--",54,Color.WHITE,true); hero.addView(clock); date=text("DATE",15,CYAN,true); hero.addView(date); root.addView(hero,new LinearLayout.LayoutParams(-1,0,1));
        TextView navTitle=text("QUICK LAUNCH",12,BLUE,true); navTitle.setPadding(4,12,4,6); root.addView(navTitle);
        LinearLayout apps=row(); apps.setGravity(Gravity.CENTER); addTile(apps,"WAZE","➤",CYAN,()->launchByName("waze")); addTile(apps,"MAPS","⌖",BLUE,()->launchByName("maps")); addTile(apps,"MEDIA","♫",PINK,()->showMedia()); addTile(apps,"APPS","▦",YELLOW,()->showApps()); addTile(apps,"MOBILE","⇄",YELLOW,()->launchNeoLink()); addTile(apps,"SETTINGS","⚙",CYAN,()->showSettings()); root.addView(apps,new LinearLayout.LayoutParams(-1,104));
        LinearLayout media= row(); media.setPadding(14,4,14,4); media.setBackground(shape(PANEL,Color.rgb(40,55,80))); TextView m=text("MEDIA HUB   •   Existing player controls when available",13,Color.WHITE,true); media.addView(m,new LinearLayout.LayoutParams(0,52,1)); TextView open=text("OPEN",12,CYAN,true); media.addView(open); media.setOnClickListener(v->showMedia()); LinearLayout.LayoutParams mp=new LinearLayout.LayoutParams(-1,60); mp.topMargin=10; root.addView(media,mp);
        dock=row(); dock.setGravity(Gravity.CENTER); String[] labels={"HOME","MEDIA","APPS","SETTINGS"}; Runnable[] acts={()->buildHome(),()->showMedia(),()->showApps(),()->showSettings()}; for(int i=0;i<labels.length;i++){ final int ix=i; TextView b=text(labels[i],11,i==0?CYAN:Color.LTGRAY,true); b.setGravity(Gravity.CENTER); b.setOnClickListener(v->acts[ix].run()); dock.addView(b,new LinearLayout.LayoutParams(0,42,1)); } root.addView(dock);
    }
    private void addTile(LinearLayout parent,String label,String glyph,int color,Runnable action){ LinearLayout tile=column(); tile.setGravity(Gravity.CENTER); tile.setBackground(shape(PANEL,neon?BLUE:Color.DKGRAY)); TextView icon=text(glyph,29,neon?color:Color.WHITE,true); icon.setGravity(Gravity.CENTER); tile.addView(icon); TextView name=text(label,10,Color.WHITE,true); name.setGravity(Gravity.CENTER); tile.addView(name); LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(0,94,1); p.setMargins(5,0,5,0); parent.addView(tile,p); tile.setOnClickListener(v->action.run()); }
    private void startClock(){ ticker=new Runnable(){public void run(){ clock.setText(new SimpleDateFormat("HH:mm",Locale.getDefault()).format(new Date())); date.setText(new SimpleDateFormat("EEEE  •  dd MMMM yyyy",Locale.getDefault()).format(new Date()).toUpperCase()); handler.postDelayed(this,1000); }}; handler.post(ticker); }
    private void launchByName(String key){ Intent found=null; for(android.content.pm.ResolveInfo r:getPackageManager().queryIntentActivities(new Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER),0)){String label=r.loadLabel(getPackageManager()).toString().toLowerCase(); if(label.contains(key)){found=getPackageManager().getLaunchIntentForPackage(r.activityInfo.packageName);break;}} if(found!=null)startActivity(found); else Toast.makeText(this,"App not found. Use Apps to browse installed apps.",Toast.LENGTH_SHORT).show(); }
    private void launchNeoLink(){ Intent i=getPackageManager().getLaunchIntentForPackage("com.neodash.neolink"); if(i!=null) startActivity(i); else Toast.makeText(this,"NeoLink is not installed.",Toast.LENGTH_LONG).show(); }\n    private void showMedia(){ page("MEDIA CENTER","NeoDash does not decode or play audio. It opens the head unit's existing music, radio or Bluetooth apps when available.",new String[]{"Open music player","Open radio app","Bluetooth settings","Back"}); }
    private void showApps(){ LinearLayout old=root; root=column(); root.setPadding(22,18,22,12); root.setBackgroundColor(BG); setContentView(root); root.addView(text("INSTALLED APPS",24,CYAN,true)); ScrollView scroll=new ScrollView(this); LinearLayout list=column(); for(android.content.pm.ResolveInfo r:getPackageManager().queryIntentActivities(new Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER),0)){String label=r.loadLabel(getPackageManager()).toString(); TextView item=text("▣   "+label,17,Color.WHITE,true); item.setPadding(14,12,14,12); item.setOnClickListener(v->{Intent in=getPackageManager().getLaunchIntentForPackage(r.activityInfo.packageName);if(in!=null)startActivity(in);}); list.addView(item);} scroll.addView(list); root.addView(scroll,new LinearLayout.LayoutParams(-1,0,1)); addBack(); }
    private void showSettings(){ page("NEODASH SETTINGS","Preview settings. Neon icon appearance is active; advanced hardware integrations are not enabled in this prototype.",new String[]{"Toggle neon / standard icons","Animation preference (preview only)","Back"}); }
    private void page(String title,String desc,String[] buttons){ root=column();root.setPadding(24,22,24,18);root.setBackgroundColor(BG);setContentView(root);root.addView(text(title,25,CYAN,true)); TextView d=text(desc,16,Color.LTGRAY,false); d.setPadding(0,18,0,24);root.addView(d); for(String s:buttons){TextView b=text("  "+s,16,Color.WHITE,true);b.setPadding(12,10,12,10);b.setBackground(shape(PANEL,BLUE));LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,54);p.setMargins(0,5,0,5);root.addView(b,p);b.setOnClickListener(v->{if(s.equals("Back"))buildHome();else if(s.contains("Toggle")){neon=!neon;showSettings();}else if(s.contains("music"))launchByName("music");else if(s.contains("radio"))launchByName("radio");else if(s.contains("Bluetooth"))startActivity(new Intent(android.provider.Settings.ACTION_BLUETOOTH_SETTINGS));});} }
    private void addBack(){ TextView b=text("←  BACK",15,CYAN,true); b.setPadding(8,12,8,12); b.setOnClickListener(v->buildHome());root.addView(b); }
    @Override public void onBackPressed(){buildHome();}
    @Override protected void onDestroy(){super.onDestroy();handler.removeCallbacksAndMessages(null);}
}
