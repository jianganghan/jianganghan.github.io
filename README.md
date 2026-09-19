# jianganghan.github.io

English | [中文](README.zh-CN.md)

Source for my blog at **<https://jianganghan.github.io/>**: notes on what I've learned and built, and what I'm learning and building now. Posts come in short series, each written in both Chinese and English.

## Series

- **[Reliable Systems from Unreliable Models](https://jianganghan.github.io/posts/reliability/index.html)** (2 parts): from von Neumann's 1952 lectures on redundancy to why adding more checks stops helping once a model's errors are correlated.
- **[A Primer on Price Optimization](https://jianganghan.github.io/posts/pricing/index.html)** (4 parts): the math of pricing, from a single item to business constraints, substitutes, and problems at scale.
- **[A Primer on Ad Bidding](https://jianganghan.github.io/posts/bidding/index.html)** (3 parts): bidding in ad auctions from the advertiser's side: one auction, a daily budget, and pacing.

## How it's built

No framework and no dependencies. Posts are written in Markdown, and `build.py` (Python standard library only) turns each one into a single HTML page that holds both languages; a button switches between them in place. Math is typeset in the browser by KaTeX. GitHub Pages serves the files as they are, so the generated HTML is committed along with the Markdown.

```
index.html               home page: the list of series, edited by hand
404.html                 shown by GitHub Pages for any missing URL
build.py                 posts/**/*.md → .html
posts/<series>/xxx.md    Chinese version of a post
posts/<series>/xxx.en.md English version; both render into xxx.html
posts/<series>/images/   figures, one SVG per language (figN.svg / figN.en.svg)
assets/css/              style.css (site-wide, colors at the top), article.css (posts)
assets/js/               lang.js (language switch), zoom.js (click to zoom figures)
```

## Writing a post

1. Write `xxx.md` (Chinese) and `xxx.en.md` (English) under `posts/<series>/`.
2. Run `python3 build.py` to regenerate the HTML (`--check` builds without writing files).
3. For a new series or part, add it to `index.html`. The visible text is the English version and `data-zh` holds the Chinese; keep reading times in sync with the posts.

`build.py` only supports the Markdown this site uses. A few conventions:

- The first blockquote after `# Title` becomes the highlighted lede. Posts with three or more level-2/3 headings get a table of contents after it.
- Math goes in `$...$` or `$$...$$`.
- Link to other posts as `xxx.md` or `xxx.en.md`; both are rewritten to `xxx.html`.
- Collapsible sections use `<details>` and `<summary>`, each tag on its own line.

## Local preview

```bash
python3 build.py
python3 -m http.server 8080    # then open http://localhost:8080
```

## License

The code (`build.py` and `assets/`) is released under the [MIT License](LICENSE). The posts and figures under `posts/` are licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/): you may share and adapt them for non-commercial purposes, with attribution.
