# Build step (exec'd after update_step.py): a branded splash screen each time the app opens.
def rep(old, new):
    global s
    assert old in s, old[:80]
    s = s.replace(old, new, 1)

SPLASH = '''<div id="splash" role="img" aria-label="Rules Study · Florida DCF">
  <svg class="sp-art" viewBox="0 0 300 300" aria-hidden="true"><circle cx="210" cy="70" r="46"/><rect x="88" y="34" width="70" height="70" rx="14" transform="rotate(14 123 69)"/><path d="M232 150 282 236H182z"/><path d="M96 190a52 52 0 0 1 104 0z"/><rect x="40" y="128" width="40" height="40" rx="10" transform="rotate(-12 60 148)"/></svg>
  <div class="sp-center">
    <div class="sp-logo"><svg viewBox="0 0 24 24"><path d="M12 2.5 4.5 5.5v6c0 4.6 3.1 8.4 7.5 10 4.4-1.6 7.5-5.4 7.5-10v-6z"/><path d="m8.5 12 2.4 2.4 4.6-4.8"/></svg></div>
    <div class="sp-name">Rules Study</div>
    <div class="sp-org">Florida DCF · RNRF</div>
    <div class="sp-line"></div>
    <div class="sp-course">Child Care Facility Rules &amp; Regulations</div>
    <div class="sp-course he" lang="he" dir="rtl">חוקים ותקנות למתקני טיפול בילדים</div>
  </div>
  <div class="sp-bar"><div></div></div>
</div>
'''
rep('<div class="wrap">', SPLASH + '<div class="wrap">')

SPLASH_JS = r'''
// ----- Splash screen -----
{const sp=document.getElementById("splash");if(sp&&navigator.webdriver){sp.remove()} // automated tests skip it
 else if(sp){const quick=matchMedia("(prefers-reduced-motion: reduce)").matches;sp.onclick=()=>{sp.classList.add("out");setTimeout(()=>sp.remove(),400)};
  setTimeout(()=>{sp.classList.add("out");setTimeout(()=>sp.remove(),quick?0:600)},quick?600:2000)}}
'''
rep('// ----- Bottom navigation -----', SPLASH_JS + '// ----- Bottom navigation -----')

SPLASH_CSS = r'''
/* splash screen */
#splash{position:fixed;inset:0;z-index:200;display:grid;place-items:center;overflow:hidden;color:#fff;
  background:radial-gradient(80% 60% at 100% 0%,#3D48C8 0%,rgba(61,72,200,0) 65%),radial-gradient(70% 50% at 0% 100%,#26318E 0%,rgba(38,49,142,0) 70%),#161C49;
  transition:opacity .6s ease,transform .6s ease}
#splash.out{opacity:0;transform:scale(1.04);pointer-events:none}
.sp-art{position:absolute;right:-40px;top:-30px;width:min(420px,85vw);fill:none;stroke:rgba(255,255,255,.1);stroke-width:2.5}
.sp-center{display:grid;justify-items:center;text-align:center;gap:8px;padding:24px;animation:sp-in .9s cubic-bezier(.2,.7,.2,1) both}
.sp-logo{display:grid;place-items:center;width:104px;height:104px;border-radius:30px;margin-bottom:14px;
  background:linear-gradient(145deg,rgba(255,255,255,.24),rgba(255,255,255,.06));border:1px solid rgba(255,255,255,.28);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.25),0 24px 50px -20px rgba(0,0,0,.6)}
.sp-logo svg{width:56px;height:56px;fill:none;stroke:#fff;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}
.sp-logo svg path:last-child{stroke-dasharray:12;stroke-dashoffset:12;animation:sp-check .6s .5s ease forwards}
.sp-name{font-size:2.3rem;font-weight:600;letter-spacing:-.02em;line-height:1.1}
.sp-org{font-size:.95rem;color:#B9C0F3;letter-spacing:.04em}
.sp-line{width:44px;height:2px;border-radius:2px;background:rgba(255,255,255,.35);margin:14px 0 8px}
.sp-course{font-size:1rem;color:#DDE1FB;max-width:30ch}
.sp-bar{position:absolute;bottom:calc(48px + env(safe-area-inset-bottom,0px));width:120px;height:3px;border-radius:3px;background:rgba(255,255,255,.18);overflow:hidden}
.sp-bar div{height:100%;width:40%;border-radius:3px;background:#fff;animation:sp-load 1.1s ease-in-out infinite}
@keyframes sp-in{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
@keyframes sp-check{to{stroke-dashoffset:0}}
@keyframes sp-load{0%{transform:translateX(-100%)}100%{transform:translateX(250%)}}
@media (prefers-reduced-motion:reduce){.sp-center,.sp-bar div{animation:none}.sp-logo svg path:last-child{animation:none;stroke-dashoffset:0}}
'''
rep('</style>', SPLASH_CSS + '</style>')
