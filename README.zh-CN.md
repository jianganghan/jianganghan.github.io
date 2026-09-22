# jianganghan.github.io

[English](README.md) | 中文

个人博客 **<https://jianganghan.github.io/>** 的源码。记录学过的、做过的，和正在学、正在做的东西。文章按专题组织，每篇都有中英两个版本。

## 专题

- **[用不可靠的模型，搭可靠的系统](https://jianganghan.github.io/zh/posts/reliability/index.html)**（两篇）：从冯·诺依曼 1952 年关于冗余的讲座，讲到模型的错误彼此相关时，为什么多加几道检查就不够了。
- **[定价优化入门](https://jianganghan.github.io/zh/posts/pricing/index.html)**（四篇）：定价的数学，从单个对象，到业务约束、替代品，再到大规模求解。
- **[广告出价入门](https://jianganghan.github.io/zh/posts/bidding/index.html)**（三篇）：站在广告主一侧看广告拍卖的出价：一次拍卖、一天的预算，以及预算平滑。

## 怎么搭的

不用框架，也没有依赖。文章用 Markdown 写，`build.py`（只用 Python 标准库）把每篇转成两个 HTML 页面，一种语言一页、各有各的网址：英文在站点根目录，中文在 `/zh/` 下，两边用 `hreflang` 关联，右上角有互相跳转的链接。公式在浏览器里由 KaTeX 排版。`build.py` 同时生成 `sitemap.xml` 和 `robots.txt`。GitHub Pages 原样发布这些文件，所以生成的 HTML 要和 Markdown 一起提交。

```
_home.html               首页源文件：专题列表，中英写在一起，手工维护
index.html               生成的英文首页（中文首页是 zh/index.html）
404.html                 访问不存在的地址时 GitHub Pages 显示这一页，只有英文
build.py                 posts/**/*.md → .html，另外生成 sitemap.xml 和 robots.txt
posts/<专题>/xxx.md      中文版  → zh/posts/<专题>/xxx.html
posts/<专题>/xxx.en.md   英文版  → posts/<专题>/xxx.html
posts/<专题>/images/     配图，中英各一份 SVG（figN.svg / figN.en.svg）
assets/css/              style.css（全站样式，配色在最上面）、article.css（文章页）
assets/js/               zoom.js（配图点击放大）
```

## 写文章

1. 在 `posts/<专题>/` 下写 `xxx.md`（中文）和 `xxx.en.md`（英文）。
2. 运行 `python3 build.py` 重新生成 HTML（加 `--check` 只检查不写文件）。
3. 新专题或新分篇，要加到 `_home.html`（不是 `index.html`，那个是生成的）：可见文字是英文版，`data-zh` 写中文版；阅读时长和文章里保持一致。

`build.py` 只支持本站用到的 Markdown 语法。几条约定：

- `# 标题` 后面的第一个引用块是导语，会加高亮；二、三级标题不少于 3 个时，导语后面自动生成目录。
- 公式写在 `$...$` 或 `$$...$$` 里。
- 站内链接：中文篇里写 `xxx.md`，英文篇里写 `xxx.en.md`，构建时都变成 `xxx.html`，各自落在本语言的目录树里。
- 可折叠内容用 `<details>` 和 `<summary>`，标签各占一行。

## 本地预览

```bash
python3 build.py
python3 -m http.server 8080    # 然后打开 http://localhost:8080（中文在 /zh/）
```

## 许可

代码（`build.py` 和 `assets/`）采用 [MIT 许可证](LICENSE)。`posts/` 下的文章和配图采用 [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/deed.zh-hans)：注明出处即可转载和改编，但不得用于商业用途。
