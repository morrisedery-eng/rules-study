// Timer: a guided 60-minute session. Start → it moves you through Review, Learn, Flashcards and Quiz,
// scrolling to each part and announcing it. Tap a part to jump there; "Next part" skips ahead.
let left=3600,run=null,curPart=-1,audioCtx=null;
const partStart=i=>SEGS.slice(0,i).reduce((a,s)=>a+s.m*60,0);
function partAt(used){let acc=0;for(let i=0;i<SEGS.length;i++){acc+=SEGS[i].m*60;if(used<acc)return i}return SEGS.length-1}
function updateClock(){const m=String(Math.floor(left/60)).padStart(2,"0"),s=String(left%60).padStart(2,"0");document.getElementById("clock").textContent=`${m}:${s}`}
function renderBlocks(){
  const el=document.getElementById("blocks"),used=3600-left,started=left<3600||run;
  el.innerHTML=SEGS.map((s,i)=>{const st=partStart(i),len=s.m*60,on=started&&left>0&&i===partAt(used),p=Math.max(0,Math.min(1,(used-st)/len));
    return `<button type="button" class="blk ${on?"on":""}" data-part="${i}" aria-label="Go to ${s.en}"><div class="fill" style="width:${p*100}%"></div><span class="full">${i+1} · ${s.m}′ ${s.en} · ${s.he}</span><span class="short">${i+1} · ${mode==="he"?s.he:s.en}</span></button>`}).join("");
  el.querySelectorAll("[data-part]").forEach(b=>b.onclick=()=>jumpTo(+b.dataset.part));
  document.getElementById("tnext").hidden=!started||left===0;
}
function scrollToPart(i){
  const el=document.getElementById("part-"+i);if(!el)return;
  const bar=document.querySelector(".timer"),offset=(bar&&bar.classList.contains("running")?bar.offsetHeight:0)+10;
  window.scrollTo({top:el.getBoundingClientRect().top+window.scrollY-offset,behavior:"smooth"});
  el.classList.remove("flash");void el.offsetWidth;el.classList.add("flash");
}
function beep(){try{audioCtx=audioCtx||new (window.AudioContext||window.webkitAudioContext)();const o=audioCtx.createOscillator(),g=audioCtx.createGain();
  o.frequency.value=880;g.gain.setValueAtTime(.0001,audioCtx.currentTime);g.gain.exponentialRampToValueAtTime(.25,audioCtx.currentTime+.02);g.gain.exponentialRampToValueAtTime(.0001,audioCtx.currentTime+.5);
  o.connect(g).connect(audioCtx.destination);o.start();o.stop(audioCtx.currentTime+.55)}catch(e){}}
function announce(en,he){beep();const parts=mode==="en"?[{text:en,lang:"en"}]:mode==="he"?[{text:he,lang:"he"}]:[{text:en,lang:"en"},{text:he,lang:"he"}];
  if(window.AndroidBridge||window.speechSynthesis)setTimeout(()=>speakParts(parts,null),600);
  const n=document.getElementById("tnow");n.textContent=mode==="he"?he:mode==="en"?en:`${en} · ${he}`}
function enterPart(i,speak){curPart=i;scrollToPart(i);const s=SEGS[i];
  if(speak)announce(`${s.en}, ${s.m} minutes.`,`${s.he}, ${s.m} דקות.`);
  else{const n=document.getElementById("tnow");n.textContent=`${i+1} · ${s.en} · ${s.he}`}}
function jumpTo(i){left=3600-partStart(i);updateClock();renderBlocks();enterPart(i,!!run)}
function tick(){
  left=Math.max(0,left-1);updateClock();renderBlocks();
  const p=partAt(3600-left);if(left>0&&p!==curPart)enterPart(p,true);
  if(left===0){clearInterval(run);run=null;document.querySelector(".timer").classList.remove("running");
    document.getElementById("tstart").textContent="Done! · סיימתם!";renderBlocks();
    announce("The hour is over. Great job! Now, the end-of-day quiz.","השעה הסתיימה. כל הכבוד! עכשיו, בוחן סוף היום.");
    setTimeout(startDayQuiz,3500)}
}
document.getElementById("tstart").onclick=e=>{
  if(left===0)return;
  const bar=document.querySelector(".timer");
  if(run){clearInterval(run);run=null;e.target.textContent="Resume · המשך";bar.classList.remove("running");renderBlocks();return}
  run=setInterval(tick,1000);e.target.textContent="Pause · השהה";bar.classList.add("running");renderBlocks();
  if(left===3600){const d=DAYS[cur];curPart=0;scrollToPart(0);
    announce(`Today's subject: ${plain(d.t.en)}. We'll study it for 60 minutes, then you'll take a quiz on it.`,`הנושא של היום: ${plain(d.t.he)}. נלמד אותו 60 דקות, ואחר כך בוחן עליו.`)}
  else enterPart(partAt(3600-left),true);
  const sd=document.getElementById("startday");if(sd)sd.textContent="⏱ Studying… · בלימוד…";
};
document.getElementById("tnext").onclick=()=>{if(curPart<SEGS.length-1)jumpTo(curPart+1)};
document.getElementById("treset").onclick=()=>{clearInterval(run);run=null;left=3600;curPart=-1;updateClock();
  document.getElementById("tstart").textContent="Start · התחל";document.querySelector(".timer").classList.remove("running");
  document.getElementById("tnow").textContent="";renderBlocks()};
