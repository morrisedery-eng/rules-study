import re, json, zipfile, os
from PIL import Image, ImageDraw, ImageFont

D = "/home/claude/android-app"
s = open(f"{D}/src.html", encoding="utf-8").read()

# 1. Standalone document head (PWA)
head = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#0f7a63">
<meta name="mobile-web-app-capable" content="yes">
<link rel="manifest" href="manifest.json">
<link rel="icon" href="icon-192.png">
<link rel="apple-touch-icon" href="icon-192.png">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}[hidden]{display:none!important}img{max-width:100%}</style>
"""
s = s.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '')
s = head + s
s = s.replace("<div class=\"wrap\">", "</head>\n<body>\n<div class=\"wrap\">", 1)

# 2. Mic button + API key settings in the helper footer
old_form = re.search(r'<form class="h-row" id="h-form">.*?</form>', s, re.S).group(0)
new_form = """<form class="h-row" id="h-form">
      <button class="mic" id="h-mic" type="button" aria-label="Speak · דבר" title="Speak · דבר"><svg viewBox="0 0 24 24"><rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0"/><path d="M12 18v3"/></svg></button>
      <textarea id="h-input" rows="1" placeholder="Ask anything… · שאלו כל דבר…"></textarea>
      <button class="btn" id="h-send" type="submit">Ask · שאל</button>
    </form>
    <div class="h-row" style="align-items:center;flex-wrap:wrap">
      <span class="h-note">Mic language · שפת מיקרופון:</span>
      <div class="seg" role="group" aria-label="Microphone language">
        <button type="button" id="ml-en" data-ml="en-US" aria-pressed="true">English</button>
        <button type="button" id="ml-he" data-ml="he-IL" aria-pressed="false">עברית</button>
      </div>
      <label class="h-note"><input type="checkbox" id="h-autosend" checked> Send when I stop talking · שלח כשאני מסיים</label>
    </div>
    <details class="h-note" id="h-keybox">
      <summary>API key settings · הגדרות מפתח</summary>
      <p style="margin:6px 0">Explanations need your own Anthropic API key (from console.anthropic.com → API Keys). It is saved only on this phone. · ההסברים דורשים מפתח API אישי של Anthropic. הוא נשמר רק בטלפון הזה.</p>
      <div class="h-row"><input id="h-key" type="password" autocomplete="off" placeholder="sk-ant-…" style="flex:1;min-width:0;border:1px solid var(--line);border-radius:8px;padding:8px;background:var(--bg);color:var(--ink);font:inherit">
      <button class="btn" type="button" id="h-keysave">Save · שמור</button></div>
    </details>"""
s = s.replace(old_form, new_form)
s = s.replace('<p class="h-note" style="margin:0">To speak instead of typing', '<p class="h-note" hidden style="margin:0">To speak instead of typing')

# 3. Mic styles
s = s.replace("@media (prefers-reduced-motion:reduce){*{transition:none!important}}",
""".mic{flex:none;width:46px;border-radius:50%;border:2px solid var(--accent);background:var(--sheet);color:var(--accent);cursor:pointer;display:grid;place-items:center}
.mic svg{width:22px;height:22px;fill:none;stroke:currentColor;stroke-width:2}
.mic.live{background:var(--bad);border-color:var(--bad);color:#fff;animation:pulse 1.2s infinite}
@keyframes pulse{50%{box-shadow:0 0 0 8px color-mix(in srgb,var(--bad) 25%,transparent)}}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}""")

# 4. Replace the Claude-in-page call with a direct Anthropic API call
start = s.index("async function askHelper(prompt,display){")
end = s.index('document.getElementById("h-form").addEventListener("submit"')
ask = r'''const getKey=()=>store.get("rr-key","");
async function askHelper(prompt,display){
  if(hEl.hidden)openHelper();
  if(busy)return;
  const shown=typeof display==="object"?(mode==="he"?display.he:display.en):(display||prompt);
  addMsg(shown,"me");
  const key=getKey();
  if(!key){document.getElementById("h-keybox").open=true;
    helperNote("To get explanations, paste your Anthropic API key in “API key settings” below. Reading aloud and the microphone work without it. · כדי לקבל הסברים, הדביקו מפתח API ב”הגדרות מפתח“ למטה.");return}
  if(!navigator.onLine){helperNote("You're offline. Explanations need internet; lessons, quizzes and reading aloud still work. · אין חיבור לאינטרנט.");return}
  turns.push({role:"user",content:prompt});
  if(turns.length>12)turns=turns.slice(-12);while(turns.length&&turns[0].role!=="user")turns.shift();
  const out=addMsg(mode==="he"?"חושב…":"Thinking… · חושב…","bot");
  busy=true;hSend.textContent="Stop · עצור";ctl=new AbortController();
  try{
    const r=await fetch("https://api.anthropic.com/v1/messages",{method:"POST",signal:ctl.signal,
      headers:{"content-type":"application/json","x-api-key":key,"anthropic-version":"2023-06-01","anthropic-dangerous-direct-browser-access":"true"},
      body:JSON.stringify({model:"claude-sonnet-5-5",max_tokens:1200,system:rules(),messages:turns})});
    if(!r.ok){const err=await r.json().catch(()=>({}));throw {status:r.status,msg:err&&err.error&&err.error.message}}
    const data=await r.json();
    const text=(data.content||[]).filter(b=>b.type==="text").map(b=>b.text).join("\n").trim()||"…";
    turns.push({role:"assistant",content:text});
    out.textContent=text;out.dir=isHe(text.slice(0,30))?"rtl":"auto";
    addReadButton(out,text);hBody.scrollTop=hBody.scrollHeight;
    if(hAuto.checked)speakMixed(text,out.querySelector(".mini"));
  }catch(e){
    turns.pop();
    let msg;
    if(e&&e.name==="AbortError")msg="Stopped. · נעצר.";
    else if(e&&e.status===401)msg="The API key wasn't accepted. Check it in “API key settings”. · המפתח לא התקבל.";
    else if(e&&e.status===429)msg="Too many questions at once, or your API credit ran out. Wait a minute and try again. · יותר מדי שאלות או שנגמר הקרדיט.";
    else if(e&&e.status===400&&/credit/i.test(e.msg||""))msg="Your API account has no credit left. Add credit at console.anthropic.com. · אין קרדיט בחשבון ה-API.";
    else msg="Couldn't reach the helper. Check your internet and try again. · לא ניתן להתחבר; בדקו את האינטרנט."+(e&&e.msg?"\n("+e.msg+")":"");
    out.textContent=msg;
  }finally{busy=false;hSend.textContent="Ask · שאל";ctl=null}
}
// API key
document.getElementById("h-key").value=getKey();
document.getElementById("h-keysave").onclick=()=>{const v=document.getElementById("h-key").value.trim();store.set("rr-key",v);
  document.getElementById("h-keybox").open=false;helperNote(v?"Key saved on this phone. · המפתח נשמר.":"Key removed. · המפתח הוסר.")};

// Microphone (speech recognition)
const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
const micBtn=document.getElementById("h-mic");
let micLang=store.get("rr-miclang",mode==="he"?"he-IL":"en-US"),rec=null,listening=false;
function setMicLang(l){micLang=l;store.set("rr-miclang",l);
  document.querySelectorAll("[data-ml]").forEach(b=>b.setAttribute("aria-pressed",b.dataset.ml===l))}
document.querySelectorAll("[data-ml]").forEach(b=>b.onclick=()=>setMicLang(b.dataset.ml));setMicLang(micLang);
if(!SR){micBtn.hidden=true}
micBtn.onclick=()=>{
  if(listening&&rec){rec.stop();return}
  stopSpeak();
  rec=new SR();rec.lang=micLang;rec.interimResults=true;rec.continuous=false;rec.maxAlternatives=1;
  const before=hInput.value?hInput.value.trim()+" ":"";let finalText="";
  rec.onstart=()=>{listening=true;micBtn.classList.add("live");hInput.placeholder=micLang==="he-IL"?"מקשיב… דברו עכשיו":"Listening… speak now"};
  rec.onresult=ev=>{let interim="";finalText="";
    for(const r of ev.results){if(r.isFinal)finalText+=r[0].transcript;else interim+=r[0].transcript}
    hInput.value=before+finalText+interim;hInput.dir=micLang==="he-IL"?"rtl":"auto"};
  rec.onerror=ev=>{const m={"not-allowed":"Microphone permission was blocked. Allow it in Chrome: tap the lock icon by the address, then Permissions → Microphone. · הגישה למיקרופון נחסמה; אפשרו אותה בהגדרות Chrome.",
    "no-speech":"I didn't hear anything. Tap the mic and try again. · לא שמעתי כלום, נסו שוב.","network":"Voice typing needs internet. · הקלטה קולית דורשת אינטרנט.",
    "language-not-supported":"This language isn't available for voice typing on this phone. · השפה לא נתמכת בטלפון הזה."}[ev.error];
    if(m)helperNote(m)};
  rec.onend=()=>{listening=false;micBtn.classList.remove("live");hInput.placeholder="Ask anything… · שאלו כל דבר…";
    if(document.getElementById("h-autosend").checked&&finalText.trim()){document.getElementById("h-form").requestSubmit()}};
  try{rec.start()}catch(e){}
};
'''
s = s[:start] + ask + s[end:]
s = s.replace('function getSample(){if(!samplePromise)samplePromise=(window.claude&&claude.use)?claude.use("sample").catch(()=>null):Promise.resolve(null);return samplePromise}\n', '')
s = s.replace("Asking questions works when this page is opened in Claude.", "")

# greeting mentions mic
s = s.replace("Type a question in English or Hebrew, or pick a button below.", "Tap the microphone and speak, or type, in English or Hebrew. Or pick a button below.")
s = s.replace("כתבו שאלה בעברית או באנגלית, או בחרו כפתור למטה.", "הקישו על המיקרופון ודברו, או כתבו, בעברית או באנגלית. אפשר גם לבחור כפתור למטה.")

# 5. Service worker registration + close document
s = s.replace("</script>\n", """
if("serviceWorker" in navigator&&location.protocol==="https:"){navigator.serviceWorker.register("sw.js").catch(()=>{})}
</script>
</body>
</html>
""")
open(f"{D}/index.html", "w", encoding="utf-8").write(s)
open(f"{D}/app.js", "w", encoding="utf-8").write(re.findall(r"<script>(.*?)</script>", s, re.S)[0])

# 6. Manifest, service worker, icons
json.dump({"name": "Child Care Rules Study", "short_name": "Rules Study", "start_url": "./", "scope": "./",
           "display": "standalone", "background_color": "#f3f6f4", "theme_color": "#0f7a63", "lang": "en",
           "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
                     {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}]},
          open(f"{D}/manifest.json", "w"), indent=2)
open(f"{D}/sw.js", "w").write("""const C="rules-study-v1";const FILES=["./","index.html","manifest.json","icon-192.png","icon-512.png"];
self.addEventListener("install",e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(FILES)));self.skipWaiting()});
self.addEventListener("activate",e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==C).map(k=>caches.delete(k)))));self.clients.claim()});
self.addEventListener("fetch",e=>{const u=new URL(e.request.url);
  if(e.request.method!=="GET"||u.hostname==="api.anthropic.com")return;
  e.respondWith(caches.match(e.request).then(hit=>hit||fetch(e.request).then(r=>{if(r.ok&&(u.origin===location.origin||u.hostname.endsWith("gstatic.com")||u.hostname.endsWith("googleapis.com"))){const cp=r.clone();caches.open(C).then(c=>c.put(e.request,cp))}return r}).catch(()=>caches.match("index.html"))))});
""")
for size in (192, 512):
    im = Image.new("RGB", (size, size), "#0f7a63"); d = ImageDraw.Draw(im)
    pad = size * .2
    d.rounded_rectangle([pad, pad * 1.1, size - pad, size - pad * .9], radius=size * .06, fill="#ffffff")
    d.rounded_rectangle([size * .38, pad * .75, size * .62, pad * 1.35], radius=size * .03, fill="#ffe08a")
    for i, y in enumerate((.42, .55, .68)):
        d.ellipse([size * .29, size * y - size * .03, size * .35, size * y + size * .03], fill="#0f7a63")
        d.rounded_rectangle([size * .4, size * y - size * .015, size * .7, size * y + size * .015], radius=4, fill="#9bb0a9")
    im.save(f"{D}/icon-{size}.png")

with zipfile.ZipFile(f"{D}/rules-study-android.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for f in ("index.html", "manifest.json", "sw.js", "icon-192.png", "icon-512.png"):
        z.write(f"{D}/{f}", f)
print("built", len(s))
