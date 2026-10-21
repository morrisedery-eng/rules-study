// ----- Speech text cleanup: turn symbols, codes and abbreviations into words a voice reads correctly -----
const HE_TERMS=[
  [/1-800-96-ABUSE/g,"1, 800, 96, אַבְּיוּז"],[/\(?\s*‎?1-800-962-2873‎?\s*\)?/g," 1, 800, 962, 2873 "],
  [/2A:10BC/g,"2 אֵיי, 10 בִּי סִי"],[/(\d+)C-(\d+)(\.\d+)?/g,(m,a,b,c)=>`${a} סִי ${b}${c||""}`],
  [/CF\/PI\s*175-24/g,"סִי אֶף פִּי אֵיי, 175, 24"],[/CF-FSP/g,"סִי אֶף, אֶף אֶס פִּי"],[/CF\s*1649A/g,"סִי אֶף, 1649 אֵיי"],[/1649A/g,"1649 אֵיי"],
  [/\bDH\b/g,"דִּי אֵייץ׳"],[/\bDCF\b/g,"דִּי סִי אֶף"],[/\bADA\b/g,"אֵיי דִּי אֵיי"],[/\bIDEA\b/g,"אַיְידִיאָה"],[/\bVPK\b/g,"וִי פִּי קֵיי"],[/\bSR\b/g,"אֶס אַר"],[/\bCDA\b/g,"סִי דִּי אֵיי"],
  [/\bFCCPC\b/g,"אֶף סִי סִי פִּי סִי"],[/\bFDLE\b/g,"אֶף דִּי אֶל אִי"],[/\bFBI\b/g,"אֶף בִּי אֵיי"],[/\bCEU\b/g,"סִי אִי יוּ"],[/\bCPR\b/g,"הַחְיָיאָה"],[/\bCO\b/g,"פַּחְמָן חַד חַמְצָנִי"],
  [/\bUSDA\b/g,"יוּ אֶס דִּי אֵיי"],[/MyPlate/g,"מַיי פְּלֵייט"],[/\bCDC\b/g,"סִי דִּי סִי"],[/\bCPSC\b/g,"סִי פִּי אֶס סִי"],[/\bNAEYC\b/g,"נַאיֵיק"],[/\bUDAP\b/g,"יוּדַאפּ"],
  [/\bRNRF\b/g,"אַר אֶן אַר אֶף"],[/LiveScan/g,"לַייב סְקָאן"],[/Gold Seal/g,"גוֹלְד סִיל"],[/School Readiness/g,"סְקוּל רֶדִינֶס"],[/Head Start/g,"הֶד סְטַארְט"],
  [/Caring for Our Children/g,"קֵרִינְג פוֹר אָוואר צִ׳ילְדְרֶן"],[/Big Pelicans Prefer Sardines/g,"בִּיג פֶּלִיקַנְס פְּרִיפֶר סַרְדִינְס"],[/\bHIV\b/g,"אֵייץ׳ אַיי וִי"],
  [/\bF\.S\./g,"חוּקֵּי פְלוֹרִידָה"],[/\bF\.A\.C\./g,"הַקּוֹד הַמִּנְהָלִי שֶׁל פְלוֹרִידָה"],[/\bSIDS\b/g,"מָוֶות בַּעֲרִיסָה"],[/\bdrop-in\b/gi,"דְּרוֹפּ אִין"],[/\bswaddling\b/gi,"עֲטִיפָה"],
  [/\bFirst Aid\b/g,"פֶרְסְט אֵייד"],[/\bKnow Your Child Care Facility\b/g,"הַכִּירוּ אֶת מִתְקַן הַטִּיפּוּל בִּילָדִים"]
];
const HE_MARKS_RX=/[\u0591-\u05BD\u05BF\u05C1\u05C2\u05C4\u05C5\u05C7]/g;
const heNoMarks=s=>String(s).replace(HE_MARKS_RX,"");
const heEsc=s=>s.replace(/[.*+?^${}()|[\]\\]/g,"\\$&");
// a pattern that matches Hebrew text with or without niqqud
const heLoose=s=>new RegExp(heEsc(s).replace(/([\u05D0-\u05EA])/g,"$1[\\u0591-\\u05C7]*"),"g");
const HE_ABBR=[["תמ״ל","תַּרְכּוֹבֶת מָזוֹן לְתִינוֹקוֹת"],["דק׳","דַּקּוֹת"],["מ״ל","מִילִילִיטֶר"],["ע״י","עַל יְדֵי"],["טמפ׳","טֶמְפֶּרָטוּרַת"],["אינץ׳","אִינְץ׳"],["יום ו׳","יוֹם שִׁישִּׁי"],["כיתה ו׳","כִּיתָּה וָו"],["מס׳","מִסְפָּר"]].map(([a,b])=>[heLoose(a),b]);
// Full niqqud: whole known sentences first (HE_SPEAK), then single words (HE_WORDS); text already with niqqud is left alone
const HE_B="(?<![\\u05D0-\\u05EA\\u0591-\\u05C7])",HE_A="(?![\\u05D0-\\u05EA\\u0591-\\u05C7])";
function heVocalize(t){
  if(typeof HE_SPEAK!=="undefined")for(const [p,v] of HE_SPEAK)if(t.includes(p))t=t.replace(new RegExp(HE_B+heEsc(p)+HE_A,"g"),()=>v);
  if(typeof HE_WORDS!=="undefined")t=t.replace(/[\u05D0-\u05EA\u0591-\u05C7]+/g,w=>/[\u0591-\u05C7]/.test(w)?w:(HE_WORDS[w]||w));
  return t.replace(/\u05C7/g,"\u05B9"); // qamatz qatan → holam, so "kol" is never read as "kal"
}
function sayHe(t){
  t=heVocalize(String(t).replace(/<[^>]+>/g,""));
  HE_TERMS.forEach(([r,w])=>t=t.replace(r,w));HE_ABBR.forEach(([r,w])=>t=t.replace(r,w));
  // Class I / II / III: after "סוג" masculine, otherwise feminine (דרגה, פרק)
  const RM={I:1,II:2,III:3,IV:4},RF=["","אַחַת","שְׁתַּיִם","שָׁלוֹשׁ","אַרְבַּע"],RMm=["","אֶחָד","שְׁנַיִם","שְׁלוֹשָׁה","אַרְבָּעָה"];
  t=t.replace(/(ס[\u0591-\u05C7]*ו[\u0591-\u05C7]*ג\s+)(IV|III|II|I)(?![A-Za-z])/g,(m,a,r)=>a+RMm[RM[r]]).replace(/(^|[^A-Za-z])(IV|III|II|I)(?![A-Za-z])/g,(m,a,r)=>a+RF[RM[r]]);
  t=t.replace(/(\d+)\s*⅜/g,"$1 וְשָׁלוֹשׁ שְׁמִינִיּוֹת").replace(/(\d+)\s*½/g,"$1 וָחֵצִי").replace(/(\d+)\s*¼/g,"$1 וָרֶבַע").replace(/¼/g,"רֶבַע").replace(/½/g,"חֵצִי").replace(/⅜/g,"שָׁלוֹשׁ שְׁמִינִיּוֹת")
    .replace(/(\d+(?:\.\d+)?)\s*°F/g,"$1 מַעֲלוֹת פָרֶנְהַייט").replace(/°F/g,"מַעֲלוֹת פָרֶנְהַייט").replace(/(\d+)\s*°C/g,"$1 מַעֲלוֹת צֶלְזְיוּס")
    .replace(/\b1:(\d+)/g,(m,n)=>"אֶחָד לְכֹל "+numHe(+n,"m"))
    .replace(/\$(\d[\d,]*)\s*[–-]\s*\$(\d[\d,]*)/g,"בֵּין $1 לְ-$2 דּוֹלָר").replace(/(\d[\d,]*)\$\s*[–-]\s*(\d[\d,]*)\$/g,"בֵּין $1 לְ-$2 דּוֹלָר")
    .replace(/\$(\d[\d,]*)/g,"$1 דּוֹלָר").replace(/(\d[\d,]*)\$/g,"$1 דּוֹלָר")
    .replace(/(\d+(?:\.\d+)?)\s*%/g,"$1 אָחוּז").replace(/(\d+)\+/g,"$1 וּמַעְלָה")
    .replace(/(\d+(?:\.\d+)?)\s*[–-]\s*(\d+(?:\.\d+)?)/g,"$1 עַד $2")
    .replace(/≤\s*/g,"עַד ").replace(/≥\s*/g,"לְפָחוֹת ").replace(/\s*≠\s*/g," אֵינוֹ ").replace(/[←→]/g,", ").replace(/[·•]/g,", ").replace(/×/g," כָּפוּל ").replace(/÷/g," חֶלְקֵי ").replace(/=/g," שָׁוֶוה ")
    .replace(/([\u05D0-\u05EA][\u0591-\u05C7]*)-(?=\d)/g,"$1").replace(/[״”“"]/g,"").replace(/\s+/g," ").trim();
  return heNumbersToWords(t).replace(/(^|\s)([ובלמכה])[\u0591-\u05C7]*-(?=([\u05D0-\u05EA][\u0591-\u05C7]*))/g,(m,a,p,w)=>a+hePrefix(p,w)).replace(/(^|\s)(ש[\u0591-\u05C7]*)-(?=[\u05D0-\u05EA])/g,"$1$2").replace(/\s\+\s/g," וְעוֹד ").replace(/\s+,/g,",").replace(/,\s*,/g,",");
}
function sayEn(t){
  t=String(t).replace(/<[^>]+>/g,"");
  t=t.replace(/1-800-96-ABUSE/g,"1 800 96 ABUSE").replace(/2A:10BC/g,"2 A 10 B C").replace(/(\d+)C-(\d+)/g,"$1 C $2")
    .replace(/\bF\.S\./g,"Florida Statutes").replace(/\bF\.A\.C\./g,"Florida Administrative Code").replace(/\bss\.\s/g,"sections ").replace(/\bs\.\s(?=\d)/g,"section ")
    .replace(/\be\.g\.,?/g,"for example,").replace(/\bi\.e\.,?/g,"that is,")
    .replace(/(\d+)\s*⅜/g,"$1 and three eighths").replace(/(\d+)\s*½/g,"$1 and a half").replace(/(\d+)\s*¼/g,"$1 and a quarter").replace(/¼/g,"a quarter").replace(/½/g,"a half")
    .replace(/(\d+(?:\.\d+)?)\s*°F/g,"$1 degrees").replace(/\b1:(\d+)/g,"1 to $1")
    .replace(/\$(\d[\d,]*)\s*[–-]\s*\$(\d[\d,]*)/g,"$1 to $2 dollars").replace(/(\d+)\+/g,"$1 or more")
    .replace(/(\d+(?:\.\d+)?)\s*[–-]\s*(\d+(?:\.\d+)?)/g,"$1 to $2").replace(/\bsq ft\b/g,"square feet").replace(/(\d)\s*ft\b/g,"$1 feet").replace(/(\d)\s*in\b\.?/g,"$1 inches").replace(/\b(eighths|half|quarter)\s+in\b\.?/g,"$1 inches")
    .replace(/≤\s*/g,"at most ").replace(/≥\s*/g,"at least ").replace(/[←→]/g,", ").replace(/[·•]/g,", ").replace(/×/g," times ").replace(/÷/g," divided by ").replace(/=/g," equals ")
    .replace(/\s+/g," ").trim();
  return t;
}
// Voice settings (stored per device)
const voicePref=lang=>store.get("rr-voice-"+lang,"");
const voiceRate=()=>store.get("rr-rate",0.9);

function listVoices(lang){
  if(window.AndroidBridge&&AndroidBridge.listVoices){try{return JSON.parse(AndroidBridge.listVoices(lang==="he"?"he-IL":"en-US")).map(v=>({name:v.name,label:`${v.name}${v.network?" · online":""}${v.installed===false?" · not downloaded":""}`}))}catch(e){return[]}}
  if(!window.speechSynthesis||!speechSynthesis.getVoices)return[];
  return speechSynthesis.getVoices().filter(v=>lang==="he"?/^(he|iw)/i.test(v.lang):/^en/i.test(v.lang)).map(v=>({name:v.name,label:`${v.name} (${v.lang})`}));
}
function fillVoices(){
  ["he","en"].forEach(l=>{const sel=document.getElementById("v-"+l);if(!sel)return;const vs=listVoices(l);
    sel.innerHTML=`<option value="">Automatic (best available) · אוטומטי (הטוב ביותר)</option>`+vs.map(v=>`<option value="${v.name.replace(/"/g,"&quot;")}">${v.label}</option>`).join("");
    sel.value=vs.some(v=>v.name===voicePref(l))?voicePref(l):"";sel.onchange=()=>store.set("rr-voice-"+l,sel.value)});
  const r=document.getElementById("v-rate"),rv=document.getElementById("v-rate-val");
  if(r){r.value=voiceRate();rv.textContent=Math.round(voiceRate()*100)+"%";r.oninput=()=>{store.set("rr-rate",+r.value);rv.textContent=Math.round(r.value*100)+"%"}}
  const n=document.getElementById("v-none");if(n)n.hidden=listVoices("he").length>0;
}
{const vs=document.getElementById("vset");if(vs)vs.addEventListener("toggle",()=>{if(vs.open)fillVoices()});
 const vt=document.getElementById("v-test");if(vt)vt.onclick=()=>speakParts([{text:"שלום! זה קול הקריאה בעברית. היחס לתינוקות הוא 1:4, והטמפרטורה בכיתה היא 65–82°F.",lang:"he"},{text:"Hello! This is the English voice. The infant ratio is 1:4, and room temperature is 65–82°F.",lang:"en"}],null);
 try{if(window.speechSynthesis&&speechSynthesis.addEventListener)speechSynthesis.addEventListener("voiceschanged",()=>{if(vs&&vs.open)fillVoices()})}catch(e){}}

// ----- Hebrew numbers → correct words with niqqud, matching the noun's gender -----
const HE_F=["אֶפֶס","אַחַת","שְׁתַּיִם","שָׁלוֹשׁ","אַרְבַּע","חָמֵשׁ","שֵׁשׁ","שֶׁבַע","שְׁמוֹנֶה","תֵּשַׁע","עֶשֶׂר"];
const HE_M=["אֶפֶס","אֶחָד","שְׁנַיִם","שְׁלוֹשָׁה","אַרְבָּעָה","חֲמִשָּׁה","שִׁשָּׁה","שִׁבְעָה","שְׁמוֹנָה","תִּשְׁעָה","עֲשָׂרָה"];
const HE_TEEN_F=["","אַחַת עֶשְׂרֵה","שְׁתֵּים עֶשְׂרֵה","שְׁלוֹשׁ עֶשְׂרֵה","אַרְבַּע עֶשְׂרֵה","חֲמֵשׁ עֶשְׂרֵה","שֵׁשׁ עֶשְׂרֵה","שְׁבַע עֶשְׂרֵה","שְׁמוֹנֶה עֶשְׂרֵה","תְּשַׁע עֶשְׂרֵה"];
const HE_TEEN_M=["","אַחַד עָשָׂר","שְׁנֵים עָשָׂר","שְׁלוֹשָׁה עָשָׂר","אַרְבָּעָה עָשָׂר","חֲמִשָּׁה עָשָׂר","שִׁשָּׁה עָשָׂר","שִׁבְעָה עָשָׂר","שְׁמוֹנָה עָשָׂר","תִּשְׁעָה עָשָׂר"];
const HE_TENS=["","","עֶשְׂרִים","שְׁלוֹשִׁים","אַרְבָּעִים","חֲמִשִּׁים","שִׁשִּׁים","שִׁבְעִים","שְׁמוֹנִים","תִּשְׁעִים"];
const HE_HUN=["","מֵאָה","מָאתַיִם","שְׁלוֹשׁ מֵאוֹת","אַרְבַּע מֵאוֹת","חֲמֵשׁ מֵאוֹת","שֵׁשׁ מֵאוֹת","שְׁבַע מֵאוֹת","שְׁמוֹנֶה מֵאוֹת","תְּשַׁע מֵאוֹת"];
const HE_THO=["","אֶלֶף","אַלְפַּיִם","שְׁלוֹשֶׁת אֲלָפִים","אַרְבַּעַת אֲלָפִים","חֲמֵשֶׁת אֲלָפִים","שֵׁשֶׁת אֲלָפִים","שִׁבְעַת אֲלָפִים","שְׁמוֹנַת אֲלָפִים","תִּשְׁעַת אֲלָפִים"];
// "and": וּ before ב/ו/מ/פ or a letter with sheva; וַ before hataf-patah; otherwise וְ
function heVav(w){if(/^[בומפ]/.test(w)||/^[\u05D0-\u05EA][\u05C1\u05C2\u05BC]*\u05B0/.test(w))return "וּ"+w;if(/^[\u05D0-\u05EA][\u05C1\u05C2\u05BC]*\u05B2/.test(w))return "וַ"+w;return "וְ"+w}
function heUnder100(n,g){const U=g==="m"?HE_M:HE_F;if(n<=10)return U[n];if(n<20)return (g==="m"?HE_TEEN_M:HE_TEEN_F)[n-10];
  const t=Math.floor(n/10),u=n%10;return u?HE_TENS[t]+" "+heVav(U[u]):HE_TENS[t]}
function numHe(n,g,construct){
  if(n===0)return "אֶפֶס";
  if(construct&&n===2)return g==="m"?"שְׁנֵי":"שְׁתֵּי";
  const th=Math.floor(n/1000),h=Math.floor(n%1000/100),r=n%100,parts=[];
  if(th)parts.push(th<10?HE_THO[th]:heUnder100(th,"m")+" אֶלֶף");
  if(h)parts.push(HE_HUN[h]);
  if(r){const w=heUnder100(r,g);parts.push(parts.length&&(r<=20||r%10===0)?heVav(w):w)}
  else if(parts.length>1)parts[parts.length-1]=heVav(parts[parts.length-1]);
  return parts.join(" ");
}
const HE_MASC=new Set("ימים יום חודשים חודש ילדים ילד דולר אחוז אחוזים שבועות שבוע אתרים אתר מקרים ניסיונות כללים כלל נושאים קורסים קורס מבחנים חלקים חלק אנשי עובדים עובד מטר מטרים אינץ סנטימטרים מיליליטר פרקים שיעורים תרגילים כיורים כיור מזרנים מקומות חלונות לוחות פריטים טפסים טופס צעדים רישומים מתקנים מבוגרים מבוגר תינוקות תינוק פעוטות פעוט רגעים סבבים מושבים מטפים מתנדבים מעסיקים צוותים שאלונים".split(" "));
const HE_FEM_IM=new Set(["שנים","פעמים","ביצים","מילים"]);
function heGender(w){if(!w)return "f";w=heNoMarks(w);const s=w.replace(/^[והבלמשכ]/,"");
  if(/^ב(ינואר|פברואר|מרץ|אפריל|מאי|יוני|יולי|אוגוסט|ספטמבר|אוקטובר|נובמבר|דצמבר)$/.test(w))return "m";
  if(HE_MASC.has(w)||HE_MASC.has(s))return "m";if(HE_FEM_IM.has(w)||HE_FEM_IM.has(s))return "f";
  return /ים$/.test(w)?"m":"f"}
const HE_VOC=[["שתיים","שְׁתַּיִם"],["שתי","שְׁתֵּי"],["שלוש","שָׁלוֹשׁ"],["שלושה","שְׁלוֹשָׁה"],["ארבע","אַרְבַּע"],["ארבעה","אַרְבָּעָה"],["חמש","חָמֵשׁ"],["חמישה","חֲמִשָּׁה"],
  ["שש","שֵׁשׁ"],["שישה","שִׁשָּׁה"],["שבע","שֶׁבַע"],["שבעה","שִׁבְעָה"],["שמונה","שְׁמוֹנֶה"],["תשע","תֵּשַׁע"],["תשעה","תִּשְׁעָה"],["עשר","עֶשֶׂר"],["עשרה","עֲשָׂרָה"],
  ["שנתיים","שְׁנָתַיִם"],["יומיים","יוֹמַיִם"],["פעמיים","פַּעֲמַיִם"],["שבועיים","שְׁבוּעַיִם"],["חודשיים","חוֹדְשַׁיִם"],["שעתיים","שְׁעָתַיִם"],["אחת","אַחַת"],["אחד","אֶחָד"],
  ["חצי","חֵצִי"],["רבע","רֶבַע"],["שמיניות","שְׁמִינִיּוֹת"],["שלישי","שְׁלִישִׁי"],["שני","שֵׁנִי"],["ראשון","רִאשׁוֹן"],["רביעי","רְבִיעִי"],["חמישי","חֲמִישִׁי"],["שישי","שִׁישִּׁי"]];
function hePrefix(p,w){const f=w[0],m=w.slice(1).match(/^[\u05BC\u05C1\u05C2]*([\u05B0-\u05BB])?/)[1]||"";
  if(p==="ו")return heVav(w).slice(0,2);
  if(p==="מ")return /[אהחער]/.test(f)?"מֵ":"מִ";
  if(p==="ה")return /[אער]/.test(f)?"הָ":"הַ";
  const d=p==="ב"||p==="כ"?"\u05BC":"";
  return p+d+(m==="\u05B0"?"\u05B4":m==="\u05B2"?"\u05B7":m==="\u05B1"?"\u05B6":"\u05B0")}
function heNumbersToWords(t){
  t=t.replace(/(^|[^\u05D0-\u05EA\u0591-\u05C7])([ובלמכה])[\u0591-\u05C7]*-?(?=\d)/g,"$1\u0001$2");
  HE_VOC.forEach(([a,b])=>{t=t.replace(new RegExp("(^|[\\s,.;:(\"״])([והבל]?)"+a+"(?=$|[\\s,.;:)!?\"״])","g"),"$1$2"+b)});
  t=t.replace(/(\d),(\d{3})/g,"$1$2");
  t=t.replace(/\b(\d{1,2}):(\d{2})\b/g,(m,h,mi)=>numHe(+h,"f")+(mi!=="00"?" "+heVav(numHe(+mi,"f"))+" דַּקּוֹת":""));
  return t.replace(/(\d+)(?:\.(\d+))?(\s*)([\u05D0-\u05EA][\u05D0-\u05EA\u0591-\u05C7]*)?/g,(m,a,dec,sp,word)=>{
    const pw=word?heNoMarks(word):"",g=heGender(pw),noun=!dec&&pw&&sp&&(HE_MASC.has(pw)||HE_FEM_IM.has(pw)||/(ים|ות)$/.test(pw)||/^(שעה|דקה|שנה|רגל|מעלות|דולר|אחוז|יום|חודש|שבוע|אינץ|פעם)$/.test(pw));
    let w=/^0\d/.test(a)?a.split("").map(d=>HE_F[+d]).join(" "):numHe(+a,g,noun);
    if(dec)w+=" נְקוּדָה "+dec.split("").map(d=>HE_F[+d]).join(" ");
    return w+(sp||"")+(word||"")}).replace(/\u0001([ובלמכה])([\u05D0-\u05EA][\u0591-\u05C7]*)/g,(m,p,w)=>hePrefix(p,w)+w).replace(/\u0001/g,"");
}
