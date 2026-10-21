# Build step (exec'd from build_offline.py after subjects_step.py, with `s` in scope): visual redesign.
# Concept: a study guide with a highlighter. Deep indigo ink, cool paper, highlighter yellow on the key facts.
# Type: IBM Plex Sans + IBM Plex Sans Hebrew everywhere (one clean family for both languages).

def rep(old, new):
    global s
    assert old in s, old[:80]
    s = s.replace(old, new, 1)

GOOGLE_FONTS = 'https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Sans+Hebrew:wght@400;500;600&display=swap'
s = re.sub(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/css2[^"]*">', f'<link rel="stylesheet" href="{GOOGLE_FONTS}">', s)

# Fonts bundled inside the Android app (fetch-fonts.sh puts them in assets/fonts at build time)
FONT_FILES = [("IBM Plex Sans", 400, "ibm-plex-sans", ["latin"]), ("IBM Plex Sans", 500, "ibm-plex-sans", ["latin"]), ("IBM Plex Sans", 600, "ibm-plex-sans", ["latin"]),
              ("IBM Plex Sans Hebrew", 400, "ibm-plex-sans-hebrew", ["hebrew"]), ("IBM Plex Sans Hebrew", 500, "ibm-plex-sans-hebrew", ["hebrew"]), ("IBM Plex Sans Hebrew", 600, "ibm-plex-sans-hebrew", ["hebrew"])]
RANGES = {"hebrew": "U+0307-0308,U+0590-05FF,U+200C-2010,U+20AA,U+25CC,U+FB1D-FB4F",
          "latin": "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2190-2199,U+2212,U+2215,U+FEFF,U+FFFD"}
FONTFACE_CSS = "".join(f'@font-face{{font-family:"{fam}";font-style:normal;font-weight:{w};font-display:swap;src:url(fonts/{pkg}-{sub}-{w}-normal.woff2) format("woff2");unicode-range:{RANGES[sub]}}}\n'
                       for fam, w, pkg, subs in FONT_FILES for sub in subs)
FONT_URLS = sorted({f"https://cdn.jsdelivr.net/npm/@fontsource/{pkg}@5.3.0/files/{pkg}-{sub}-{w}-normal.woff2" for fam, w, pkg, subs in FONT_FILES for sub in subs})

# ---- markup: hero header, subject list as its own section, progress bar ----
rep('<span class="label">Florida DCF · Child Care Facility Rules &amp; Regulations (RNRF)</span>',
    '<p class="course"><span class="en">Florida DCF · Child Care Facility Rules &amp; Regulations</span><span class="he" lang="he" dir="rtl">משרד הילדים והמשפחות של פלורידה · חוקים ותקנות למתקני טיפול בילדים</span></p>')
rep('<span class="progress" id="prog"></span>', '<div class="progwrap"><div class="progrow"><span class="progress" id="prog"></span><span id="resetwrap"><button type="button" class="reset" id="resetprog">Reset · איפוס</button></span></div><div class="pbar" aria-hidden="true"><div id="pbar"></div></div></div>')
rep('<span class="label subj-label">Pick a subject · בחרו נושא</span>\n    <nav class="days" id="days" aria-label="Subjects"></nav>\n  </header>',
    '</header>\n  <section class="subjects" aria-labelledby="subj-h">\n    <div class="bi subj-head"><h2 class="en" id="subj-h">Pick a subject</h2><h2 class="he" lang="he">בחרו נושא</h2></div>\n    <nav class="days" id="days" aria-label="Subjects"></nav>\n  </section>')
rep('document.getElementById("prog").textContent=`${done.length}/${DAYS.length} subjects done · ${done.length}/${DAYS.length} נושאים הושלמו`;',
    'document.getElementById("prog").textContent=`${done.length} of ${DAYS.length} subjects done · ${done.length} מתוך ${DAYS.length} נושאים הושלמו`;\n  {const pb=document.getElementById("pbar");if(pb)pb.style.width=(done.length/DAYS.length*100)+"%"}\n  if(window.refreshReset)refreshReset();')
rep('<span class="label">Session timer · טיימר</span>', '<span class="label">Lesson timer · טיימר השיעור</span>')
rep('<p class="en thint">Press <b>Start</b>. The timer takes you through the 4 parts, beeps and tells you when to switch. Tap any part to jump to it.</p><p class="he thint" lang="he">לחצו <b>התחל</b>. הטיימר מעביר אתכם בין 4 החלקים, מצפצף ומודיע מתי לעבור. הקישו על חלק כדי לקפוץ אליו.</p>',
    '<p class="en thint">Press <b>Start</b> and the lesson guides you: 50 minutes of rules, then 10 minutes of key facts, then the quiz.</p><p class="he thint" lang="he">לחצו <b>התחל</b> והשיעור ידריך אתכם: 50 דקות של כללים, 10 דקות של עובדות חשובות, ואחר כך הבוחן.</p>')

rep('<div><h3>Study helper · עוזר לימוד</h3>', '<div><h3>Study helper · עוזר לימוד <span class="ai-badge" id="h-ai" hidden>AI tutor · מורה AI</span></h3>')

THEME = r'''
/* ===== Theme: study guide + highlighter ===== */
[hidden]{display:none!important}
:root{
  --bg:#F3F5FA; --sheet:#FFFFFF; --ink:#1A2142; --muted:#5D6585; --line:#E0E4EF;
  --accent:#3245C4; --accent-ink:#FFFFFF; --accent-soft:#ECEFFC; --hero:#1C2457; --hero-2:#2A3480;
  --mark:#FFE15A; --mark-ink:#1A2142; --tip:#FFF7D1;
  --good:#0F8558; --bad:#C23B26; --chip:#EDF0F7;
  --display:"IBM Plex Sans","IBM Plex Sans Hebrew",Roboto,"Noto Sans Hebrew",system-ui,sans-serif;
  --body:"IBM Plex Sans","IBM Plex Sans Hebrew",Roboto,"Noto Sans Hebrew",system-ui,"Segoe UI",Arial,sans-serif;
  --mono:var(--body);
  --r-lg:22px; --r-md:14px; --r-sm:10px;
  --shadow:0 1px 2px rgba(26,33,66,.05),0 10px 30px -12px rgba(26,33,66,.16);
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#0E1226; --sheet:#161B35; --ink:#E8EBF8; --muted:#A3AAC8; --line:#283058;
  --accent:#B3BDFF; --accent-ink:#0E1226; --accent-soft:#1F2650; --hero:#1A2152; --hero-2:#27318A;
  --mark:#FFE15A; --mark-ink:#1A2142; --tip:#2A2714;
  --good:#4FD49A; --bad:#FF8A73; --chip:#1D2345; color-scheme:dark;
  --shadow:0 1px 2px rgba(0,0,0,.3),0 10px 30px -12px rgba(0,0,0,.5)}}
:root[data-theme="dark"]{
  --bg:#0E1226; --sheet:#161B35; --ink:#E8EBF8; --muted:#A3AAC8; --line:#283058;
  --accent:#B3BDFF; --accent-ink:#0E1226; --accent-soft:#1F2650; --hero:#1A2152; --hero-2:#27318A;
  --mark:#FFE15A; --mark-ink:#1A2142; --tip:#2A2714;
  --good:#4FD49A; --bad:#FF8A73; --chip:#1D2345; color-scheme:dark;
  --shadow:0 1px 2px rgba(0,0,0,.3),0 10px 30px -12px rgba(0,0,0,.5)}

body{font-family:var(--body);font-size:16.5px;line-height:1.6;-webkit-font-smoothing:antialiased;padding-block:16px 48px}
.he{font-family:"IBM Plex Sans Hebrew","IBM Plex Sans",Roboto,"Noto Sans Hebrew",system-ui,sans-serif}
h1,h2,h3{font-family:var(--display);font-weight:700;letter-spacing:-.005em}
h2{font-size:clamp(1.45rem,3.6vw,1.9rem);line-height:1.2}
h3{font-size:1.2rem;letter-spacing:0}
.wrap{gap:22px;max-width:1080px}
.label{font-family:var(--body);text-transform:none;letter-spacing:0;font-size:.84rem;font-weight:500;color:var(--muted)}
.ex{color:var(--muted)}
button{-webkit-tap-highlight-color:transparent}
button:focus-visible,.daytab:focus-visible,.card:focus-visible,.opt:focus-visible{outline:3px solid var(--accent);outline-offset:3px}

/* highlighter on key facts */
mark{background:linear-gradient(100deg,transparent 0 .25em,var(--mark) .3em calc(100% - .3em),transparent calc(100% - .25em));
  color:var(--mark-ink);padding:.05em .35em;margin:0 -.1em;border-radius:.35em .2em .45em .25em;-webkit-box-decoration-break:clone;box-decoration-break:clone}

/* hero */
header{background:radial-gradient(120% 140% at 100% 0%,var(--hero-2) 0%,var(--hero) 55%);color:#fff;border-radius:var(--r-lg);
  padding:clamp(22px,5vw,40px);gap:16px;box-shadow:var(--shadow)}
header .course{margin:0;font-size:.88rem;font-weight:500;color:#C9CFF5;display:grid;gap:2px}
header .course .he{text-align:right}
header h1{font-size:clamp(2rem,6.4vw,3.2rem);line-height:1.08;color:#fff;font-weight:700}
header .sub{color:#D6DBF7;font-size:1.02rem;max-width:56ch}
header .bi{gap:10px 36px}
header .topbar{margin-top:6px;gap:14px}
header .seg{background:rgba(255,255,255,.08);border-color:rgba(255,255,255,.22)}
header .seg button{color:#E5E8FB;padding:8px 14px;font-weight:500}
header .seg button[aria-pressed="true"]{background:#fff;color:var(--hero)}
.progwrap{display:grid;gap:6px;min-width:200px}
header .progress{font-family:var(--body);color:#E5E8FB;font-size:.88rem}
.pbar{height:6px;border-radius:99px;background:rgba(255,255,255,.18);overflow:hidden}
.pbar div{height:100%;width:0;background:var(--mark);border-radius:99px;transition:width .6s ease}
header #exam-btn{background:var(--mark);border-color:var(--mark);color:var(--mark-ink);font-weight:600}
@media (max-width:640px){header .bi .he{border-top:1px solid rgba(255,255,255,.18)}}

/* subject list */
.subjects{display:grid;gap:12px}
.subj-head{align-items:end}
.subj-head h2{font-size:1.5rem}
.days{gap:10px}
.daytab.subj{background:var(--sheet);border:1px solid var(--line);border-radius:var(--r-md);padding:14px 16px;gap:14px;min-height:68px;
  box-shadow:0 1px 2px rgba(26,33,66,.04);transition:border-color .15s,box-shadow .15s}
.daytab.subj:hover{border-color:var(--accent);box-shadow:var(--shadow)}
.daytab.subj .n{display:grid;place-items:center;width:38px;height:38px;border-radius:50%;background:var(--accent-soft);color:var(--accent);
  font-family:var(--display);font-weight:700;font-size:1.1rem;line-height:1}
.daytab.subj .t{font-size:.98rem;font-weight:500;gap:3px}
.daytab.subj .t .he{font-weight:400;color:var(--muted)}
body.m-he .daytab.subj .t .he{color:var(--ink);font-weight:500}
.daytab.subj[aria-current="true"]{border-color:var(--accent);box-shadow:inset 0 0 0 1px var(--accent),var(--shadow)}
.daytab.subj[aria-current="true"] .n{background:var(--accent);color:var(--accent-ink)}
.daytab.subj.done{background:var(--sheet)}
.daytab.subj.done .n{background:color-mix(in srgb,var(--good) 14%,transparent);color:var(--good)}

/* buttons */
.btn{border-radius:12px;padding:11px 18px;font-weight:600;font-size:.95rem;border-width:1px;transition:transform .08s,filter .15s}
.btn:active{transform:translateY(1px)}
.btn:hover{filter:brightness(1.06)}
.btn.ghost{background:var(--sheet);border-color:var(--line);color:var(--accent)}
.mini{background:var(--chip);border-color:transparent;color:var(--accent);padding:6px 12px;font-size:.84rem;font-weight:500}
.mini:hover{border-color:var(--accent)}

/* timer */
.timer{border:1px solid var(--line);border-radius:var(--r-lg);padding:18px 20px;box-shadow:var(--shadow);gap:14px}
.clock{font-family:var(--body);font-size:2.6rem;font-weight:600;letter-spacing:-.02em;line-height:1.05}
.blocks{gap:6px}
.blk{border-radius:10px;padding:9px 12px;font-size:.86rem;font-weight:500;background:var(--chip)}
.blk .fill{background:var(--accent);opacity:.22}
.blk.on{outline:2px solid var(--accent);outline-offset:-2px}
.thint{color:var(--muted)}
#tnow{color:var(--accent)}
.timer.running{border-radius:0 0 var(--r-md) var(--r-md);box-shadow:0 8px 24px -8px rgba(26,33,66,.25)}
.timer.running .clock{font-size:1.35rem}

/* subject page */
.sheet{border-radius:var(--r-lg);padding:clamp(20px,4vw,40px);gap:34px;box-shadow:var(--shadow)}
.sheet>.sec:first-child h2{font-size:clamp(1.9rem,5.4vw,2.7rem);line-height:1.12}
.sec{gap:14px}
.sec-head{border-bottom:0;padding-bottom:0;align-items:center;gap:12px}
.sec-head h3{font-size:1.35rem}
.mins{font-family:var(--body);font-weight:600;font-size:.8rem;color:var(--accent);background:var(--accent-soft);padding:3px 10px;border-radius:99px}
.plan{background:var(--accent-soft);border-radius:var(--r-md);padding:20px 22px;border:0}
.plan #startday{font-size:1.05rem;padding:14px 26px;border-radius:14px;box-shadow:0 8px 20px -8px color-mix(in srgb,var(--accent) 70%,transparent)}
ul.points{gap:12px}
ul.points li{background:var(--sheet);border:1px solid var(--line);border-radius:var(--r-md);padding:16px 18px}
.bi{gap:8px 32px}
@media (max-width:640px){.bi .he{border-top:1px solid var(--line);padding-top:8px}}
.cards{gap:12px}
.card{background:var(--sheet);border:1px solid var(--line);border-radius:var(--r-md);min-height:132px;padding:16px;box-shadow:0 1px 2px rgba(26,33,66,.04);transition:border-color .15s}
.card .front{font-family:var(--display);font-weight:700;font-size:1.08rem}
.card.flip{border-color:var(--accent);background:var(--accent-soft)}
.card.flip .back{color:var(--ink)}
table th{font-family:var(--body);text-transform:none;letter-spacing:0;font-size:.84rem;font-weight:600}
td b{font-family:var(--display);font-size:1.1rem}
.tbl{border:1px solid var(--line);border-radius:var(--r-md);padding:4px 10px}
.note{border-left:3px solid var(--mark);font-size:.84rem}

/* quiz */
.qbar{height:8px;border-radius:99px;background:var(--chip)}.qbar div{border-radius:99px}
.q{background:var(--sheet);border:1px solid var(--line);border-radius:var(--r-md);padding:18px;gap:12px}
.q>.bi{font-family:var(--display);font-size:1.18rem;font-weight:700;line-height:1.35}
.opts{gap:8px}
.opt{border-radius:12px;padding:13px 16px;font-size:1rem;border-color:var(--line);transition:border-color .12s,background .12s}
.opt:hover{border-color:var(--accent);background:var(--accent-soft)}
.opt.right{background:color-mix(in srgb,var(--good) 10%,var(--sheet))}
.opt.wrong{background:color-mix(in srgb,var(--bad) 9%,var(--sheet))}
.verdict{border-radius:12px;padding:10px 14px}
.grade{border-radius:var(--r-lg);padding:22px 24px;background:var(--accent-soft)}
.grade .big{font-size:4rem;font-weight:700}
.score{font-family:var(--body);font-variant-numeric:tabular-nums}

/* guided lesson */
#coach .c-top{padding-top:14px;padding-bottom:12px;gap:10px;box-shadow:0 1px 0 var(--line)}
#coach .c-head .label{color:var(--ink);font-weight:600}
#coach .c-clock{font-family:var(--body);font-weight:600;font-size:1.5rem;color:var(--accent)}
#coach .c-body{padding-top:28px;gap:18px;max-width:720px}
#coach .c-body>.label{color:var(--accent);font-weight:600}
#coach .c-big{font-family:var(--display);font-size:clamp(1.3rem,4.4vw,1.6rem);line-height:1.55;font-weight:500}
#coach .c-big .he{font-family:var(--display)}
#coach h2{font-size:clamp(1.6rem,5vw,2.1rem)}
#coach .c-box{border:0;border-radius:var(--r-md);padding:16px 18px;background:var(--accent-soft);gap:6px}
#coach .c-box>b{color:var(--accent);font-size:.86rem;font-weight:600}
#coach .c-box.tip{background:var(--tip);border-inline-start:4px solid var(--mark)}
#coach .c-box.tip>b{color:var(--mark-ink)}
:root[data-theme="dark"] #coach .c-box.tip>b{color:var(--mark)}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]) #coach .c-box.tip>b{color:var(--mark)}}
#coach .c-card{border:0;border-radius:var(--r-lg);padding:32px 22px;background:var(--sheet);box-shadow:var(--shadow)}
#coach .c-q{font-family:var(--display);font-weight:700;font-size:1.55rem}
#coach .c-a{font-size:1.25rem;font-weight:500}
#coach .c-count{font-family:var(--body);font-weight:600}
#coach .c-foot{box-shadow:0 -1px 0 var(--line);border-top:0}
#coach .c-nav .btn{padding:15px 12px;font-size:1.02rem;border-radius:14px}
#coach .mini{background:var(--chip)}

/* helper button */
.fab{background:var(--hero);color:#fff;padding:14px 20px;box-shadow:0 12px 28px -10px rgba(26,33,66,.55)}
@media (prefers-reduced-motion:reduce){.pbar div{transition:none}}
/* refinements */
/* answers: unmistakable right / wrong marking in every quiz and exam */
:root{--ok:#13804A;--ok-soft:#E5F5EC;--no:#C4372A;--no-soft:#FCEAE8}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--ok:#4FD49A;--ok-soft:rgba(79,212,154,.14);--no:#FF8A73;--no-soft:rgba(255,138,115,.14)}}
:root[data-theme="dark"]{--ok:#4FD49A;--ok-soft:rgba(79,212,154,.14);--no:#FF8A73;--no-soft:rgba(255,138,115,.14)}
.q .opt.right{background:var(--ok-soft);border-color:var(--ok);box-shadow:inset 0 0 0 2px var(--ok);color:var(--ink);opacity:1}
.q .opt.wrong{background:var(--no-soft);border-color:var(--no);box-shadow:inset 0 0 0 2px var(--no);color:var(--ink);opacity:1}
.q .opt.right::after,.q .opt.wrong::after{content:none}
.q .opt.right::before,.q .opt.wrong::before{display:block;width:max-content;max-width:100%;margin-bottom:6px;padding:3px 10px;border-radius:99px;font-size:.8rem;font-weight:600;color:#fff}
.q .opt.right::before{content:"✓ Correct answer · התשובה הנכונה";background:var(--ok)}
.q .opt.wrong::before{content:"✗ Your answer · התשובה שלך";background:var(--no)}
:root[data-theme="dark"] .q .opt.right::before,:root[data-theme="dark"] .q .opt.wrong::before{color:#0E1226}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]) .q .opt.right::before,:root:not([data-theme="light"]) .q .opt.wrong::before{color:#0E1226}}
.q[data-done] .opt:not(.right):not(.wrong){opacity:.5}
.q .opt.right .bi .he,.q .opt.wrong .bi .he{color:var(--ink)}
.q .verdict.good{background:var(--ok-soft);color:var(--ok)}
.q .verdict.bad{background:var(--no-soft);color:var(--no)}
.q .verdict span{color:var(--ink)}
.progrow{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap}
header .reset{border:1px solid rgba(255,255,255,.35);background:transparent;color:#fff;border-radius:99px;padding:4px 12px;font:inherit;font-size:.82rem;font-weight:500;cursor:pointer}
#resetwrap.open{display:flex;flex-wrap:wrap;gap:8px;width:100%;margin-top:4px}
#resetwrap .rq{width:100%;font-size:.9rem;color:#E5E8FB}
#resetwrap .rq>span{display:block}
body.m-en #resetwrap .rq>span.he,body.m-he #resetwrap .rq>span.en{display:none}
.rpick{display:grid;gap:8px;width:100%}
.rsub{display:flex;align-items:center;gap:12px;width:100%;text-align:start;border:1px solid rgba(255,255,255,.3);background:rgba(255,255,255,.06);color:#fff;border-radius:12px;padding:12px 14px;font:inherit;font-size:.95rem;cursor:pointer}
.rsub .box{flex:none;width:22px;height:22px;border-radius:6px;border:2px solid rgba(255,255,255,.7);display:grid;place-items:center}
.rsub[aria-checked="true"]{background:#fff;color:var(--hero);border-color:#fff}
.rsub[aria-checked="true"] .box{background:var(--accent);border-color:var(--accent)}
.rsub[aria-checked="true"] .box::after{content:"✓";color:#fff;font-size:.8rem;font-weight:700}
.rsub:focus-visible{outline:3px solid #fff;outline-offset:2px}
header .reset:disabled{opacity:.45;cursor:not-allowed}
header .reset.yes{background:#fff;color:var(--hero);border-color:#fff}
header .reset:focus-visible{outline:3px solid #fff;outline-offset:2px}
#donebox{flex-direction:column;align-items:stretch;gap:12px}
.donemsg{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;background:var(--accent-soft);color:var(--accent);border-radius:var(--r-md);padding:14px 16px}
.donemsg b>span{display:block}
body.m-en .donemsg b>span.he,body.m-he .donemsg b>span.en{display:none}
#nextsubj{padding:14px 18px}
ul.facts li .bi+.bi{margin-top:6px}
#coach .c-fact .c-q{margin-bottom:4px}
#coach .c-fact .c-a{border-top:1px solid var(--line);padding-top:12px;color:var(--accent);font-weight:500}
h1,h2,h3{font-weight:600;letter-spacing:-.015em}
header h1{font-weight:600;letter-spacing:-.02em}
#coach .c-big{font-weight:400;line-height:1.6}
#coach .c-big .he{font-family:"IBM Plex Sans Hebrew",Roboto,"Noto Sans Hebrew",sans-serif}
#coach .c-q{font-weight:600;font-size:1.3rem;line-height:1.4}
#coach .c-a{font-size:1.15rem;line-height:1.5;border-top:1px solid var(--line)}
#coach .c-card{text-align:start}
#coach .c-card .bi{gap:6px 24px}
.card{text-align:start;align-content:start}
.card .front{font-weight:600;font-size:1rem}
.card .back{font-size:.95rem}
.card.flip .back{display:grid}
.daytab.subj .n,.grade .big,td b{font-weight:600}
/* key facts: calm blue bold instead of a yellow highlighter (easier on the eyes) */
mark{background:none;color:var(--accent);font-weight:600;padding:0;margin:0;border-radius:0}
#coach .c-box.tip{background:var(--chip);border-inline-start:4px solid var(--accent)}
#coach .c-box.tip>b{color:var(--accent)!important}
.pbar div{background:#fff}
.note{border-left-color:var(--accent)}
/* one look everywhere: blue for actions and for the right answer; no green or red buttons */
#coach .btn.good{background:var(--accent);border-color:var(--accent);color:var(--accent-ink)}
#coach .btn.bad{background:var(--sheet);border-color:var(--line);color:var(--accent)}
#coach .c-a{color:var(--ink)}
.opt{position:relative}
.opt.right{border-color:var(--accent);box-shadow:inset 0 0 0 1px var(--accent);background:var(--accent-soft)}
.opt.wrong{border-color:var(--line);box-shadow:none;background:var(--chip);color:var(--muted)}
.opt.right::after,.opt.wrong::after{position:absolute;top:12px;inset-inline-end:14px;font-weight:600}
.opt.right::after{content:"✓";color:var(--accent)}
.opt.wrong::after{content:"✗";color:var(--muted)}
.opt.right .bi,.opt.wrong .bi,.opt.right>span,.opt.wrong>span{padding-inline-end:22px}
.verdict.good,.verdict.bad{color:var(--ink);background:var(--accent-soft)}
.verdict span{color:var(--muted)}
.grade.good .big,.grade.bad .big{color:var(--accent)}
.daytab.subj.done .n{background:var(--accent-soft);color:var(--accent)}
header #exam-btn{background:#fff;border-color:#fff;color:var(--hero)}
.ai-badge{background:var(--accent-soft);color:var(--accent)}
/* lesson buttons sit right under the content, so they're visible even when the page is shown inside a tall frame */
#coach{overflow-y:auto}
#coach .c-body{flex:none;overflow:visible}
#coach .c-foot{background:transparent;box-shadow:none;border:0;padding-top:4px;padding-bottom:28px}
.ai-badge{display:inline-block;vertical-align:middle;margin-inline-start:6px;font-family:var(--body);font-size:.72rem;font-weight:600;color:var(--mark-ink);background:var(--mark);padding:2px 8px;border-radius:99px}
header .bi .he,.subj-head .he,.bi>h2.he,.bi>h1.he{border-top:0!important;padding-top:0!important}
.subj-head{display:flex;justify-content:space-between;align-items:baseline;gap:12px;flex-wrap:wrap}
body.m-both .subj-head h2.he{font-size:1.35rem}
.opt .bi{gap:2px 24px}
.opt .bi .he{border-top:0!important;padding-top:0;color:var(--muted)}
body.m-he .opt .bi .he{color:var(--ink)}
#coach .c-body>.label .he{margin-left:1em}
@media (max-width:640px){.fab{padding:16px;border-radius:50%}.fab span{display:none}.fab svg{width:24px;height:24px}}

'''
rep('</style>', THEME + '</style>')
