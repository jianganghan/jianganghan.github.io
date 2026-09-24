#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Render one social card per page: the picture X, LinkedIn, WeChat and Slack show
when someone shares a link.

    python3 make-cards.py            # render every card
    python3 make-cards.py --missing  # only the ones that aren't there yet

Why this is not part of build.py: rendering needs a browser, and build.py is
deliberately standard library only. Run this when you add a post, then run
build.py, which picks up whatever cards exist and warns about the ones missing.

The card leads with the post's title, because that is what a stranger scrolling
past needs in order to decide whether to click. The name is a byline. The two
home pages keep the site-wide card instead, where "who is this" is the point.
"""
import html, os, re, subprocess, sys
import build   # the site's own notion of paths, languages and titles

CHROME   = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CARD_DIR = "assets/og"
W, H     = 1200, 630

# "> **Ad Bidding · Part 1 of 3** · 8 min read" — the author already writes this
# line at the top of every post, so the card takes it rather than inventing one.
NAV = re.compile(r"^> \*\*(.+?)\*\*\s*·\s*(.+?)\s*$", re.M)
SERIES_LABEL = {"en": "{n} part series", "zh": "专题 · 共 {n} 篇"}


def card_parts(md_path, lang, title):
    """Eyebrow and reading time for one page."""
    text = build.split_front_matter(open(md_path, encoding="utf-8").read())[1]
    m = NAV.search(text)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    # A series index has no such line: say how many parts it has instead
    d = os.path.dirname(md_path)
    n = len([f for f in os.listdir(d) if f.endswith(".md")
             and not f.endswith(".en.md") and f != "index.md"])
    return SERIES_LABEL[lang].format(n=n), ""


def card_html(eyebrow, title, reading, lang):
    e = lambda t: html.escape(t, quote=False)
    # Letter-spaced uppercase reads well in Latin and badly in Chinese
    eyebrow_css = ("letter-spacing:.08em; text-transform:uppercase;"
                   if lang == "en" else "letter-spacing:.02em;")
    foot = [f'<span class="who">{e(build.SITE_NAME)}</span>',
            f'<span>{e(build.SITE_URL.split("//")[1])}</span>']
    if reading:
        foot.append(f"<span>{e(reading)}</span>")
    sep = '<span class="sep">|</span>'
    return f"""<!DOCTYPE html><html lang="{build.HTML_LANG[lang]}"><head><meta charset="utf-8"><style>
  :root{{ --bg:#ffffff; --text:#24292f; --title:#111418; --muted:#6b7280; --line:#e8e8e6; --link:#1f6feb; }}
  *{{ box-sizing:border-box; margin:0; padding:0; }}
  html,body{{ width:{W}px; height:{H}px; }}
  body{{ background:var(--bg);
    font-family:-apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    display:flex; flex-direction:column; padding:78px 92px 72px; position:relative; }}
  .accent{{ position:absolute; left:0; top:0; bottom:0; width:12px; background:var(--link); }}
  .eyebrow{{ font-size:25px; font-weight:600; color:var(--link); {eyebrow_css} }}
  .titlebox{{ height:336px; display:flex; align-items:center; }}
  h1{{ font-size:64px; font-weight:700; color:var(--title);
      letter-spacing:-.025em; line-height:1.16; }}
  .foot{{ margin-top:auto; display:flex; align-items:baseline; gap:18px;
          font-size:26px; color:var(--muted); }}
  .foot .who{{ color:var(--text); font-weight:600; }}
  .sep{{ color:var(--line); }}
</style></head><body>
  <div class="accent"></div>
  <div class="eyebrow">{e(eyebrow)}</div>
  <div class="titlebox"><h1>{e(title)}</h1></div>
  <div class="foot">{sep.join(foot)}</div>
<script>
// Titles vary from four words to a full sentence: shrink until it fits the box,
// so every card has the largest type its own title allows.
(function(){{
  var h = document.querySelector('h1'), box = document.querySelector('.titlebox');
  var size = parseFloat(getComputedStyle(h).fontSize);
  while (h.scrollHeight > box.clientHeight && size > 30) {{
    size -= 1.5; h.style.fontSize = size + 'px';
  }}
}})();
</script>
</body></html>"""


def render(doc, out_path):
    tmp = os.path.join(build.ROOT, ".card.tmp.html")
    open(tmp, "w", encoding="utf-8").write(doc)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    r = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        f"--window-size={W},{H}", "--virtual-time-budget=4000",
                        f"--screenshot={out_path}", f"file://{tmp}"],
                       capture_output=True, text=True)
    os.remove(tmp)
    if not os.path.exists(out_path):
        raise RuntimeError(f"Chrome wrote nothing for {out_path}\n{r.stderr[-400:]}")


def main():
    only_missing = "--missing" in sys.argv
    if not os.path.exists(CHROME):
        print(f"Chrome not found at {CHROME}"); return 1

    mds = []
    for dirpath, _, files in os.walk(build.POSTS_DIR):
        for f in sorted(files):
            if f.endswith(".md") and not f.endswith(".en.md"):
                mds.append(os.path.join(dirpath, f))

    made = skipped = 0
    for md in sorted(mds):
        base_rel = os.path.relpath(md, build.ROOT).replace(os.sep, "/")[:-3] + ".html"
        sources = {"zh": md}
        en = md[:-3] + ".en.md"
        if os.path.exists(en):
            sources["en"] = en
        for lang, src in sorted(sources.items()):
            out = os.path.join(build.ROOT, CARD_DIR,
                               build.lang_path(lang, base_rel)[:-5] + ".png")
            rel_out = os.path.relpath(out, build.ROOT)
            if only_missing and os.path.exists(out):
                skipped += 1; continue
            title = build.render_body(src, lang)[0]
            eyebrow, reading = card_parts(src, lang, title)
            render(card_html(eyebrow, title, reading, lang), out)
            made += 1
            print(f"  {rel_out:<52}{os.path.getsize(out)/1024:>5.0f}K  {eyebrow}")
    print(f"Done: {made} card(s) rendered" + (f", {skipped} already there" if skipped else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
