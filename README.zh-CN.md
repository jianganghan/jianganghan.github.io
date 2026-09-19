# jianganghan.github.io

[English](README.md) | 中文

个人博客 **<https://jianganghan.github.io/>** 的源码。记录学过的、做过的，和正在学、正在做的东西。文章按专题组织，每篇都有中英两个版本。

## 专题

- **[用不可靠的模型，搭可靠的系统](https://jianganghan.github.io/posts/reliability/index.html)**（两篇）：从冯·诺依曼 1952 年关于冗余的讲座，讲到模型的错误彼此相关时，为什么多加几道检查就不够了。
- **[定价优化入门](https://jianganghan.github.io/posts/pricing/index.html)**（四篇）：定价的数学，从单个对象，到业务约束、替代品，再到大规模求解。
- **[广告出价入门](https://jianganghan.github.io/posts/bidding/index.html)**（三篇）：站在广告主一侧看广告拍卖的出价：一次拍卖、一天的预算，以及预算平滑。

## 怎么搭的

不用框架，也没有依赖。文章用 Markdown 写，`build.py`（只用 Python 标准库）把每篇转成一个 HTML 页面，中英两版都在里面，右上角按钮原地切换。公式在浏览器里由 KaTeX 排版。GitHub Pages 原样发布这些文件，所以生成的 HTML 要和 Markdown 一起提交。

```
index.html               首页：专题列表，手工维护
404.html                 访问不存在的地址时，GitHub Pages 显示这个页面
build.py                 posts/**/*.md → .html
posts/<专题>/xxx.md      中文版
posts/<专题>/xxx.en.md   英文版，和中文渲染进同一个 xxx.html
posts/<专题>/images/     配图，中英各一份 SVG（figN.svg / figN.en.svg）
assets/css/              style.css（全站样式，配色在最上面）、article.css（文章页）
assets/js/               lang.js（中英切换）、zoom.js（配图点击放大）
```

## 写文章

1. 在 `posts/<专题>/` 下写 `xxx.md`（中文）和 `xxx.en.md`（英文）。
2. 运行 `python3 build.py` 重新生成 HTML（加 `--check` 只检查不写文件）。
3. 新专题或新分篇，要加到 `index.html`：可见文字是英文版，`data-zh` 写中文版；阅读时长和文章里保持一致。

`build.py` 只支持本站用到的 Markdown 语法。几条约定：

- `# 标题` 后面的第一个引用块是导语，会加高亮；二、三级标题不少于 3 个时，导语后面自动生成目录。
- 公式写在 `$...$` 或 `$$...$$` 里。
- 站内链接写 `xxx.md` 或 `xxx.en.md`，构建时都改成 `xxx.html`。
- 可折叠内容用 `<details>` 和 `<summary>`，标签各占一行。

## 本地预览

```bash
python3 build.py
python3 -m http.server 8080    # 然后打开 http://localhost:8080
```

## 许可

代码（`build.py` 和 `assets/`）采用 [MIT 许可证](LICENSE)。`posts/` 下的文章和配图采用 [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/deed.zh-hans)：注明出处即可转载和改编，但不得用于商业用途。
