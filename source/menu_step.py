# Build step (exec'd after align_step.py): a menu button (☰) at the top right, with the same
# four places as the bottom bar: Subjects, Practice exam, Helper, Settings.
def rep(old, new):
    global s
    assert old in s, old[:80]
    s = s.replace(old, new, 1)

BURGER = ('<button type="button" class="burger" aria-label="Menu · תפריט" aria-haspopup="true" aria-expanded="false">'
          '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>')

# top right of the home screen
rep('<span id="resetwrap">', BURGER.replace('class="burger"', 'class="burger on-hero"') + '<span id="resetwrap">')
# top right of the lesson screen, next to the clock
rep('<div class="c-clock" id="c-clock">60:00</div></div>',
    '<div class="c-right"><div class="c-clock" id="c-clock">60:00</div>' + BURGER + '</div></div>')

MENU = '''<div class="menu-pop" id="menu-pop" role="menu" hidden>
  <button type="button" role="menuitem" data-go="tab-subjects"></button>
  <button type="button" role="menuitem" data-go="tab-exam"></button>
  <button type="button" role="menuitem" data-go="tab-helper"></button>
  <button type="button" role="menuitem" data-go="tab-settings"></button>
</div>
'''
rep('<nav class="tabbar"', MENU + '<nav class="tabbar"')

MENU_JS = r'''
// ----- Top-right menu (same places as the bottom bar) -----
{const pop=document.getElementById("menu-pop");let opener=null;
  pop.querySelectorAll("[data-go]").forEach(b=>{const t=document.getElementById(b.dataset.go);
    b.innerHTML=t.querySelector("svg").outerHTML+`<span class="mi-t"><span class="en">${t.querySelector(".en").textContent}</span><span class="he" lang="he">${t.querySelector(".he").textContent}</span></span>`;
    b.onclick=()=>{close();t.click()}});
  const close=()=>{if(pop.hidden)return;pop.hidden=true;if(opener){opener.setAttribute("aria-expanded","false");opener=null}};
  const open=btn=>{opener=btn;btn.setAttribute("aria-expanded","true");pop.hidden=false;
    const r=btn.getBoundingClientRect();pop.style.top=(r.bottom+8)+"px";pop.style.right=Math.max(12,innerWidth-r.right)+"px";pop.querySelector("button").focus()};
  document.querySelectorAll(".burger").forEach(btn=>btn.onclick=e=>{e.stopPropagation();const same=opener===btn;close();if(!same)open(btn)});
  document.addEventListener("click",e=>{if(!pop.contains(e.target))close()});
  document.addEventListener("keydown",e=>{if(e.key==="Escape")close()});
  addEventListener("resize",close);addEventListener("scroll",close,{passive:true});}
'''
rep('// ----- Bottom navigation -----', MENU_JS + '// ----- Bottom navigation -----')

MENU_CSS = r'''
/* top-right menu */
.burger{display:grid;place-items:center;width:44px;height:44px;border-radius:14px;cursor:pointer;flex:none;
  border:1px solid var(--line);background:var(--sheet);color:var(--ink)}
.burger svg{width:22px;height:22px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round}
.burger:focus-visible{outline:3px solid var(--accent);outline-offset:2px}
.burger.on-hero{order:2;background:rgba(255,255,255,.12);border-color:rgba(255,255,255,.25);color:#fff}
.burger.on-hero:hover{background:rgba(255,255,255,.2)}
.hero-top #resetwrap{order:1;margin-left:auto}
.hero-top #resetwrap.open{order:3}
.hero-top .brand{order:0}
#coach .c-right{display:flex;align-items:center;gap:12px}
.menu-pop{position:fixed;z-index:120;min-width:240px;display:grid;gap:2px;padding:8px;border-radius:18px;background:var(--sheet);
  border:1px solid var(--line);box-shadow:0 24px 48px -16px rgba(16,22,64,.45)}
.menu-pop button{display:flex;align-items:center;gap:14px;width:100%;padding:12px 14px;border:0;border-radius:12px;background:none;
  color:var(--ink);font:inherit;font-size:1rem;font-weight:500;text-align:left;cursor:pointer}
.menu-pop button:hover,.menu-pop button:focus-visible{background:var(--accent-soft);color:var(--accent);outline:none}
.menu-pop svg{width:22px;height:22px;flex:none;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.menu-pop .mi-t{display:grid;line-height:1.25;text-align:left}
.menu-pop .mi-t .he{font-weight:400;font-size:.9rem;color:var(--muted)}
.menu-pop button:hover .mi-t .he{color:inherit}
body.m-en .menu-pop .mi-t .he,body.m-he .menu-pop .mi-t .en{display:none}
body.m-he .menu-pop .mi-t .he{font-size:1rem;font-weight:500;color:inherit}
'''
rep('</style>', MENU_CSS + '</style>')
