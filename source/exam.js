// ----- Practice exam: 30 random questions from all days -----
function startExam(){
  stopSpeak();
  const pool=[];DAYS.forEach((d,di)=>d.quiz.forEach((q,qi)=>pool.push({di,qi})));
  const picks=shuffle(pool.slice(),Date.now()%99991).slice(0,30),N=picks.length;
  document.querySelectorAll(".daytab").forEach(b=>b.setAttribute("aria-current","false"));
  const sheet=document.getElementById("sheet");
  let h=`<div class="sec"><span class="label">Practice exam · מבחן תרגול</span><div class="bi">${bi({en:`${N} questions from all ${DAYS.length} days, in random order. Your score and the days to review appear at the end.`,he:`${N} שאלות מכל ${DAYS.length} הימים בסדר אקראי. הציון והימים לחזרה יופיעו בסוף.`},"p")}</div></div>`;
  picks.forEach((p,i)=>{const q=DAYS[p.di].quiz[p.qi],order=shuffle([0,1,2,3],i*31+7+p.qi);
    h+=`<div class="q" data-i="${i}"><span class="label">${i+1}/${N} · Day ${p.di+1} · יום ${p.di+1}</span><div class="bi">${bi(q.q)}</div><div class="opts">${order.map(oi=>`<button class="opt" data-o="${oi}"><div class="bi">${bi(q.o[oi],"span")}</div></button>`).join("")}</div><div class="ex" hidden><div class="bi">${bi(q.x)}</div></div></div>`});
  h+=`<div class="sec" id="exam-result"><p class="ex score" id="exam-progress">0/${N}</p></div><div class="foot"><button class="btn" id="exam-new">New exam · מבחן חדש</button><button class="btn ghost" id="exam-back">Back to lessons · חזרה לשיעורים</button></div>`;
  sheet.innerHTML=h;sheet.scrollIntoView({behavior:"smooth",block:"start"});
  let right=0,answered=0;const missed={};
  sheet.querySelectorAll(".q").forEach(qel=>{const p=picks[+qel.dataset.i],q=DAYS[p.di].quiz[p.qi];
    qel.querySelectorAll(".opt").forEach(b=>b.onclick=()=>{
      if(qel.dataset.done)return;qel.dataset.done=1;answered++;
      const ok=+b.dataset.o===q.a;if(ok)right++;else missed[p.di]=(missed[p.di]||0)+1;
      b.classList.add(ok?"right":"wrong");qel.querySelector(`.opt[data-o="${q.a}"]`).classList.add("right");qel.querySelector(".ex").hidden=false;sayFeedback(ok,q);
      document.getElementById("exam-progress").textContent=`${answered}/${N} · ${right} ✓`;
      if(answered===N)result()})});
  function result(){
    const pct=Math.round(right/N*100),best=Math.max(pct,store.get("rr-best",0));store.set("rr-best",best);
    const weak=Object.entries(missed).sort((a,b)=>b[1]-a[1]);
    const el=document.getElementById("exam-result");
    el.innerHTML=`<h2 class="score">${right}/${N} · ${pct}%</h2><div class="bi">${bi(pct>=70
      ?{en:`That's 70% or more, the passing level for DCF competency exams. Best so far: ${best}%.`,he:`זה 70% ומעלה, רמת המעבר במבחני הכשירות של DCF. השיא שלכם: ${best}%.`}
      :{en:`Below 70%, the passing level. Review the days below, then try again. Best so far: ${best}%.`,he:`מתחת ל-70%, רמת המעבר. חזרו על הימים שלמטה ונסו שוב. השיא שלכם: ${best}%.`},"p")}</div>`
      +(weak.length?`<span class="label">Review these days · ימים לחזרה</span><div class="tools">${weak.map(([di,n])=>`<button class="mini" data-day="${di}">Day ${+di+1}: ${DAYS[di].t.en} · ${n} ✗</button>`).join("")}</div>`:"");
    el.querySelectorAll("[data-day]").forEach(b=>b.onclick=()=>{cur=+b.dataset.day;renderDays();renderDay();document.getElementById("sheet").scrollIntoView({behavior:"smooth",block:"start"})});
    if(hAuto&&hAuto.checked)speakParts([{text:`${right} out of ${N}. ${pct} percent.`,lang:"en"}],null);
  }
  document.getElementById("exam-new").onclick=startExam;
  document.getElementById("exam-back").onclick=()=>{renderDays();renderDay();document.getElementById("sheet").scrollIntoView({behavior:"smooth",block:"start"})};
}
document.getElementById("exam-btn").onclick=startExam;
