# jianganghan.github.io

[English](README.md) | 中文

个人博客 **<https://jianganghan.github.io/>** 的源码。记录学过的、做过的，和正在学、正在做的东西。文章按专题组织，每篇都有中英两个版本。

## 专题

- **[用不可靠的模型，搭可靠的系统](https://jianganghan.github.io/zh/posts/reliability/index.html)**（两篇）：从冯·诺依曼 1952 年关于冗余的讲座，讲到模型的错误彼此相关时，为什么多加几道检查就不够了。
- **[定价优化入门](https://jianganghan.github.io/zh/posts/pricing/index.html)**（四篇）：定价的数学，从单个对象，到业务约束、替代品，再到大规模求解。
- **[广告出价入门](https://jianganghan.github.io/zh/posts/bidding/index.html)**（三篇）：站在广告主一侧看广告拍卖的出价：一次拍卖、一天的预算，以及预算平滑。

## 怎么搭的

不用框架，也没有依赖。文章用 Markdown 写，`build.py`（只用 Python 标准库）把每篇转成两个 HTML 页面，一种语言一页、各有各的网址：英文在站点根目录，中文在 `/zh/` 下，两边用 `hreflang` 关联，右上角有互相跳转的链接。公式在浏览器里由 KaTeX 排版。`build.py` 同时生成 `sitemap.xml`、`robots.txt`，以及中英各一份 Atom feed。GitHub Pages 原样发布这些文件，所以生成的 HTML 要和 Markdown 一起提交。

```
_home.html               首页源文件：专题列表，中英写在一起，手工维护
index.html               生成的英文首页（中文首页是 zh/index.html）
404.html                 访问不存在的地址时 GitHub Pages 显示这一页，只有英文
build.py                 posts/**/*.md → .html，另外生成 sitemap.xml、robots.txt 和 feed
feed.xml, zh/feed.xml    Atom 订阅源，中英各一份，每个页面都链到它
posts/<专题>/xxx.md      中文版  → zh/posts/<专题>/xxx.html
posts/<专题>/xxx.en.md   英文版  → posts/<专题>/xxx.html
posts/<专题>/images/     配图，中英各一份 SVG（figN.svg / figN.en.svg）
make-cards.py            生成社交卡片图（需要 Chrome，不属于 build.py）
assets/og/               每个页面一张卡片：大字是文章标题，名字缩为署名
assets/img/og.png        全站卡片：首页用它，某页没有自己的卡片时也回退到它
assets/img/og-card.html  全站那张卡片的来源
assets/css/              style.css（全站样式，配色在最上面）、article.css（文章页）
assets/js/               zoom.js（配图点击放大）
```

## 写文章

1. 在 `posts/<专题>/` 下写 `xxx.md`（中文）和 `xxx.en.md`（英文）。在 `xxx.md` 顶部写一行 front matter `date: YYYY-MM-DD`——feed 按它排序和标注日期，没有这一行的文章不会进 feed。
2. 运行 `python3 make-cards.py --missing` 给新文章渲染社交卡片。
3. 运行 `python3 build.py` 重新生成 HTML（加 `--check` 只检查不写文件）。如果某页还在用全站卡片、或者缺 `date:` 因而进不了 feed，它会提示。
4. 新专题或新分篇，要加到 `_home.html`（不是 `index.html`，那个是生成的）：可见文字是英文版，`data-zh` 写中文版；阅读时长和文章里保持一致。

`build.py` 只支持本站用到的 Markdown 语法。几条约定：

- `# 标题` 后面的第一个引用块是导语，会加高亮；二、三级标题不少于 3 个时，导语后面自动生成目录。
- 公式写在 `$...$` 或 `$$...$$` 里。
- 站内链接：中文篇里写 `xxx.md`，英文篇里写 `xxx.en.md`，构建时都变成 `xxx.html`，各自落在本语言的目录树里。
- 可折叠内容用 `<details>` 和 `<summary>`，标签各占一行。
- 日期只写在中文源里：它属于这篇文章，而不属于某个语言版本。页面上显示在标题正下方。
- `updated: YYYY-MM-DD` 可选，手写，用于值得声明的大改：页面会显示「…更新」，订阅者也会重新看到这条。**刻意不从 git 或文件时间推断**——那两者在重新构建或改个错别字时就会变，会让读者误以为你修订了内容。
- 每篇文末自动链到它在 GitHub 上的提交历史，「哪天改了什么」由提交记录本身回答，不用另外手工维护一份。
- 卡片上的眉标和阅读时长，直接取自文章里本来就有的 `> **专题 · 第 N 篇 / 共 M 篇** · 阅读约 T` 那一行，不用另外写。
- 要重画全部卡片，运行 `python3 make-cards.py`；想改样式，改里面的 `card_html()`。全站那张是单独的：改 `assets/img/og-card.html`，再用 headless Chrome 按 1200x630 重新渲染。

## 本地预览

```bash
python3 build.py
python3 -m http.server 8080    # 然后打开 http://localhost:8080（中文在 /zh/）
```

## 许可

代码（`build.py` 和 `assets/`）采用 [MIT 许可证](LICENSE)。`posts/` 下的文章和配图采用 [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/deed.zh-hans)：注明出处即可转载和改编，但不得用于商业用途。
