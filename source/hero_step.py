# Build step (exec'd after nav_step.py): a designed home banner — brand row, title, progress ring, and an "Up next" card.
def rep(old, new):
    global s
    assert old in s, old[:80]
    s = s.replace(old, new, 1)

i = s.index('<header>'); j = s.index('</header>', i) + len('</header>')
LOGO = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.5 4.5 5.5v6c0 4.6 3.1 8.4 7.5 10 4.4-1.6 7.5-5.4 7.5-10v-6z"/>'
        '<path d="m8.5 12 2.4 2.4 4.6-4.8"/></svg>')
BLOCKS = ('<svg class="hero-art" viewBox="0 0 300 300" aria-hidden="true">'
          '<circle cx="210" cy="70" r="46"/><rect x="88" y="34" width="70" height="70" rx="14" transform="rotate(14 123 69)"/>'
          '<path d="M232 150 282 236H182z"/><path d="M96 190a52 52 0 0 1 104 0z"/><rect x="40" y="128" width="40" height="40" rx="10" transform="rotate(-12 60 148)"/>'
          '</svg>')
HEADER = f'''<header class="hero">
    {BLOCKS}
    <div class="hero-top">
      <div class="brand"><span class="logo">{LOGO}</span><span class="brand-t"><b><span class="en">Rules Study</span><span class="he" lang="he">לימוד חוקים ותקנות</span></b><small>Florida DCF · RNRF</small></span></div>
      <span id="resetwrap"><button type="button" class="reset" id="resetprog">Reset · איפוס</button></span>
    </div>
    <div class="hero-main">
      <div class="hero-text">
        <h1 class="en">Child Care Facility Rules &amp; Regulations</h1>
        <h1 class="he" lang="he">חוקים ותקנות למתקני טיפול בילדים</h1>
        <p class="en sub">Pick any subject, at your own pace. Each one is a 60-minute guided lesson, then a quiz.</p>
        <p class="he sub" lang="he">בחרו כל נושא, בקצב שלכם. כל נושא הוא שיעור מודרך של 60 דקות, ואחר כך בוחן.</p>
      </div>
    </div>
    <div class="hero-row">
      <div class="hero-prog">
        <div class="ring"><svg viewBox="0 0 36 36"><circle class="ring-bg" cx="18" cy="18" r="15.9"/><circle class="ring-fg" id="ring" cx="18" cy="18" r="15.9" pathLength="100"/></svg><div class="ring-n"><b id="ring-n">0</b><span>/15</span></div></div>
        <div class="ring-l"><b><span class="en">Subjects done</span><span class="he" lang="he">נושאים שהושלמו</span></b><span id="ring-pct">0%</span></div>
      </div>
      <div class="hero-next" id="hero-next"></div>
    </div>
    <div hidden><div class="seg" role="group" aria-label="Language"><button id="m-both" data-m="both" aria-pressed="true">EN | עב</button><button id="m-en" data-m="en" aria-pressed="false">English</button><button id="m-he" data-m="he" aria-pressed="false">עברית</button></div>
      <span class="progress" id="prog"></span><div id="pbar"></div><button class="btn" id="exam-btn" type="button">Practice exam · מבחן תרגול</button></div>
  </header>'''
s = s[:i] + HEADER + s[j:]

HERO_JS = r'''
// ----- Home banner: progress ring and "Up next" -----
function heroUpdate(){const n=done.length,N=DAYS.length,pct=Math.round(n/N*100);
  const r=document.getElementById("ring");if(r)r.style.strokeDashoffset=100-pct;
  const rn=document.getElementById("ring-n");if(rn)rn.textContent=n;const rp=document.getElementById("ring-pct");if(rp)rp.textContent=pct+"%";
  const box=document.getElementById("hero-next");if(!box)return;
  const nx=DAYS.findIndex((_,i)=>!done.includes(i));
  if(nx<0){box.innerHTML=`<div class="hn-text"><span class="hn-l">${bi(B("All subjects done","כל הנושאים הושלמו"),"span")}</span><b>${bi(B("Great work! Now take the practice exam.","כל הכבוד! עכשיו עשו את מבחן התרגול."),"span")}</b></div><button type="button" class="btn" id="hn-go">Practice exam · מבחן תרגול</button>`;
    document.getElementById("hn-go").onclick=()=>startExam();return}
  box.innerHTML=`<div class="hn-text"><span class="hn-l">${bi(B(`Up next · Subject ${nx+1} of ${N}`,`הבא בתור · נושא ${nx+1} מתוך ${N}`),"span")}</span><b>${bi(DAYS[nx].t,"span")}</b></div><button type="button" class="btn" id="hn-go">Open lesson · פתח שיעור</button>`;
  document.getElementById("hn-go").onclick=()=>{if(nx!==cur){if(run||left<3600)document.getElementById("treset").click();cur=nx;renderDays();renderDay()}document.getElementById("sheet").scrollIntoView({behavior:"smooth",block:"start"})}}
'''
rep('// ----- Bottom navigation -----', HERO_JS + '// ----- Bottom navigation -----')
rep('if(window.refreshReset)refreshReset();', 'if(window.refreshReset)refreshReset();if(typeof heroUpdate==="function")heroUpdate();')
rep('wireReset();applyTheme();syncSettings();', 'wireReset();applyTheme();syncSettings();heroUpdate();')
rep('function setMode(m){', 'function setMode(m){setTimeout(()=>{if(typeof heroUpdate==="function")heroUpdate()},0);')

HERO_CSS = r'''
/* ===== home banner ===== */
header.hero{position:relative;overflow:hidden;isolation:isolate;display:grid;gap:26px;padding:clamp(22px,4.5vw,40px);border-radius:28px;color:#fff;
  background:radial-gradient(90% 120% at 100% 0%,#3D48C8 0%,rgba(61,72,200,0) 60%),radial-gradient(70% 90% at 0% 100%,#202A7E 0%,rgba(32,42,126,0) 70%),#161C49;
  box-shadow:0 30px 60px -30px rgba(22,28,73,.65)}
.hero-art{position:absolute;z-index:-1;right:-30px;top:-30px;width:min(340px,70%);fill:none;stroke:rgba(255,255,255,.12);stroke-width:2.5;pointer-events:none}
.hero-top{display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:12px}
.logo{display:grid;place-items:center;width:46px;height:46px;border-radius:15px;background:linear-gradient(145deg,rgba(255,255,255,.22),rgba(255,255,255,.06));border:1px solid rgba(255,255,255,.25);box-shadow:inset 0 1px 0 rgba(255,255,255,.2)}
.logo svg{width:26px;height:26px;fill:none;stroke:#fff;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.brand-t{display:grid;line-height:1.25}
.brand-t b{font-weight:600;font-size:1.02rem;color:#fff}
body.m-both .brand-t b .he{display:none}
.brand-t small{font-size:.8rem;color:#AFB7F0;letter-spacing:.01em}
#resetwrap.open{flex-basis:100%}
.hero-main{display:block}
.hero-text{display:grid;grid-template-columns:1fr 1fr;column-gap:48px;row-gap:12px;align-items:end}
.hero-text h1.en{grid-column:1;grid-row:1}.hero-text h1.he{grid-column:2;grid-row:1}
.hero-text p.en{grid-column:1;grid-row:2;align-self:start}.hero-text p.he{grid-column:2;grid-row:2;align-self:start}
body.m-en .hero-text,body.m-he .hero-text{grid-template-columns:1fr}
body.m-en .hero-text>*,body.m-he .hero-text>*{grid-column:1}
body.m-he .hero-text p.he{grid-row:2}
@media (max-width:700px){.hero-text{grid-template-columns:1fr}.hero-text>*{grid-column:1!important;grid-row:auto!important}}
.hero-row{display:grid;grid-template-columns:auto 1fr;gap:16px;align-items:stretch}
@media (max-width:700px){.hero-row{grid-template-columns:1fr}}
.hero h1{font-size:clamp(1.9rem,5.6vw,3rem);line-height:1.08;font-weight:600;letter-spacing:-.025em;color:#fff;margin:0}
.hero h1.he{text-align:right}
@media (max-width:700px){body.m-both .hero h1.he{font-size:clamp(1.5rem,6vw,2rem);margin-top:4px}}
.hero .sub{margin:0;color:#C9CEF4;font-size:1.02rem;line-height:1.6;max-width:58ch}
.hero .sub.he{text-align:right}
.hero-prog{display:flex;align-items:center;gap:16px;padding:16px 22px;border-radius:20px;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.14);backdrop-filter:blur(6px)}
.ring{position:relative;width:86px;height:86px;flex:none}
.ring svg{width:100%;height:100%;transform:rotate(-90deg)}
.ring circle{fill:none;stroke-width:3.2}
.ring-bg{stroke:rgba(255,255,255,.16)}
.ring-fg{stroke:#fff;stroke-linecap:round;stroke-dasharray:100;stroke-dashoffset:100;transition:stroke-dashoffset .8s ease}
.ring-n{position:absolute;inset:0;display:flex;align-items:baseline;justify-content:center;padding-top:27px;color:#fff}
.ring-n b{font-size:1.6rem;font-weight:600;line-height:1}
.ring-n span{font-size:.85rem;color:#AFB7F0;margin-left:1px}
.ring-l{display:grid;gap:2px}
.ring-l b{font-weight:600;font-size:.95rem;display:grid}
.ring-l b .he{text-align:right;font-weight:500;color:#DDE1FB}
body.m-he .ring-l b .he,body.m-en .ring-l b .en{display:block}
#ring-pct{font-size:.85rem;color:#AFB7F0}
.hero-next{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;background:var(--sheet);color:var(--ink);border-radius:20px;padding:16px 18px 16px 20px;box-shadow:0 12px 30px -18px rgba(0,0,0,.6)}
.hn-text{display:grid;gap:4px;min-width:0}
.hn-l{font-size:.8rem;font-weight:600;color:var(--accent)}
.hn-l .he,.hn-text b .he{margin-inline-start:.6em}
body.m-both .hn-l .he{display:none}
.hn-text b{font-size:1.08rem;font-weight:600;line-height:1.35}
body.m-both .hn-text b .he{display:block;margin:2px 0 0;text-align:right;font-weight:500;color:var(--muted)}
.hero-next .btn{padding:12px 22px;border-radius:14px}
@media (prefers-reduced-motion:reduce){.ring-fg{transition:none}}
'''
rep('</style>', HERO_CSS + '</style>')
