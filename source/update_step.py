# Build step (exec'd after hero_step.py): in-app updates for the Android app (check GitHub, download, install).
def rep(old, new):
    global s
    assert old in s, old[:80]
    s = s.replace(old, new, 1)

# Settings card (shown only inside the installed Android app)
rep('<div class="set-row"><span class="set-l">About · אודות</span>',
    '''<div class="set-row" id="upd-card" hidden><span class="set-l">App updates · עדכוני אפליקציה</span>
      <p class="set-note" id="upd-ver"></p>
      <p class="upd-status" id="upd-status" aria-live="polite"></p>
      <div class="upd-btns"><button type="button" class="btn ghost" id="upd-check">Check for updates · בדיקת עדכונים</button><button type="button" class="btn" id="upd-go" hidden>Update now · עדכן עכשיו</button></div></div>
    <div class="set-row"><span class="set-l">About · אודות</span>''')

# Home banner when a new version is ready
rep('<header class="hero">', '<div class="upd-banner" id="upd-banner" hidden></div>\n  <header class="hero">')

UPD_JS = r'''
// ----- In-app updates (Android app only) -----
{const NB2=window.AndroidBridge,can=NB2&&typeof NB2.checkUpdate==="function";
  const card=document.getElementById("upd-card"),st=document.getElementById("upd-status"),go=document.getElementById("upd-go"),chk=document.getElementById("upd-check"),ban=document.getElementById("upd-banner");
  let latest=null,manual=false;
  const T2=(en,he)=>mode==="he"?he:mode==="en"?en:en+" · "+he;
  const setSt=t=>{st.textContent=t};
  if(can){card.hidden=false;
    try{const v=JSON.parse(NB2.appVersion());document.getElementById("upd-ver").textContent=T2("Installed version: "+v.versionName,"הגרסה המותקנת: "+v.versionName)}catch(e){}
    const showBanner=()=>{ban.hidden=false;ban.innerHTML=`<div class="ub-text"><b>${bi(B("A new version is ready","גרסה חדשה מוכנה"),"span")}</b><span>${latest.versionName}</span></div><button type="button" class="btn" id="ub-go">Update now · עדכן עכשיו</button>`;
      document.getElementById("ub-go").onclick=()=>NB2.installUpdate()};
    window.onUpdateInfo=info=>{chk.disabled=false;
      if(info.error||!info.latest){if(manual)setSt(T2("Couldn't check for updates. Check the internet connection and try again.","לא הצלחנו לבדוק עדכונים. בדקו את החיבור לאינטרנט ונסו שוב."));return}
      latest=info.latest;
      if(info.latest.versionCode>info.current.versionCode){setSt(T2("New version "+latest.versionName+" is available.","גרסה חדשה "+latest.versionName+" זמינה."));go.hidden=false;showBanner()}
      else{setSt(T2("You have the latest version.","יש לכם את הגרסה העדכנית."));go.hidden=true;ban.hidden=true}};
    window.onUpdateStatus=(state,pct)=>{
      const msg=state==="downloading"?T2("Downloading the update… "+(pct||0)+"%","מוריד את העדכון… "+(pct||0)+"%")
        :state==="installing"?T2("Download complete. Tap Update on the next screen.","ההורדה הסתיימה. הקישו על עדכון במסך הבא.")
        :state==="permission"?T2("Allow Rules Study to install updates (turn on the switch), come back, and tap Update now again.","אפשרו ל-Rules Study להתקין עדכונים (הפעילו את המתג), חזרו לכאן והקישו שוב על עדכן עכשיו.")
        :T2("The download failed. Check the internet connection and try again.","ההורדה נכשלה. בדקו את החיבור לאינטרנט ונסו שוב.");
      setSt(msg);if(!ban.hidden){const t=ban.querySelector(".ub-text span");if(t)t.textContent=msg}};
    chk.onclick=()=>{manual=true;chk.disabled=true;setSt(T2("Checking…","בודק…"));NB2.checkUpdate()};
    go.onclick=()=>NB2.installUpdate();
    setTimeout(()=>{try{NB2.checkUpdate()}catch(e){}},2500); // quiet check each time the app opens
  }}
'''
rep('// ----- Bottom navigation -----', UPD_JS + '// ----- Bottom navigation -----')

UPD_CSS = r'''
/* update banner and settings card */
.upd-banner{display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap;background:var(--accent);color:var(--accent-ink);border-radius:18px;padding:14px 16px 14px 20px;box-shadow:var(--shadow)}
.upd-banner .ub-text{display:grid;gap:2px}
.upd-banner .ub-text b{font-weight:600}
.upd-banner .ub-text b>span{display:block}
body.m-en .upd-banner .ub-text b>span.he,body.m-he .upd-banner .ub-text b>span.en{display:none}
.upd-banner .ub-text>span{opacity:.9;font-size:.92rem}
.upd-banner .btn{background:var(--accent-ink);color:var(--accent);border-color:var(--accent-ink)}
.upd-status{margin:0;font-weight:500;color:var(--ink)}
.upd-status:empty{display:none}
.upd-btns{display:flex;gap:10px;flex-wrap:wrap}
.upd-btns .btn:disabled{opacity:.5}
'''
rep('</style>', UPD_CSS + '</style>')
