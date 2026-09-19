# Reliable Systems from Unreliable Models

> Short essays on the reliability of AI systems. Any call to a model can be wrong, yet what we want are systems that almost never are. Von Neumann took this problem seriously more than seventy years ago.

The series starts with von Neumann's 1952 lectures, where he showed that if components fail independently, redundancy can make a machine as reliable as you like. Part 2 asks what becomes of that result when, as with language models, the errors aren't independent. Each part stands on its own.

---

## The argument in brief

Von Neumann proved that as long as failures in different places are independent, redundancy buys arbitrarily high reliability. He also wrote down plainly that this assumption isn't realistic, and set it aside. Language models are a case where it often fails: a model tends to trip over the same part of a question every time it tries. Then each extra layer of redundancy helps less than the last, and the gains can stop altogether. **What works better is making the errors less correlated.**

---

## The 1952 problem and today's

Nearly every part of von Neumann's construction has a counterpart in today's AI systems:

| Von Neumann (1952) | LLM systems today |
|---|---|
| A component that fails with probability ε per operation | A model call that is wrong some of the time |
| A long chain of operations, his "chains of reasoning" | Multi-step reasoning; an agent working through a task |
| Majority organ | Sampling several answers and voting (self-consistency; Wang et al., 2023) |
| Executive organ: does the actual computation | The call that does the work: generating, rewriting, using a tool |
| Restoring organ: pulls a degraded signal back | A verifier, an LLM judge, an aggregator |
| A bundle of N lines read against a threshold Δ | A set of candidate answers and a rule for which to accept |
| Random permutation: keeps errors independent | Varying the prompt, the model, the temperature, the evidence |
| "The machine remembers its mistakes … and thereafter perpetuates them" | A mistake enters the context and keeps getting cited |
| Threshold ε < 1/6: below it, voting helps | For a yes/no question, voting helps only if one call is right more than half the time |

## Where the analogy breaks

The table makes it look like one and the same problem. There are four important differences:

- **Errors are correlated.** Von Neumann's components fail independently. A model facing the same question tends to fail in the same place each time, wherever the question is actually hard.
- **Outputs aren't 0 or 1.** Every line in a bundle has two states, so the majority is obvious. Open-ended answers have no built-in majority; first you have to decide whether two answers mean the same thing.
- **The error rate isn't a constant.** He gave every component the same ε, and admitted near the end of the paper that this is unrealistic. A model's error rate depends on the question: easy ones it almost never misses, hard ones it may get wrong most of the time.
- **The checker is made of the same stuff as the thing it checks.** Von Neumann's restoring organs fail too, just like today's checkers. But their failures are independent of the executive organs', and that part no longer holds. When a model checks a model, the checker often shares the generator's blind spots.

Part 1 covers what he got out of the independence assumption. Part 2 covers what happens when it breaks.

---

## What the two posts cover

### [1 · Von Neumann, 1952: Majority Voting, Thresholds, and Multiplexing](1-von-neumann.en.md)　`18 min`

**The question**: can you build a machine that almost never fails out of components that can fail on every operation?

It starts with the question as he first posed it in 1948. From the majority organ's error map comes the 1/6 threshold. Then it shows why stacking triplication layer by layer costs a factor of $3^\mu$ and could never be built, while replacing each line with a bundle of lines works. It ends with the assumption he explicitly set aside: that errors are independent.

**Takeaways**: the two conditions under which majority voting corrects errors, where the 1/6 threshold comes from, and why von Neumann's entire construction rests on independence.

### [2 · Why More Checks Stop Helping: Correlated Verifiers and the Reliability Ceiling](2-verifier-cascades.en.md)　`20 min`

**The question**: when a verifier shares blind spots with the generator it checks, how much does each additional check actually buy?

If checks are independent, each one multiplies the odds of a correct answer by the same factor, and the error rate falls exponentially. Once errors are correlated, the wrong answers that survive several checks are exactly the ones the checker can't see, so each further check does less. The error rate then falls only polynomially and reliability can stall below a ceiling; if the checker also rejects correct answers, past a certain point more checks make things worse. This post is a plain-language version of my paper [arXiv:2607.13918](https://arxiv.org/abs/2607.13918).

**Takeaways**: the survivorship picture at the heart of it, how far the independence assumption understates the failure rate, why decorrelating the checker from the generator (a different model, a different modality, a different source of evidence) beats piling on checks, and how to estimate that correlation by having the same answer judged twice.

---

## Formula cheat sheet

**Part 1**

| Setting | Result |
|---|---|
| Memory unit that flips with probability ε per step | $p_s - \tfrac12 = (1-2\varepsilon)^s\,(p_0 - \tfrac12)$ |
| Accuracy limit when signals travel on single lines | $\delta \ge \varepsilon$ |
| Majority organ, general case | Output wrong with probability $\le \varepsilon + \eta_1 + \eta_2 + \eta_3$ |
| Majority organ, inputs fail independently and should agree | $f_\varepsilon(\eta) = \varepsilon + (1-2\varepsilon)(3\eta^2 - 2\eta^3)$ |
| Stable error under repeated voting | $\eta_0 = \tfrac12\bigl(1 - \sqrt{(1-6\varepsilon)/(1-2\varepsilon)}\bigr) = \varepsilon + 3\varepsilon^2 + \cdots$ |
| Threshold for voting to help | $\varepsilon < 1/6$, equivalently $f_\varepsilon'(\tfrac12) = \tfrac32(1-2\varepsilon) > 1$ |
| Rigorous single-line construction | Needs $\varepsilon < 0.0073$; error bound $\approx 4\varepsilon + 152\varepsilon^2$; $3^\mu$ times the components |
| Restoring organ | $\alpha^* = 3\alpha^2 - 2\alpha^3$ |
| Multiplexing (Sheffer strokes, Δ = 0.07) | Needs $\varepsilon < 0.0107$; at $\varepsilon = 0.005$, malfunction probability $\approx Q(0.062\sqrt N)$; about $3N$ times the components |

$Q(\kappa)$ is the probability that a standard normal variable exceeds κ.

**Part 2**

| Setting | Result |
|---|---|
| Independent errors, each check accepts a wrong answer with probability α | $o_k = o_0 / \alpha^k$; failure falls exponentially |
| α varies across wrong answers, α ~ G | $o_k = o_0 / m_k$, $r_k = p_0 / \bigl(p_0 + (1-p_0)\,m_k\bigr)$, $m_k = \mathbb E[\alpha^k]$ |
| Correlation | $\rho_v = \operatorname{Var}(\alpha) / \bigl(\bar\alpha(1-\bar\alpha)\bigr)$; $1/(a+b+1)$ for Beta(a, b) |
| Evidence from check $j+1$ | $\ln(m_j/m_{j+1})$, decreasing in $j$, so $\ln o_k$ is concave |
| Density of α near 1 behaves like $(1-\alpha)^{b-1}$ | $1 - r_k \sim C\,k^{-b}$: polynomial decline |
| Blind spot: a share $1-\pi$ of wrong answers has α = 1 | $r_\infty = p_0 / \bigl(p_0 + (1-p_0)(1-\pi)\bigr) < 1$ |
| Checker also rejects correct answers, β ~ H | $\ln o_k = \ln o_0 + \ln \mathbb E[\beta^k] - \ln \mathbb E[\alpha^k] \approx \text{const} + (b_\alpha - b_\beta)\ln k$ |
| Turning point when both sides are Beta | $k^\dagger = (a_\alpha b_\beta - a_\beta b_\alpha)/(b_\alpha - b_\beta)$ |
| Two verdicts per wrong answer | $\hat m_1 = q_2 + q_1/2$, $\hat m_2 = q_2$, $\hat\rho_v = (\hat m_2 - \hat m_1^2)/\bigl(\hat m_1(1-\hat m_1)\bigr)$ |

---

## References

1. John von Neumann. [Probabilistic Logics and the Synthesis of Reliable Organisms from Unreliable Components](https://static.ias.edu/pitp/archive/2012files/Probabilistic_Logics.pdf). In C. E. Shannon, J. McCarthy (eds.), *Automata Studies*, Annals of Mathematics Studies 34, pp. 43–98. Princeton University Press, 1956.
2. John von Neumann. The General and Logical Theory of Automata. In L. A. Jeffress (ed.), *Cerebral Mechanisms in Behavior: The Hixon Symposium*, pp. 1–41. Wiley, 1951.
3. Jiangang Han. [Partially Correlated Verifier Cascades in LLM Harnesses: Concave Log-Odds, Polynomial Reliability, and Blind-Spot Ceilings](https://arxiv.org/abs/2607.13918). arXiv:2607.13918, 2026.
4. Hidayet Aksu. [Odds Law: The Decomposition Algebra on How Intelligence Organizes Itself to Solve Difficult Problems Reliably](https://arxiv.org/abs/2606.15712). arXiv:2606.15712, 2026.
5. Ken Tsui. [Self-Correction Bench: Uncovering and Addressing the Self-Correction Blind Spot in Large Language Models](https://arxiv.org/abs/2507.02778). arXiv:2507.02778, 2025.
6. Jie Huang, Xinyun Chen, Swaroop Mishra, Huaixiu Steven Zheng, Adams Wei Yu, Xinying Song, Denny Zhou. [Large Language Models Cannot Self-Correct Reasoning Yet](https://arxiv.org/abs/2310.01798). ICLR 2024.
7. Krishna K. Ladha. Condorcet's Jury Theorem in Light of de Finetti's Theorem: Majority-Rule Voting with Correlated Votes. *Social Choice and Welfare*, 10(1):69–85, 1993.
8. Xuezhi Wang, Jason Wei, Dale Schuurmans, Quoc Le, Ed Chi, Sharan Narang, Aakanksha Chowdhery, Denny Zhou. [Self-Consistency Improves Chain of Thought Reasoning in Language Models](https://arxiv.org/abs/2203.11171). ICLR 2023.

---

*Every figure in this series is computed directly from the models in the text; none of them are sketches. Every number quoted in Part 1 was recomputed against the original paper, including the fixed points, the 0.73% cutoff and the multiplexing malfunction probabilities, and the restoring-organ simulation follows his construction. The tables and examples in Part 2 were recomputed from the closed-form formulas and match the paper. If you spot a mistake, please let me know.*
