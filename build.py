#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert the .md files under posts/ into .html pages that use the site's styles.

    python3 build.py            # rebuild everything
    python3 build.py --check    # check only, write nothing

Design choices:
  · Standard library only, no dependencies. The Markdown parser covers only
    the syntax this site uses; anything outside that subset may not render
    correctly. The build stops with an error if a placeholder is left
    unrestored or two headings end up with the same anchor id.
  · Math is typeset by KaTeX in the browser at page load (CSS/JS from a CDN).
    Doing it at build time would mean bundling KaTeX's fonts into the repo.
  · The .md sources are only read, never modified, so they can be republished
    elsewhere as is.
  · Bilingual, one language per URL: xxx.md is the Chinese version and
    xxx.en.md, in the same folder, is the English one. Each becomes its own
    page -- English at the site root, Chinese under /zh/ -- so a search engine
    can index and rank them separately and a shared link keeps its language.
    The two are tied together by hreflang and by the link in the top right.
    A post without an .en.md is published in Chinese only.
  · The home page comes from _home.html, a fragment holding both languages,
    rendered into /index.html and /zh/index.html by the same template.
  · sitemap.xml and robots.txt are generated too, so a crawler can find the
    pages without waiting to stumble on a link to them.
"""
import html, os, re, sys, datetime, unicodedata

ROOT      = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(ROOT, "posts")
SITE_NAME = "Jiangang Han"
SITE_URL  = "https://jianganghan.github.io"   # no trailing slash; used for canonical URLs and the sitemap
KATEX_VER = "0.16.9"
KATEX_CDN = f"https://cdnjs.cloudflare.com/ajax/libs/KaTeX/{KATEX_VER}"


# ══════════════════════════════════════════════════════════════
#  1. Protected spans: math, inline code, fenced code blocks.
#     Markdown rules must not touch these, so they are cut out
#     first and replaced with placeholders.
# ══════════════════════════════════════════════════════════════
SENTINEL = "\x00"

class Vault:
    def __init__(self):
        self.items = []
    def stash(self, kind, payload):
        self.items.append((kind, payload))
        return f"{SENTINEL}{len(self.items)-1}{SENTINEL}"
    def restore(self, text, render):
        def sub(m):
            kind, payload = self.items[int(m.group(1))]
            return render(kind, payload)
        return re.sub(rf"{SENTINEL}(\d+){SENTINEL}", sub, text)


def protect(text, vault):
    # Fenced code blocks (the whole block)
    text = re.sub(r"^```[^\n]*\n(.*?)^```\s*$",
                  lambda m: vault.stash("fence", m.group(1)),
                  text, flags=re.S | re.M)
    # Display math
    text = re.sub(r"\$\$(.+?)\$\$",
                  lambda m: vault.stash("mathblock", m.group(1)),
                  text, flags=re.S)
    # Inline math
    text = re.sub(r"\$([^$\n]+?)\$",
                  lambda m: vault.stash("mathinline", m.group(1)), text)
    # Inline code
    text = re.sub(r"`([^`\n]+?)`",
                  lambda m: vault.stash("code", m.group(1)), text)
    return text


def render_plain(kind, payload):
    """Restore as plain text. TOC entries, anchor ids and <title> don't need
       real typesetting, but they can't keep the placeholders either (those
       would turn into invisible control characters)."""
    if kind in ("mathinline", "mathblock"):
        return payload.strip()
    if kind == "code":
        return payload
    return ""


def render_protected(kind, payload):
    if kind == "fence":
        return f'<pre><code>{html.escape(payload.rstrip())}</code></pre>'
    if kind == "code":
        return f"<code>{html.escape(payload)}</code>"
    if kind == "mathinline":
        return f'<span class="math math-inline">{html.escape(payload)}</span>'
    if kind == "mathblock":
        return f'<div class="math math-display">{html.escape(payload.strip())}</div>'
    raise AssertionError(kind)


# ══════════════════════════════════════════════════════════════
#  2. Inline syntax
# ══════════════════════════════════════════════════════════════
def md_link_target(url):
    """Point links to local .md files at the generated .html.
       xxx.en.md and xxx.md share the same xxx.html."""
    if re.match(r"^(https?:|mailto:|#|/)", url):
        return url
    base, _, frag = url.partition("#")
    if base.endswith(".en.md"):
        base = base[:-6] + ".html"
    elif base.endswith(".md"):
        base = base[:-3] + ".html"
    return base + (("#" + frag) if frag else "")


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)",
               lambda m: f'<img src="{m.group(2)}" alt="{m.group(1)}" loading="lazy">', s)
    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)",
               lambda m: f'<a href="{md_link_target(m.group(2))}">{m.group(1)}</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![*\w])\*([^*\n]+?)\*(?![*\w])", r"<em>\1</em>", s)
    return s


# ══════════════════════════════════════════════════════════════
#  3. Block syntax
# ══════════════════════════════════════════════════════════════
RAW_HTML_LINE = re.compile(r"^\s*</?(details|summary)\b[^>]*>.*$", re.I)
HEADING       = re.compile(r"^(#{1,6})\s+(.*)$")
HR            = re.compile(r"^-{3,}\s*$")
UL            = re.compile(r"^[-*]\s+(.*)$")
OL            = re.compile(r"^\d+\.\s+(.*)$")
QUOTE         = re.compile(r"^>\s?(.*)$")
TABLE_SEP     = re.compile(r"^\|[\s:|-]+\|\s*$")


def blocks_to_html(text, slugs=None, vault=None):
    lines = text.split("\n")
    out, i, n = [], 0, len(lines)

    while i < n:
        line = lines[i]

        if not line.strip():
            i += 1; continue

        # Pass <details> / <summary> through as is
        if RAW_HTML_LINE.match(line):
            out.append(line.strip()); i += 1; continue

        # A placeholder on a line of its own (a fenced code block)
        m = re.fullmatch(rf"{SENTINEL}(\d+){SENTINEL}", line.strip())
        if m:
            out.append(line.strip()); i += 1; continue

        if HR.match(line):
            out.append("<hr>"); i += 1; continue

        m = HEADING.match(line)
        if m:
            lvl, txt = len(m.group(1)), m.group(2).strip()
            attr = ""
            if slugs is not None and 2 <= lvl <= 3:
                plain = vault.restore(txt, render_plain) if vault else txt
                sid = slugify(plain)
                slugs.append((lvl, txt, sid))   # raw text; rendered like the body later
                attr = f' id="{sid}"'
            out.append(f"<h{lvl}{attr}>{inline(txt)}</h{lvl}>")
            i += 1; continue

        # Tables
        if line.lstrip().startswith("|") and i + 1 < n and TABLE_SEP.match(lines[i+1].strip()):
            head = split_row(line)
            i += 2
            body = []
            while i < n and lines[i].lstrip().startswith("|"):
                body.append(split_row(lines[i])); i += 1
            out.append(render_table(head, body)); continue

        # Blockquotes
        if QUOTE.match(line):
            buf = []
            while i < n and QUOTE.match(lines[i]):
                buf.append(QUOTE.match(lines[i]).group(1)); i += 1
            out.append("<blockquote>" + blocks_to_html("\n".join(buf), vault=vault) + "</blockquote>")
            continue

        # Lists
        for pat, tag in ((UL, "ul"), (OL, "ol")):
            if pat.match(line):
                items = []
                while i < n and pat.match(lines[i]):
                    items.append(pat.match(lines[i]).group(1)); i += 1
                out.append(f"<{tag}>" + "".join(f"<li>{inline(t)}</li>" for t in items) + f"</{tag}>")
                break
        else:
            # Paragraph: runs until a blank line or the start of another block
            buf = []
            while i < n and lines[i].strip() and not (
                HEADING.match(lines[i]) or HR.match(lines[i]) or UL.match(lines[i])
                or OL.match(lines[i]) or QUOTE.match(lines[i])
                or RAW_HTML_LINE.match(lines[i])
                or lines[i].lstrip().startswith("|")
                or re.fullmatch(rf"{SENTINEL}(\d+){SENTINEL}", lines[i].strip())):
                buf.append(lines[i].strip()); i += 1
            if buf:
                out.append("<p>" + inline(join_lines(buf)) + "</p>")
            continue
        continue

    return "\n".join(out)


# CJK characters and full-width punctuation
CJK = r"[\u3000-\u303f\u3400-\u4dbf\u4e00-\u9fff\uff00-\uffef]"

def join_lines(lines):
    """Join a paragraph that was wrapped across several source lines.
       English lines get a space between them; if the character on either
       side of the join is CJK or full-width punctuation, they are joined
       directly, with no space."""
    out = ""
    for ln in lines:
        if out and not (re.search(CJK + r"$", out) or re.match(CJK, ln)):
            out += " "
        out += ln
    return out


def split_row(line):
    cells = line.strip().strip("|").split("|")
    return [c.strip() for c in cells]


def render_table(head, body):
    th = "".join(f"<th>{inline(c)}</th>" for c in head)
    rows = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body)
    return f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead><tbody>{rows}</tbody></table></div>'


def slugify(text):
    s = re.sub(r"[\x00-\x1f]", "", text)
    s = re.sub(r"[`*_\[\]()$\\]", "", s).strip().lower()
    s = re.sub(r"[\s.,:/\uff1a\uff0c\u3002\u3001]+", "-", s)   # also full-width colon, comma, full stop, enumeration comma
    return re.sub(r"-+", "-", s).strip("-")


# ══════════════════════════════════════════════════════════════
#  4. Front matter (optional)
# ══════════════════════════════════════════════════════════════
def split_front_matter(text):
    meta = {}
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            for ln in text[4:end].split("\n"):
                if ":" in ln:
                    k, _, v = ln.partition(":")
                    meta[k.strip()] = v.strip().strip('"\'')
            text = text[end + 5:]
    return meta, text


# ══════════════════════════════════════════════════════════════
#  4b. Meta description
#      Search results and link previews show this text, so it is
#      taken from the lede (the opening blockquote), which is
#      already written as a summary of the post.
# ══════════════════════════════════════════════════════════════
DESC_WIDTH = 160        # upper bound, counting a CJK character as two
GREEK = {r"\lambda": "\u03bb", r"\varepsilon": "\u03b5", r"\epsilon": "\u03b5",
         r"\delta": "\u03b4", r"\eta": "\u03b7", r"\mu": "\u03bc",
         r"\alpha": "\u03b1", r"\beta": "\u03b2", r"\gamma": "\u03b3",
         r"\theta": "\u03b8", r"\sigma": "\u03c3", r"\rho": "\u03c1",
         r"\pi": "\u03c0", r"\times": "\u00d7", r"\cdot": "\u00b7",
         r"\le": "\u2264", r"\ge": "\u2265", r"\approx": "\u2248"}


def math_to_text(latex):
    """A formula has no place in a meta description, so keep only what reads as prose."""
    for k, v in GREEK.items():
        latex = re.sub(re.escape(k) + r"(?![A-Za-z])", v, latex)
    return re.sub(r"[\\{}$]", "", latex).strip()


def text_width(s):
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)


def shorten(s, width=DESC_WIDTH):
    if text_width(s) <= width:
        return s
    cut, w = "", 0
    for c in s:
        w += 2 if unicodedata.east_asian_width(c) in "WF" else 1
        if w > width - 1:
            break
        cut += c
    # Prefer ending on a sentence, as long as that doesn't throw away too much
    m = max((cut.rfind(c) for c in "\u3002\uff01\uff1f.!?"), default=-1)
    if m >= len(cut) * 0.6:
        return cut[:m + 1]
    return cut.rstrip() + "\u2026"


def summarize(body):
    """Pull the lede out of the rendered body and flatten it to plain text."""
    m = re.search(r'<blockquote class="lede">(.*?)</blockquote>', body, re.S)
    if not m:      # no lede: fall back to the first paragraph
        m = re.search(r"</h1>\s*<p>(.*?)</p>", body, re.S)
    if not m:
        return ""
    chunk = re.sub(r'<span class="math[^"]*">(.*?)</span>',
                   lambda mm: math_to_text(mm.group(1)), m.group(1), flags=re.S)
    # Paragraph breaks become a space so sentences don't run together;
    # inline tags (<strong>, <a>, <em>) just go away, leaving the text as written.
    chunk = re.sub(r"</(?:p|div|li|h[1-6]|blockquote)>|<br\s*/?>", " ", chunk)
    text = html.unescape(re.sub(r"<[^>]+>", "", chunk))
    return shorten(re.sub(r"\s+", " ", text).strip())


# ══════════════════════════════════════════════════════════════
#  5. Page template
# ══════════════════════════════════════════════════════════════
# One page holds one language. The default language sits at the site root and
# the other mirrors it under /<lang>/, so every version has its own URL and
# hreflang can tie them together. Interface text is content, so it stays here.
DEFAULT_LANG = "en"
TOC_LABEL   = {"zh": "目录", "en": "Contents"}
NAV_POSTS   = {"zh": "文章", "en": "Posts"}
FOOTER_NOTE = {"zh": "观点仅代表个人。", "en": "Opinions are my own."}
SWITCH_TO   = {"zh": "EN", "en": "中文"}        # the link names the language it leads to
HTML_LANG   = {"zh": "zh-CN", "en": "en"}
HREFLANG    = {"zh": "zh-Hans", "en": "en"}
OG_LOCALE   = {"zh": "zh_CN", "en": "en_US"}
HOME_SRC    = "_home.html"


def lang_path(lang, base_rel):
    """Output path of one language version, relative to the site root."""
    return base_rel if lang == DEFAULT_LANG else f"{lang}/{base_rel}"


def canonical_url(lang, base_rel):
    """The one URL that stands for this page. A directory index is addressed as
       the directory, so /posts/x/ and /posts/x/index.html don't compete."""
    p = lang_path(lang, base_rel)
    if p.endswith("index.html"):
        p = p[:-len("index.html")]
    return f"{SITE_URL}/{p}"


def point_assets_at_root(body, rel_dir, up):
    """Figures live next to the Markdown they belong to. A translated page sits
       one level deeper, under /<lang>/, so send its <img> paths back there
       instead of keeping a second copy of every file."""
    return re.sub(r'(<img[^>]*?\ssrc=")(?!https?:|/)([^"]+)"',
                  lambda m: f'{m.group(1)}{up}{rel_dir}/{m.group(2)}"', body)


def decorate(body, toc, lang):
    """Add the lede class and the table of contents, once per language."""
    toc_html = ""
    if len(toc) >= 3:
        items = "".join(
            f'<li class="toc__l{lvl}"><a href="#{sid}">{txt}</a></li>'
            for lvl, txt, sid in toc)
        label = TOC_LABEL[lang]
        toc_html = (f'<nav class="toc" aria-label="{label}">'
                    f'<div class="toc__t">{label}</div><ul>{items}</ul></nav>')
    # The first blockquote right after the h1 is the lede (the highlighted
    # opening) and gets its own class. The table of contents goes after the
    # lede, so readers see what the post is about first.
    m = re.search(r"</h1>\s*<blockquote>", body)
    if m:
        body = (body[:m.start()] + "</h1>\n<blockquote class=\"lede\">"
                + body[m.end():])
        end = body.index("</blockquote>", m.start()) + len("</blockquote>")
    else:
        m2 = re.search(r"</h1>", body)
        end = m2.end() if m2 else 0

    if toc_html:
        body = body[:end] + "\n" + toc_html + body[end:]
    return body


def page(title, body, lang, base_rel, desc, langs, article=True):
    out_rel = lang_path(lang, base_rel)
    up      = "../" * out_rel.count("/")
    prefix  = "" if lang == DEFAULT_LANG else f"{lang}/"
    home    = f"{up}{prefix}index.html"
    full    = html.escape(SITE_NAME if title == SITE_NAME else f"{title} — {SITE_NAME}")
    d       = html.escape(desc, quote=True)
    canon   = canonical_url(lang, base_rel)
    og_type = "website" if base_rel.endswith("index.html") else "article"

    # hreflang has to be bidirectional and self-referencing, or it is ignored.
    # x-default is the fallback for a reader whose language matches neither.
    alt = [f'<link rel="alternate" hreflang="{HREFLANG[l]}" href="{canonical_url(l, base_rel)}">'
           for l in sorted(langs)]
    if DEFAULT_LANG in langs:
        alt.append('<link rel="alternate" hreflang="x-default" '
                   f'href="{canonical_url(DEFAULT_LANG, base_rel)}">')

    others = sorted(l for l in langs if l != lang)
    switch = (f'<a class="head__lang" href="{up}{lang_path(others[0], base_rel)}"'
              f' hreflang="{HREFLANG[others[0]]}">{SWITCH_TO[lang]}</a>') if others else ""
    alt_locale = (f'\n<meta property="og:locale:alternate" content="{OG_LOCALE[others[0]]}">'
                  if others else "")

    # KaTeX and the image zoom are only worth loading on a post
    extra_css = f'\n<link rel="stylesheet" href="{up}assets/css/article.css">\n' \
                f'<link rel="stylesheet" href="{KATEX_CDN}/katex.min.css">' if article else ""
    extra_js  = f'''
<script src="{up}assets/js/zoom.js"></script>
<script src="{KATEX_CDN}/katex.min.js"></script>
<script>
// The build only marks formulas up; the actual typesetting happens here.
// If KaTeX fails to load, the page still shows readable LaTeX source instead of going blank.
(function(){{
  if (typeof katex === 'undefined') return;
  document.querySelectorAll('.math').forEach(function(el){{
    try {{
      katex.render(el.textContent, el, {{
        displayMode: el.classList.contains('math-display'),
        throwOnError: false
      }});
    }} catch(e) {{ el.classList.add('math--failed'); }}
  }});
}})();
</script>''' if article else ""

    return f"""<!DOCTYPE html>
<html lang="{HTML_LANG[lang]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{full}</title>
<meta name="description" content="{d}">
<meta name="author" content="{SITE_NAME}">
<link rel="canonical" href="{canon}">
{chr(10).join(alt)}
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:title" content="{full}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{canon}">
<meta property="og:locale" content="{OG_LOCALE[lang]}">{alt_locale}
<meta name="twitter:card" content="summary">
<link rel="icon" href="{up}assets/img/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{up}assets/css/style.css">{extra_css}
</head>
<body>

<header class="head">
  <a class="head__name" href="{home}">{SITE_NAME}</a>
  <nav class="head__nav">
    <a href="{home}">{NAV_POSTS[lang]}</a>
    {switch}
  </nav>
</header>

<main{' class="article"' if article else ""}>
{body}
</main>

<footer class="foot">&copy; <span id="y">{datetime.date.today().year}</span> {SITE_NAME}　·　{FOOTER_NOTE[lang]}</footer>

<script>document.getElementById('y').textContent = new Date().getFullYear();</script>{extra_js}
</body>
</html>
"""


# ══════════════════════════════════════════════════════════════
#  6. Sitemap and robots.txt
#     A new site has nothing linking to it, so these two files are
#     how a crawler finds the pages in the first place.
# ══════════════════════════════════════════════════════════════
def newest(paths):
    """Last modified date of the sources a page is built from, as YYYY-MM-DD."""
    return datetime.date.fromtimestamp(max(os.path.getmtime(p) for p in paths)).isoformat()


def write_sitemap(entries):
    urls = "\n".join(
        f"  <url><loc>{html.escape(loc)}</loc><lastmod>{mod}</lastmod></url>"
        for loc, mod in entries)
    doc = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           f"{urls}\n</urlset>\n")
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(doc)


def write_robots():
    open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8").write(
        "# Everything on this site is meant to be indexed, except the home page\n"
        "# source, which is a fragment rather than a page of its own.\n"
        "User-agent: *\n"
        "Allow: /\n"
        f"Disallow: /{HOME_SRC}\n"
        "\n"
        f"Sitemap: {SITE_URL}/sitemap.xml\n")


# ══════════════════════════════════════════════════════════════
#  7. Main
# ══════════════════════════════════════════════════════════════
def render_body(md_path, lang):
    raw = open(md_path, encoding="utf-8").read()
    meta, text = split_front_matter(raw)

    vault = Vault()
    text = protect(text, vault)
    toc = []
    body = blocks_to_html(text, slugs=toc, vault=vault)
    body = vault.restore(body, render_protected)

    title = meta.get("title")
    if not title:
        m = re.search(r"^#\s+(.*)$", text, re.M)
        title = m.group(1).strip() if m else os.path.basename(md_path)[:-3]
    title = vault.restore(title, render_plain).strip()

    # TOC entries are rendered like the body, so math in a heading shows up properly in the TOC too
    toc = [(lvl, vault.restore(inline(txt), render_protected), sid)
           for lvl, txt, sid in toc]
    return title, decorate(body, toc, lang), len(toc)


def verify(doc, out_rel):
    leftovers = doc.count(SENTINEL)
    if leftovers:
        raise RuntimeError(f"{out_rel}: {leftovers} placeholder(s) were not restored")
    ids = re.findall(r'\sid="([^"]+)"', doc)
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        raise RuntimeError(f"{out_rel}: duplicate anchor ids: {dup}")


def emit(out_rel, doc, check):
    if not check:
        path = os.path.join(ROOT, out_rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w", encoding="utf-8").write(doc)


def convert(md_path, check=False):
    """Build every language version of one post. Returns a row per output."""
    rel      = os.path.relpath(md_path, ROOT).replace(os.sep, "/")
    base_rel = rel[:-3] + ".html"
    rel_dir  = os.path.dirname(rel)

    # xxx.md is the Chinese version, xxx.en.md the English one. A post without a
    # translation is published in the language it was written in, and says so
    # with a single hreflang instead of pointing at a page that isn't there.
    sources = {"zh": md_path}
    en_path = md_path[:-3] + ".en.md"
    if os.path.exists(en_path):
        sources["en"] = en_path
    langs   = set(sources)
    lastmod = newest(list(sources.values()))

    rows = []
    for lang in sorted(sources):
        src = sources[lang]
        title, body, nsec = render_body(src, lang)
        out_rel = lang_path(lang, base_rel)
        if lang != DEFAULT_LANG:
            body = point_assets_at_root(body, rel_dir, "../" * out_rel.count("/"))
        doc = page(title, body, lang, base_rel, summarize(body), langs)
        verify(doc, out_rel)
        emit(out_rel, doc, check)
        rows.append((os.path.relpath(src, ROOT), out_rel, len(doc), nsec,
                     canonical_url(lang, base_rel), lastmod))
    return rows


def pick_lang(fragment, lang):
    """The home page fragment holds both languages: the visible text is the
       default one and data-zh is the translation. Neither output keeps the
       other language, not even in an attribute."""
    if lang != DEFAULT_LANG:
        fragment = re.sub(r'(<(\w+)[^>]*?\sdata-' + lang + r'="([^"]*)"[^>]*>)(.*?)(</\2>)',
                          lambda m: m.group(1) + m.group(3) + m.group(5),
                          fragment, flags=re.S)
    fragment = re.sub(r'\s+data-(?:en|zh)="[^"]*"', "", fragment)
    # The comments in the source are notes to the author, not part of the page
    return re.sub(r"<!--.*?-->\s*", "", fragment, flags=re.S)


def build_home(check=False):
    src = os.path.join(ROOT, HOME_SRC)
    meta, fragment = split_front_matter(open(src, encoding="utf-8").read())
    langs = {"en", "zh"}
    rows  = []
    for lang in sorted(langs):
        doc = page(meta[f"title_{lang}"], pick_lang(fragment, lang).strip(),
                   lang, "index.html", meta[f"desc_{lang}"], langs, article=False)
        out_rel = lang_path(lang, "index.html")
        verify(doc, out_rel)
        emit(out_rel, doc, check)
        rows.append((HOME_SRC, out_rel, len(doc), 0,
                     canonical_url(lang, "index.html"), newest([src])))
    return rows


def main():
    check = "--check" in sys.argv
    mds = []
    for dirpath, _, files in os.walk(POSTS_DIR):
        for f in sorted(files):
            # xxx.en.md is the English version of xxx.md: both are built from the same call
            if f.endswith(".md") and not f.endswith(".en.md"):
                mds.append(os.path.join(dirpath, f))
    if not mds:
        print("No .md files found under posts/"); return 1

    rows = build_home(check)
    for p in sorted(mds):
        rows += convert(p, check)

    print(f"{'Source':<44}{'Output':<47}{'Size':>7}{'Sections':>10}")
    print("-" * 108)
    for src, out, size, nsec, _, _ in rows:
        print(f"{src:<44}{out:<47}{size/1024:>6.0f}K{nsec or '':>10}")
    print("-" * 108)

    entries = [(loc, mod) for _, _, _, _, loc, mod in rows]
    if not check:
        write_sitemap(entries)
        write_robots()
    print(f"{'Checked (--check, nothing written)' if check else 'Done'}: "
          f"{len(mds)} posts, {len(rows)} pages, {len(entries)} URLs in sitemap.xml")
    return 0


if __name__ == "__main__":
    sys.exit(main())
