// ---------- Offline study helper: no internet, no API ----------
const ICON={spk:'<svg viewBox="0 0 24 24"><path d="M4 9h4l5-4v14l-5-4H4z"/><path d="M16 9a4 4 0 0 1 0 6"/><path d="M19 6a8 8 0 0 1 0 12"/></svg>',
  ask:'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.7.3-1 .9-1 1.7"/><path d="M12 17h.01"/></svg>'};
const plain=s=>s.replace(/<[^>]+>/g,"").replace(/\s+/g," ").trim();
const isHe=s=>/[֐-׿]/.test(s);
const NB=window.AndroidBridge||null; // native Android voice + microphone

// ----- Voice output -----
let speakingBtn=null,speakId=0;
function stopSpeak(){try{if(NB)NB.stopSpeaking();else if(window.speechSynthesis)speechSynthesis.cancel()}catch(e){}
  if(speakingBtn)speakingBtn.classList.remove("speaking");speakingBtn=null}
function bestWebVoice(lang){if(!window.speechSynthesis||!speechSynthesis.getVoices)return null;const want=voicePref(lang),vs=speechSynthesis.getVoices();
  if(want){const v=vs.find(v=>v.name===want);if(v)return v}
  const pool=vs.filter(v=>lang==="he"?/^(he|iw)/i.test(v.lang):/^en(-US)?/i.test(v.lang));
  return pool.find(v=>/natural|neural|online|premium|enhanced/i.test(v.name))||pool.find(v=>/google/i.test(v.name))||pool[0]||null}
function speakParts(parts,btn){
  const same=btn&&speakingBtn===btn;stopSpeak();if(same)return; // second tap stops
  parts=parts.filter(p=>p.text&&p.text.trim())
    .map(p=>({lang:p.lang,text:p.lang==="he"?sayHe(p.text):sayEn(p.text)}))
    // English phrases inside Hebrew text go to the English voice
    .flatMap(p=>p.lang!=="he"?[p]:p.text.split(/((?:[A-Za-z][\w'’.\-]*)(?:[\s,:;\-–/?]+[A-Za-z0-9][\w'’.\-]*)+\??)/).map((x,i)=>({lang:i%2?"en":"he",text:i%2?sayEn(x):x})).filter(x=>/[A-Za-z\u05D0-\u05EA0-9]/.test(x.text)))
    .flatMap(p=>p.text.split(/(?<=[.!?;])\s+/).filter(s=>s.trim()).map(s=>({lang:p.lang,text:s})));
  if(!parts.length)return;
  if(btn){btn.classList.add("speaking");speakingBtn=btn}
  const id=++speakId,rate=voiceRate();
  if(NB){NB.speak(JSON.stringify(parts.map(p=>({text:p.text,lang:p.lang==="he"?"he-IL":"en-US",voice:voicePref(p.lang),rate}))),String(id));return}
  if(!window.speechSynthesis){helperNote(T("Reading aloud isn't available on this device.","הקראה בקול לא זמינה במכשיר הזה."));return}
  parts.forEach((p,i)=>{const u=new SpeechSynthesisUtterance(p.text);u.lang=p.lang==="he"?"he-IL":"en-US";u.rate=rate;const v=bestWebVoice(p.lang);if(v)u.voice=v;
    if(i===parts.length-1)u.onend=u.onerror=()=>window.onNativeSpeakDone(String(id));speechSynthesis.speak(u)});
}
window.onNativeSpeakDone=id=>{if(String(id)===String(speakId)&&speakingBtn){speakingBtn.classList.remove("speaking");speakingBtn=null}};
window.onNativeSpeakError=code=>{
  if(speakingBtn){speakingBtn.classList.remove("speaking");speakingBtn=null}
  if(code==="he-missing")helperNote(T("This phone has no Hebrew voice installed. Open Settings → Accessibility (or System) → Text-to-speech → Speech Services by Google → Install voice data → Hebrew.","לא מותקן קול בעברית. פתחו הגדרות ← נגישות (או מערכת) ← המרת טקסט לדיבור ← שירותי הדיבור של Google ← התקנת נתוני קול ← עברית."));
  else if(code==="no-tts")helperNote(T("Text-to-speech isn't ready on this phone. Install “Speech Services by Google” from the Play Store.","המרת טקסט לדיבור לא מוכנה. התקינו את ”שירותי הדיבור של Google“ מחנות Play."));
};
function speakBi(o,btn){const en={text:plain(o.en),lang:"en"},he={text:plain(o.he),lang:"he"};
  speakParts(mode==="en"?[en]:mode==="he"?[he]:[en,he],btn)}
function speakMixed(text,btn){const parts=[];
  text.split(/\n+/).forEach(line=>{line=line.replace(/[•\-–]\s/g,"");const lang=isHe(line)?"he":"en";const last=parts[parts.length-1];
    if(last&&last.lang===lang)last.text+=". "+line;else parts.push({text:line,lang})});speakParts(parts,btn)}

// ----- Search over the course material -----
const STOP=new Set(("a an the is are was were what whats how many much do does did i im my me to of in on at for and or can could you your tell about please explain why when who which it its that this be with there should must need needs have has get rule rules out child children childs kid kids allowed okay ok "+
 "מה מהו מהי איך כמה האם של את על עם זה זו זאת יש אני לי מי מתי למה צריך צריכה צריכים חייב חייבת אפשר בבקשה תסביר תסבירי הסבר לגבי או גם כל הם היא הוא אתה את לך ילד ילדים ילדה לילד לילדים מותר בסדר בן בת בעלי").split(" "));
const norm=s=>s.toLowerCase().replace(/(^|\s)[והבלמשכ]-(?=\d)/g,"$1").replace(/time[\s-]+outs?/g,"timeout").replace(/פסק[\s-]+זמן/g,"פסקזמן").replace(/[׳״'"“”‘’.,!?;:()\[\]\/]/g," ").replace(/\s+/g," ").trim();
const heStrip=w=>(w.length>3&&/^[והבלמשכ]/.test(w))?w.slice(1):w;
function toks(s){const out=[];norm(s).split(" ").forEach(w=>{if(!w||STOP.has(w))return;out.push(w);
  if(isHe(w)){let a=heStrip(w);if(a!==w){out.push(a);let b=heStrip(a);if(b!==a)out.push(b)}if(w.endsWith("ים")||w.endsWith("ות"))out.push(w.slice(0,-2))}
  else if(w.length>3&&w.endsWith("s"))out.push(w.slice(0,-1))});return out}
const INDEX=[];
DAYS.forEach((d,di)=>d.pts.forEach((p,pi)=>{const kb=KB[di][pi];
  INDEX.push({d:di,p:pi,kw:new Set(toks(kb.k)),tx:new Set(toks(plain(p.en)+" "+plain(p.he)+" "+d.t.en+" "+d.t.he))})}));
const DF={},TF={};INDEX.forEach(e=>{e.kw.forEach(k=>DF[k]=(DF[k]||0)+1);e.tx.forEach(k=>TF[k]=(TF[k]||0)+1)});
const rare=(n)=>Math.log(INDEX.length/(n||1))/Math.log(INDEX.length); // 0 = everywhere, 1 = in one place
const kwW=k=>1.5+3*rare(DF[k])+(DF[k]===1?1:0); // rarer keyword = stronger signal
const txW=k=>.4+1.2*rare(TF[k]);
function search(q){const qt=[...new Set(toks(q))];if(!qt.length)return[];
  return INDEX.map(e=>{let s=0;qt.forEach(t=>{
      if(e.kw.has(t))s+=/^\d/.test(t)?2:kwW(t);
      else if(t.length>=4&&[...e.kw].some(k=>k.length>=4&&(k.startsWith(t)||t.startsWith(k))))s+=1.5;
      if(e.tx.has(t))s+=/^\d/.test(t)?1.2:txW(t);});
    if(s>0&&e.d===cur)s+=.5;return{...e,s}}).filter(e=>e.s>=3).sort((a,b)=>b.s-a.s)}

// ----- Helper UI -----
const hEl=document.getElementById("helper"),hBody=document.getElementById("h-body"),hInput=document.getElementById("h-input"),
  fab=document.getElementById("fab"),hAuto=document.getElementById("h-auto");
let lastLang="en",pendingQuiz=null;
hAuto.checked=store.get("rr-auto",false);hAuto.onchange=()=>store.set("rr-auto",hAuto.checked);
const L=q=>mode==="en"?"en":mode==="he"?"he":(q&&isHe(q)?"he":"en");
const T=(en,he)=>mode==="he"?he:mode==="en"?en:en+"\n\n"+he;
function openHelper(){hEl.hidden=false;fab.hidden=true;fab.setAttribute("aria-expanded","true");if(!hBody.children.length)greet()}
function closeHelper(){hEl.hidden=true;fab.hidden=false;fab.setAttribute("aria-expanded","false");stopSpeak();stopMic()}
fab.onclick=openHelper;document.getElementById("h-close").onclick=closeHelper;document.getElementById("h-stop").onclick=stopSpeak;
window.onNativeBack=()=>{if(!hEl.hidden){closeHelper();return true}return false};
function addMsg(text,who){const m=document.createElement("div");m.className="msg "+who;m.textContent=text;
  m.dir=isHe(text.slice(0,40))?"rtl":"auto";hBody.append(m);hBody.scrollTop=hBody.scrollHeight;return m}
function helperNote(t){if(hEl.hidden)openHelper();const n=addMsg(t,"bot");n.classList.add("h-note")}
function tools(m,text,extra){const t=document.createElement("div");t.className="tools";
  const b=document.createElement("button");b.className="mini";b.innerHTML=ICON.spk+" Listen · הקשב";b.onclick=()=>speakMixed(text,b);t.append(b);
  (extra||[]).forEach(x=>t.append(x));m.append(t);hBody.scrollTop=hBody.scrollHeight}
function btn(label,fn){const b=document.createElement("button");b.className="mini";b.textContent=label;b.onclick=fn;return b}
function reply(text,extra){const m=addMsg(text,"bot");tools(m,text,extra);if(hAuto.checked)speakMixed(text,m.querySelector(".mini"));return m}
function goDayBtn(di){return btn(`Open Day ${di+1} · פתח יום ${di+1}`,()=>{cur=di;renderDays();renderDay();closeHelper();window.scrollTo({top:0})})}
function greet(){if(AI)return reply(T("Hi! I'm your AI tutor for the child care rules course. Ask me anything, in English or Hebrew, and I'll explain it simply. To speak instead of typing, tap the box below and use your keyboard's microphone. You can also say “quiz me”, “summarize today” or “practice exam”.",
  "שלום! אני המורה הדיגיטלי שלכם לקורס חוקי הטיפול בילדים. שאלו אותי כל שאלה, בעברית או באנגלית, ואסביר בפשטות. כדי לדבר במקום להקליד, הקישו על התיבה למטה והשתמשו במיקרופון של המקלדת. אפשר גם לומר ”בחן אותי“, ”סכם את היום“ או ”מבחן תרגול“."));
  reply(T("Hi! I'm your study helper, and I work fully offline. Tap the microphone and speak, or type, in English or Hebrew. Ask about any rule (for example “ratio for 2-year-olds” or “fire drills”), or say “quiz me”, “summarize today”, “read the lesson” or “practice exam”.",
  "שלום! אני עוזר הלימוד שלכם, ואני עובד בלי אינטרנט. הקישו על המיקרופון ודברו, או כתבו, בעברית או באנגלית. שאלו על כל כלל (למשל ”יחס לבני שנתיים“ או ”תרגילי אש“), או אמרו ”בחן אותי“, ”סכם את היום“, ”הקרא את השיעור“ או ”מבחן תרגול“."))}

function pointAnswer(di,pi,lang,part){const d=DAYS[di],p=d.pts[pi],kb=KB[di][pi];
  const one=lg=>lg==="he"
    ?(part==="ex"?`דוגמה (יום ${di+1}):\n${kb.ex.he}`:`מתוך יום ${di+1}: ${d.t.he}\n\n${plain(p.he)}\n\nדוגמה: ${kb.ex.he}\n\nטיפ לזיכרון: ${kb.tip.he}`)
    :(part==="ex"?`Example (Day ${di+1}):\n${kb.ex.en}`:`From Day ${di+1}: ${d.t.en}\n\n${plain(p.en)}\n\nExample: ${kb.ex.en}\n\nMemory tip: ${kb.tip.en}`);
  return mode==="both"?one(lang)+"\n\n— — —\n\n"+one(lang==="he"?"en":"he"):one(lang)}
function answerPoint(di,pi,lang,part){reply(pointAnswer(di,pi,lang,part),[goDayBtn(di)])}

function summary(lang){const d=DAYS[cur];
  const en=`Key facts for Day ${cur+1} (${d.t.en}):\n`+d.cards.map(c=>`• ${c.en} ${c.ae}`).join("\n");
  const he=`עיקרי יום ${cur+1} (${d.t.he}):\n`+d.cards.map(c=>`• ${c.qhe} ${c.ah}`).join("\n");
  reply(mode==="en"?en:mode==="he"?he:(lang==="he"?he+"\n\n"+en:en+"\n\n"+he))}

const LETTERS=["A","B","C","D"],HE_LET=["א","ב","ג","ד"];
function quiz(all,lang){
  const di=all?Math.floor(Math.random()*DAYS.length):cur,qi=Math.floor(Math.random()*DAYS[di].quiz.length),q=DAYS[di].quiz[qi];
  const order=shuffle([0,1,2,3],Date.now()%9973);pendingQuiz={di,qi,order,lang};
  const one=lg=>(lg==="he"?`שאלה (יום ${di+1}):\n${q.q.he}\n`:`Question (Day ${di+1}):\n${q.q.en}\n`)+order.map((oi,i)=>`${lg==="he"?HE_LET[i]:LETTERS[i]}) ${q.o[oi][lg]}`).join("\n");
  const text=mode==="both"?one(lang)+"\n\n"+one(lang==="he"?"en":"he"):one(mode);
  reply(text+"\n\n"+T("Tap your answer.","הקישו על התשובה."),order.map((oi,i)=>btn(`${LETTERS[i]} · ${HE_LET[i]}`,()=>handle(LETTERS[i],true))))}
const WORDNUM={"1":0,"2":1,"3":2,"4":3,first:0,second:1,third:2,fourth:3,one:0,two:1,three:2,four:3,"אחת":0,"אחד":0,"שתיים":1,"שניים":1,"שלוש":2,"ארבע":3,"ראשון":0,"ראשונה":0,"שני":1,"שנייה":1,"שלישי":2,"שלישית":2,"רביעי":3,"רביעית":3,
  a:0,b:1,c:2,d:3,ay:0,bee:1,be:1,see:2,sea:2,dee:3,"א":0,"ב":1,"ג":2,"ד":3,"אלף":0,"בית":1,"גימל":2,"דלת":3};
function gradeQuiz(text){const pq=pendingQuiz,q=DAYS[pq.di].quiz[pq.qi],n=norm(text);let pick=-1;
  const first=n.replace(/^(answer|the answer is|it's|it is|option|letter|תשובה|התשובה היא|התשובה)\s*/,"").split(" ")[0];
  if(first in WORDNUM)pick=WORDNUM[first];
  else pq.order.forEach((oi,i)=>{const o=norm(q.o[oi].en),h=norm(q.o[oi].he);if(pick<0&&(n.includes(o)||n.includes(h)||o.includes(n)&&n.length>2))pick=i});
  if(pick<0)return false;
  pendingQuiz=null;const ok=pq.order[pick]===q.a,right=pq.order.indexOf(q.a);
  const en=(ok?"Correct! ":`Not quite. The answer is ${LETTERS[right]}) ${q.o[q.a].en}. `)+q.x.en;
  const he=(ok?"נכון! ":`לא בדיוק. התשובה היא ${HE_LET[right]}) ${q.o[q.a].he}. `)+q.x.he;
  reply(mode==="en"?en:mode==="he"?he:(pq.lang==="he"?he+"\n\n"+en:en+"\n\n"+he),[btn("Another question · שאלה נוספת",()=>handle(pq.lang==="he"?"בחן אותי":"quiz me",true))]);
  return true}

function handle(text,silentEcho){
  if(hEl.hidden)openHelper();
  const q=text.trim();if(!q)return;addMsg(q,"me");
  const lang=L(q);lastLang=lang;const n=norm(q);
  if(pendingQuiz&&gradeQuiz(q))return;
  if(/\b(help|what can you)\b|עזרה|מה אתה יודע|מה אתה יכול/.test(n))return greet();
  if(/practice exam|mock exam|full exam|whole exam|מבחן תרגול|מבחן מלא|מבחן ניסיון/.test(n)){closeHelper();startExam();return}
  if(/\b(quiz|test me|practice question|ask me)\b|בחן|תבחן|בחני|שאל אותי|תשאל אותי|מבחן|בוחן|שאלת תרגול/.test(n))return quiz(/\b(all|any|random|everything)\b|הכול|הכל|כל הימים|אקראי/.test(n),lang);
  if(/\b(summar|summary|key facts|review)\w*|סכם|סיכום|תסכם|עיקרי|חזרה/.test(n))return summary(lang);
  if(/\b(read|listen)\b.*\b(lesson|today|day)\b|הקרא|תקריא|הקריא|להקריא|תקרא/.test(n)){const d=DAYS[cur];
    reply(T(`Reading Day ${cur+1}. Tap Stop to end.`,`מקריא את יום ${cur+1}. הקישו עצור כדי להפסיק.`));
    speakBi({en:d.pts.map(p=>plain(p.en)).join(" "),he:d.pts.map(p=>plain(p.he)).join(" ")},null);return}
  const dm=n.match(/(?:day|יום)\s*(\d{1,2})/);
  if(dm&&/\b(go|open|show|start)\b|פתח|עבור|תפתח|הראה|לך/.test(n)){const di=+dm[1]-1;if(di>=0&&di<DAYS.length){reply(T(`Opening Day ${di+1}.`,`פותח את יום ${di+1}.`));cur=di;renderDays();renderDay();return}}
  if(/\bnext day\b|היום הבא|יום הבא/.test(n)&&cur<DAYS.length-1){cur++;renderDays();renderDay();return reply(T(`Opening Day ${cur+1}.`,`פותח את יום ${cur+1}.`))}
  if(AI)return aiAnswer(q,lang);
  if(/\b(ratio|ratios)\b|יחס|יחסים/.test(n)&&!/mix|מעורב|swim|water|שחי|מים/.test(n)){
    const t="Staff-to-child ratios · יחסי צוות-ילדים:\n"+RATIOS.map(r=>`• ${r[0]} · ${r[1]}: ${r[2]}`).join("\n");
    return reply(t+"\n\n"+T("Mixed group with a baby under 1 → 1:4 for everyone. Swimming ratios are stricter.","קבוצה מעורבת עם תינוק מתחת לשנה ← 1:4 לכולם. יחסים בשחייה מחמירים יותר."),[goDayBtn(6)])}
  const hits=search(q);
  if(!hits.length)return reply(T(`I couldn't find that in the course material. Try other key words, like “toilets”, “nap”, “car seat” or “background check”. You can also say “quiz me” or “summarize today”. For anything outside the course, ask your instructor.`,
    `לא מצאתי את זה בחומר הקורס. נסו מילות מפתח אחרות, כמו ”שירותים“, ”מנוחה“, ”מושב בטיחות“ או ”בדיקת רקע“. אפשר גם לומר ”בחן אותי“ או ”סכם את היום“. לשאלות מחוץ לקורס, פנו למדריך.`));
  const top=hits[0];answerPoint(top.d,top.p,lang);
  const more=hits.slice(1,3).filter(h=>h.s>=top.s*.7&&!(h.d===top.d&&h.p===top.p));
  if(more.length){const m=addMsg(T("Related:","קשור:"),"bot");m.classList.add("h-note");
    tools(m,"",more.map(h=>btn((lang==="he"?plain(DAYS[h.d].pts[h.p].he):plain(DAYS[h.d].pts[h.p].en)).slice(0,48)+"…",()=>answerPoint(h.d,h.p,lang))));
    m.querySelector(".tools .mini").remove()}
}
function whyAnswer(q){addMsg(mode==="he"?q.q.he:q.q.en,"me");const hit=search(q.q.en+" "+q.o[q.a].en)[0];
  const en=`Answer: ${q.o[q.a].en}\n${q.x.en}`+(hit?`\n\nMemory tip: ${KB[hit.d][hit.p].tip.en}`:"");
  const he=`תשובה: ${q.o[q.a].he}\n${q.x.he}`+(hit?`\n\nטיפ לזיכרון: ${KB[hit.d][hit.p].tip.he}`:"");
  reply(mode==="en"?en:mode==="he"?he:en+"\n\n"+he,hit?[goDayBtn(hit.d)]:[])}
function renderChips(){const d=DAYS[cur];
  document.getElementById("h-day").textContent=mode==="he"?`נושא ${cur+1}: ${d.t.he}`:`Subject ${cur+1}: ${d.t.en}`;
  const chips=[[{en:"Read this lesson",he:"הקרא את השיעור"},"read the lesson today","הקרא את השיעור"],
    [{en:"Summarize this subject",he:"סכם את הנושא"},"summarize today","סכם את היום"],
    [{en:"Quiz me",he:"בחן אותי"},"quiz me","בחן אותי"],
    [{en:"Quiz me on everything",he:"בחן אותי על הכול"},"quiz me on all days","בחן אותי על הכול"]];
  const el=document.getElementById("h-chips");el.innerHTML="";
  chips.forEach(([lab,en,he])=>{el.append(btn(mode==="he"?lab.he:mode==="en"?lab.en:`${lab.en} · ${lab.he}`,()=>handle(mode==="he"?he:en)))})}
document.getElementById("h-form").addEventListener("submit",e=>{e.preventDefault();const q=hInput.value;hInput.value="";handle(q)});
hInput.addEventListener("keydown",e=>{if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();document.getElementById("h-form").requestSubmit()}});

// ----- Microphone -----
const micBtn=document.getElementById("h-mic"),SR=window.SpeechRecognition||window.webkitSpeechRecognition;
let micLang=store.get("rr-miclang",mode==="he"?"he-IL":"en-US"),listening=false,webRec=null,micBase="";
function setMicLang(l){micLang=l;store.set("rr-miclang",l);document.querySelectorAll("[data-ml]").forEach(b=>b.setAttribute("aria-pressed",b.dataset.ml===l))}
document.querySelectorAll("[data-ml]").forEach(b=>b.onclick=()=>setMicLang(b.dataset.ml));setMicLang(micLang);
if(!NB&&!SR)micBtn.hidden=true;
function micOn(){listening=true;micBtn.classList.add("live");hInput.placeholder=micLang==="he-IL"?"מקשיב… דברו עכשיו":"Listening… speak now"}
function micOff(){listening=false;micBtn.classList.remove("live");hInput.placeholder="Ask anything… · שאלו כל דבר…"}
function stopMic(){if(!listening)return;try{if(NB)NB.stopListening();else if(webRec)webRec.stop()}catch(e){}}
window.onNativeSpeech=ev=>{ // {type:"start"|"partial"|"final"|"error"|"end", text, error}
  if(typeof ev==="string")ev=JSON.parse(ev);
  if(ev.type==="start")micOn();
  else if(ev.type==="partial"){hInput.value=micBase+ev.text;hInput.dir=micLang==="he-IL"?"rtl":"auto"}
  else if(ev.type==="final"){micOff();hInput.value=micBase+ev.text;
    if(document.getElementById("h-autosend").checked&&ev.text.trim())document.getElementById("h-form").requestSubmit()}
  else if(ev.type==="error"){micOff();const m={
      permission:T("Microphone permission is off. Tap the mic again and choose Allow, or turn it on in Settings → Apps → Rules Study → Permissions.","הרשאת המיקרופון כבויה. הקישו שוב על המיקרופון ובחרו אישור, או הפעילו אותה בהגדרות ← אפליקציות ← Rules Study ← הרשאות."),
      "no-match":T("I didn't catch that. Tap the mic and try again.","לא הבנתי. הקישו על המיקרופון ונסו שוב."),
      "no-speech":T("I didn't hear anything. Tap the mic and try again.","לא שמעתי כלום. הקישו על המיקרופון ונסו שוב."),
      network:T("Voice typing for this language needs its offline pack. See “Set up offline voice” below.","הקלטה קולית בשפה הזו דורשת חבילה לא מקוונת. ראו ”הגדרת קול ללא אינטרנט“ למטה."),
      "language":T("This language isn't installed for voice typing. See “Set up offline voice” below.","השפה הזו לא מותקנת להקלטה קולית. ראו ”הגדרת קול ללא אינטרנט“ למטה."),
      "unavailable":T("Speech recognition isn't available on this phone. Install the Google app from the Play Store.","זיהוי דיבור לא זמין בטלפון. התקינו את אפליקציית Google מחנות Play.")}[ev.error];
    if(m)helperNote(m)}
  else if(ev.type==="end")micOff();
};
micBtn.onclick=()=>{
  if(listening){stopMic();return}
  stopSpeak();micBase=hInput.value.trim()?hInput.value.trim()+" ":"";
  if(NB){NB.startListening(micLang);return}
  webRec=new SR();webRec.lang=micLang;webRec.interimResults=true;webRec.continuous=false;let fin="";
  webRec.onstart=()=>window.onNativeSpeech({type:"start"});
  webRec.onresult=e=>{let it="";fin="";for(const r of e.results){if(r.isFinal)fin+=r[0].transcript;else it+=r[0].transcript}
    window.onNativeSpeech({type:"partial",text:fin+it})};
  webRec.onerror=e=>window.onNativeSpeech({type:"error",error:e.error==="not-allowed"?"permission":e.error});
  webRec.onend=()=>{if(listening)window.onNativeSpeech({type:"final",text:fin})};
  try{webRec.start()}catch(e){}
};

// ----- AI tutor: real answers from Claude when the page runs on claude.ai (the Android build keeps the offline helper) -----
let AI=null,aiHist=[],aiBusy=false;
(async()=>{try{if(window.claude&&typeof claude.use==="function")AI=await claude.use("sample")}catch(e){AI=null}
  if(AI){const t=document.getElementById("h-ai");if(t)t.hidden=false;hAuto.checked=store.get("rr-autoread",true);hAuto.addEventListener("change",()=>store.set("rr-autoread",hAuto.checked));
    if(hBody.children.length===1){hBody.innerHTML="";greet()}}})();
function aiContext(q){const seen=new Set(),rows=[];
  const add=(d,p)=>{const k=d+"-"+p;if(seen.has(k))return;seen.add(k);const P=DAYS[d].pts[p],K=KB[d][p];
    rows.push(`[Subject ${d+1}: ${DAYS[d].t.en}] ${plain(P.en)} Example: ${plain(K.ex.en)} Memory tip: ${plain(K.tip.en)}`)};
  search(q).slice(0,8).forEach(h=>add(h.d,h.p));DAYS[cur].pts.forEach((p,pi)=>add(cur,pi));
  return rows.join("\n")+"\nStaff-to-child ratios: "+RATIOS.map(r=>`${r[0]} ${r[2]}`).join("; ")+"."}
async function aiAnswer(q,lang){
  if(aiBusy)return;aiBusy=true;stopSpeak();
  const he=lang==="he",m=addMsg(he?"חושב…":"Thinking…","bot");m.dir=he?"rtl":"ltr";
  const prompt=`You are a warm, patient tutor helping an adult student prepare for the Florida DCF course test "Child Care Facility Rules and Regulations" (RNRF). The rules come from the DCF Child Care Facility Handbook in force since September 1, 2026. The student is currently studying Subject ${cur+1}: ${DAYS[cur].t.en}.
How to answer:
- Base your answer on the course material below. If the answer isn't in it, say you're not sure the course covers it and suggest asking the instructor. Never invent numbers or rules.
- Use simple, friendly words. Keep it short: 2 to 5 sentences. Add one short memory tip when it helps.
- Plain text only: no markdown, no asterisks, no bullet symbols, no headings.
- Answer in ${he?"Hebrew":"English"}.${he?`
- After the answer, write a line with only === and then the exact same answer again with full Hebrew niqqud (vowel points) on every Hebrew word, for a text-to-speech voice. Write numbers as digits.`:""}

Course material:
${aiContext(q)}

Student's question: ${q}`;
  const msgs=[...aiHist.slice(-6),{role:"user",content:prompt}];
  const show=t=>{const i=t.indexOf("===");return (i>=0?t.slice(0,i):t).trim()};
  try{
    const r=await AI(msgs,{cache:false,onText:({text})=>{const v=show(text);if(v){m.textContent=v;hBody.scrollTop=hBody.scrollHeight}}});
    const full=r.text||"",ans=show(full),spoken=full.includes("===")?full.slice(full.indexOf("===")+3).trim():ans;
    m.textContent=ans;aiHist.push({role:"user",content:q},{role:"assistant",content:ans});
    tools(m,ans,[]);
    const lb=m.querySelector(".mini");lb.onclick=()=>speakParts([{text:spoken,lang:he?"he":"en"}],lb);
    if(hAuto.checked)speakParts([{text:spoken,lang:he?"he":"en"}],lb);
  }catch(e){m.remove();
    if(e&&e.code==="not_granted")AI=null;
    if(e&&e.code==="rate_limited")helperNote(T("The AI tutor is busy for a moment. Here's the answer from the course:","המורה הדיגיטלי עסוק לרגע. הנה התשובה מתוך הקורס:"));
    aiBusy=false;const keep=AI;AI=null;handle2(q,lang);AI=keep;return}
  aiBusy=false}
// offline answer (used when the AI tutor isn't available)
function handle2(q,lang){const hits=search(q);
  if(!hits.length)return reply(T("I couldn't find that in the course material. Try other key words, like “toilets”, “nap”, “car seat” or “background check”.","לא מצאתי את זה בחומר הקורס. נסו מילות מפתח אחרות, כמו ”שירותים“, ”מנוחה“, ”מושב בטיחות“ או ”בדיקת רקע“."));
  answerPoint(hits[0].d,hits[0].p,lang)}
