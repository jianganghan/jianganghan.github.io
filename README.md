# jianganghan.github.io

English | [中文](README.zh-CN.md)

Source for my blog at **<https://jianganghan.github.io/>**: notes on what I've learned and built, and what I'm learning and building now. Posts come in short series, each written in both Chinese and English.

## Series

- **[Reliable Systems from Unreliable Models](https://jianganghan.github.io/posts/reliability/index.html)** (2 parts): from von Neumann's 1952 lectures on redundancy to why adding more checks stops helping once a model's errors are correlated.
- **[A Primer on Price Optimization](https://jianganghan.github.io/posts/pricing/index.html)** (4 parts): the math of pricing, from a single item to business constraints, substitutes, and problems at scale.
- **[A Primer on Ad Bidding](https://jianganghan.github.io/posts/bidding/index.html)** (3 parts): bidding in ad auctions from the advertiser's side: one auction, a daily budget, and pacing.

## How it's built

No framework and no dependencies. Posts are written in Markdown, and `build.py` (Python standard library only) turns each one into two HTML pages, one per language, each at its own URL: English at the site root and Chinese under `/zh/`, tied together with `hreflang` and a link in the top right. Math is typeset in the browser by KaTeX. `build.py` also writes `sitemap.xml` and `robots.txt`. GitHub Pages serves the files as they are, so the generated HTML is committed along with the Markdown.

```
_home.html               home page source: the list of series, both languages, edited by hand
index.html               generated English home page (zh/index.html is the Chinese one)
404.html                 shown by GitHub Pages for any missing URL, English only
build.py                 posts/**/*.md → .html, plus sitemap.xml and robots.txt
posts/<series>/xxx.md    Chinese version of a post  → zh/posts/<series>/xxx.html
posts/<series>/xxx.en.md English version            → posts/<series>/xxx.html
posts/<series>/images/   figures, one SVG per language (figN.svg / figN.en.svg)
assets/css/              style.css (site-wide, colors at the top), article.css (posts)
assets/js/               zoom.js (click to zoom figures)
```

## Writing a post

1. Write `xxx.md` (Chinese) and `xxx.en.md` (English) under `posts/<series>/`.
2. Run `python3 build.py` to regenerate the HTML (`--check` builds without writing files).
3. For a new series or part, add it to `_home.html` (not `index.html`, which is generated). The visible text is the English version and `data-zh` holds the Chinese; keep reading times in sync with the posts.

`build.py` only supports the Markdown this site uses. A few conventions:

- The first blockquote after `# Title` becomes the highlighted lede. Posts with three or more level-2/3 headings get a table of contents after it.
- Math goes in `$...$` or `$$...$$`.
- Link to other posts as `xxx.md` from a Chinese post and `xxx.en.md` from an English one; both become `xxx.html`, which resolves inside that language's own tree.
- Collapsible sections use `<details>` and `<summary>`, each tag on its own line.

## Local preview

```bash
python3 build.py
python3 -m http.server 8080    # then open http://localhost:8080 (Chinese at /zh/)
```

## License

The code (`build.py` and `assets/`) is released under the [MIT License](LICENSE). The posts and figures under `posts/` are licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/): you may share and adapt them for non-commercial purposes, with attribution.
