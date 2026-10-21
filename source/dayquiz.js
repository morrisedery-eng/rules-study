// ----- End-of-day quiz: after the 60 minutes, one question at a time, right/wrong feedback, grade -----
let dq=null,qCtx=null;
const soundOn=()=>store.get("rr-qsound",true);
function tone(ok){if(!soundOn())return;try{qCtx=qCtx||new (window.AudioContext||window.webkitAudioContext)();const t=qCtx.currentTime;
  (ok?[[660,0],[990,.12]]:[[220,0],[180,.18]]).forEach(([f,dt])=>{const o=qCtx.createOscillator(),g=qCtx.createGain();o.type=ok?"sine":"square";o.frequency.value=f;
    g.gain.setValueAtTime(.0001,t+dt);g.gain.exponentialRampToValueAtTime(ok?.25:.12,t+dt+.02);g.gain.exponentialRampToValueAtTime(.0001,t+dt+.3);o.connect(g).connect(qCtx.destination);o.start(t+dt);o.stop(t+dt+.32)})}catch(e){}}
let sayT=null;
function hush(){clearTimeout(sayT);sayT=null;stopSpeak()} // stop any feedback still being read
function say(en,he){if(!soundOn()||(!window.AndroidBridge&&!window.speechSynthesis))return;const parts=mode==="en"?[{text:en,lang:"en"}]:mode==="he"?[{text:he,lang:"he"}]:[{text:en,lang:"en"},{text:he,lang:"he"}];clearTimeout(sayT);sayT=setTimeout(()=>{sayT=null;speakParts(parts,null)},350)}
function sayFeedback(ok,q){tone(ok);say(ok?"Right!":`Wrong. The answer is: ${plain(q.o[q.a].en)}.`,ok?"נכון!":`לא נכון. התשובה היא: ${plain(q.o[q.a].he)}.`)}
function quizHead(){return `<div class="sec-head"><h3>3 · Quiz · בוחן</h3><span class="mins">not timed · לא בזמן</span>
  <button type="button" class="mini" id="qsound">${soundOn()?"🔊 Sound on · קול פועל":"🔇 Sound off · קול כבוי"}</button></div>`}
function wireSound(){const b=document.getElementById("qsound");if(b)b.onclick=()=>{store.set("rr-qsound",!soundOn());b.textContent=soundOn()?"🔊 Sound on · קול פועל":"🔇 Sound off · קול כבוי";if(!soundOn())stopSpeak()}}
function quizIntroHTML(){const n=DAYS[cur].quiz.length,best=store.get("rr-q"+cur,null);
  return quizHead()+`<div class="bi">${bi({en:`After your 60 minutes, the quiz starts by itself: ${n} questions about what you learned. First the key facts, with the same questions, then the rules from the lesson. One question at a time. You'll hear if you're right or wrong, and get a grade at the end. 70% passes.`,he:`אחרי 60 הדקות הבוחן מתחיל לבד: ${n} שאלות על מה שלמדתם. קודם העובדות החשובות, עם אותן שאלות, ואחר כך הכללים מהשיעור. שאלה אחת בכל פעם. תשמעו אם עניתם נכון או לא, ותקבלו ציון בסוף. 70% עובר.`},"p")}</div>`
  +(best!==null?`<p class="ex score">Best score · הציון הטוב ביותר: ${best}%</p>`:"")
  +`<div class="tools"><button type="button" class="btn" id="qstart">Start the quiz now · התחל בוחן עכשיו</button></div>`}
function startDayQuiz(){
  const sec=document.getElementById("part-3");if(!sec)return;stopSpeak();
  const items=DAYS[cur].quiz.map((q,qi)=>({di:cur,qi}));
  const seed=Date.now()%104729,facts=items.filter(it=>DAYS[it.di].quiz[it.qi].fact),rest=items.filter(it=>!DAYS[it.di].quiz[it.qi].fact);
  dq={items:shuffle(facts,seed).concat(shuffle(rest,seed+7)),i:0,right:0,wrong:[]}; // key facts first, then the lesson rules
  showQ();sec.scrollIntoView({behavior:"smooth",block:"start"});
}
function showQ(){hush();
  const sec=document.getElementById("part-3"),it=dq.items[dq.i],q=DAYS[it.di].quiz[it.qi],N=dq.items.length,order=shuffle([0,1,2,3],(Date.now()%977)+dq.i);
  sec.innerHTML=quizHead()+`<p class="label">Question ${dq.i+1} of ${N} · שאלה ${dq.i+1} מתוך ${N}</p>
    <div class="qbar"><div style="width:${dq.i/N*100}%"></div></div>
    <div class="q"><div class="bi">${bi(q.q)}</div><div class="opts">${order.map(oi=>`<button class="opt" data-o="${oi}">${plain(q.o[oi].en)===plain(q.o[oi].he)?`<span>${q.o[oi].en}</span>`:`<div class="bi">${bi(q.o[oi],"span")}</div>`}</button>`).join("")}</div>
    <div class="verdict" hidden></div><div class="ex" hidden><div class="bi">${bi(q.x)}</div></div></div>
    <div class="tools"><button type="button" class="btn" id="qnext" hidden>${dq.i+1<N?"Next question · שאלה הבאה":"See my grade · הצג ציון"}</button></div>
    <p class="ex score">✓ ${dq.right} · ✗ ${dq.wrong.length}</p>`;
  wireSound();
  const qel=sec.querySelector(".q");
  qel.querySelectorAll(".opt").forEach(b=>b.onclick=()=>{
    if(qel.dataset.done)return;qel.dataset.done=1;
    const ok=+b.dataset.o===q.a;if(ok)dq.right++;else dq.wrong.push({it,picked:+b.dataset.o});
    b.classList.add(ok?"right":"wrong");qel.querySelector(`.opt[data-o="${q.a}"]`).classList.add("right");
    const v=qel.querySelector(".verdict");v.hidden=false;v.className="verdict "+(ok?"good":"bad");
    v.innerHTML=ok?`✓ Right! · נכון!`:`✗ Wrong · לא נכון`;
    qel.querySelector(".ex").hidden=false;sayFeedback(ok,q);
    sec.querySelector(".score").textContent=`✓ ${dq.right} · ✗ ${dq.wrong.length}`;
    const nx=document.getElementById("qnext");nx.hidden=false;nx.onclick=()=>{dq.i++;dq.i<N?showQ():showGrade()};
    nx.scrollIntoView({behavior:"smooth",block:"nearest"})});
}
function showGrade(){hush();
  const sec=document.getElementById("part-3"),N=dq.items.length,pct=Math.round(dq.right/N*100),pass=pct>=70;
  store.set("rr-q"+cur,Math.max(pct,store.get("rr-q"+cur,0)));
  if(pass&&!done.includes(cur)){done.push(cur);store.set("rr-done",done);renderDays();renderDoneBox()}
  const mistakes=dq.wrong.map(({it,picked})=>{const q=DAYS[it.di].quiz[it.qi];return `<li><div class="bi">${bi(q.q,"b")}</div><div class="bi">${bi({en:`Your answer: ${plain(q.o[picked].en)}. Correct: <b>${plain(q.o[q.a].en)}</b>. ${q.x.en}`,he:`ענית: ${plain(q.o[picked].he)}. נכון: <b>${plain(q.o[q.a].he)}</b>. ${q.x.he}`})}</div></li>`}).join("");
  sec.innerHTML=quizHead()+`<div class="grade ${pass?"good":"bad"}"><div class="big">${pct}%</div><div>${dq.right} / ${N}</div></div>
    <div class="bi">${bi(pass?{en:`You passed! This subject is marked complete.`,he:`עברתם! הנושא הזה סומן כהושלם.`}:{en:"Below 70%. Review the questions you missed, then retake the quiz.",he:"מתחת ל-70%. עברו על השאלות שטעיתם בהן ונסו שוב."},"p")}</div>
    ${mistakes?`<span class="label">Review your mistakes · טעויות לחזרה</span><ul class="points">${mistakes}</ul>`:`<p class="ex">${bi({en:"No mistakes. Perfect!",he:"בלי טעויות. מושלם!"},"span")}</p>`}
    <div class="tools"><button type="button" class="btn ghost" id="qretake">Retake quiz · בוחן חוזר</button><button type="button" class="btn" id="qnextday">Pick another subject · בחרו נושא אחר</button></div>`;
  wireSound();tone(pass);
  say(pass?`You scored ${pct} percent. You passed! Great job.`:`You scored ${pct} percent. Let's review and try again.`,pass?`קיבלתם ${pct} אחוז. עברתם! כל הכבוד.`:`קיבלתם ${pct} אחוז. בואו נחזור על החומר וננסה שוב.`);
  document.getElementById("qretake").onclick=startDayQuiz;
  const nd=document.getElementById("qnextday");if(nd)nd.onclick=()=>{document.getElementById("treset").click();window.scrollTo({top:0,behavior:"smooth"})};
  sec.scrollIntoView({behavior:"smooth",block:"start"});
}
