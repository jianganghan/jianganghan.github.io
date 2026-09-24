# jianganghan.github.io

English | [中文](README.zh-CN.md)

Source for my blog at **<https://jianganghan.github.io/>**: notes on what I've learned and built, and what I'm learning and building now. Posts come in short series, each written in both Chinese and English.

## Series

- **[Reliable Systems from Unreliable Models](https://jianganghan.github.io/posts/reliability/index.html)** (2 parts): from von Neumann's 1952 lectures on redundancy to why adding more checks stops helping once a model's errors are correlated.
- **[A Primer on Price Optimization](https://jianganghan.github.io/posts/pricing/index.html)** (4 parts): the math of pricing, from a single item to business constraints, substitutes, and problems at scale.
- **[A Primer on Ad Bidding](https://jianganghan.github.io/posts/bidding/index.html)** (3 parts): bidding in ad auctions from the advertiser's side: one auction, a daily budget, and pacing.

## How it's built

No framework and no dependencies. Posts are written in Markdown, and `build.py` (Python standard library only) turns each one into two HTML pages, one per language, each at its own URL: English at the site root and Chinese under `/zh/`, tied together with `hreflang` and a link in the top right. Math is typeset in the browser by KaTeX. `build.py` also writes `sitemap.xml`, `robots.txt` and an Atom feed per language. GitHub Pages serves the files as they are, so the generated HTML is committed along with the Markdown.

```
_home.html               home page source: the list of series, both languages, edited by hand
index.html               generated English home page (zh/index.html is the Chinese one)
404.html                 shown by GitHub Pages for any missing URL, English only
build.py                 posts/**/*.md → .html, plus sitemap.xml, robots.txt and the feeds
feed.xml, zh/feed.xml    Atom feed, one per language, linked from every page
posts/<series>/xxx.md    Chinese version of a post  → zh/posts/<series>/xxx.html
posts/<series>/xxx.en.md English version            → posts/<series>/xxx.html
posts/<series>/images/   figures, one SVG per language (figN.svg / figN.en.svg)
make-cards.py            renders the social cards (needs Chrome; not part of build.py)
assets/og/               one card per page: the post's title, large, with a byline
assets/img/og.png        the site-wide card: used by the home pages, and as the fallback
assets/img/og-card.html  what that site-wide card was rendered from
assets/css/              style.css (site-wide, colors at the top), article.css (posts)
assets/js/               zoom.js (click to zoom figures)
```

## Writing a post

1. Write `xxx.md` (Chinese) and `xxx.en.md` (English) under `posts/<series>/`. Give `xxx.md` a `date: YYYY-MM-DD` front matter line; it is what the feed sorts and dates by, and a post without one is simply left out of the feed.
2. Run `python3 make-cards.py --missing` to render the new post's social cards.
3. Run `python3 build.py` to regenerate the HTML (`--check` builds without writing files). It says so if a page is still falling back to the site-wide card, or has no `date:` and so stays out of the feed.
4. For a new series or part, add it to `_home.html` (not `index.html`, which is generated). The visible text is the English version and `data-zh` holds the Chinese; keep reading times in sync with the posts.

`build.py` only supports the Markdown this site uses. A few conventions:

- The first blockquote after `# Title` becomes the highlighted lede. Posts with three or more level-2/3 headings get a table of contents after it.
- Math goes in `$...$` or `$$...$$`.
- Link to other posts as `xxx.md` from a Chinese post and `xxx.en.md` from an English one; both become `xxx.html`, which resolves inside that language's own tree.
- Collapsible sections use `<details>` and `<summary>`, each tag on its own line.
- The date goes in the Chinese source only: it belongs to the post, not to a translation. It is shown on the post, directly under the title.
- `updated: YYYY-MM-DD` is optional and written by hand, for a revision worth announcing: the post then reads "Updated ...", and subscribers see the entry again. It is deliberately not taken from git or from file times, which move on a rebuild or a typo fix and would tell a reader the piece was revised when it wasn't.
- Every post links to its own commit log on GitHub, so "what changed and when" is answered by the history itself rather than by a summary kept in step by hand.
- A card's eyebrow and reading time are read from the `> **Series · Part N of M** · T` line the post already carries, so there is nothing extra to write.
- To redraw every card, run `python3 make-cards.py`. To change how they look, edit `card_html()` in it. The site-wide card is separate: edit `assets/img/og-card.html` and re-render it with headless Chrome at 1200x630.

## Local preview

```bash
python3 build.py
python3 -m http.server 8080    # then open http://localhost:8080 (Chinese at /zh/)
```

## License

The code (`build.py` and `assets/`) is released under the [MIT License](LICENSE). The posts and figures under `posts/` are licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/): you may share and adapt them for non-commercial purposes, with attribution.
