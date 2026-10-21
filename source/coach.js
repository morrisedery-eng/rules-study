// ----- Coach: a step-by-step guided lesson that runs during the 60 minutes -----
// Review → yesterday's cards one at a time; Learn → read each rule, example + tip, then "your turn";
// Key facts → each question shown with its answer. Moves on by itself; Next/Back/Pause/Skip available.
let coach={open:false,part:-1,steps:[],i:0,pass:0,paused:false,t:null,cd:null,phase:"",tok:0};
const speakCbs={};
{const _done=window.onNativeSpeakDone;window.onNativeSpeakDone=id=>{_done(id);const f=speakCbs[String(id)];if(f)setTimeout(f,500)}}
const canSpeak=()=>soundOn()&&(window.AndroidBridge||window.speechSynthesis);
function partsFor(o){const en={text:plain(o.en),lang:"en"},he={text:plain(o.he),lang:"he"};return mode==="en"?[en]:mode==="he"?[he]:[en,he]}
function cClear(){clearTimeout(coach.t);clearInterval(coach.cd);coach.t=null;coach.cd=null;for(const k in speakCbs)delete speakCbs[k]}
function speakThen(parts,cb){
  parts=parts.filter(p=>p.text&&p.text.trim());const words=parts.reduce((a,p)=>a+p.text.split(/\s+/).length,0);
  const tok=coach.tok;
  if(!canSpeak()||!parts.length){coach.t=setTimeout(()=>{if(tok===coach.tok&&coach.open&&!coach.paused)cb()},Math.min(30000,2000+words*380));return}
  stopSpeak();speakParts(parts,null);const id=String(speakId);let fired=false;
  const start=Date.now(),minMs=Math.max(3500,words*320);
  const fire=()=>{if(fired)return;fired=true;delete speakCbs[id];if(tok!==coach.tok||!coach.open||coach.paused)return;clearTimeout(coach.t);
    coach.t=setTimeout(()=>{if(tok===coach.tok&&coach.open&&!coach.paused)cb()},Math.max(0,start+minMs-Date.now()))};
  speakCbs[id]=fire;coach.t=setTimeout(fire,5000+words*800); // safety net if the voice never reports "done"
}
const cardParts=c=>{const p=c.he.split(" · ");return{q:{en:c.en,he:c.en},a:{en:p[0],he:p[p.length-1]}}};
function stepsFor(part,pass,intro){
  const d=DAYS[cur],S=[];
  if(part===0){
    if(intro&&pass===0)S.push({type:"say",title:d.t,body:B(`Today's subject: ${d.t.en}. We'll study it for 60 minutes, then you'll take a quiz on it.`,`הנושא של היום: ${d.t.he}. נלמד אותו 60 דקות, ואחר כך בוחן עליו.`)});
    if(pass>0)S.push({type:"say",title:B(`Round ${pass+1}`,`סבב ${pass+1}`),body:B("Let's go over the rules again.","בואו נעבור שוב על הכללים.")});
    d.pts.forEach((p,pi)=>S.push({type:"point",pi,round:pass+1}));
    S.push({type:"end",part:0});
  }else{
    S.push({type:"say",title:B("Key facts","עובדות חשובות"),body:pass===0?B("Now the key facts of this subject, one by one: a question and its answer.","עכשיו העובדות החשובות של הנושא, אחת אחת: שאלה והתשובה שלה."):B("Let's go over the key facts again.","בואו נעבור שוב על העובדות החשובות.")});
    d.cards.forEach((c,ci)=>S.push({type:"fact",c,ci,n:d.cards.length}));
    S.push({type:"end",part:1});
  }
  return S;
}
function coachLoad(part,intro){coach.part=part;coach.pass=0;coach.steps=stepsFor(part,0,intro);coach.i=0;renderStep()}
function next(){coach.i++;renderStep()}
function cBtn(id,label,cls){return `<button type="button" class="btn ${cls||""}" id="${id}">${label}</button>`}
function countdown(secs,el,done){const tok=coach.tok;let s=secs;if(!el)return;el.textContent=s;clearInterval(coach.cd);coach.cd=setInterval(()=>{if(coach.paused)return;if(tok!==coach.tok){clearInterval(coach.cd);return}s--;el.textContent=Math.max(0,s);if(s<=0){clearInterval(coach.cd);done()}},1000)}
function renderStep(){
  cClear();coach.tok++;if(!coach.open)return;
    if(coach.i>=coach.steps.length){coach.pass++;coach.steps=stepsFor(coach.part,coach.pass,false);coach.i=0}
  const st=coach.steps[coach.i],d=DAYS[cur],body=document.getElementById("c-body"),foot=document.getElementById("c-foot"),S=SEGS[coach.part]||SEGS[0];
  document.getElementById("c-part").textContent=`${d.t.en} · ${S.en} · ${S.he}`;
  document.getElementById("c-prog").style.width=(coach.i/coach.steps.length*100)+"%";
  document.getElementById("c-skip").textContent=coach.part<SEGS.length-1?"Go to key facts · לעובדות החשובות":"Finish → Quiz · סיום ← בוחן";
  document.getElementById("c-pause").textContent=coach.paused?"▶ Resume · המשך":"⏸ Pause · השהה";
  if(coach.paused){body.innerHTML=`<div class="c-center"><h2>${bi(B("Paused","מושהה"),"span")}</h2><p class="ex">${bi(B("The timer is stopped. Press Resume to continue.","הטיימר עצר. לחצו המשך כדי להמשיך."),"span")}</p></div>`;foot.innerHTML="";return}
  const nav=(label)=>`<div class="c-nav">${cBtn("c-back","◀ Back · אחורה","ghost")}${cBtn("c-next",label||"Next ▶ · הבא")}</div>`;
  const wireNav=()=>{const b=document.getElementById("c-back");if(b)b.onclick=()=>{coach.i=Math.max(0,coach.i-1);renderStep()};const n=document.getElementById("c-next");if(n)n.onclick=next};
  if(st.type==="end"){
    const again=()=>{coach.pass++;coach.steps=stepsFor(coach.part,coach.pass,false);coach.i=0;renderStep()};
    const left2=Math.max(0,Math.round(left/60)),tl=B(`${left2} minutes left in this hour.`,`נשארו ${left2} דקות בשעה הזו.`);
    const msg=st.part===0?B("You've gone through all the rules of this subject.","עברתם על כל הכללים של הנושא הזה."):B("You've gone through all the key facts.","עברתם על כל העובדות החשובות.");
    body.innerHTML=`<div class="c-center"><h2>${bi(msg,"span")}</h2><p class="ex">${bi(tl,"span")}</p></div>`;
    foot.innerHTML=`<div class="c-nav">${cBtn("c-again",st.part===0?"Go over the rules again · לעבור שוב על הכללים":"Go over the key facts again · לעבור שוב על העובדות","ghost")}${cBtn("c-go",st.part===0?"Go to key facts · לעובדות החשובות":"Start the quiz · התחל את הבוחן")}</div>`;
    document.getElementById("c-again").onclick=again;
    document.getElementById("c-go").onclick=()=>{if(st.part===0)jumpTo(1);else finishEarly()};
    speakThen(partsFor({en:msg.en+" What would you like to do next?",he:msg.he+" מה תרצו לעשות עכשיו?"}),()=>{});
    return;
  }
  if(st.type==="say"){
    body.innerHTML=`<h2>${bi(st.title,"span")}</h2><div class="bi c-big">${bi(st.body,"p")}</div>`;foot.innerHTML=nav();wireNav();
    speakThen(partsFor(st.body),next);
  }else if(st.type==="recap"){
    const dd=DAYS[st.di],p=dd.pts[st.pi],kb=KB[st.di][st.pi],N=dd.pts.length;
    body.innerHTML=`<span class="label">Review · Day ${st.di+1} · rule ${st.pi+1} of ${N} · חזרה · יום ${st.di+1} · כלל ${st.pi+1} מתוך ${N}</span><div class="bi c-big">${bi(p)}</div><div class="c-box tip"><b>${bi(B("Memory tip","טיפ לזיכרון"),"span")}</b><div class="bi">${bi(kb.tip)}</div></div>`;
    foot.innerHTML=nav();wireNav();
    speakThen(partsFor(p),()=>speakThen(partsFor({en:"Memory tip: "+kb.tip.en,he:"טיפ לזיכרון: "+kb.tip.he}),next));
  }else if(st.type==="point"||st.type==="recall"){
    const p=d.pts[st.pi],kb=KB[cur][st.pi],N=d.pts.length;
    if(st.type==="recall"){
      body.innerHTML=`<span class="label">Rule ${st.pi+1} of ${N} · כלל ${st.pi+1} מתוך ${N}</span><h2>${bi(B("What do you remember?","מה אתם זוכרים?"),"span")}</h2><div class="bi c-hint">${bi(kb.tip)}</div><div class="c-count" id="c-count"></div>`;
      foot.innerHTML=nav("Show the rule ▶ · הצג את הכלל");wireNav();
      speakThen(partsFor({en:"Before I read it, what do you remember? Hint: "+kb.tip.en,he:"לפני שאקריא, מה אתם זוכרים? רמז: "+kb.tip.he}),()=>countdown(20,document.getElementById("c-count"),next));
      return;
    }
    body.innerHTML=`<span class="label">${bi(B(`${st.round>1?`Round ${st.round} · `:""}Rule ${st.pi+1} of ${N}`,`${st.round>1?`סבב ${st.round} · `:""}כלל ${st.pi+1} מתוך ${N}`),"span")}</span><div class="bi c-big">${bi(p)}</div><div id="c-extra"></div>`;
    foot.innerHTML=nav();wireNav();
    speakThen(partsFor(p),()=>{
      document.getElementById("c-extra").innerHTML=`<div class="c-box"><b>${bi(B("Example","דוגמה"),"span")}</b><div class="bi">${bi(kb.ex)}</div></div><div class="c-box tip"><b>${bi(B("Memory tip","טיפ לזיכרון"),"span")}</b><div class="bi">${bi(kb.tip)}</div></div>`;
      speakThen(partsFor({en:"For example: "+kb.ex.en+" Memory tip: "+kb.tip.en,he:"לדוגמה: "+kb.ex.he+" טיפ לזיכרון: "+kb.tip.he}),next)});
  }else if(st.type==="turn"){
    const p=d.pts[st.pi],kb=KB[cur][st.pi],other=mode==="he"?B("in English","באנגלית"):mode==="en"?B("in Hebrew","בעברית"):B("in your own words","במילים שלכם");
    body.innerHTML=`<span class="label">Your turn · תורכם</span><h2>${bi(B(`Explain rule ${st.pi+1} out loud, ${other.en}.`,`הסבירו את כלל ${st.pi+1} בקול, ${other.he}.`),"span")}</h2><div class="bi c-hint">${bi(kb.tip)}</div><div class="c-count" id="c-count"></div><details class="c-peek"><summary>${bi(B("Peek at the rule","הצצה בכלל"),"span")}</summary><div class="bi">${bi(p)}</div></details>`;
    foot.innerHTML=nav("I'm done ▶ · סיימתי");wireNav();
    speakThen(partsFor({en:`Your turn. Explain this rule out loud, ${other.en}.`,he:`תורכם. הסבירו את הכלל בקול, ${other.he}.`}),()=>countdown(st.secs,document.getElementById("c-count"),next));
  }else if(st.type==="fact"){
    const Q={en:st.c.en,he:st.c.qhe},A={en:st.c.ae,he:st.c.ah};
    body.innerHTML=`<span class="label">${bi(B(`Key fact ${st.ci+1} of ${st.n}`,`עובדה ${st.ci+1} מתוך ${st.n}`),"span")}</span><div class="c-card c-fact"><div class="bi c-q">${bi(Q)}</div><div class="bi c-a">${A.en===A.he?`<div>${A.en}</div>`:bi(A)}</div></div>`;
    foot.innerHTML=nav();wireNav();
    speakThen(partsFor(Q),()=>speakThen(partsFor(A),next));
  }else if(st.type==="card"){
    const Q={en:st.c.en,he:st.c.qhe},A={en:st.c.ae,he:st.c.ah};
    body.innerHTML=`<span class="label">${bi(B("Question","שאלה"),"span")}</span><div class="c-card"><div class="bi c-q">${bi(Q)}</div><div class="bi c-a" id="c-a" hidden>${A.en===A.he?`<div>${A.en}</div>`:bi(A)}</div></div><p class="ex" id="c-say">${bi(B("Think of the answer, then tap Show answer.","חשבו על התשובה, ואז הקישו על הצג תשובה."),"span")}</p><div class="c-count" id="c-count"></div>`;
    foot.innerHTML=`<div class="c-nav">${cBtn("c-back","◀ Back · אחורה","ghost")}${cBtn("c-show","Show answer · הצג תשובה")}</div>`;wireNav();
    const reveal=()=>{cClear();const a=document.getElementById("c-a");if(!a)return;a.hidden=false;document.getElementById("c-count").textContent="";document.getElementById("c-say").innerHTML=bi(B("Did you know it?","ידעתם?"),"span");
      foot.innerHTML=`<div class="c-nav">${cBtn("c-no","✗ Not yet · עוד לא","ghost bad")}${cBtn("c-yes","✓ I knew it · ידעתי","good")}</div>`;
      document.getElementById("c-yes").onclick=()=>{tone(true);next()};
      document.getElementById("c-no").onclick=()=>{tone(false);coach.steps.splice(coach.steps.length-1,0,{type:"card",c:st.c});next()};
      speakThen(partsFor(A),()=>{})};
    document.getElementById("c-show").onclick=reveal;
    speakThen(partsFor(Q),()=>countdown(15,document.getElementById("c-count"),reveal));
  }
}
function openCoach(){coach.open=true;document.getElementById("coach").hidden=false;document.body.classList.add("coach-on");updateOpenBtn()}
function closeCoach(){coach.open=false;cClear();stopSpeak();document.getElementById("coach").hidden=true;document.body.classList.remove("coach-on");updateOpenBtn()}
function updateOpenBtn(){const b=document.getElementById("c-open");if(b)b.hidden=!(run&&!coach.open)}
function finishEarly(){clearInterval(run);run=null;left=0;updateClock();document.querySelector(".timer").classList.remove("running");document.getElementById("tstart").textContent="Done! · סיימתם!";renderBlocks();closeCoach();startDayQuiz()}
// Hooks into the timer
updateClock=(o=>function(){o();const c=document.getElementById("c-clock");if(c)c.textContent=document.getElementById("clock").textContent})(updateClock);
announce=(o=>function(en,he){if(run){beep();const n=document.getElementById("tnow");if(n)n.textContent=mode==="he"?he:mode==="en"?en:`${en} · ${he}`;return}o(en,he)})(announce);
enterPart=(o=>function(i,speak){o(i,speak);if(run){if(!coach.open){openCoach();coachLoad(i,false)}else if(coach.part!==i)coachLoad(i,false)}})(enterPart);
startDayQuiz=(o=>function(){closeCoach();o()})(startDayQuiz);
document.getElementById("tstart").addEventListener("click",()=>{
  if(run){coach.paused=false;if(!coach.open){openCoach();coachLoad(curPart<0?0:curPart,left>=3598)}else renderStep()}
  else if(coach.open){coach.paused=true;cClear();stopSpeak();renderStep()}
  updateOpenBtn()});
document.getElementById("treset").addEventListener("click",closeCoach);
document.getElementById("c-pause").onclick=()=>document.getElementById("tstart").click();
document.getElementById("c-skip").onclick=()=>{if(coach.part<SEGS.length-1)jumpTo(coach.part+1);else finishEarly()};
document.getElementById("c-close").onclick=closeCoach;
document.getElementById("c-open").onclick=()=>{openCoach();coachLoad(curPart<0?0:curPart,false)};
