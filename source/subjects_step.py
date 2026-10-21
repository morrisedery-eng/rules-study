# Build step (exec'd from build_offline.py after guided_step.py, with `s` in scope):
# study by subject, at your own pace. Each subject = 60-minute lesson (50 lesson + 10 flashcards), then a quiz on that subject only.
import re

def rep(old, new):
    global s
    assert old in s, old[:80]
    s = s.replace(old, new, 1)

rep('const SEGS=[{m:10,en:"Review",he:"חזרה"},{m:40,en:"Learn",he:"לימוד"},{m:10,en:"Flashcards",he:"כרטיסיות"}];',
    'const SEGS=[{m:50,en:"Lesson",he:"שיעור"},{m:10,en:"Key facts",he:"עובדות חשובות"}];')
rep('.blocks{display:grid;grid-template-columns:1fr 3fr 1fr;gap:4px}', '.blocks{display:grid;grid-template-columns:3fr 1.4fr;gap:4px}')
rep('@media (max-width:560px){.blocks{grid-template-columns:1fr 1.5fr 1fr}}', '@media (max-width:560px){.blocks{grid-template-columns:2fr 1fr}}')

# header text
rep('One hour a day: a short review (only as long as it takes), new material, and 10 min of flashcards at the end. Then an end-of-day quiz with your grade (not counted in the hour).',
    'Pick any subject, at your own pace. Each one is a 60-minute lesson, then a quiz on that subject.')
rep('שעה אחת ביום: חזרה קצרה (רק כמה שצריך), חומר חדש, ו-10 דק׳ כרטיסיות בסוף. אחר כך בוחן סוף יום עם ציון (לא נכלל בשעה).',
    'בחרו כל נושא, בקצב שלכם. כל נושא הוא שיעור של 60 דקות, ואחר כך בוחן על הנושא הזה.')
rep('<nav class="days" id="days" aria-label="Days"></nav>',
    '<span class="label subj-label">Pick a subject · בחרו נושא</span>\n    <nav class="days" id="days" aria-label="Subjects"></nav>')

# subject list
i = s.index('function renderDays(){'); j = s.index('function renderDay(){')
s = s[:i] + '''function renderDays(){
  const nav=document.getElementById("days");
  nav.innerHTML=DAYS.map((d,i)=>`<button class="daytab subj ${done.includes(i)?"done":""}" aria-current="${i===cur}" data-i="${i}"><span class="n">${done.includes(i)?"✓":i+1}</span><span class="t"><span class="en" lang="en">${d.t.en}</span><span class="he" lang="he" dir="rtl">${d.t.he}</span></span></button>`).join("");
  nav.querySelectorAll(".daytab").forEach(b=>b.onclick=()=>{const i=+b.dataset.i;if(i!==cur){if(run||left<3600)document.getElementById("treset").click();cur=i;renderDays();renderDay()}
    document.getElementById("sheet").scrollIntoView({behavior:"smooth",block:"start"})});
  document.getElementById("prog").textContent=`${done.length}/${DAYS.length} subjects done · ${done.length}/${DAYS.length} נושאים הושלמו`;
}

''' + s[j:]

# subject page: plan, lesson, flashcards, quiz
i = s.index('function renderDay(){'); j = s.index('  const sheet=document.getElementById("sheet");sheet.innerHTML=h;')
s = s[:i] + '''function renderDay(){
  const d=DAYS[cur];
  let h=`<div class="sec"><span class="label">Subject ${cur+1} of ${DAYS.length} · נושא ${cur+1} מתוך ${DAYS.length}</span><div class="bi">${bi(d.t,"h2")}</div></div>`;
  h+=`<div class="sec plan"><span class="label">How it works · איך זה עובד</span><div class="bi">${bi({en:`Press Start. For 60 minutes I'll teach you <b>${d.t.en}</b>: first I read each rule with an example (50 min), then we go over the key facts (10 min). When the hour is over, a quiz on this subject starts by itself.`,he:`לחצו התחל. במשך 60 דקות אלמד אתכם את <b>${d.t.he}</b>: קודם אקריא כל כלל עם דוגמה (50 דקות), ואחר כך נעבור על העובדות החשובות (10 דקות). כשהשעה נגמרת, בוחן על הנושא הזה מתחיל לבד.`},"p")}</div>
  <div class="tools"><button type="button" class="btn" id="startday">▶ Start the 60 minutes · התחל 60 דקות</button></div></div>`;
  // Lesson
  h+=`<div class="sec part" id="part-0"><div class="sec-head"><h3>1 · Lesson · שיעור</h3><span class="mins">50 min</span></div>`;
  if(d.table){h+=`<div class="tbl"><table><thead><tr><th>Age group</th><th style="text-align:right" dir="rtl">קבוצת גיל</th><th>Staff : children</th></tr></thead><tbody>${RATIOS.map(r=>`<tr><td>${r[0]}</td><td dir="rtl" style="text-align:right">${r[1]}</td><td><b>${r[2]}</b></td></tr>`).join("")}</tbody></table></div>`;}
  h+=`<div class="tools"><button class="mini" data-readall>${ICON.spk} Listen to all · הקשב להכול</button></div>`;
  h+=`<ul class="points">${d.pts.map((p,pi)=>`<li><div class="bi">${bi(p)}</div><div class="tools"><button class="mini" data-read="${pi}">${ICON.spk} Listen · הקשב</button><button class="mini" data-explain="${pi}">${ICON.ask} Explain simply · הסבר בפשטות</button><button class="mini" data-example="${pi}">${ICON.ask} Example · דוגמה</button></div></li>`).join("")}</ul></div>`;
  // Key facts: each question shown with its answer
  h+=`<div class="sec part" id="part-1"><div class="sec-head"><h3>2 · Key facts · עובדות חשובות</h3><span class="mins">10 min</span></div>
  <ul class="points facts">${d.cards.map(c=>`<li><div class="bi">${bi({en:c.en,he:c.qhe},"b")}</div><div class="bi">${c.ae===c.ah?`<span>${c.ae}</span>`:bi({en:c.ae,he:c.ah},"span")}</div></li>`).join("")}</ul></div>`;
  // Quiz on this subject (not part of the 60 minutes)
  h+=`<div class="sec part" id="part-3">${quizIntroHTML()}</div>`;
  h+=`<div class="foot" id="donebox"></div>`;
''' + s[j:]

# styles for the subject list
rep('@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}',
'''.subj-label{display:block;margin:12px 0 6px}
.days{grid-template-columns:repeat(2,minmax(0,1fr))!important}
@media (max-width:640px){.days{grid-template-columns:1fr!important}}
.daytab.subj{display:flex;align-items:center;gap:10px;text-align:left;padding:10px 12px;min-height:52px}
.daytab.subj .n{flex:none;width:30px;text-align:center}
.daytab.subj .t{display:flex;flex-direction:column;gap:2px;min-width:0;font-size:.9rem;line-height:1.3}
.daytab.subj .t .he{text-align:right}
.daytab.subj.done .n{color:var(--good)}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}''')

# wording elsewhere: "Day N" → "Subject N"
for a, b in [('Day ${cur+1}', 'Subject ${cur+1}'), ('Day ${di+1}', 'Subject ${di+1}'), ('Day ${p.di+1}', 'Subject ${p.di+1}'),
             ('Day ${+di+1}', 'Subject ${+di+1}'), ('יום ${cur+1}', 'נושא ${cur+1}'), ('יום ${di+1}', 'נושא ${di+1}'),
             ('יום ${p.di+1}', 'נושא ${p.di+1}'), ('Review these days · ימים לחזרה', 'Review these subjects · נושאים לחזרה'),
             ('הימים בסדר אקראי. הציון והימים לחזרה יופיעו בסוף.', 'הנושאים בסדר אקראי. הציון והנושאים לחזרה יופיעו בסוף.'),
             ('חזרו על הימים שלמטה ונסו שוב.', 'חזרו על הנושאים שלמטה ונסו שוב.'),
             ('Opening Day', 'Opening Subject'), ('Reading Day', 'Reading Subject'), ('Key facts for Day', 'Key facts for Subject'),
             ('From Day', 'From Subject')]:
    s = s.replace(a, b)
s = s.replace('questions from all ${DAYS.length} days, in random order. Your score and the days to review appear at the end.',
              'questions from all ${DAYS.length} subjects, in random order. Your score and the subjects to review appear at the end.')
s = s.replace('below 70%, the passing level. Review the days below', 'below 70%, the passing level. Review the subjects below')

# "Mark subject complete": one clear action, no toggle, no page reload; then offer the next subject
rep('''  document.getElementById("markdone").onclick=()=>{
    if(done.includes(cur))done=done.filter(x=>x!==cur);else done.push(cur);
    store.set("rr-done",done);renderDays();renderDay();
  };''', '''  renderDoneBox();''')
rep('function shuffle(a,seed){', '''function renderDoneBox(){const box=document.getElementById("donebox");if(!box)return;
  const isDone=done.includes(cur),nxt=DAYS.findIndex((_,i)=>i>cur&&!done.includes(i)),nx=nxt>=0?nxt:DAYS.findIndex((_,i)=>!done.includes(i));
  const goNext=nx>=0&&nx!==cur?`<button class="btn" id="nextsubj">Next subject: ${DAYS[nx].t.en} · הנושא הבא: ${DAYS[nx].t.he}</button>`:"";
  box.innerHTML=isDone
    ?`<div class="donemsg"><b>${bi(B("✓ This subject is complete","✓ הנושא הזה הושלם"),"span")}</b><button class="mini" id="undodone">Reset this subject · איפוס הנושא</button></div>${goNext}`
    :`<button class="btn" id="markdone">Mark subject complete · סמן נושא כהושלם</button>`;
  const m=document.getElementById("markdone");if(m)m.onclick=()=>{if(!done.includes(cur))done.push(cur);store.set("rr-done",done);renderDays();renderDoneBox()};
  const u=document.getElementById("undodone");if(u)u.onclick=()=>{resetSubject(cur);renderDays();renderDay()};
  const g=document.getElementById("nextsubj");if(g)g.onclick=()=>{if(run||left<3600)document.getElementById("treset").click();cur=nx;renderDays();renderDay();document.getElementById("sheet").scrollIntoView({behavior:"smooth",block:"start"})};
}
function shuffle(a,seed){''')

# Reset progress (asks once, inline: no pop-up)
rep('function renderDoneBox(){', '''function resetSubject(i){done=done.filter(x=>x!==i);store.set("rr-done",done);store.set("rr-q"+i,null)}
function wireReset(){const w=document.getElementById("resetwrap");if(!w)return;
  const B2=(id,label,cls)=>`<button type="button" class="reset ${cls||""}" id="${id}">${label}</button>`;
  const plainBtn=()=>{w.className="";if(!done.length){w.innerHTML="";return} // nothing done yet: no reset button
    w.innerHTML=B2("resetprog","Reset · איפוס");document.getElementById("resetprog").onclick=ask};
  window.refreshReset=()=>{if(!w.classList.contains("open"))plainBtn()};
  const ask=()=>{w.className="open";w.innerHTML=`<span class="rq">${bi(B("What do you want to reset?","מה לאפס?"),"span")}</span>`+B2("r-all","All subjects · כל הנושאים")+B2("r-one","Select subjects · בחירת נושאים")+B2("r-no","Cancel · ביטול");
    document.getElementById("r-all").onclick=()=>{w.innerHTML=`<span class="rq">${bi(B("Reset all 15 subjects to zero?","לאפס את כל 15 הנושאים?"),"span")}</span>`+B2("r-yes","Yes, reset all · כן, לאפס הכול","yes")+B2("r-no","Cancel · ביטול");
      document.getElementById("r-yes").onclick=()=>{DAYS.forEach((_,i)=>resetSubject(i));renderDays();renderDay();plainBtn()};document.getElementById("r-no").onclick=plainBtn};
    document.getElementById("r-one").onclick=()=>{const list=done.slice().sort((a,b)=>a-b),sel=new Set();
      const name=i=>mode==="he"?DAYS[i].t.he:mode==="en"?DAYS[i].t.en:`${DAYS[i].t.en} · ${DAYS[i].t.he}`;
      w.innerHTML=`<span class="rq">${bi(B("Select the subjects to reset, then tap Confirm.","בחרו את הנושאים לאיפוס, ואז הקישו על אישור."),"span")}</span>`
        +`<div class="rpick">${list.map(i=>`<button type="button" class="rsub" role="checkbox" aria-checked="false" data-i="${i}"><span class="box"></span><span class="nm">${i+1}. ${name(i)}</span></button>`).join("")}</div>`
        +B2("r-ok","Confirm reset · אישור איפוס","yes")+B2("r-no","Cancel · ביטול");
      const ok=document.getElementById("r-ok");ok.disabled=true;
      w.querySelectorAll(".rsub").forEach(b=>b.onclick=()=>{const i=+b.dataset.i;sel.has(i)?sel.delete(i):sel.add(i);b.setAttribute("aria-checked",sel.has(i));ok.disabled=!sel.size});
      ok.onclick=()=>{if(!sel.size)return;sel.forEach(resetSubject);renderDays();if(sel.has(cur))renderDay();plainBtn()};
      document.getElementById("r-no").onclick=plainBtn};
    document.getElementById("r-no").onclick=plainBtn};
  plainBtn()}
function renderDoneBox(){''')
rep('setMode(mode);renderDays();renderDay();renderBlocks();', 'setMode(mode);renderDays();renderDay();renderBlocks();wireReset();')
