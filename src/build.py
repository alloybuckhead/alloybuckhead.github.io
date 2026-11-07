#!/usr/bin/env python3
"""Static site builder for Alloy Personal Training Buckhead.

Usage: python3 src/build.py   (run from the repo root)
Reads src/site.json and src/posts.json, writes the site to the repo root:
index.html, blog/index.html, blog/<slug>/index.html, sitemap.xml, robots.txt,
404.html, style.css, CNAME (if custom_domain set), .nojekyll.

To add a post: insert a new object at the TOP of src/posts.json, then rebuild.
"""
import json, os, shutil, html, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
S = json.load(open(os.path.join(SRC, "site.json")))
POSTS = json.load(open(os.path.join(SRC, "posts.json")))
POSTS.sort(key=lambda p: p["date"], reverse=True)
PAGES = json.load(open(os.path.join(SRC, "pages.json")))

BASE = ("https://" + S["custom_domain"]) if S.get("custom_domain") else S["base_url"].rstrip("/")
e = lambda t: html.escape(str(t), quote=True)


def fmt(d):
    dt = datetime.date.fromisoformat(d)
    return dt.strftime("%B ") + str(dt.day) + dt.strftime(", %Y")


def excerpt(p):
    return p.get("dek") or next((b["p"] for b in p["body"] if "p" in b), "")


def book(campaign):
    """Booking link tagged so GoHighLevel shows which page/button the lead came from."""
    sep = "&" if "?" in S["booking_url"] else "?"
    return f"{S['booking_url']}{sep}utm_source=alloybuckhead.com&utm_medium=website&utm_campaign={campaign}"


def guide(campaign):
    """Link to the Longevity Strength Guide page, tagged so GoHighLevel shows where the lead came from."""
    return f"/guide/?utm_source=alloybuckhead.com&utm_medium=website&utm_campaign={campaign}"


def guide_cta(campaign, cls="post-cta guide-cta"):
    return (f'<div class="{cls}"><div><b>Free: The Longevity Strength Guide</b>'
            f'<p>Simple strength habits to stay strong, steady and independent for decades.</p></div>'
            f'<a class="btn" href="{guide(campaign)}">Get the Free Guide</a></div>')


def ext(url, label, cls="btn"):
    return f'<a class="{cls}" href="{e(url)}" target="_blank" rel="noopener">{label}</a>'


def page(title, desc, path, body, jsonld=None, og_type="website"):
    canon = BASE + path
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(canon)}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(canon)}">
<meta property="og:site_name" content="{e(S['name'])}">
<meta name="twitter:card" content="summary">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' fill='%23EBE821'/%3E%3Ctext x='16' y='23' font-family='Arial' font-weight='900' font-size='20' text-anchor='middle' fill='%23221E1F'%3EA%3C/text%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;800;900&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css">
{ld}
</head>
<body>
<header class="nav"><div class="wrap">
  <a class="brand" href="/"><span class="brand-mark">A</span><span class="brand-name">Alloy Personal Training<small>Buckhead</small></span></a>
  <nav class="links"><a href="/">Home</a><a href="/blog/">Blog</a><a href="/guide/">Free Guide</a><a href="/#visit">Visit</a>{ext(book('nav'), 'Book an Intro', 'btn sm')}</nav>
</div></header>
{body}
<footer><div class="wrap">
  <div>© {datetime.date.today().year} {e(S['name'])} · {e(S['street'])}, {e(S['city'])}, {e(S['region'])} {e(S['postal'])} · <a href="tel:{e(S['phone_e164'])}">{e(S['phone'])}</a></div>
  <div class="foot-links"><b>Training in Buckhead</b>{''.join(f'<a href="/{e(x["slug"])}/">{e(x["title"])}</a>' for x in PAGES)}</div>
  <div class="disc">Blog content is for general education and isn't medical advice. Talk with your doctor before starting a new exercise or nutrition program.</div>
</div></footer>
<div class="sticky-cta">{ext(book('sticky-mobile'), 'Book Free Intro')}<a class="btn ghost" href="sms:{e(S['phone_e164'])}">Text Us</a><a class="btn ghost" href="tel:{e(S['phone_e164'])}">Call</a></div>
</body>
</html>
"""


def card(p):
    return f"""<a class="post-card" data-cat="{e(p['category'])}" href="/blog/{e(p['slug'])}/"><div class="bar"></div><div class="body">
    <span class="tag">{e(p['category'])} · {fmt(p['date'])}</span>
    <h3>{e(p['title'])}</h3><p>{e(excerpt(p))}</p><span class="more">Read post →</span></div></a>"""


BUSINESS = {
    "@context": "https://schema.org", "@type": "HealthClub", "name": S["name"],
    "description": S["description"], "url": BASE + "/", "telephone": S["phone_e164"],
    "address": {"@type": "PostalAddress", "streetAddress": S["street"], "addressLocality": S["city"],
                "addressRegion": S["region"], "postalCode": S["postal"], "addressCountry": "US"},
    "areaServed": "Buckhead, Atlanta, GA",
}


def home():
    latest = "".join(card(p) for p in POSTS[:3]) or '<p class="empty">First post coming soon.</p>'
    body = f"""<main>
  <section class="hero" style="padding:0">
    <div class="hero-bars" aria-hidden="true"><i></i><i></i><i></i></div>
    <div class="wrap">
      <div class="eyebrow">Members-only small-group training · Buckhead, Atlanta</div>
      <h1>Strength for <span>every</span> decade.</h1>
      <p class="lede">45-minute, coach-led personal training sessions in Buckhead built around you — whether you're 25 or 75, brand new or getting back to it. Small groups. Real coaching. Results that last.</p>
      <div class="ctas">{ext(book('home-hero'), 'Book Your Intro Session')}<a class="btn ghost" href="/blog/">Read the Blog</a></div>
    </div>
  </section>
  <div class="stats"><div class="wrap">
    <div class="stat"><b>45</b><span>Minute sessions</span></div>
    <div class="stat"><b>150</b><span>Member cap</span></div>
    <div class="stat"><b>30+</b><span>Years of Alloy</span></div>
    <div class="stat"><b>100%</b><span>Coach-led</span></div>
  </div></div>
  <section><div class="wrap">
    <div class="sec-head"><div class="kicker">The Alloy difference</div>
      <h2>Personal training, without the personal-training price.</h2>
      <p>Every session is led by a certified coach and scaled to your level — so you get the attention of one-on-one training with the energy of a small group.</p></div>
    <div class="grid3">
      <div class="card"><span class="num">01</span><h3>Small groups</h3><p>Coaches know your name, your goals, and your limits. Nobody gets lost in the crowd.</p></div>
      <div class="card"><span class="num">02</span><h3>Customized</h3><p>Every workout is adjusted for your fitness level, history and goals — not a one-size class.</p></div>
      <div class="card"><span class="num">03</span><h3>Members only</h3><p>Membership is capped at 150, so the studio stays personal and coaching stays hands-on.</p></div>
    </div>
  </div></section>
  <section class="who"><div class="wrap">
    <div class="sec-head"><div class="kicker">Who we train</div><h2>Built for real schedules and real lives.</h2></div>
    <div class="grid3">
      <div class="card"><h3>Busy professionals</h3><p>Efficient 45-minute sessions that fit before work, at lunch, or after the day is done.</p></div>
      <div class="card"><h3>Moms</h3><p>Rebuild strength and energy with coaching that respects where you are right now.</p></div>
      <div class="card"><h3>Active agers</h3><p>Strength, balance and mobility training to keep you doing what you love for decades.</p></div>
    </div>
  </div></section>
  <section class="how"><div class="wrap">
    <div class="sec-head"><div class="kicker">How it works</div><h2>Getting started is simple.</h2>
      <p>No intimidation, no guesswork. Here's what your first steps look like.</p></div>
    <div class="grid3">
      <div class="card"><span class="num">STEP 1</span><h3>Book an intro</h3><p>Meet a coach, tour the studio and talk through your goals.</p></div>
      <div class="card"><span class="num">STEP 2</span><h3>Get your plan</h3><p>We assess where you're starting and map out the right membership for you.</p></div>
      <div class="card"><span class="num">STEP 3</span><h3>Train &amp; progress</h3><p>Show up, get coached, and watch your strength build week over week.</p></div>
    </div>
  </div></section>
  <section><div class="wrap">
    <div class="sec-head"><div class="kicker">From the blog</div><h2>Latest from the studio.</h2>
      <p>Practical tips on strength, longevity, nutrition and staying consistent — new posts every day.</p></div>
    <div class="posts">{latest}</div>
    <div style="margin-top:32px"><a class="btn" href="/blog/" style="background:var(--char);color:var(--white)">See All Posts</a></div>
  </div></section>
  <section style="padding:0 0 72px"><div class="wrap">{guide_cta('home-guide')}</div></section>
  <section class="visit" id="visit"><div class="wrap inner">
    <div><div class="kicker">Visit the studio</div>
      <h2 class="display" style="font-size:clamp(32px,4.5vw,52px);font-weight:900;text-transform:uppercase">Your first session starts with a conversation.</h2>
      <p style="color:var(--muted);margin-top:16px;font-size:17px">Stop by, meet the coaches and see if {e(S['name'])} is the right fit. Spots are limited — membership is capped at 150.</p></div>
    <div class="addr"><h3>{e(S['name'])}</h3>
      <p>{e(S['street'])}<br>{e(S['city'])}, {e(S['region'])} {e(S['postal'])}</p>
      <p style="font:800 22px Archivo;color:var(--yellow);margin-bottom:24px"><a href="tel:{e(S['phone_e164'])}" style="text-decoration:none">{e(S['phone'])}</a></p>
      <div style="display:flex;gap:12px;flex-wrap:wrap">{ext(book('home-visit'), 'Book Online')}<a class="btn ghost" href="tel:{e(S['phone_e164'])}">Call to Book</a>{ext(S['maps_url'], 'Get Directions', 'btn ghost')}</div>
    </div>
  </div></section>
</main>"""
    return page(f"{S['name']} | Small-Group Personal Training in Buckhead, Atlanta", S["description"], "/", body, BUSINESS)


def blog_index():
    cats = ["All"] + sorted({p["category"] for p in POSTS})
    btns = "".join(f'<button class="{"on" if c == "All" else ""}" data-cat="{e(c)}">{e(c)}</button>' for c in cats)
    cards = "".join(card(p) for p in POSTS) or '<p class="empty">No posts yet.</p>'
    body = f"""<main>
  <div class="blog-hero"><div class="wrap"><div class="eyebrow">The Alloy Blog</div><h1>Stronger every day.</h1>
    <p>Daily, no-fluff advice from {e(S['name'])} on training, longevity, nutrition and habits that stick.</p></div></div>
  <div class="wrap"><div class="filters" id="filters">{btns}</div><div class="posts" id="all-posts">{cards}</div><div style="height:96px"></div></div>
</main>
<script>
document.querySelectorAll('#filters button').forEach(function(b){{b.addEventListener('click',function(){{
  document.querySelectorAll('#filters button').forEach(function(x){{x.classList.toggle('on',x===b)}});
  var c=b.dataset.cat;document.querySelectorAll('#all-posts .post-card').forEach(function(p){{p.style.display=(c==='All'||p.dataset.cat===c)?'':'none'}});
}})}});
</script>"""
    return page(f"Blog | {S['name']}", f"Daily strength, longevity, nutrition and habit tips from {S['name']} in Atlanta.", "/blog/", body)


def post_page(p):
    parts = []
    for b in p["body"]:
        if "h" in b: parts.append(f"<h2>{e(b['h'])}</h2>")
        elif "ul" in b: parts.append("<ul>" + "".join(f"<li>{e(i)}</li>" for i in b["ul"]) + "</ul>")
        else: parts.append(f"<p>{e(b['p'])}</p>")
    ld = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"], "description": p.get("dek", ""),
          "datePublished": p["date"], "dateModified": p["date"], "mainEntityOfPage": f"{BASE}/blog/{p['slug']}/",
          "author": {"@type": "Organization", "name": S["name"]},
          "publisher": {"@type": "Organization", "name": S["name"]}}
    body = f"""<main><article class="post">
  <a class="back" href="/blog/">← All posts</a>
  <div class="meta"><span class="tag">{e(p['category'])}</span><span class="tag"><time datetime="{e(p['date'])}">{fmt(p['date'])}</time></span></div>
  <h1>{e(p['title'])}</h1><p class="dek">{e(p.get('dek',''))}</p>
  {''.join(parts)}
  {guide_cta('blog-' + p['slug'])}
  <div class="post-cta"><b>Ready to train with a coach?</b>{ext(book('blog-' + p['slug']), 'Book Your Intro')}</div>
</article></main>"""
    return page(f"{p['title']} | {S['name']}", excerpt(p), f"/blog/{p['slug']}/", body, ld, "article")


def landing(pg):
    parts = []
    for s in pg["sections"]:
        parts.append(f"<h2>{e(s['h'])}</h2>")
        for para in s.get("p", []): parts.append(f"<p>{e(para)}</p>")
        if s.get("ul"): parts.append("<ul>" + "".join(f"<li>{e(i)}</li>" for i in s["ul"]) + "</ul>")
    faq = "".join(f"<details class=\"faq\"><summary>{e(f['q'])}</summary><p>{e(f['a'])}</p></details>" for f in pg["faq"])
    latest = "".join(card(p) for p in POSTS[:3])
    ld = [dict(BUSINESS, url=BASE + "/"),
          {"@context": "https://schema.org", "@type": "FAQPage",
           "mainEntity": [{"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in pg["faq"]]}]
    body = f"""<main>
  <section class="hero" style="padding:0">
    <div class="hero-bars" aria-hidden="true"><i></i><i></i><i></i></div>
    <div class="wrap">
      <div class="eyebrow">{e(pg['eyebrow'])}</div>
      <h1 style="max-width:16ch">{e(pg['headline'])}</h1>
      <p class="lede">{e(pg['lede'])}</p>
      <div class="ctas">{ext(book('page-' + pg['slug']), 'Book Your Free Intro')}<a class="btn ghost" href="sms:{e(S['phone_e164'])}">Text Us</a></div>
    </div>
  </section>
  <article class="post" style="padding-top:56px">
    <h1 style="font-size:clamp(28px,4vw,40px)">{e(pg['title'])}</h1>
    {''.join(parts)}
    {guide_cta('page-' + pg['slug'])}
    <h2>Frequently asked questions</h2>
    {faq}
    <div class="post-cta"><b>Start with a free intro session</b>{ext(book('page-' + pg['slug'] + '-bottom'), 'Book Your Free Intro')}</div>
  </article>
  <section class="who" style="padding:64px 0"><div class="wrap">
    <div class="sec-head"><div class="kicker">From the blog</div><h2>Tips from our coaches.</h2></div>
    <div class="posts">{latest}</div>
  </div></section>
</main>"""
    return page(f"{pg['title']} | {S['name']}", pg["meta"], f"/{pg['slug']}/", body, ld)


def guide_page():
    fid, host = S["guide_form_id"], S["form_host"]
    body = f"""<main>
  <section class="hero" style="padding:0">
    <div class="hero-bars" aria-hidden="true"><i></i><i></i><i></i></div>
    <div class="wrap">
      <div class="eyebrow">Free guide · {e(S['name'])}</div>
      <h1 style="max-width:16ch">The Longevity Strength Guide.</h1>
      <p class="lede">Practical strength training for adults who want to stay strong, steady and independent for decades. Tell us where to send it and it's yours, free.</p>
    </div>
  </section>
  <section style="padding:56px 0 96px"><div class="wrap guide-grid">
    <div>
      <div class="kicker">What's inside</div>
      <h2 class="display" style="font:900 clamp(28px,3.5vw,40px) Archivo;text-transform:uppercase;margin:12px 0 16px">Strength for every decade.</h2>
      <ul class="guide-list">
        <li>Why strength is the foundation of healthy aging</li>
        <li>How to start safely, whatever your age or fitness level</li>
        <li>Simple habits that build strength, balance and confidence</li>
      </ul>
      <p style="color:var(--muted);margin-top:20px">From the coaches at {e(S['name'])}, {e(S['street'])}, {e(S['city'])}, {e(S['region'])}.</p>
    </div>
    <div class="guide-form">
      <iframe src="{host}/widget/form/{fid}" style="width:100%;height:924px;border:none;border-radius:8px"
        id="inline-{fid}" data-layout="{{'id':'INLINE'}}" data-trigger-type="alwaysShow" data-trigger-value=""
        data-activation-type="alwaysActivated" data-activation-value="" data-deactivation-type="neverDeactivate"
        data-deactivation-value="" data-form-name="Longevity Strength Guide" data-height="924"
        data-layout-iframe-id="inline-{fid}" data-form-id="{fid}" data-cookie-consent="true"
        data-cookie-consent-provider="auto" title="Longevity Strength Guide"></iframe>
      <script src="{host}/js/form_embed.js"></script>
    </div>
  </div></section>
</main>"""
    return page(f"Free Longevity Strength Guide | {S['name']}",
                f"Get the free Longevity Strength Guide from {S['name']}: practical strength training to stay strong, steady and independent as you age.",
                "/guide/", body)


def write(rel, text):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(text)


def main():
    slugs = [p["slug"] for p in POSTS]
    assert len(slugs) == len(set(slugs)), "duplicate slug in posts.json"
    blog_dir = os.path.join(ROOT, "blog")
    if os.path.isdir(blog_dir): shutil.rmtree(blog_dir)
    shutil.copy(os.path.join(SRC, "style.css"), os.path.join(ROOT, "style.css"))
    write("index.html", home())
    write("blog/index.html", blog_index())
    for p in POSTS: write(f"blog/{p['slug']}/index.html", post_page(p))
    for pg in PAGES:
        d = os.path.join(ROOT, pg["slug"])
        if os.path.isdir(d): shutil.rmtree(d)
        write(f"{pg['slug']}/index.html", landing(pg))
    write("guide/index.html", guide_page())
    write("404.html", page(f"Page not found | {S['name']}", S["description"], "/404.html",
          '<main><article class="post"><h1>Page not found.</h1><p>That page doesn\'t exist. <a href="/">Go home</a> or <a href="/blog/">read the blog</a>.</p></article></main>'))
    today = datetime.date.today().isoformat()
    urls = [("/", today), ("/blog/", POSTS[0]["date"] if POSTS else today)] + [("/guide/", today)] + [(f"/{pg['slug']}/", today) for pg in PAGES] + [(f"/blog/{p['slug']}/", p["date"]) for p in POSTS]
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
          "".join(f"  <url><loc>{BASE}{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls) + "</urlset>\n")
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
    fwd = S["booking_url"]
    book_html = ('<!DOCTYPE html><html><head><meta charset="utf-8"><title>Book Your Intro | ' + e(S["name"]) + '</title><meta name="robots" content="noindex">'
                 '<script>var u=' + json.dumps(fwd) + ';var q=location.search.slice(1);'
                 'if(!/utm_source=/.test(q)){q=(q?q+"&":"")+"utm_source=direct&utm_medium=short-link&utm_campaign=book"}'
                 'location.replace(u+(u.indexOf("?")<0?"?":"&")+q);</script>'
                 '<noscript><meta http-equiv="refresh" content="0; url=' + e(fwd) + '"></noscript></head>'
                 '<body><a href="' + e(fwd) + '">Book your intro session</a></body></html>')
    write("book/index.html", book_html)
    write(".nojekyll", "")
    cname = os.path.join(ROOT, "CNAME")
    if S.get("custom_domain"): write("CNAME", S["custom_domain"] + "\n")
    elif os.path.exists(cname): os.remove(cname)
    print(f"Built {len(POSTS)} posts → {BASE}")


if __name__ == "__main__":
    main()
