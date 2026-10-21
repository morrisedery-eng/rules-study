# Build step (exec'd after menu_step.py): the app becomes separate screens
# (Home, Subject, Quiz, Practice exam, Settings). Every screen except Home has a top bar
# that stays visible while scrolling, with a Back button. The lesson overlay gets a Back button too.
def rep(old, new):
    global s
    assert old in s, old[:80]
    s = s.replace(old, new, 1)

BACK_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg>'
APPBAR = ('<div class="appbar" id="appbar" hidden><button type="button" class="ab-back" id="ab-back">' + BACK_SVG +
          '<span>Back · חזרה</span></button><span class="ab-title" id="ab-title"></span>'
          '<button type="button" class="burger" aria-label="Menu · תפריט" aria-haspopup="true" aria-expanded="false">'
          '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button></div>\n')
rep('<div class="upd-banner" id="upd-banner" hidden></div>', APPBAR + '<div class="upd-banner" id="upd-banner" hidden></div>')

# lesson overlay: Back at the top left (replaces the small "Close" button)
rep('<div class="c-head"><span class="label" id="c-part"></span>',
    '<div class="c-head"><div class="c-left"><button type="button" class="ab-back" id="c-exit">' + BACK_SVG +
    '<span>Back · חזרה</span></button><span class="label" id="c-part"></span></div>')

SCR_JS = r'''
// ----- Screens with Back -----
{const body=document.body,bar=document.getElementById("appbar"),ttl=document.getElementById("ab-title"),setSec=document.getElementById("settings");
  let stack=["home"];
  const title=sc=>sc==="subject"?bi(B(`Subject ${cur+1} of ${DAYS.length}`,`נושא ${cur+1} מתוך ${DAYS.length}`),"span")
    :sc==="quiz"?bi(B("Quiz","בוחן"),"span"):sc==="exam"?bi(B("Practice exam","מבחן תרגול"),"span"):sc==="settings"?bi(B("Settings","הגדרות"),"span"):"";
  function paint(){const sc=stack[stack.length-1];body.dataset.screen=sc;bar.hidden=sc==="home";ttl.innerHTML=title(sc);
    if(sc!=="settings"&&!setSec.hidden){setSec.hidden=true;const t=document.getElementById("tab-settings");if(t)t.setAttribute("aria-expanded","false")}
    if(sc==="subject"&&!document.getElementById("part-0"))renderDay(); // the page still held the practice exam
    window.scrollTo({top:0})}
  function show(sc){if(sc==="home")stack=["home"];else if(stack[stack.length-1]!==sc){if(sc!=="quiz")stack=stack.filter(x=>x!==sc&&x!=="quiz");stack.push(sc)}paint()}
  function back(){if(stack.length>1)stack.pop();if(stack[stack.length-1]==="quiz")stack.pop();paint()}
  window.showScreen=show;window.screenBack=back;
  document.getElementById("ab-back").onclick=back;
  document.getElementById("c-exit").onclick=()=>closeCoach();
  // what opens which screen
  const _exam=startExam;startExam=function(){_exam.apply(this,arguments);show("exam")};
  const _quiz=startDayQuiz;startDayQuiz=function(){_quiz.apply(this,arguments);if(document.getElementById("part-3"))show("quiz")};
  document.addEventListener("click",e=>{const t=e.target.closest("button");if(!t)return;
    if(t.classList.contains("daytab"))show("subject");
    else if(t.id==="hn-go"&&document.getElementById("part-0"))show("subject");
    else if(t.id==="tab-subjects"||t.id==="qnextday")show("home");
    else if(t.id==="exam-back")back();
    else if(/^Open Subject|^Next subject/.test(t.textContent)){if(stack[stack.length-1]==="quiz")stack.pop();show("subject")}});
  new MutationObserver(()=>{if(!setSec.hidden)show("settings");else if(stack[stack.length-1]==="settings")back()}).observe(setSec,{attributes:true,attributeFilter:["hidden"]});
  // the Android back button: close what is open first, then go back one screen
  window.onNativeBack=()=>{const pop=document.getElementById("menu-pop");
    if(pop&&!pop.hidden){pop.hidden=true;return true}
    if(!hEl.hidden){closeHelper();return true}
    if(typeof coach!=="undefined"&&coach.open){closeCoach();return true}
    if(stack.length>1){back();return true}return false};
  body.dataset.screen="home";}
'''
rep('// ----- Bottom navigation -----', SCR_JS + '// ----- Bottom navigation -----')

SCR_CSS = r'''
/* ===== screens ===== */
body[data-screen="home"] .timer,body[data-screen="home"] #sheet{display:none!important}
body:not([data-screen="home"]) .hero,body:not([data-screen="home"]) .subjects,body:not([data-screen="home"]) #upd-banner{display:none!important}
body[data-screen="exam"] .timer,body[data-screen="settings"] .timer,body[data-screen="settings"] #sheet,body[data-screen="quiz"] .timer{display:none!important}
body[data-screen="quiz"] #sheet>:not(#part-3):not(#donebox){display:none!important}
/* top bar with Back: stays at the top while scrolling */
.appbar{position:sticky;top:0;z-index:40;display:grid;grid-template-columns:auto 1fr auto;align-items:center;gap:12px;
  margin:0 calc(50% - 50vw) 4px;padding:calc(10px + env(safe-area-inset-top,0px)) max(16px,calc(50vw - 50%)) 10px;
  background:var(--bg);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border-bottom:1px solid var(--line)}
.ab-back{display:inline-flex;align-items:center;gap:6px;min-height:44px;padding:0 16px 0 10px;border-radius:14px;border:1px solid var(--line);
  background:var(--sheet);color:var(--accent);font:inherit;font-size:.95rem;font-weight:600;cursor:pointer;white-space:nowrap}
.ab-back svg{width:20px;height:20px;fill:none;stroke:currentColor;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}
.ab-back:hover{background:var(--accent-soft)}
.ab-back:focus-visible{outline:3px solid var(--accent);outline-offset:2px}
.ab-title{font-weight:600;font-size:1rem;color:var(--ink);min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.ab-title>span{display:inline}
.ab-title>span.he{margin-left:.5em;color:var(--muted);font-weight:500}
body.m-en .ab-title .he,body.m-he .ab-title .en{display:none}
body.m-he .ab-title>span.he{margin:0;color:var(--ink)}
/* lesson overlay header: Back on the left */
#coach .c-head{flex-wrap:wrap;row-gap:8px}
#coach .c-left{display:contents}
#coach .c-left .ab-back{order:0}
#coach .c-right{order:1;margin-left:auto}
#coach .c-left .label{order:2;flex-basis:100%}
#c-close{display:none!important}
'''
rep('</style>', SCR_CSS + '</style>')
