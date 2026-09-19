# A Primer on Price Optimization

> Four short posts that build up the math of price optimization one layer at a time: from **a single item**, to **many items at once**, to the **business constraints** that tie them together, and finally to **items that compete for the same demand**.

Every post comes with full derivations, figures, and notes on what each parameter means in your business and what tends to break once it goes live. The posts build on each other, but **each one stands on its own**, so start wherever you like.

---

## What the four posts cover

### [1 · Pricing a Single Product](1-single.en.md)　`12 min`

> One number to set. Raise the price and you make more on each sale, but fewer people buy — so profit traces an inverted U.

We find the top of that curve: the general condition the optimal price has to satisfy, two worked examples (linear and logit demand), and a marginal breakdown of what you gain and what you lose when you raise the price.

**Takeaways**: a pricing formula you can apply directly, plus a benchmark you can estimate without a calculator — the optimal price sits roughly halfway between your cost and the price at which nobody buys.

### [2 · Pricing Many Items Under Constraints](2-constraints.en.md)　`15 min`

> Going from one item to $N$ doesn't make the problem harder — it splits cleanly into $N$ independent small problems. What makes it hard is the business red line that ties all the prices back together.

First, why the problem breaks apart on its own when nothing links the items, and why that solution usually can't ship as is. Then we add the constraints no real business can avoid, and a **knob** appears.

**Takeaways**: a single scalar $\lambda$ (the shadow price) that you can bisect on to reach the optimum, and how to use that number itself to decide between price cuts, ad spend and budget allocation.

### [3 · Pricing Substitutable Products](3-substitution.en.md)　`13 min`

> Raise the price of one product and another one sells more — they're competing for the same demand. Once prices are linked like this, you can no longer set them one at a time.

We model substitution with a discrete choice model and derive the most elegant result of the series: **at the optimum, every product's marginal unit economics (what one more sale nets you) sits at the same water level**.

**Takeaways**: a pricing health check that needs no re-optimization — a single SQL query will do — and a counterintuitive result: moving every price by the same amount keeps the optimal structure intact, while applying the same percentage discount breaks it.

### [4 · Pricing at Scale](4-scale.en.md)　`10 min`

> At scale, closed-form solutions stop working. This post trades a little accuracy for tractability, and shows where that approximation quietly breaks down.

Real problems are $M$ user segments × $N$ items plus a pile of constraints, which calls for an optimization solver. This post covers linearization by Taylor expansion, **where it stops being valid**, and trust-region iterations, and ends with an honest list of what the series leaves out.

**Takeaways**: the standard way to turn a nonlinear pricing problem into a linear program (LP), and a validation routine for checking how large a price change the linear approximation can handle on your own data.

---

## Notation

Shared by all four posts. Each post also opens with a collapsible table of the symbols it introduces.

| Symbol | Meaning | In your business, this might be |
|---|---|---|
| $i, j$ | Index of a pricing unit (the thing being priced) | A SKU, a customer segment, a route, a plan tier |
| $p_i$ | Price of unit $i$, **the decision variable** | The number you actually get to change |
| $c_i$ | Unit cost of unit $i$, **a known constant** | Purchase cost, marginal cost to serve, cost per delivery |
| $u_i = p_i - c_i$ | Margin per order | What you make on each sale |
| $q_i(p_i)$ | Purchase probability / conversion rate | Impression → order, visit → purchase, quote → policy |
| $q_0$ | Probability of buying nothing | The user swiped away |
| $k_i$ | Price coefficient: the larger it is, the faster conversion drops when the price moves | The price term's coefficient in your demand model |
| $\Pi$ | Total profit (gross margin throughout this series, not revenue) | Your objective |
| $\lambda$ | Lagrange multiplier of the constraint | Shadow price: how much profit one extra order costs you |

A note on the "price coefficient": it's related to the price elasticity of economics, but it isn't the same thing. Elasticity is a ratio of two percentage changes; under logit demand it equals $-k\,p\,(1-q)$. This series sticks to the **price–demand curve** and the **price coefficient $k$**, which simply measures how steep that curve is.

---

## Formula cheat sheet

| Setting | Optimality condition |
|---|---|
| Single unit, general demand | $p^\star = c + \dfrac{q}{-q'}$ |
| Single unit, linear demand $q = a - bp$ | $p^\star = \dfrac{a}{2b} + \dfrac{c}{2} = \dfrac{p_{\max} + c}{2}$ |
| Single unit, logit demand | $p^\star - c = \dfrac{1}{k\,q_0}$ |
| $N$ units, no coupling | $p_i^\star = c_i + \dfrac{q_i}{-q_i'}$, each solved independently |
| $N$ units + total volume constraint | $p_i^\star = c_i - \lambda + \dfrac{q_i}{-q_i'}$, one $\lambda$ shared by all, found by bisection |
| One list (MNL), unconstrained | $u_j - \dfrac{1}{k_j} = \Pi$, the same for every $j$ |
| One list (MNL) + total volume constraint | $u_j - \dfrac{1}{k_j} = \Pi - \lambda q_0$, the same for every $j$ |
| MNL own-price derivative | $\dfrac{\partial q_j}{\partial p_j} = -k_jq_j(1-q_j)$ |
| MNL cross-price derivative | $\dfrac{\partial q_m}{\partial p_j} = k_jq_jq_m \quad (m\ne j)$ |
| MNL derivative of total volume | $\sum_m \dfrac{\partial q_m}{\partial p_j} = -k_jq_jq_0$ |
| Hessian of total conversion | $H_{ij} = \bigl(k_i^2q_i\delta_{ij} - 2k_ik_jq_iq_j\bigr)q_0$ |

---

## What this series doesn't cover

All four posts assume **you already have a reliable curve from price to purchase probability**, and ask how to set prices once you have it.

**Getting** that curve is actually the hardest and most error-prone step of the whole pipeline (the core difficulty is endogeneity: historical prices were not set at random). That, along with engineering large-scale solvers, dynamics and competition, uncertainty, and regulatory limits, is laid out honestly in [Section 4 of Part 4](4-scale.en.md#4-what-the-series-leaves-out).

---

## References

1. Guillermo Gallego, Ruxian Wang. [Multiproduct Price Optimization and Competition Under the Nested Logit Model with Product-Differentiated Price Sensitivities](https://pubsonline.informs.org/doi/10.1287/opre.2013.1249). Operations Research, 62(2):450–461, 2014.
2. Hongmin Li, Woonghee Tim Huh. [Pricing Multiple Products with the Multinomial Logit and Nested Logit Models: Concavity and Implications](https://pubsonline.informs.org/doi/10.1287/msom.1110.0344). Manufacturing & Service Operations Management, 13(4):549–563, 2011.

---

*Every figure in this series is computed directly from the models in the text; none of them are sketches. Every derivation has been checked numerically (gradients and Hessians against finite differences, optimal solutions cross-checked with two independent methods). If you spot a mistake, please let me know.*
