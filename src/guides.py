"""Builds the two branded lead-magnet PDFs. Usage: python3 src/guides.py .  (needs playwright + Inter fonts)"""
import sys, html
from playwright.sync_api import sync_playwright

OUT = sys.argv[1]
e = html.escape

CSS = """
@page { size: Letter; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Inter', sans-serif; color: #221E1F; font-size: 10.5pt; line-height: 1.5; }
.page { width: 8.5in; height: 11in; position: relative; overflow: hidden; page-break-after: always; padding: 0.7in 0.75in 0.8in; }
.page:last-child { page-break-after: auto; }
h1, h2, h3, .disp { font-family: 'Inter Display', 'Inter', sans-serif; font-weight: 900; text-transform: uppercase; letter-spacing: -0.01em; line-height: 1.02; }
h2 { font-size: 22pt; margin: 0 0 10pt; }
h2 .y { background: #EBE821; padding: 0 4pt; }
h3 { font-size: 11.5pt; margin: 14pt 0 5pt; letter-spacing: 0.02em; }
p { margin: 0 0 8pt; }
.kicker { font-size: 8pt; font-weight: 700; letter-spacing: 0.18em; text-transform: uppercase; color: #6b6567; margin-bottom: 6pt; display: flex; align-items: center; gap: 8pt; }
.kicker::before { content: ''; width: 22pt; height: 3pt; background: #EBE821; display: inline-block; }
ul { margin: 2pt 0 10pt 14pt; } li { margin-bottom: 4pt; }
.foot { position: absolute; left: 0.75in; right: 0.75in; bottom: 0.4in; display: flex; justify-content: space-between; font-size: 7.5pt; color: #8a8486; border-top: 1px solid #e4e2e2; padding-top: 6pt; }
/* cover */
.cover { background: #221E1F; color: #fff; padding: 0.8in 0.75in; }
.cover .bars { position: absolute; right: -1.2in; top: -0.5in; width: 5in; height: 13in; transform: skewX(-14deg); }
.cover .bars i { position: absolute; top: 0; bottom: 0; }
.cover .bars i:nth-child(1) { left: 0; width: 1.6in; background: #2c2829; }
.cover .bars i:nth-child(2) { left: 2.0in; width: 0.55in; background: #EBE821; }
.cover .bars i:nth-child(3) { left: 2.8in; width: 1.6in; background: #2c2829; }
.brand { display: flex; align-items: center; gap: 10pt; position: relative; }
.mark { width: 30pt; height: 30pt; background: #EBE821; color: #221E1F; font: 900 19pt 'Inter Display'; display: flex; align-items: center; justify-content: center; }
.brand b { font: 800 11pt 'Inter Display'; letter-spacing: 0.06em; text-transform: uppercase; display: block; }
.brand small { color: #EBE821; font-size: 7.5pt; font-weight: 700; letter-spacing: 0.22em; text-transform: uppercase; }
.cover .eyebrow { position: relative; margin-top: 2.3in; color: #EBE821; font-size: 9pt; font-weight: 700; letter-spacing: 0.2em; text-transform: uppercase; }
.cover h1 { position: relative; font-size: 50pt; margin: 12pt 0 16pt; max-width: 5.6in; }
.cover h1 span { color: #EBE821; }
.cover .sub { position: relative; font-size: 13pt; color: #d6d3d3; max-width: 4.6in; line-height: 1.45; }
.cover .inside { position: absolute; z-index: 2; background: #221E1F; left: 0.5in; bottom: 0.6in; right: 0.5in; padding-left: 0.25in; padding-right: 0.25in; padding-bottom: 14pt; border-top: 1px solid #3a3536; padding-top: 14pt; display: flex; gap: 22pt; }
.cover .inside div { flex: 1; font-size: 9pt; color: #d6d3d3; }
.cover .inside b { display: block; color: #fff; font: 800 10pt 'Inter Display'; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 3pt; }
/* blocks */
.stat-row { display: flex; gap: 10pt; margin: 10pt 0 14pt; }
.stat { flex: 1; background: #221E1F; color: #fff; padding: 12pt; }
.stat b { display: block; font: 900 24pt 'Inter Display'; color: #EBE821; line-height: 1; margin-bottom: 4pt; }
.stat span { font-size: 8.5pt; color: #d6d3d3; line-height: 1.35; display: block; }
.box { background: #f6f5f0; border-left: 4pt solid #EBE821; padding: 10pt 12pt; margin: 10pt 0; }
.box b { font-weight: 700; }
.three { display: flex; gap: 10pt; margin: 8pt 0 6pt; }
.three > div { flex: 1; border: 1px solid #e4e2e2; padding: 10pt; }
.three .n { font: 900 9pt 'Inter Display'; color: #221E1F; background: #EBE821; display: inline-block; padding: 1pt 5pt; margin-bottom: 6pt; }
.three h4 { font: 800 10.5pt 'Inter Display'; text-transform: uppercase; margin-bottom: 4pt; }
.three p { font-size: 9pt; margin: 0; }
table { width: 100%; border-collapse: collapse; margin: 6pt 0 10pt; font-size: 9pt; }
th { background: #221E1F; color: #fff; text-align: left; padding: 6pt 7pt; font: 700 8pt 'Inter'; text-transform: uppercase; letter-spacing: 0.06em; }
td { padding: 6pt 7pt; border-bottom: 1px solid #e4e2e2; vertical-align: top; }
td:first-child { font-weight: 700; }
.track td { height: 20pt; }
.cta { background: #221E1F; color: #fff; padding: 16pt 18pt; margin-top: 14pt; }
.cta h3 { color: #EBE821; font-size: 15pt; margin: 0 0 6pt; }
.cta p { color: #d6d3d3; margin: 0 0 4pt; }
.cta .big { color: #fff; font: 800 12pt 'Inter Display'; margin-top: 8pt; }
.disc { font-size: 7.5pt; color: #8a8486; margin-top: 10pt; line-height: 1.4; }
"""

def foot(title, n):
    return f'<div class="foot"><span>{e(title)} · Alloy Personal Training Buckhead</span><span>{n}</span></div>'

def cover(eyebrow, h1, sub, inside):
    ins = "".join(f"<div><b>{e(a)}</b>{e(b)}</div>" for a, b in inside)
    return f"""<section class="page cover"><div class="bars"><i></i><i></i><i></i></div>
<div class="brand"><div class="mark">A</div><div><b>Alloy Personal Training</b><small>Buckhead</small></div></div>
<div class="eyebrow">{e(eyebrow)}</div><h1>{h1}</h1><p class="sub">{e(sub)}</p>
<div class="inside">{ins}</div></section>"""

def workout_table(rows):
    r = "".join(f"<tr><td>{e(a)}</td><td>{e(b)}</td><td>{e(c)}</td><td>{e(d)}</td></tr>" for a, b, c, d in rows)
    return f"<table><tr><th>Move</th><th>Sets × reps</th><th>Easier option</th><th>Coach tip</th></tr>{r}</table>"

def tracker(cols, n=8):
    head = "".join(f"<th>{e(c)}</th>" for c in cols)
    rows = "".join("<tr>" + "".join("<td></td>" for _ in cols) + "</tr>" for _ in range(n))
    return f'<table class="track"><tr>{head}</tr>{rows}</table>'

CTA = """<div class="cta"><h3>Train with a coach in Buckhead</h3>
<p>Every session at Alloy Personal Training Buckhead is coach-led, about 50 minutes, and scaled to your level in a small group. Your first visit starts with a conversation about your goals.</p>
<p class="big">Book a free intro: alloybuckhead.com/book</p>
<p>Call or text 762-245-4442 · 3330 Piedmont Rd NE, Suite 24, Atlanta, GA 30305</p></div>"""

DISC = '<p class="disc">This guide is general education, not medical advice. Talk with your doctor or prescriber before starting a new exercise or nutrition program, especially if you take medication or have a health condition, bone loss or an injury.</p>'

# ---------------- GLP-1 ----------------
T1 = "Strong on a GLP-1"
glp = [
 cover("Free guide", "Strong on a <span>GLP-1</span>",
       "Protect your muscle while you lose weight on Ozempic, Wegovy, Mounjaro or Zepbound.",
       [("Why it matters", "What happens to muscle during fast weight loss"),
        ("The 3 habits", "Strength, protein and tracking the right numbers"),
        ("Your plan", "A twice-weekly starter routine and a progress tracker")]),
 f"""<section class="page"><div class="kicker">Why it matters</div>
<h2>The scale isn't the <span class="y">whole story</span></h2>
<p>GLP-1 medications quiet your appetite, so you eat less and lose weight. That's a real win. But when researchers measure body composition in GLP-1 trials, a meaningful share of the weight lost is lean mass, not just fat.</p>
<div class="stat-row">
<div class="stat"><b>25–40%</b><span>of weight lost showed up as lean mass in GLP-1 trial body-composition studies</span></div>
<div class="stat"><b>2–3×</b><span>strength sessions a week is the most common recommendation to protect muscle</span></div>
<div class="stat"><b>20–30g</b><span>of protein per meal is a practical target many experts suggest</span></div></div>
<p>Lean mass isn't only muscle; it also includes water and organ tissue. But part of it is the muscle you use to climb stairs, carry groceries and catch yourself if you trip. This happens with any fast weight loss, not just medication, and it's largely within your control.</p>
<div class="box"><b>The good news:</b> in studies where people paired a calorie deficit with resistance training, the share of weight lost as lean mass dropped substantially. Training tells your body which tissue to keep.</div>
<h3>Why muscle is worth protecting</h3>
<ul><li>It keeps you strong and independent for everyday tasks.</li>
<li>It supports your joints, balance and fall prevention as you age.</li>
<li>It helps your body manage blood sugar.</li>
<li>It makes it easier to keep weight off once you reach your goal.</li></ul>
<h3>The three habits that make the difference</h3>
<div class="three">
<div><span class="n">01</span><h4>Lift 2–3× a week</h4><p>Work your whole body: legs, hips, back, chest and arms. Challenge matters more than duration.</p></div>
<div><span class="n">02</span><h4>Protein first</h4><p>With a smaller appetite, every meal counts. Eat your protein before anything else on the plate.</p></div>
<div><span class="n">03</span><h4>Track strength</h4><p>If your weights hold steady or climb while the scale drops, you're losing mostly fat.</p></div></div>
{foot(T1, 2)}</section>""",
 f"""<section class="page"><div class="kicker">Your starter plan</div>
<h2>Two workouts. <span class="y">Twice a week.</span></h2>
<p>Alternate Workout A and Workout B on non-consecutive days (for example Monday and Thursday). Rest 60–90 seconds between sets. Choose a weight where the last two reps feel hard but your form stays clean.</p>
<h3>Workout A</h3>
{workout_table([("Squat to a chair","3 × 8–10","Sit-to-stand, hands on thighs","Push through your whole foot"),
("Dumbbell row","3 × 10 each side","Band row","Pull elbow toward your hip"),
("Incline push-up","3 × 8–10","Wall push-up","Body in one straight line"),
("Farmer carry","3 × 30–40 sec","Lighter weights, shorter walk","Stand tall, shoulders down")])}
<h3>Workout B</h3>
{workout_table([("Hip hinge / deadlift","3 × 8–10","Hands-on-hips hinge","Push hips back, flat back"),
("Step-up","3 × 8 each leg","Lower step, hold a rail","Drive through the front heel"),
("Overhead press","3 × 8–10","Seated, lighter dumbbells","Ribs down, exhale as you press"),
("Dead bug","3 × 8 each side","Arms only or legs only","Low back stays on the floor")])}
<h3>On low-energy days</h3>
<ul><li>Do fewer sets rather than skipping the session. Consistency beats intensity.</li>
<li>Eat a little protein and drink water an hour or so before you train.</li>
<li>Feeling queasy? Go lighter, slow down and skip moves that make it worse.</li>
<li>Add weight or reps only when the current load feels manageable for two sessions in a row.</li></ul>
<div class="box"><b>Keep moving between sessions:</b> a daily walk supports your heart and energy. Lifting protects muscle; walking complements it.</div>
{foot(T1, 3)}</section>""",
 f"""<section class="page"><div class="kicker">Protein made easy</div>
<h2>Make protein the <span class="y">first bite</span></h2>
<p>Many experts suggest roughly 0.5–0.7 grams of protein per pound of body weight a day while losing weight, spread across your meals. Ask your prescriber for the target that's right for you. These foods each give you roughly 20 grams or more:</p>
<table><tr><th>Food</th><th>Serving</th><th>About</th></tr>
<tr><td>Chicken or turkey breast</td><td>3 oz cooked</td><td>25g</td></tr>
<tr><td>Cottage cheese</td><td>1 cup</td><td>25g</td></tr>
<tr><td>Salmon or other fish</td><td>3 oz cooked</td><td>20g</td></tr>
<tr><td>Greek yogurt (plain)</td><td>1 cup</td><td>20g</td></tr>
<tr><td>Protein shake</td><td>1 serving</td><td>20–30g</td></tr>
<tr><td>Eggs plus egg whites</td><td>2 eggs + ½ cup whites</td><td>25g</td></tr></table>
<h3>When your appetite is small</h3>
<ul><li>Eat protein first, then vegetables, then everything else.</li>
<li>Choose smaller, more frequent protein snacks if full meals are hard.</li>
<li>A protein shake is an easy backup on days you can't face food.</li></ul>
<h3>Track the right numbers</h3>
<p>Write down one key lift from each workout. The goal: your strength holds or improves while your weight comes down.</p>
{tracker(["Date","Body weight","Squat / step-up","Row","Push-up / press","Energy (1–10)"], 2)}
{CTA}{DISC}{foot(T1, 4)}</section>"""
]

# ---------------- Menopause ----------------
T2 = "Strong Through Menopause"
meno = [
 cover("Free guide", "Strong Through <span>Menopause</span>",
       "Weight training for muscle, bone and energy through perimenopause, menopause and beyond.",
       [("Why it matters", "What falling estrogen does to muscle and bone"),
        ("What works", "The kind of training bone actually responds to"),
        ("Your plan", "A twice-weekly routine, how heavy to go and a tracker")]),
 f"""<section class="page"><div class="kicker">Why it matters</div>
<h2>Less estrogen. <span class="y">More strength.</span></h2>
<p>As estrogen declines, women lose muscle and bone faster than before. That affects strength, metabolism, balance and the risk of fractures. Your body still responds to training at every age, and lifting is one of the most effective ways to push back.</p>
<div class="stat-row">
<div class="stat"><b>~10%</b><span>average loss of lower-spine bone density over the 10-year SWAN study, much of it around menopause</span></div>
<div class="stat"><b>~3 yrs</b><span>window of fastest bone loss: from about a year before the final period to two years after</span></div>
<div class="stat"><b>2×</b><span>weekly supervised sessions improved spine and hip bone density in the LIFTMOR trial</span></div></div>
<h3>Why lifting beats gentler exercise for bone</h3>
<p>Walking, yoga and swimming are great for your health, but on their own they don't give bone much reason to get stronger. Bone responds to load: challenging resistance and some impact.</p>
<div class="box"><b>The LIFTMOR trial:</b> postmenopausal women with low bone mass did two supervised 30-minute sessions a week of high-intensity resistance and impact training for eight months. Their spine and hip bone density improved compared with a gentler home program, and no fractures were reported. The key was close supervision and gradual progression.</div>
<h3>What a good plan includes</h3>
<div class="three">
<div><span class="n">01</span><h4>Real challenge</h4><p>Weights where the last two reps of each set take real effort, not light weights for endless reps.</p></div>
<div><span class="n">02</span><h4>Progression</h4><p>Add a little weight or a few reps as you get stronger, week after week.</p></div>
<div><span class="n">03</span><h4>Impact &amp; balance</h4><p>Small hops or heel drops if your doctor agrees, plus balance work to prevent falls.</p></div></div>
{foot(T2, 2)}</section>""",
 f"""<section class="page"><div class="kicker">Your starter plan</div>
<h2>Two workouts. <span class="y">Twice a week.</span></h2>
<p>Alternate Workout A and Workout B on non-consecutive days. Rest 90 seconds between sets. Start lighter for the first two weeks while you learn the moves, then build up.</p>
<h3>Workout A</h3>
{workout_table([("Goblet squat","3 × 8","Sit-to-stand from a chair","Chest tall, knees track over toes"),
("Dumbbell row","3 × 8 each side","Band row","Squeeze shoulder blade back"),
("Push-up","3 × 6–10","Incline or wall push-up","Lower slowly, one straight line"),
("Heel drops","3 × 10","Rise onto toes, lower slowly","Only if cleared for impact")])}
<h3>Workout B</h3>
{workout_table([("Romanian deadlift","3 × 8","Hip hinge with a dowel","Hips back, weights close to legs"),
("Split squat","3 × 8 each leg","Hold a rail, shorter range","Front heel stays down"),
("Overhead press","3 × 8","Seated, lighter dumbbells","Ribs down, exhale as you press"),
("Single-leg balance","3 × 20–30 sec each","Fingertips on a wall","Soft knee, eyes on one spot")])}
<h3>How heavy should it feel?</h3>
<table><tr><th>Effort 1–10</th><th>What it feels like</th><th>When to use it</th></tr>
<tr><td>5–6</td><td>Could do 4–5 more reps</td><td>Weeks 1–2, learning the moves</td></tr>
<tr><td>7–8</td><td>Could do 2–3 more reps</td><td>Most of your training</td></tr>
<tr><td>9</td><td>One more rep, maybe</td><td>Occasionally, with a coach watching</td></tr></table>
{foot(T2, 3)}</section>""",
 f"""<section class="page"><div class="kicker">Common worries, answered</div>
<h2>Lift with <span class="y">confidence</span></h2>
<h3>"Won't I get bulky?"</h3>
<p>Building large muscles takes years of very specific training and eating. For most women, lifting creates a stronger, firmer and more capable body.</p>
<h3>"Is it safe if I have low bone density?"</h3>
<p>Supervised, progressive training has been studied in women with low bone mass with good results. Talk with your doctor first, and work with a coach who builds you up gradually.</p>
<h3>"What about leaking or pelvic pressure?"</h3>
<p>Exhale as you lift and don't hold your breath. If symptoms continue, a pelvic floor physical therapist can help, and you can keep training while you work on it.</p>
<h3>Support your training</h3>
<ul><li><b>Protein at every meal:</b> it gives your muscles what they need to rebuild after training.</li>
<li><b>Sleep and recovery:</b> leave a day between strength sessions and protect your sleep when you can.</li>
<li><b>Keep walking:</b> it supports your heart and mood alongside your lifting.</li></ul>
<h3>Track your progress</h3>
{tracker(["Date","Squat","Deadlift","Row","Press","Energy (1–10)"], 6)}
{CTA}{DISC}{foot(T2, 4)}</section>"""
]

def build(pages, title, fname, pw):
    doc = f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>{e(title)}</title><style>{CSS}</style></head><body>{''.join(pages)}</body></html>"
    pass
    pg = pw.new_page()
    pg.set_content(doc)
    pg.pdf(path=f"{OUT}/{fname}.pdf", format="Letter", print_background=True, prefer_css_page_size=True)
    pg.close()

with sync_playwright() as p:
    b = p.chromium.launch()
    build(glp, "Strong on a GLP-1 | Alloy Personal Training Buckhead", "strong-on-a-glp-1", b)
    build(meno, "Strong Through Menopause | Alloy Personal Training Buckhead", "strong-through-menopause", b)
    b.close()
print("ok")
