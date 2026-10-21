# Build step (exec'd after helper_step.py): app-style bottom navigation; language and settings leave the top banner.
def rep(old, new):
    global s
    assert old in s, old[:80]
    s = s.replace(old, new, 1)

ICONS = {
 "subjects": '<svg viewBox="0 0 24 24"><path d="M4 6h16M4 12h16M4 18h10"/></svg>',
 "exam": '<svg viewBox="0 0 24 24"><rect x="5" y="3" width="14" height="18" rx="2"/><path d="M9 3v3h6V3"/><path d="m9 13 2 2 4-4"/></svg>',
 "helper": '<svg viewBox="0 0 24 24"><path d="M4 5h16v11H9l-5 4z"/><path d="M9 10h6"/></svg>',
 "settings": '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M4.2 4.2l2.1 2.1M17.7 17.7l2.1 2.1M2 12h3M19 12h3M4.2 19.8l2.1-2.1M17.7 6.3l2.1-2.1"/></svg>',
}
def tab(id_, icon, en, he):
    return f'<button type="button" class="tab" id="{id_}">{ICONS[icon]}<span class="en">{en}</span><span class="he" lang="he">{he}</span></button>'

NAV = ('<nav class="tabbar" aria-label="Main">'
       + tab("tab-subjects", "subjects", "Subjects", "נושאים")
       + tab("tab-exam", "exam", "Practice exam", "מבחן תרגול")
       + tab("tab-helper", "helper", "Helper", "עוזר")
       + tab("tab-settings", "settings", "Settings", "הגדרות")
       + '</nav>\n')
rep('<button class="fab" id="fab"', NAV + '<button class="fab" id="fab"')

# the settings button moves from the top banner to the bottom bar
rep('<button class="btn ghost" id="set-btn" type="button" aria-expanded="false" aria-controls="settings">⚙ Settings · הגדרות</button>', '')
rep('const sec=document.getElementById("settings"),btn=document.getElementById("set-btn");',
    'const sec=document.getElementById("settings"),btn=document.getElementById("tab-settings");')

NAV_JS = r'''
// ----- Bottom navigation -----
{const go=el=>{const t=document.getElementById(el);if(t)t.scrollIntoView({behavior:"smooth",block:"start"})};
  const leaveLesson=()=>{if(typeof coach!=="undefined"&&coach.open)closeCoach()}; // the lesson timer keeps running; "Open lesson" brings it back
  document.getElementById("tab-subjects").onclick=()=>{leaveLesson();const st=document.getElementById("settings");if(st&&!st.hidden){st.hidden=true;document.getElementById("tab-settings").setAttribute("aria-expanded","false")}go("subj-h")};
  document.getElementById("tab-exam").onclick=()=>{leaveLesson();startExam()};
  document.getElementById("tab-helper").onclick=()=>{hEl.hidden?openHelper():closeHelper()};}
'''
rep('setMode(mode);renderDays();renderDay();renderBlocks();wireReset();', NAV_JS + 'setMode(mode);renderDays();renderDay();renderBlocks();wireReset();')

NAV_CSS = r'''
/* language lives in Settings now */
header .topbar>.seg{display:none}
header #exam-btn{display:none}
/* app-style bottom bar */
.fab{display:none!important}
.tabbar{position:fixed;left:0;right:0;bottom:0;z-index:25;display:grid;grid-template-columns:repeat(4,1fr);background:var(--sheet);border-top:1px solid var(--line);
  padding:6px max(8px,env(safe-area-inset-right,0px)) calc(6px + env(safe-area-inset-bottom,0px)) max(8px,env(safe-area-inset-left,0px));box-shadow:0 -8px 24px -16px rgba(26,33,66,.35)}
.tab{display:grid;justify-items:center;align-content:center;gap:3px;min-height:58px;border:0;background:none;color:var(--muted);font:inherit;font-size:.74rem;font-weight:500;line-height:1.15;cursor:pointer;border-radius:12px;padding:4px 2px;text-align:center}
.tab svg{width:24px;height:24px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.tab:hover,.tab[aria-expanded="true"]{color:var(--accent)}
.tab[aria-expanded="true"]{background:var(--accent-soft)}
.tab:focus-visible{outline:3px solid var(--accent);outline-offset:-3px}
body.m-both .tab .he{font-size:.7rem}
.wrap{padding-bottom:110px}
/* the bottom bar stays on every screen, including lessons and quizzes */
.tabbar{z-index:50}
#coach{bottom:calc(71px + env(safe-area-inset-bottom,0px))}
.helper{z-index:60}
@media (max-width:560px){.helper{bottom:calc(71px + env(safe-area-inset-bottom,0px));height:calc(88vh - 71px)}}
/* full width on every screen; on wide screens (tablets, computers) the four buttons stay grouped in the middle */
@media (min-width:700px){.tabbar{padding-left:calc(50% - 320px);padding-right:calc(50% - 320px)}}
'''
rep('</style>', NAV_CSS + '</style>')
