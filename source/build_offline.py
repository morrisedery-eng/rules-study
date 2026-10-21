import re, os, shutil, zipfile
from PIL import Image, ImageDraw

D = "/home/claude/android-app"
P = f"{D}/RulesStudy"
shutil.rmtree(P, ignore_errors=True)

s = open(f"{D}/src.html", encoding="utf-8").read()
days = open(f"{D}/days.js", encoding="utf-8").read() + "\n" + open(f"{D}/cards.js", encoding="utf-8").read()
exam = open(f"{D}/exam.js", encoding="utf-8").read()

# --- course data: 15 exam-focused days ---
a = s.index("const B=(en,he)=>({en,he});"); e = s.index("const SEGS")
s = s[:a] + days + "\n" + s[e:]
for old, new in [
  ('Rules &amp; Regs: 10-Day Study Plan', 'Rules &amp; Regs: Study by Subject'),
  ('חוקים ותקנות: תוכנית לימוד ל-10 ימים', 'חוקים ותקנות: לימוד לפי נושאים'),
  ('${done.length}/10 days complete · ${done.length}/10 ימים הושלמו', '${done.length}/${DAYS.length} days complete · ${done.length}/${DAYS.length} ימים הושלמו'),
  ('Day ${cur+1} of 10 · יום ${cur+1} מתוך 10', 'Day ${cur+1} of ${DAYS.length} · יום ${cur+1} מתוך ${DAYS.length}'),
  ('cur<9?', 'cur<DAYS.length-1?'),
  ('Last day: retake every quiz from Days 1–9 and aim for 100%.', 'Last day: take the practice exam until you score 90% or more.'),
  ('יום אחרון: עשו שוב את כל הבחנים מימים 1–9 ושאפו ל-100%.', 'יום אחרון: עשו את מבחן התרגול עד שתגיעו ל-90% ומעלה.'),
  ('.days{display:grid;grid-template-columns:repeat(10,minmax(0,1fr));gap:6px}', '.days{display:grid;grid-template-columns:repeat(auto-fill,minmax(58px,1fr));gap:6px}'),
  ('@media (max-width:640px){.days{grid-template-columns:repeat(5,minmax(0,1fr))}}', ''),
  ('<span class="progress" id="prog"></span>', '<div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap"><span class="progress" id="prog"></span><button class="btn" id="exam-btn" type="button">Practice exam · מבחן תרגול</button></div>'),
]:
    assert old in s, old
    s = s.replace(old, new)
# --- guided session timer ---
timer = open(f"{D}/timer.js", encoding="utf-8").read()
t0 = s.index("// Timer\nlet left=3600,run=null;"); t1 = s.index("// ---------- Study helper")
s = s[:t0] + timer + "\n" + s[t1:]
for i, label in enumerate(["1 · Review", "2 · Learn", "3 · Flashcards", "4 · Quiz"]):
    old = f'<div class="sec"><div class="sec-head"><h3>{label}'
    assert old in s, old
    s = s.replace(old, f'<div class="sec part" id="part-{i}"><div class="sec-head"><h3>{label}')
old = '<button class="btn ghost" id="treset">Reset · אפס</button>'
assert old in s
s = s.replace(old, '<button class="btn ghost" id="tnext" type="button" hidden>Next part · החלק הבא</button>\n        ' + old)
old = '<div class="blocks" id="blocks"></div>'
assert old in s
s = s.replace(old, old + """
    <p class="thint" id="tnow" aria-live="polite"></p>
    <div class="bi thint-help"><p class="en thint">Press <b>Start</b>. The timer takes you through the 4 parts, beeps and tells you when to switch. Tap any part to jump to it.</p><p class="he thint" lang="he">לחצו <b>התחל</b>. הטיימר מעביר אתכם בין 4 החלקים, מצפצף ומודיע מתי לעבור. הקישו על חלק כדי לקפוץ אליו.</p></div>""")
s = s.replace(".btn.ghost{background:none;color:var(--accent)}", """.btn.ghost{background:none;color:var(--accent)}
button.blk{border:0;font:inherit;color:var(--ink);text-align:start;cursor:pointer}
.timer.running{position:sticky;top:env(safe-area-inset-top,0px);z-index:15;box-shadow:0 6px 18px rgba(0,0,0,.12)}
.timer.running .thint-help{display:none}
.blk .short{display:none}
.timer.running{padding:8px 10px;gap:6px}
.timer.running .label{display:none}
.timer.running .clock{font-size:1.25rem}
.timer.running .timer-row{flex-wrap:nowrap;gap:8px}
.timer.running .timer-row .btn{padding:5px 9px;font-size:.78rem}
.timer.running .blocks{grid-template-columns:repeat(3,minmax(0,1fr))}
.timer.running .blk{padding:4px 6px;font-size:.72rem}
.timer.running .blk .full{display:none}.timer.running .blk .short{display:inline}
.timer.running #tnow{font-size:.78rem}
.thint{margin:0;font-size:.85rem;color:var(--muted)}
#tnow{font-weight:600;color:var(--accent)}#tnow:empty{display:none}
.part.flash{animation:partflash 2.4s ease-out}
@keyframes partflash{0%,40%{box-shadow:0 0 0 3px var(--accent);border-radius:12px}100%{box-shadow:0 0 0 0 transparent}}""")
assert "partflash" in s
dayquiz = open(f"{D}/dayquiz.js", encoding="utf-8").read()
coachjs = open(f"{D}/coach.js", encoding="utf-8").read()
exec(open(f"{D}/guided_step.py", encoding="utf-8").read())
note_old = re.search(r'<p class="note">.*?</p>', s, re.S).group(0)
s = s.replace(note_old, """<p class="note"><span class="en">Built for the DCF course “Child Care Facility Rules and Regulations” (RNRF) from the DCF Child Care Facility Handbook (December 2025 edition, in force since September 1, 2026), the RNRF participant guide, Florida Statutes 402.26–402.319 and rule 65C-22, including the enforcement rule effective September 1, 2026. If your course materials show a different number, follow your course.</span>
  <span class="he" lang="he" dir="rtl" style="display:block">נבנה עבור קורס DCF ”חוקים ותקנות למתקני טיפול בילדים“ (RNRF) לפי מדריך מתקני הטיפול בילדים (מהדורת דצמבר 2025, בתוקף מ-1 בספטמבר 2026), מדריך המשתתף של הקורס, חוקי פלורידה 402.26–402.319 ותקנה 65C-22, כולל תקנת האכיפה שבתוקף מ-1 בספטמבר 2026. אם בחומרי הקורס מופיע מספר אחר, פעלו לפי הקורס.</span></p>""")
helper = open(f"{D}/hespeak.js", encoding="utf-8").read() + "\n" + open(f"{D}/speechfix.js", encoding="utf-8").read() + "\n" + open(f"{D}/helper.js", encoding="utf-8").read()

# --- helper footer: mic, language, auto-send, offline voice setup ---
old_foot = re.search(r'<form class="h-row" id="h-form">.*?</label>', s, re.S).group(0)
new_foot = """<form class="h-row" id="h-form">
      <button class="mic" id="h-mic" type="button" aria-label="Speak · דבר" title="Speak · דבר"><svg viewBox="0 0 24 24"><rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0"/><path d="M12 18v3"/></svg></button>
      <textarea id="h-input" rows="1" placeholder="Ask anything… · שאלו כל דבר…"></textarea>
      <button class="btn" id="h-send" type="submit">Ask · שאל</button>
    </form>
    <div class="h-row" style="align-items:center;flex-wrap:wrap">
      <span class="h-note">Mic · מיקרופון:</span>
      <div class="seg" role="group" aria-label="Microphone language">
        <button type="button" id="ml-en" data-ml="en-US" aria-pressed="true">English</button>
        <button type="button" id="ml-he" data-ml="he-IL" aria-pressed="false">עברית</button>
      </div>
      <label class="h-note"><input type="checkbox" id="h-autosend" checked> Send when I stop · שלח כשאני מסיים</label>
    </div>
    <label class="h-note"><input type="checkbox" id="h-auto"> Read answers aloud · הקראת תשובות בקול</label>
    <details class="h-note" id="vset">
      <summary>Voice settings · הגדרות קול</summary>
      <div style="display:grid;gap:8px;margin-top:8px">
        <label>Hebrew voice · קול בעברית<br><select id="v-he" style="width:100%"></select></label>
        <label>English voice · קול באנגלית<br><select id="v-en" style="width:100%"></select></label>
        <label>Speed · מהירות: <span id="v-rate-val"></span><br><input type="range" id="v-rate" min="0.6" max="1.2" step="0.05" style="width:100%"></label>
        <button type="button" class="mini" id="v-test">▶ Test the voices · בדיקת הקולות</button>
        <p id="v-none" hidden style="margin:0">No Hebrew voice is installed yet. See “Set up offline voice” below. · לא מותקן קול בעברית. ראו ”הגדרת קול ללא אינטרנט“ למטה.</p>
        <p style="margin:0">Tip: try each Hebrew voice with “Test” and keep the clearest one. A speed of 80–90% is easiest to follow. · טיפ: נסו כל קול בעברית עם ”בדיקה“ ובחרו את הברור ביותר. מהירות של 80–90% הכי נוחה.</p>
      </div>
    </details>
    <details class="h-note">
      <summary>Set up offline voice · הגדרת קול ללא אינטרנט</summary>
      <p style="margin:6px 0">Do this once, while connected to Wi-Fi:</p>
      <ol style="margin:0;padding-left:18px">
        <li>Voice typing: Settings → System → Languages &amp; input → On-screen keyboard → Gboard → Voice typing → Offline speech recognition → download <b>English (US)</b> and <b>Hebrew</b>.</li>
        <li>Reading aloud: Settings → Accessibility → Text-to-speech output → Speech Services by Google (gear icon) → Install voice data → <b>Hebrew</b>.</li>
      </ol>
      <p style="margin:6px 0" dir="rtl">עשו זאת פעם אחת, כשאתם מחוברים ל-Wi-Fi: (1) הקלדה קולית: הגדרות ← מערכת ← שפות וקלט ← מקלדת וירטואלית ← Gboard ← הקלדה קולית ← זיהוי דיבור אופליין ← הורידו אנגלית ועברית. (2) הקראה: הגדרות ← נגישות ← המרת טקסט לדיבור ← שירותי הדיבור של Google ← התקנת נתוני קול ← עברית.</p>
      <p style="margin:6px 0">Menu names differ a little between phone brands. · שמות התפריטים משתנים מעט בין יצרנים.</p>
    </details>"""
s = s.replace(old_foot, new_foot)

# --- styles ---
s = s.replace("@media (prefers-reduced-motion:reduce){*{transition:none!important}}",
""".mic{flex:none;width:48px;height:48px;border-radius:50%;border:2px solid var(--accent);background:var(--sheet);color:var(--accent);cursor:pointer;display:grid;place-items:center;align-self:center}
.mic svg{width:24px;height:24px;fill:none;stroke:currentColor;stroke-width:2}
.mic.live{background:var(--bad);border-color:var(--bad);color:#fff;animation:pulse 1.2s infinite}
@keyframes pulse{50%{box-shadow:0 0 0 8px rgba(184,64,47,.25)}}
details summary{cursor:pointer;color:var(--accent)}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}""")

# --- swap the Claude-powered helper for the offline one ---
start = s.index("// ---------- Study helper: read aloud + ask Claude ----------")
end = s.index('document.querySelectorAll(".seg button").forEach(b=>b.onclick=()=>{setMode(b.dataset.m);renderChips()});')
s = s[:start] + helper + "\n" + exam + "\n" + dayquiz + "\n" + coachjs + "\n" + s[end:]

new_handlers = '''  sheet.querySelectorAll("[data-explain]").forEach(b=>b.onclick=()=>{openHelper();addMsg(mode==="he"?"הסבר בפשטות":"Explain simply","me");answerPoint(cur,+b.dataset.explain,mode==="he"?"he":"en")});
  sheet.querySelectorAll("[data-example]").forEach(b=>b.onclick=()=>{openHelper();addMsg(mode==="he"?"תן דוגמה":"Give an example","me");answerPoint(cur,+b.dataset.example,mode==="he"?"he":"en","ex")});
  sheet.querySelectorAll("[data-why]").forEach(b=>b.onclick=()=>{openHelper();whyAnswer(d.quiz[+b.dataset.why])});
'''
s, n = re.subn(r'  sheet\.querySelectorAll\("\[data-explain\]"\).*?(?=  let right=0)', new_handlers, s, flags=re.S)
assert n == 1
exec(open(f"{D}/subjects_step.py", encoding="utf-8").read())
exec(open(f"{D}/theme_step.py", encoding="utf-8").read())
exec(open(f"{D}/settings_step.py", encoding="utf-8").read())
exec(open(f"{D}/helper_step.py", encoding="utf-8").read())
exec(open(f"{D}/nav_step.py", encoding="utf-8").read())
exec(open(f"{D}/hero_step.py", encoding="utf-8").read())
exec(open(f"{D}/update_step.py", encoding="utf-8").read())
exec(open(f"{D}/splash_step.py", encoding="utf-8").read())
exec(open(f"{D}/align_step.py", encoding="utf-8").read())
exec(open(f"{D}/menu_step.py", encoding="utf-8").read())
exec(open(f"{D}/screens_step.py", encoding="utf-8").read())
art = s.replace('if(!NB&&!SR)micBtn.hidden=true;', 'micBtn.hidden=true;')
art = art.replace('<div class="h-row" style="align-items:center;flex-wrap:wrap">\n      <span class="h-note">Mic', '<div class="h-row" hidden style="align-items:center;flex-wrap:wrap">\n      <span class="h-note">Mic')
art = art.replace('<details class="h-note">\n      <summary>Set up offline voice', '<details class="h-note" hidden>\n      <summary>Set up offline voice')
assert art.count(' hidden ') >= 2
open(f"{D}/artifact.html", "w", encoding="utf-8").write(art)
# --- Android: standalone document, no external resources ---
s = s.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '')
s = re.sub(r'<link rel="preconnect"[^>]*>\n', '', s)
s = re.sub(r'<link rel="stylesheet" href="https://fonts.googleapis.com[^>]*>\n', '', s)
s = ("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
     "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n"
     "<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'self' 'unsafe-inline' data:; font-src 'self' file: data:; connect-src 'none'\">\n"
     "<style>" + FONTFACE_CSS + "</style>\n"
     "<style>body{margin:0}[hidden]{display:none!important}img{max-width:100%}</style>\n") + s
s = s.replace('<div class="wrap">', '</head>\n<body>\n<div class="wrap">', 1)
assert "http" not in re.sub(r'xmlns="http://www.w3.org/2000/svg"', '', s.split("<script>")[0]).replace("http-equiv", ""), "external URL left in markup"

s = s.replace("</script>\n", "</script>\n</body>\n</html>\n")
s = s.replace('if(window.claude&&typeof claude.use==="function")AI=await claude.use("sample")', 'AI=null')  # the Android build has no Claude connection
assert "claude.use" not in s and "fetch(" not in s

assets = f"{P}/app/src/main/assets"; os.makedirs(assets)
open(f"{assets}/index.html", "w", encoding="utf-8").write(s)
open(f"{D}/offline.js", "w", encoding="utf-8").write(re.findall(r"<script>(.*?)</script>", s, re.S)[0])

def w(path, text):
    full = f"{P}/{path}"; os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(text.lstrip("\n"))

w("settings.gradle.kts", """
pluginManagement {
    repositories { google(); mavenCentral(); gradlePluginPortal() }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories { google(); mavenCentral() }
}
rootProject.name = "RulesStudy"
include(":app")
""")
w("build.gradle.kts", """
plugins {
    id("com.android.application") version "8.5.2" apply false
    id("org.jetbrains.kotlin.android") version "1.9.24" apply false
}
""")
w("gradle.properties", """
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
kotlin.code.style=official
""")
w("app/build.gradle.kts", """
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.rulesstudy.app"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.rulesstudy.app"
        minSdk = 24
        targetSdk = 34
        // Every GitHub build gets a higher number, so each update installs over the previous version.
        val run = (System.getenv("GITHUB_RUN_NUMBER") ?: "0").toInt()
        versionCode = 100 + run
        versionName = "5.$run"
    }

    // One permanent key for every build, so each new version installs over the old one (your progress stays).
    signingConfigs {
        create("rulesstudy") {
            storeFile = file("rulesstudy.jks")
            storePassword = "rulesstudy"
            keyAlias = "rulesstudy"
            keyPassword = "rulesstudy"
        }
    }
    buildTypes {
        release {
            isMinifyEnabled = false
            signingConfig = signingConfigs.getByName("rulesstudy")
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
}
""")
w("app/src/main/AndroidManifest.xml", """
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <!-- Microphone for voice questions. -->
    <uses-permission android:name="android.permission.RECORD_AUDIO" />
    <!-- Internet only to check GitHub for app updates and download them; the course itself works offline. -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.REQUEST_INSTALL_PACKAGES" />

    <queries>
        <intent><action android:name="android.speech.RecognitionService" /></intent>
        <intent><action android:name="android.intent.action.TTS_SERVICE" /></intent>
    </queries>

    <application
        android:label="Rules Study"
        android:icon="@mipmap/ic_launcher"
        android:roundIcon="@mipmap/ic_launcher"
        android:allowBackup="true"
        android:supportsRtl="true"
        android:theme="@style/AppTheme">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:configChanges="orientation|screenSize|screenLayout|keyboardHidden|uiMode"
            android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
""")
w("app/src/main/res/values/themes.xml", """
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="AppTheme" parent="android:Theme.Material.Light.NoActionBar">
        <item name="android:statusBarColor">#161C49</item>
        <item name="android:navigationBarColor">#161C49</item>
        <item name="android:windowBackground">#161C49</item>
    </style>
</resources>
""")
w("app/src/main/res/values-v31/themes.xml", """
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="AppTheme" parent="android:Theme.Material.Light.NoActionBar">
        <item name="android:statusBarColor">#161C49</item>
        <item name="android:navigationBarColor">#161C49</item>
        <item name="android:windowBackground">#161C49</item>
        <item name="android:windowSplashScreenBackground">#161C49</item>
        <item name="android:windowSplashScreenAnimatedIcon">@drawable/splash_icon</item>
    </style>
</resources>
""")
w("app/src/main/java/com/rulesstudy/app/MainActivity.kt", open(f"{D}/MainActivity.kt", encoding="utf-8").read())
w(".github/workflows/build.yml", open(f"{D}/build.yml", encoding="utf-8").read())
w("README.md", open(f"{D}/README.md", encoding="utf-8").read())
shutil.copy(f"{D}/rulesstudy.jks", f"{P}/app/rulesstudy.jks")
w("fetch-fonts.sh", "#!/bin/sh\n# Downloads the app's fonts (IBM Plex Sans, IBM Plex Sans Hebrew, Frank Ruhl Libre; SIL Open Font License) into the app.\n# The app works without them (it falls back to the phone's fonts), but looks best with them.\nset -e\nmkdir -p app/src/main/assets/fonts\ncd app/src/main/assets/fonts\n" + "".join(f"curl -fsSLO {u}\n" for u in FONT_URLS))
w(".gitignore", ".gradle/\nbuild/\napp/build/\nlocal.properties\n*.iml\n.idea/\n")

def _bez(p0,p1,p2,p3,n=40):
    return [((1-t)**3*p0[0]+3*(1-t)**2*t*p1[0]+3*(1-t)*t*t*p2[0]+t**3*p3[0],(1-t)**3*p0[1]+3*(1-t)**2*t*p1[1]+3*(1-t)*t*t*p2[1]+t**3*p3[1]) for t in [k/n for k in range(n+1)]]
def shield_points():
    # same shield as the app's logo, in a 24x24 box
    left=_bez((4.5,11.5),(4.5,16.1),(7.6,19.9),(12,21.5)); right=_bez((12,21.5),(16.4,19.9),(19.5,16.1),(19.5,11.5))
    return [(12,2.5),(4.5,5.5)]+left+right+[(19.5,5.5),(12,2.5)]
def draw_shield(d, cx, cy, scale, color, width):
    pts=[(cx+(x-12)*scale, cy+(y-12)*scale) for x,y in shield_points()]
    d.line(pts, fill=color, width=width, joint="curve")
    chk=[(cx+(x-12)*scale, cy+(y-12)*scale) for x,y in [(8.5,12),(10.9,14.4),(15.5,9.6)]]
    d.line(chk, fill=color, width=width, joint="curve")
    for x,y in chk[::2]+[pts[0]]:
        r=width/2; d.ellipse([x-r,y-r,x+r,y+r], fill=color)
def icon(size):
    S=1024; im=Image.new("RGB",(S,S),"#161C49"); px=im.load()
    for y in range(S):            # navy with an indigo glow from the top right, like the app banner
        for x in range(0,S,1):
            dx=(S-x)/S; dy=y/S; t=max(0,1-((dx*dx+dy*dy)**.5)/1.05)
            px[x,y]=(int(22+(61-22)*t),int(28+(72-28)*t),int(73+(200-73)*t))
    d=ImageDraw.Draw(im); draw_shield(d,S/2,S/2+8,S*0.026,"#FFFFFF",int(S*0.05))
    return im.resize((size,size),Image.LANCZOS)
def splash_icon(size=432):
    S=1296; im=Image.new("RGBA",(S,S),(0,0,0,0)); d=ImageDraw.Draw(im)
    draw_shield(d,S/2,S/2+10,S*0.016,"#FFFFFF",int(S*0.03))
    return im.resize((size,size),Image.LANCZOS)
for name, px in {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}.items():
    os.makedirs(f"{P}/app/src/main/res/mipmap-{name}", exist_ok=True)
    icon(px).save(f"{P}/app/src/main/res/mipmap-{name}/ic_launcher.png")
os.makedirs(f"{P}/app/src/main/res/drawable-nodpi", exist_ok=True)
splash_icon().save(f"{P}/app/src/main/res/drawable-nodpi/splash_icon.png")
icon(512).save(f"{D}/icon-512.png"); icon(192).save(f"{D}/icon-192.png")

z = f"{D}/RulesStudy-android-project.zip"
if os.path.exists(z): os.remove(z)
with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
    for root, _, files in os.walk(P):
        for f in files:
            full = os.path.join(root, f); zf.write(full, os.path.relpath(full, D))
print("ok", len(s))
