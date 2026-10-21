# Build step (exec'd last): one alignment rule everywhere when both languages are shown.
# Hebrew keeps right-to-left reading (punctuation stays correct) but lines up on the same
# left edge as the English above it, so nothing zig-zags left/right.
def rep(old, new):
    global s
    assert old in s, old[:80]
    s = s.replace(old, new, 1)

ALIGN_CSS = r'''
/* ===== alignment: one edge for both languages ===== */
body.m-both .he,body.m-both [dir="rtl"]:not(.msg):not(.msg *){text-align:left!important}
body.m-both .hero-text{grid-template-columns:1fr!important;row-gap:6px}
body.m-both .hero-text>*{grid-column:1!important;grid-row:auto!important}
body.m-both .subj-head{flex-direction:column;align-items:flex-start;gap:2px}
body.m-both .hero-text h1.en{margin-bottom:0}
body.m-both .hero-text p.he{margin-top:-2px}
/* settings: every control fills its card, so all right edges line up */
.set-row .seg,.set-row select,.set-row .set-field,.settings select,.settings .set-field,.set-row input[type=range]{max-width:none!important;width:100%!important;box-sizing:border-box}
/* lesson timer boxes: equal size, text on the same edge */
.blocks{grid-template-columns:repeat(2,minmax(0,1fr))!important}
.blocks>*{text-align:left;justify-content:flex-start;align-items:center}
'''
rep('</style>', ALIGN_CSS + '</style>')
