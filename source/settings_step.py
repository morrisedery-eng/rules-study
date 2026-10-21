# Build step (exec'd after theme_step.py): an app Settings panel — appearance (auto/light/dark), language, read aloud, reading speed.
def rep(old, new):
    global s
    assert old in s, old[:80]
    s = s.replace(old, new, 1)

rep('<button class="btn" id="exam-btn" type="button">Practice exam · מבחן תרגול</button>',
    '<button class="btn" id="exam-btn" type="button">Practice exam · מבחן תרגול</button><button class="btn ghost" id="set-btn" type="button" aria-expanded="false" aria-controls="settings">⚙ Settings · הגדרות</button>')
rep('</header>\n  <section class="subjects"', '''</header>
  <section class="settings" id="settings" hidden aria-labelledby="set-h">
    <div class="set-head"><div class="bi"><h2 class="en" id="set-h">Settings</h2><h2 class="he" lang="he">הגדרות</h2></div><button type="button" class="btn" id="set-done">Done · סיום</button></div>
    <div class="set-row"><span class="set-l">Appearance · מראה</span>
      <div class="seg" role="group" aria-label="Appearance"><button type="button" data-th="auto">Automatic · אוטומטי</button><button type="button" data-th="light">Light · בהיר</button><button type="button" data-th="dark">Dark · כהה</button></div></div>
    <div class="set-row"><span class="set-l">Language · שפה</span>
      <div class="seg" role="group" aria-label="Language setting"><button type="button" data-sm="both">EN | עב</button><button type="button" data-sm="en">English</button><button type="button" data-sm="he">עברית</button></div></div>
    <div class="set-row"><span class="set-l">Read aloud · הקראה בקול</span>
      <div class="seg" role="group" aria-label="Read aloud"><button type="button" data-snd="1">On · פועל</button><button type="button" data-snd="0">Off · כבוי</button></div></div>
    <div class="set-row"><span class="set-l">Reading speed · מהירות הקראה: <b id="set-rate-v"></b></span>
      <input type="range" id="set-rate" min="0.6" max="1.2" step="0.05"></div>
    <div class="set-row"><span class="set-l">Voices · קולות</span><button type="button" class="btn ghost" id="set-voices">Choose and test voices · בחירה ובדיקה של קולות</button></div>
  </section>
  <section class="subjects"''')

SETTINGS_JS = r'''
// ----- Settings: appearance, language, read aloud, reading speed -----
function applyTheme(){const t=store.get("rr-theme","auto"),r=document.documentElement;if(t==="auto")r.removeAttribute("data-theme");else r.setAttribute("data-theme",t)}
function syncSettings(){const t=store.get("rr-theme","auto");
  document.querySelectorAll("#settings [data-th]").forEach(b=>b.setAttribute("aria-pressed",b.dataset.th===t));
  document.querySelectorAll("#settings [data-sm]").forEach(b=>b.setAttribute("aria-pressed",b.dataset.sm===mode));
  document.querySelectorAll("#settings [data-snd]").forEach(b=>b.setAttribute("aria-pressed",(b.dataset.snd==="1")===soundOn()));
  const r=document.getElementById("set-rate");if(r){r.value=voiceRate();document.getElementById("set-rate-v").textContent=Math.round(voiceRate()*100)+"%"}}
{const sec=document.getElementById("settings"),btn=document.getElementById("set-btn");
  const open=v=>{sec.hidden=!v;btn.setAttribute("aria-expanded",v);if(v){syncSettings();sec.scrollIntoView({behavior:"smooth",block:"start"})}};
  btn.onclick=()=>{if(typeof coach!=="undefined"&&coach.open)closeCoach();open(sec.hidden)};document.getElementById("set-done").onclick=()=>{open(false);window.scrollTo({top:0,behavior:"smooth"})};
  sec.querySelectorAll("[data-th]").forEach(b=>b.onclick=()=>{store.set("rr-theme",b.dataset.th);applyTheme();syncSettings()});
  sec.querySelectorAll("[data-sm]").forEach(b=>b.onclick=()=>{setMode(b.dataset.sm);renderChips();renderDays();renderDay();renderBlocks();syncSettings()});
  sec.querySelectorAll("[data-snd]").forEach(b=>b.onclick=()=>{store.set("rr-qsound",b.dataset.snd==="1");if(!soundOn())stopSpeak();syncSettings();const q=document.getElementById("qsound");if(q)q.textContent=soundOn()?"🔊 Sound on · קול פועל":"🔇 Sound off · קול כבוי"});
  const r=document.getElementById("set-rate");r.oninput=()=>{store.set("rr-rate",+r.value);syncSettings()};
  document.getElementById("set-voices").onclick=()=>{openHelper();const v=document.getElementById("vset");if(v){v.open=true;fillVoices();v.scrollIntoView({block:"nearest"})}};
  document.querySelectorAll(".topbar .seg button").forEach(b=>b.addEventListener("click",syncSettings))}
'''
rep('setMode(mode);renderDays();renderDay();renderBlocks();wireReset();', SETTINGS_JS + 'setMode(mode);renderDays();renderDay();renderBlocks();wireReset();applyTheme();syncSettings();')

rep('/* refinements */', '''/* refinements */
.settings{background:var(--sheet);border:1px solid var(--line);border-radius:var(--r-lg);padding:clamp(18px,4vw,28px);display:grid;gap:18px;box-shadow:var(--shadow)}
.set-head{display:flex;justify-content:space-between;align-items:center;gap:12px}
.set-head .bi{gap:2px 16px}
.set-row{display:grid;gap:8px;padding-top:14px;border-top:1px solid var(--line)}
.set-l{font-weight:600}
.settings .seg{display:grid;grid-template-columns:repeat(auto-fit,minmax(0,1fr));border-radius:14px;width:100%}
.settings .seg button{padding:10px 6px;text-align:center;line-height:1.3}
.settings input[type=range]{width:100%;accent-color:var(--accent)}
.settings .btn.ghost{justify-self:start}
header #set-btn{background:transparent;border-color:rgba(255,255,255,.5);color:#fff}''')

# The sources note leaves the main screen; a short "About" card in Settings replaces it
s = re.sub(r'\s*<p class="note">.*?</p>', '', s, count=1, flags=re.S)
rep('  </section>\n  <section class="subjects"', """    <div class="set-row"><span class="set-l">About · אודות</span>
      <p class="set-note">The lessons come from the official Florida DCF Child Care Facility Handbook and Florida's child care rules, current since September 1, 2026. If your course materials show a different number, follow your course.<br><span dir="rtl">השיעורים מבוססים על המדריך הרשמי של DCF למתקני טיפול בילדים ועל חוקי הטיפול בילדים של פלורידה, בתוקף מ-1 בספטמבר 2026. אם בחומרי הקורס מופיע מספר אחר, פעלו לפי הקורס.</span></p></div>
  </section>
  <section class="subjects\"""")
