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
  · Bilingual: xxx.md is the Chinese version and xxx.en.md, in the same
    folder, is the English one. Both bodies are rendered into the same
    xxx.html, and the language button in the top right switches between
    them in place, without loading another page. A post without an .en.md is
    rendered in Chinese only.
"""
import html, os, re, sys, datetime

ROOT      = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(ROOT, "posts")
SITE_NAME = "Jiangang Han"
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
#  5. Page template
# ══════════════════════════════════════════════════════════════
# Interface text shown on the page. These are content, so the Chinese strings stay.
TOC_LABEL   = {"zh": "目录", "en": "Contents"}
NAV_POSTS   = {"zh": "文章", "en": "Posts"}
FOOTER_NOTE = {"zh": "观点仅代表个人。", "en": "Opinions are my own."}
LANG_BUTTON = "中文"   # the button shows the language it switches to; lang.js updates it


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


def page(titles, body, depth):
    zh_title, en_title = titles
    up = "../" * depth
    full_zh = html.escape(f"{zh_title} — {SITE_NAME}")
    if en_title:
        full_en = html.escape(f"{en_title} — {SITE_NAME}")
        # lang.js swaps the <title> text for the current language, so the browser tab follows too
        title_tag = f'<title data-zh="{full_zh}" data-en="{full_en}">{full_zh}</title>'
    else:
        title_tag = f"<title>{full_zh}</title>"

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{title_tag}
<script>
// Pick the language before the first paint (same rules as lang.js), so a bilingual post never flashes the other language
(function(){{
  var l = null;
  try {{ l = localStorage.getItem('lang'); }} catch (e) {{}}
  if (!l) l = /^zh/i.test(navigator.language || '') ? 'zh' : 'en';
  document.documentElement.setAttribute('lang', l === 'zh' ? 'zh-CN' : 'en');
}})();
</script>
<link rel="icon" href="{up}assets/img/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{up}assets/css/style.css">
<link rel="stylesheet" href="{up}assets/css/article.css">
<link rel="stylesheet" href="{KATEX_CDN}/katex.min.css">
</head>
<body>

<header class="head">
  <a class="head__name" href="{up}index.html">{SITE_NAME}</a>
  <nav class="head__nav">
    <a href="{up}index.html" data-en="{NAV_POSTS['en']}" data-zh="{NAV_POSTS['zh']}">{NAV_POSTS['en']}</a>
    <button type="button" class="head__lang" id="langBtn" hidden>{LANG_BUTTON}</button>
  </nav>
</header>

<main class="article">
{body}
</main>

<footer class="foot">&copy; <span id="y">{datetime.date.today().year}</span> {SITE_NAME}　·　<span data-en="{FOOTER_NOTE['en']}" data-zh="{FOOTER_NOTE['zh']}">{FOOTER_NOTE['en']}</span></footer>

<script>document.getElementById('y').textContent = new Date().getFullYear();</script>
<script src="{up}assets/js/lang.js"></script>
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
</script>
</body>
</html>
"""


# ══════════════════════════════════════════════════════════════
#  6. Main
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


def convert(md_path, check=False):
    zh_title, zh_body, nsec = render_body(md_path, "zh")
    en_path = md_path[:-3] + ".en.md"
    if os.path.exists(en_path):
        en_title, en_body, _ = render_body(en_path, "en")
        # Both bodies go into the same page; <html lang> decides which one is shown (see article.css)
        body = (f'<div class="lang-zh" lang="zh-CN">\n{zh_body}\n</div>\n'
                f'<div class="lang-en" lang="en">\n{en_body}\n</div>')
    else:
        en_title, body = None, zh_body

    rel   = os.path.relpath(md_path, ROOT)
    depth = rel.count(os.sep)
    out_path = md_path[:-3] + ".html"
    doc = page((zh_title, en_title), body, depth)

    leftovers = doc.count(SENTINEL)
    if leftovers:
        raise RuntimeError(f"{rel}: {leftovers} placeholder(s) were not restored")

    ids = re.findall(r'\sid="([^"]+)"', doc)
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        raise RuntimeError(f"{rel}: duplicate anchor ids (do a Chinese and an English heading collide?): {dup}")

    if not check:
        open(out_path, "w", encoding="utf-8").write(doc)
    return rel, os.path.relpath(out_path, ROOT), len(doc), nsec, bool(en_title)


def main():
    check = "--check" in sys.argv
    mds = []
    for dirpath, _, files in os.walk(POSTS_DIR):
        for f in sorted(files):
            # xxx.en.md is the English version of xxx.md: it's rendered along with the Chinese and gets no page of its own
            if f.endswith(".md") and not f.endswith(".en.md"):
                mds.append(os.path.join(dirpath, f))
    if not mds:
        print("No .md files found under posts/"); return 1

    print(f"{'Source':<42}{'Output':<44}{'Size':>7}{'Sections':>10}{'EN':>5}")
    print("-" * 108)
    for p in sorted(mds):
        src, dst, size, nsec, has_en = convert(p, check)
        print(f"{src:<42}{dst:<44}{size/1024:>6.0f}K{nsec:>10}{'✓' if has_en else '—':>5}")
    print("-" * 108)
    print(f"{'Checked (--check, nothing written)' if check else 'Done'}: {len(mds)} posts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
