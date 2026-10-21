# Build step (exec'd after settings_step.py): a clean, roomy Study helper panel; voice pickers live in Settings.
def rep(old, new):
    global s
    assert old in s, old[:80]
    s = s.replace(old, new, 1)

s = re.sub(r'\s*<details class="h-note" id="vset">.*?</details>', '', s, count=1, flags=re.S)

rep('<div><h3>Study helper · עוזר לימוד <span class="ai-badge" id="h-ai" hidden>AI tutor · מורה AI</span></h3><span class="h-note" id="h-day"></span></div>\n    <div style="display:flex;gap:6px">\n      <button class="mini" id="h-stop" title="Stop reading">Stop · עצור</button>\n      <button class="mini" id="h-close" title="Close">Close · סגור</button>\n    </div>',
    '<div class="h-title"><h3><span class="en">Study helper</span><span class="he" lang="he">עוזר לימוד</span></h3><span class="ai-badge" id="h-ai" hidden>AI tutor · מורה AI</span><span class="h-sub" id="h-day"></span></div>\n    <div class="h-actions">\n      <button class="mini" id="h-stop" title="Stop reading">■ Stop · עצור</button>\n      <button class="h-x" id="h-close" title="Close" aria-label="Close · סגור">✕</button>\n    </div>')

rep('<label class="h-note"><input type="checkbox" id="h-auto"> Read answers aloud · הקראת תשובות בקול</label>',
    '<label class="h-toggle"><input type="checkbox" id="h-auto"><span>Read answers aloud · הקראת תשובות בקול</span></label>')

rep('<div class="set-row"><span class="set-l">Voices · קולות</span><button type="button" class="btn ghost" id="set-voices">Choose and test voices · בחירה ובדיקה של קולות</button></div>',
    '<div class="set-row"><span class="set-l">Voices · קולות</span>'
    '<label class="set-field"><span>Hebrew voice · קול בעברית</span><select id="v-he"></select></label>'
    '<label class="set-field"><span>English voice · קול באנגלית</span><select id="v-en"></select></label>'
    '<button type="button" class="btn ghost" id="v-test">▶ Test the voices · בדיקת הקולות</button>'
    '<p id="v-none" class="set-note" hidden>No Hebrew voice is installed on this device. · אין קול בעברית במכשיר הזה.</p>'
    '<p class="set-note">Tip: test each Hebrew voice and keep the clearest one. A speed of 80–90% is easiest to follow.<br><span dir="rtl">טיפ: בדקו כל קול בעברית ובחרו את הברור ביותר. מהירות של 80–90% הכי נוחה.</span></p></div>')

rep('  document.getElementById("set-voices").onclick=()=>{openHelper();const v=document.getElementById("vset");if(v){v.open=true;fillVoices();v.scrollIntoView({block:"nearest"})}};\n', '')
rep('document.getElementById("set-rate-v").textContent=Math.round(voiceRate()*100)+"%"}}',
    'document.getElementById("set-rate-v").textContent=Math.round(voiceRate()*100)+"%"}\n  try{fillVoices()}catch(e){}}')

HELPER_CSS = """
/* study helper panel */
.helper{display:flex;flex-direction:column;width:min(440px,calc(100vw - 32px));height:min(720px,calc(100vh - 32px));max-height:none;background:var(--sheet);border:1px solid var(--line);border-radius:22px;overflow:hidden;box-shadow:0 24px 60px -20px rgba(26,33,66,.45)}
@media (max-width:560px){.helper{width:100%;max-height:none;height:88vh;border-radius:22px 22px 0 0}}
.h-head{align-items:flex-start;gap:12px;padding:18px 18px 16px;background:var(--sheet);border-bottom:1px solid var(--line)}
.h-title{display:grid;gap:6px;min-width:0}
.h-title h3{font-size:1.2rem;font-weight:600;display:flex;flex-wrap:wrap;gap:0 10px}
.h-title .ai-badge{justify-self:start;margin:0}
.h-sub{font-size:.88rem;color:var(--muted);line-height:1.4}
.h-actions{display:flex;align-items:center;gap:8px;flex:none}
.h-actions .mini{padding:7px 12px}
.h-x{width:36px;height:36px;border-radius:50%;border:1px solid var(--line);background:var(--sheet);color:var(--ink);font-size:1rem;cursor:pointer;display:grid;place-items:center}
.h-x:hover{border-color:var(--accent);color:var(--accent)}
.h-body{flex:1 1 auto;min-height:0;overflow-y:auto;padding:18px;gap:14px;background:var(--bg)}
.h-head,.h-foot{flex:none}
.msg{padding:12px 16px;border-radius:18px;line-height:1.6;font-size:.98rem;max-width:88%}
.msg.bot{background:var(--sheet);border:1px solid var(--line);border-bottom-left-radius:6px;color:var(--ink)}
.msg.bot[dir="rtl"]{border-bottom-left-radius:18px;border-bottom-right-radius:6px}
.msg.me{border-bottom-right-radius:6px}
.msg .tools{margin-top:10px;gap:8px}
.msg.h-note{background:transparent;border:0;padding:4px 2px;font-size:.85rem}
.h-foot{padding:16px 18px 18px;gap:14px;border-top:1px solid var(--line);background:var(--sheet)}
.chips{gap:8px;flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;margin:0 -18px;padding:0 18px}
.chips::-webkit-scrollbar{display:none}
.chips .mini{flex:none;white-space:nowrap}
.chips .mini{padding:8px 14px;font-size:.88rem}
.h-row{gap:10px;align-items:stretch}
.h-row textarea{border-radius:14px;padding:12px 14px;min-height:50px;background:var(--bg);font-size:1rem;line-height:1.4}
.h-row textarea:focus{outline:2px solid var(--accent);outline-offset:0;border-color:transparent}
.h-row .btn{padding:0 22px;border-radius:14px}
.h-toggle{display:flex;align-items:center;gap:10px;font-size:.92rem;color:var(--ink);cursor:pointer}
.h-toggle input{width:20px;height:20px;accent-color:var(--accent);margin:0}
/* settings: each setting is its own card */
.settings{gap:14px}
.set-row{background:var(--bg);border:1px solid var(--line);border-top:1px solid var(--line);border-radius:16px;padding:16px 18px;gap:12px}
.set-l{font-size:1rem}
.settings .seg{background:var(--sheet)}
.set-field select{background:var(--sheet)}
.set-head{padding-bottom:4px}
/* settings: voice fields */
.settings .seg,.settings input[type=range],.set-field{max-width:560px}
.set-field{display:grid;gap:6px;font-size:.92rem;color:var(--muted)}
.set-field select{font:inherit;color:var(--ink);background:var(--bg);border:1px solid var(--line);border-radius:12px;padding:11px 12px;width:100%}
.set-note{margin:0;font-size:.85rem;color:var(--muted);line-height:1.5}
"""
rep('</style>', HELPER_CSS + '</style>')
