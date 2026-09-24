---
date: 2026-09-20
---
# 用不可靠的模型，搭可靠的系统

> 关于 AI 系统可靠性的一组短文。每次调用模型都可能出错，我们想要的却是几乎不出错的系统。这个问题，冯·诺依曼七十多年前就认真研究过。

专题从冯·诺依曼 1952 年的讲座讲起：他在元件各自独立出错的前提下，证明了冗余可以换来任意高的可靠性。第 2 篇讨论大模型的错误并不独立时，这个结论会变成什么样。两篇都能单独读。

---

## 一句话主线

冯·诺依曼证明了：只要各处的错误互相独立，冗余就能换来任意高的可靠性。他也明确写下，这个假设并不现实，然后把它搁在了一边。大模型的错误却常常不独立：同一道题，每次都容易错在同一个地方。这时再多的冗余，收益也会越来越小，甚至封顶；**更有效的办法，是让错误彼此去相关。**

---

## 1952 年的问题，和今天的问题

冯·诺依曼构造里的部件，几乎都能在今天的 AI 系统里找到对应：

| 冯·诺依曼（1952） | 今天的大模型系统 |
|---|---|
| 元件，每次操作以概率 ε 出错 | 一次模型调用，有一定概率答错 |
| 很长的操作链，他称之为「推理链」 | 多步推理，agent 一步接一步地执行任务 |
| 多数表决器 | 多次采样后投票（self-consistency，Wang 等，2023） |
| 执行器官：完成运算本身 | 干活的那次调用：生成、改写、调用工具 |
| 恢复器官：把退化的信号拉回来 | 验证器、LLM 评审、结果聚合 |
| 一束 N 根线，加上判定阈值 Δ | 多份候选答案，加上「采纳哪一个」的规则 |
| 随机置换：让错误互相独立 | 换提示词、换模型、调高温度、换证据来源 |
| 「机器会记住自己的错误，并一直延续下去」 | 错误写进上下文，之后被反复引用 |
| 门槛 ε < 1/6：元件太差，表决无效 | 二选一的问题，单次答对率要过半，投票才有用 |

## 哪里不一样

对照表容易让人以为这就是同一个问题。其实有四处关键的不同：

- **错误相关。** 冯·诺依曼的元件各自独立地出错。同一个模型面对同一道题，却常常错在同一个地方：题目难在哪里，每次调用就在哪里栽跟头。
- **输出不是 0 和 1。** 线束里每根线只有两种状态，谁是多数一目了然。开放式的回答没有天然的「多数」，得先判断两个答案说的是不是一回事。
- **出错率不是常数。** 他假设每个元件都有同一个 ε，并在讲稿最后承认这不现实。模型的出错率取决于题目：简单题几乎不错，难题可能多数时候都错。
- **检查者和被检查者是同一种东西。** 冯·诺依曼的恢复器官也会出错，这一点和今天一样；但它的错误和执行器官相互独立，这一点不一样。用模型检查模型，检查者往往和生成者有同样的盲区。

第 1 篇讲他在独立假设下得到了什么，第 2 篇讲这个假设不成立时会发生什么。

---

## 两篇讲什么

### [一 · 冯·诺依曼 1952：多数表决、阈值与多路复用](1-von-neumann.md)　`18 分钟`

**回答的问题**：用每次都可能出错的元件，能不能搭出一台几乎不出错的机器？

从 1948 年他第一次提出这个问题讲起。先推出多数表决器的误差映射，得到 1/6 这道门槛；再看为什么逐层三重化的成本是 $3^\mu$，根本造不出来，而把一根线换成一束线就行得通。最后回到他在讲稿里明确搁置的那个假设：错误互相独立。

**读完能带走**：多数表决能纠错的两个条件，1/6 这道门槛从哪来，以及冯·诺依曼的整个构造为什么都建立在独立性上。

### [二 · 多加几道检查，为什么不够：相关错误与验证天花板](2-verifier-cascades.md)　`20 分钟`

**回答的问题**：验证器和生成器有共同的盲区时，一道接一道地加检查，可靠性还能涨多少？

如果各道检查独立，每多一道，答对与答错的几率就乘上一个固定的倍数，出错率按指数下降。错误一旦相关，能连过好几道检查的错答，恰恰是检查者看不出的那些，后面的检查就越来越不管用：出错率只按多项式下降，可靠性可能停在一道天花板之下；检查者还会冤枉正确答案时，检查加多了甚至会不升反降。这一篇是我的论文 [arXiv:2607.13918](https://arxiv.org/abs/2607.13918) 的通俗版。

**读完能带走**：幸存者偏差这个核心图像，独立假设会把出错率低估多少，为什么让检查者和生成者去相关（换模型、换模态、换证据来源）比一味加检查更有效，以及怎样用「同一个答案判两次」估计这种相关性。

---

## 公式速查

**第 1 篇**

| 场景 | 结论 |
|---|---|
| 记忆单元，每步以概率 ε 翻转 | $p_s - \tfrac12 = (1-2\varepsilon)^s\,(p_0 - \tfrac12)$ |
| 信号走单根线时的精度下限 | $\delta \ge \varepsilon$ |
| 多数表决，一般情形 | 输出出错概率 $\le \varepsilon + \eta_1 + \eta_2 + \eta_3$ |
| 多数表决，输入独立出错且本该一致 | $f_\varepsilon(\eta) = \varepsilon + (1-2\varepsilon)(3\eta^2 - 2\eta^3)$ |
| 反复表决后的稳定误差 | $\eta_0 = \tfrac12\bigl(1 - \sqrt{(1-6\varepsilon)/(1-2\varepsilon)}\bigr) = \varepsilon + 3\varepsilon^2 + \cdots$ |
| 表决有效的门槛 | $\varepsilon < 1/6$，即 $f_\varepsilon'(\tfrac12) = \tfrac32(1-2\varepsilon) > 1$ |
| 单线方案的严格证明 | 需要 $\varepsilon < 0.0073$，误差上界 $\approx 4\varepsilon + 152\varepsilon^2$，元件数乘以 $3^\mu$ |
| 恢复器官 | $\alpha^* = 3\alpha^2 - 2\alpha^3$ |
| 多路复用（Sheffer 元件，Δ = 0.07） | 需要 $\varepsilon < 0.0107$；$\varepsilon = 0.005$ 时失效概率 $\approx Q(0.062\sqrt N)$，元件数乘以约 $3N$ |

$Q(\kappa)$ 是标准正态变量大于 κ 的概率。

**第 2 篇**

| 场景 | 结论 |
|---|---|
| 错误独立，每道检查以概率 α 放行错答 | $o_k = o_0 / \alpha^k$，出错率按指数下降 |
| 错答的 α 因题而异，α ~ G | $o_k = o_0 / m_k$，$r_k = p_0 / \bigl(p_0 + (1-p_0)\,m_k\bigr)$，$m_k = \mathbb E[\alpha^k]$ |
| 相关系数 | $\rho_v = \operatorname{Var}(\alpha) / \bigl(\bar\alpha(1-\bar\alpha)\bigr)$；Beta(a, b) 时为 $1/(a+b+1)$ |
| 第 $j+1$ 道检查带来的证据 | $\ln(m_j/m_{j+1})$，随 $j$ 递减，$\ln o_k$ 是凹函数 |
| α 在 1 附近的密度像 $(1-\alpha)^{b-1}$ | $1 - r_k \sim C\,k^{-b}$，多项式下降 |
| 盲区：比例 $1-\pi$ 的错答 α = 1 | $r_\infty = p_0 / \bigl(p_0 + (1-p_0)(1-\pi)\bigr) < 1$ |
| 检查者也冤枉正确答案，β ~ H | $\ln o_k = \ln o_0 + \ln \mathbb E[\beta^k] - \ln \mathbb E[\alpha^k] \approx \text{常数} + (b_\alpha - b_\beta)\ln k$ |
| 两侧都是 Beta 时的拐点 | $k^\dagger = (a_\alpha b_\beta - a_\beta b_\alpha)/(b_\alpha - b_\beta)$ |
| 每个错答判两次 | $\hat m_1 = q_2 + q_1/2$，$\hat m_2 = q_2$，$\hat\rho_v = (\hat m_2 - \hat m_1^2)/\bigl(\hat m_1(1-\hat m_1)\bigr)$ |

---

## 参考文献

1. John von Neumann. [Probabilistic Logics and the Synthesis of Reliable Organisms from Unreliable Components](https://static.ias.edu/pitp/archive/2012files/Probabilistic_Logics.pdf). In C. E. Shannon, J. McCarthy (eds.), *Automata Studies*, Annals of Mathematics Studies 34, pp. 43–98. Princeton University Press, 1956.
2. John von Neumann. The General and Logical Theory of Automata. In L. A. Jeffress (ed.), *Cerebral Mechanisms in Behavior: The Hixon Symposium*, pp. 1–41. Wiley, 1951.
3. Jiangang Han. [Partially Correlated Verifier Cascades in LLM Harnesses: Concave Log-Odds, Polynomial Reliability, and Blind-Spot Ceilings](https://arxiv.org/abs/2607.13918). arXiv:2607.13918, 2026.
4. Hidayet Aksu. [Odds Law: The Decomposition Algebra on How Intelligence Organizes Itself to Solve Difficult Problems Reliably](https://arxiv.org/abs/2606.15712). arXiv:2606.15712, 2026.
5. Ken Tsui. [Self-Correction Bench: Uncovering and Addressing the Self-Correction Blind Spot in Large Language Models](https://arxiv.org/abs/2507.02778). arXiv:2507.02778, 2025.
6. Jie Huang, Xinyun Chen, Swaroop Mishra, Huaixiu Steven Zheng, Adams Wei Yu, Xinying Song, Denny Zhou. [Large Language Models Cannot Self-Correct Reasoning Yet](https://arxiv.org/abs/2310.01798). ICLR 2024.
7. Krishna K. Ladha. Condorcet's Jury Theorem in Light of de Finetti's Theorem: Majority-Rule Voting with Correlated Votes. *Social Choice and Welfare*, 10(1):69–85, 1993.
8. Xuezhi Wang, Jason Wei, Dale Schuurmans, Quoc Le, Ed Chi, Sharan Narang, Aakanksha Chowdhery, Denny Zhou. [Self-Consistency Improves Chain of Thought Reasoning in Language Models](https://arxiv.org/abs/2203.11171). ICLR 2023.

---

*专题里所有图均由代码根据文中模型直接计算生成，非示意图。第 1 篇引用的数字都对照原文重新算过：不动点、0.73% 的临界值、多路复用的失效概率；恢复器官的模拟也按原文的构造实现。第 2 篇的表格和例子都由文中的闭式公式重新算过，与论文一致。如果你发现哪一步有问题，欢迎指出。*
