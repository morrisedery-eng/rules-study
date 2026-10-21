# Build step (exec'd from build_offline.py with `s` and `D` in scope):
# plan card, 60-minute study (10/40/10), untimed end-of-day quiz.
import re
for old, new in [
  ('const SEGS=[{m:10,en:"Review",he:"חזרה"},{m:30,en:"Learn",he:"לימוד"},{m:10,en:"Flashcards",he:"כרטיסיות"},{m:10,en:"Quiz",he:"בוחן"}];',
   'const SEGS=[{m:10,en:"Review",he:"חזרה"},{m:40,en:"Learn",he:"לימוד"},{m:10,en:"Flashcards",he:"כרטיסיות"}];'),
  ('.blocks{display:grid;grid-template-columns:1fr 3fr 1fr 1fr;gap:4px}', '.blocks{display:grid;grid-template-columns:1fr 3fr 1fr;gap:4px}'),
  ('@media (max-width:560px){.blocks{grid-template-columns:1fr 1fr}}', '@media (max-width:560px){.blocks{grid-template-columns:1fr 1.5fr 1fr}}'),
  ('<h3>2 · Learn · לימוד</h3><span class="mins">30 min</span>', '<h3>2 · Learn · לימוד</h3><span class="mins">rest of the hour</span>'),
  ('<h3>1 · Review · חזרה</h3><span class="mins">10 min</span>', '<h3>1 · Review · חזרה</h3><span class="mins">a few min</span>'),
  ('One hour a day. Each session: 10 min review, 30 min new material, 10 min flashcards, 10 min quiz.',
   'One hour a day: a short review (only as long as it takes), new material, and 10 min of flashcards at the end. Then an end-of-day quiz with your grade (not counted in the hour).'),
  ('שעה אחת ביום. כל מפגש: 10 דק׳ חזרה, 30 דק׳ חומר חדש, 10 דק׳ כרטיסיות, 10 דק׳ בוחן.',
   'שעה אחת ביום: חזרה קצרה (רק כמה שצריך), חומר חדש, ו-10 דק׳ כרטיסיות בסוף. אחר כך בוחן סוף יום עם ציון (לא נכלל בשעה).'),
  ('const sheet=document.getElementById("sheet");sheet.innerHTML=h;',
   'const sheet=document.getElementById("sheet");sheet.innerHTML=h;\n  {const qs=document.getElementById("qstart");if(qs)qs.onclick=startDayQuiz;wireSound();const sd=document.getElementById("startday");if(sd){sd.onclick=()=>{if(!run&&left>0)document.getElementById("tstart").click()};if(run)sd.textContent="⏱ Studying… · בלימוד…"}}'),
]:
    assert old in s, old[:50]
    s = s.replace(old, new)

s, n = re.subn(r'  // Quiz\n.*?(?=  h\+=`<div class="foot">)',
               lambda m: '  // End-of-day quiz (not timed)\n  h+=`<div class="sec part" id="part-3">${quizIntroHTML()}</div>`;\n',
               s, flags=re.S)
assert n == 1

PLAN = ("  h+=`<div class=\"sec plan\"><span class=\"label\">Today's plan · התוכנית להיום</span>"
        "<div class=\"bi\">${bi({en:`Today you'll study <b>${d.t.en}</b> for 60 minutes: a short Review (only as long as it takes), Learn (the rest of the time) and Flashcards (the last 10 min). "
        "When the hour is over, the end-of-day quiz starts by itself. It isn't part of the 60 minutes.`,"
        "he:`היום תלמדו <b>${d.t.he}</b> במשך 60 דקות: חזרה קצרה (רק כמה שצריך), לימוד (שאר הזמן) וכרטיסיות (10 הדקות האחרונות). "
        "כשהשעה נגמרת, בוחן סוף היום מתחיל לבד. הוא לא חלק מ-60 הדקות.`},\"p\")}</div>"
        "<p class=\"ex\">Key topics · נושאים עיקריים: ${d.cards.map(c=>c.en).join(\" · \")}</p>"
        "<div class=\"tools\"><button type=\"button\" class=\"btn\" id=\"startday\">▶ Start today's hour · התחל את שעת הלימוד</button></div></div>`;\n")
m = re.search(r'  let h=`<div class="sec"><span class="label">Day \$\{cur\+1\} of .*?</div></div>`;\n', s)
assert m
s = s[:m.end()] + PLAN + s[m.end():]

CSS = """.btn.ghost{background:none;color:var(--accent)}
.wrap{padding-bottom:96px}
.plan{background:var(--chip);border-radius:14px;padding:14px}
.qbar{height:6px;background:var(--chip);border-radius:3px;overflow:hidden}.qbar div{height:100%;background:var(--accent)}
.verdict{font-weight:700;font-size:1.15rem;padding:8px 12px;border-radius:10px}
.verdict.good{color:var(--good);background:color-mix(in srgb,var(--good) 12%,transparent)}
.verdict.bad{color:var(--bad);background:color-mix(in srgb,var(--bad) 12%,transparent)}.verdict span{font-weight:500;font-size:.95rem}
.grade{display:flex;align-items:baseline;gap:14px;padding:14px;border-radius:14px;background:var(--chip)}
.grade .big{font-family:var(--display);font-size:3rem;line-height:1}.grade.good .big{color:var(--good)}.grade.bad .big{color:var(--bad)}"""
assert ".btn.ghost{background:none;color:var(--accent)}" in s
s = s.replace(".btn.ghost{background:none;color:var(--accent)}", CSS, 1)

# --- coach overlay (step-by-step lesson during the hour) ---
COACH_HTML = """
<section id="coach" hidden aria-label="Guided lesson">
  <div class="c-top">
    <div class="c-head"><span class="label" id="c-part"></span><div class="c-clock" id="c-clock">60:00</div></div>
    <div class="c-ctl">
      <button type="button" class="mini" id="c-pause">⏸ Pause · השהה</button>
      <button type="button" class="mini" id="c-skip">Next part · החלק הבא</button>
      <button type="button" class="mini" id="c-close">Close · סגור</button>
    </div>
    <div class="qbar"><div id="c-prog"></div></div>
  </div>
  <div class="c-body" id="c-body"></div>
  <div class="c-foot" id="c-foot"></div>
</section>
"""
assert '<button class="fab"' in s
s = s.replace('<button class="fab"', COACH_HTML + '<button class="fab"', 1)
old = '<button class="btn ghost" id="tnext" type="button" hidden>'
assert old in s
s = s.replace(old, '<button class="btn" id="c-open" type="button" hidden>Open lesson · פתח שיעור</button>\n        ' + old, 1)
COACH_CSS = """
#coach{position:fixed;inset:0;z-index:40;background:var(--bg);display:flex;flex-direction:column;
  padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
#coach .c-top{display:grid;gap:8px;padding:12px max(16px,env(safe-area-inset-left,0px)) 10px max(16px,env(safe-area-inset-right,0px));background:var(--sheet);border-bottom:1px solid var(--line)}
#coach .c-head{display:flex;justify-content:space-between;align-items:center;gap:10px}
#coach .c-clock{font-family:var(--mono);font-size:1.4rem;font-variant-numeric:tabular-nums;font-weight:500}
#coach .c-ctl{display:flex;flex-wrap:wrap;gap:6px}
#coach .c-body{flex:1;overflow-y:auto;padding:18px max(16px,env(safe-area-inset-left,0px)) 18px max(16px,env(safe-area-inset-right,0px));display:grid;gap:14px;align-content:start;max-width:760px;width:100%;margin:0 auto}
#coach .c-foot{padding:10px max(16px,env(safe-area-inset-left,0px)) 14px max(16px,env(safe-area-inset-right,0px));background:var(--sheet);border-top:1px solid var(--line)}
#coach .c-nav{display:flex;gap:10px;justify-content:space-between;max-width:760px;margin:0 auto}
#coach .c-nav .btn{flex:1;padding:12px 10px;font-size:1rem}
#coach .btn.good{background:var(--good);border-color:var(--good);color:#fff}
#coach .btn.bad{color:var(--bad);border-color:var(--bad)}
#coach .c-big{font-size:1.18rem;line-height:1.6}
#coach .c-box{background:var(--sheet);border:1px solid var(--line);border-radius:12px;padding:12px;display:grid;gap:6px}
#coach .c-box.tip{border-color:var(--mark)}
#coach .c-hint{background:var(--sheet);border-radius:12px;padding:12px;color:var(--muted)}
#coach .c-count{font-family:var(--mono);font-size:2.6rem;text-align:center;color:var(--accent);font-variant-numeric:tabular-nums}
#coach .c-count:empty{display:none}
#coach .c-card{background:var(--sheet);border:2px solid var(--accent);border-radius:16px;padding:22px 16px;text-align:center;display:grid;gap:14px}
#coach .c-q{font-size:1.35rem;font-weight:600}
#coach .c-a{font-size:1.2rem;color:var(--good);border-top:1px dashed var(--line);padding-top:12px}
#coach .c-center{text-align:center;padding-top:15vh}
#coach .c-peek summary{cursor:pointer;color:var(--accent)}
body.coach-on{overflow:hidden}body.coach-on .fab{display:none}
body.m-both #coach h2 span.he,body.m-both #coach .ex span.he,body.m-both #coach summary span.he,body.m-both #coach b span.he{display:block}
#coach h2{display:grid;gap:4px}
"""
s = s.replace(".plan{background:var(--chip);border-radius:14px;padding:14px}", ".plan{background:var(--chip);border-radius:14px;padding:14px}" + COACH_CSS, 1)
assert "#coach{position:fixed" in s
