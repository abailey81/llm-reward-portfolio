# Paper Benchmark Extractions

First-hand extractions from the on-disk primary PDFs (read via PyMuPDF + image rendering of
formula regions where text extraction dropped math glyphs). Each entry gives: (1) bibliographic
coordinates verified off page 1; (2) the exact reward formula / allocator algorithm / evaluation
protocol with a short verbatim quote + page number; (3) a one-line mapping to this project's
per-step reward contract `reward(w, r, prev_w, port_ret, turnover)` or report-only comparator, and
whether it is deterministic + numpy-implementable.

Anything not located in the PDF is marked **NOT-FOUND** (no formula or coordinate is fabricated).
Verbatim quotes use straight quotes; em-dashes in source rendered as `--`. Symbols transcribed from
rendered page images are marked "(read from rendered page image)".

Source root: `c:\Users\User\Desktop\dissertation_papers\01_literature\`

---

## REWARDS

### 1. Moody & Saffell -- Learning to Trade via Direct Reinforcement (Differential Sharpe Ratio)

**File:** `H_manual_journal/MoodySaffell-DirectRL__2001.pdf` (15 pp.)

**Bibliographic coordinates (verified page 1):**
- Title: "Learning to Trade via Direct Reinforcement"
- Authors: John Moody and Matthew Saffell
- Venue: IEEE Transactions on Neural Networks, Vol. 12, No. 4, July 2001, pp. 875--889
- Affiliation: Computational Finance Program, Oregon Graduate Institute; Nonlinear Prediction Systems
- Publisher Item Identifier: S 1045-9227(01)05010-X (no DOI/arXiv printed)

**Exact formula -- Differential Sharpe Ratio (DSR), page 878, Eqs. (13)-(16)** (read from rendered page image):

The Sharpe ratio is expanded to first order in the adaptation rate eta:
> "S_t|_{eta>0} ~= S_t|_{eta=0} + eta dS_t/d eta|_{eta=0} + O(eta^2) = S_{t-1} + eta dS_t/d eta|_{eta=0} + O(eta^2)."  (Eq. 13)

The **differential Sharpe ratio** is the first-order term:

    D_t == dS_t/d eta = ( B_{t-1} * dA_t - (1/2) * A_{t-1} * dB_t ) / ( B_{t-1} - A_{t-1}^2 )^{3/2}     (Eq. 14)

where A_t, B_t are exponential moving estimates of the first and second moments of R_t:

    A_t = A_{t-1} + eta * dA_t = A_{t-1} + eta * (R_t - A_{t-1})
    B_t = B_{t-1} + eta * dB_t = B_{t-1} + eta * (R_t^2 - B_{t-1})            (Eq. 15)

with the increments dA_t = R_t - A_{t-1} and dB_t = R_t^2 - B_{t-1}. The learning-gradient form:

    dD_t/dR_t = ( B_{t-1} - A_{t-1} * R_t ) / ( B_{t-1} - A_{t-1}^2 )^{3/2}    (Eq. 16)

Verbatim (p. 878): "we define the differential Sharpe ratio as [Eq. 14] where the quantities A_t and
B_t are exponential moving estimates of the first and second moments of R_t [Eq. 15]." Also p. 878:
"The current return R_t enters expression (14) only in the numerator through dA_t = R_t - A_{t-1}
and dB_t = R_t^2 - B_{t-1}."

R_t is the trading return (Eqs. 5-8, pp. 877). Risk-free-adjusted form uses R~_t = R_t - R^f_t (p. 878,
footnote 6: for futures/forwards use R_t directly). Downside Deviation Ratio (DDR) variant: p. 879,
Eqs. (19)-(20): DD = sqrt(mean of squared negative returns); DDR = Average / DD.

**Mapping to project:** DIRECT per-step reward. Set R_t = port_ret (or port_ret - rf), keep running
A_{t-1}, B_{t-1} state; emit D_t (Eq. 14) as the step reward. DETERMINISTIC + numpy-implementable
(scalar recurrence; only requires carrying A, B and choosing eta). This is the canonical online
risk-adjusted reward and the most natural scalar comparator for the reward channel.

---

### 2. Markowitz -- Portfolio Selection (Mean-Variance)

**File:** `H_manual_journal/Markowitz-PortfolioSelection__1952.pdf` (16 pp.)

**Bibliographic coordinates (verified page 1, JSTOR cover):**
- Title: "Portfolio Selection"
- Author: Harry Markowitz (The Rand Corporation; work done at Cowles Commission)
- Venue: The Journal of Finance, Vol. 7, No. 1 (March 1952), pp. 77--91
- Publisher: American Finance Association
- Stable URL (JSTOR): sici 0022-1082(195203)7:1<77:PS>2.0.CO;2-1 (no DOI printed)

**Exact formulas -- the E-V rule, page 81** (read from rendered page image; the 1952 scan stores
display equations as images, so transcribed visually):

Portfolio return is a weighted sum of asset returns:

    R = sum_i R_i X_i

Expected return of the portfolio:

    E = sum_{i=1}^N X_i mu_i                                  (p.81)

Portfolio variance:

    V = sum_{i=1}^N sum_{j=1}^N sigma_ij X_i X_j              (p.81)

(NOTE: the last factor prints as "X_i X" with the trailing subscript j clipped in the original
typesetting; the unambiguous reading from the derivation immediately above -- V(R) = sum_i sum_j
a_i a_j sigma_ij -- is X_i X_j.) Constraints stated p.81: "Since the X_i are percentages we have
sum X_i = 1 ... we will exclude negative values of the X_i (i.e., short sales); therefore X_i >= 0
for all i." Covariance definition p.80: sigma_ij = rho_ij * sigma_i * sigma_j.

Verbatim (p.81): "the expected return E from the portfolio as a whole is [E = sum X_i mu_i] and the
variance is [V = sum_i sum_j sigma_ij X_i X_j]." The E-V rule itself (p.79): "the investor does (or
should) consider expected return a desirable thing and variance of return an undesirable thing."

**Mapping to project:** NOT a per-step reward in raw form (it is a one-shot allocator objective).
Two uses: (a) REPORT-ONLY comparator -- the mean-variance / minimum-variance / tangency portfolio as
an allocator baseline (max_w mu'w - (gamma/2) w'Sigma w, long-only sum w = 1); (b) a single-step
reward of the form port_ret - (gamma/2)*variance-proxy. The allocator is DETERMINISTIC + numpy-
implementable given mu and Sigma (quadratic program via `scipy.optimize` / closed form for min-var).

---

### 3. Rockafellar & Uryasev -- Optimization of Conditional Value-at-Risk (CVaR)

**File:** `H_manual_journal/RockafellarUryasev-CVaR__2000.pdf` (26 pp.)

**Bibliographic coordinates (verified page 1):**
- Title: "Optimization of Conditional Value-at-Risk"
- Authors: R. Tyrrell Rockafellar (Univ. of Washington, Applied Mathematics) and Stanislav Uryasev
  (Univ. of Florida, Industrial & Systems Engineering)
- Dated: September 5, 1999 (filename "2000" = published year in Journal of Risk, NOT printed in this
  PDF). **Journal coordinates (Journal of Risk, 2(3):21--41) NOT-FOUND in the PDF** -- this is the
  working-paper version; no DOI/volume/pages printed.

**Exact formulas (text extracted cleanly):**

beta-VaR (Eq. 2, p.4):  alpha_beta(x) = min { alpha in R : Psi(x, alpha) >= beta }
where Psi(x, alpha) = integral over {f(x,y) <= alpha} of p(y) dy   (Eq. 1, the loss CDF)

beta-CVaR (Eq. 3, p.4):  phi_beta(x) = (1 - beta)^{-1} * integral over {f(x,y) >= alpha_beta(x)} of
f(x,y) p(y) dy

The key auxiliary function (Eq. 4, p.5):

    F_beta(x, alpha) = alpha + (1 - beta)^{-1} * integral_{y in R^m} [ f(x,y) - alpha ]^+ p(y) dy

where [t]^+ = t if t > 0, else 0. Theorem 1 (p.5): phi_beta(x) = min_{alpha in R} F_beta(x, alpha)
(Eq. 5), and beta-VaR is the left endpoint of argmin_alpha F_beta (Eqs. 6-7).

**Sample/scenario approximation (Eq. 9, p.6)** -- the directly implementable estimator:

    F~_beta(x, alpha) = alpha + ( 1 / (q (1 - beta)) ) * sum_{k=1}^q [ f(x, y_k) - alpha ]^+

"convex and piecewise linear with respect to alpha." Theorem 2 (Eq. 10, p.6): minimizing beta-CVaR
over x is equivalent to jointly minimizing F_beta(x, alpha) over (x, alpha).

Verbatim (p.5): "Fbeta(x, alpha) = alpha + (1 - beta)^{-1} integral ... [f(x,y) - alpha]^+ p(y) dy"
(Eq. 4). Verbatim (p.6): "the corresponding approximation to Fbeta(x, alpha) is F~beta(x, alpha) =
alpha + 1/(q(1-beta)) sum_{k=1}^q [f(x, y_k) - alpha]^+" (Eq. 9).

**Mapping to project:** The losses here are f(x,y); for portfolio returns set f = -port_ret. The
Rockafellar-Uryasev sample estimator (Eq. 9) is exactly the numpy CVaR computation
(`alpha + mean(relu(losses - alpha))/(1-beta)`, then minimize over alpha, OR empirically:
mean of the worst (1-beta) tail of -returns). For the per-step risk-sensitive reward, a window-CVaR
penalty term (reward = port_ret - lambda * CVaR_beta(recent losses)) is the canonical construction;
DETERMINISTIC + numpy-implementable. This is the gold-standard tail-risk definition for the H2-Tail
co-primary (CVaR-5%). beta is the confidence level (e.g. 0.95 => 5% tail).

---

### 4. Jiang, Xu & Liang -- Deep Portfolio Management / EIIE (portfolio-RL reward + cost model)

**File:** `H_foundational_canon/DeepRL-Portfolio-Mgmt-EIIE-Jiang__1706.10059.pdf` (31 pp.)

**Bibliographic coordinates (verified page 1):**
- Title: "A Deep Reinforcement Learning Framework for the Financial Portfolio Management Problem"
  (running title "Deep Portfolio Management")
- Authors: Zhengyao Jiang, Dixing Xu, Jinjun Liang (Xi'an Jiaotong-Liverpool University, Suzhou, China)
- arXiv: arXiv:1706.10059v2 [q-fin.CP], 16 Jul 2017 (preprint; no journal venue printed)

**Exact formulas (text extracted cleanly):**

Period rate of return (Eq. 3, p.5):  rho_t = p_t/p_{t-1} - 1 = y_t . w_{t-1} - 1
Log return, no cost (Eq. 4, p.5):    r_t = ln(p_t/p_{t-1}) = ln(y_t . w_{t-1})
  where y_t is the price-relative vector (close/open quotients) and w_{t-1} the portfolio weights.

Weights drift over the period (Eq. 7, p.5):  w'_t = (y_t (elementwise*) w_{t-1}) / (y_t . w_{t-1})

With transaction cost (Eqs. 9-10, p.6):
    rho_t = mu_t * y_t . w_{t-1} - 1
    r_t   = ln( mu_t * y_t . w_{t-1} )
where mu_t in (0,1] is the **transaction remainder factor** (portfolio shrinkage from rebalancing
w'_t -> w_t). mu_t solves the implicit equation (Eq. 13 simplified, p.7):

    mu_t = (1 / (1 - c_p w_{t,0})) * [ 1 - c_p w'_{t,0} - (c_s + c_p - c_s c_p) * sum_i ( w'_{t,i} -
           mu_t w_{t,i} )^+ ]

with c_s, c_p the sell/buy commission rates; solved by fixed-point iteration (a common approximation
is mu_t = c * sum_i |w'_{t,i} - w_{t,i}| with single rate c).

**The explicit RL reward (Eq. 21, p.11)** -- "average logarithmic cumulated return R":

    R = (1/t_f) * ln(p_f/p_0) = (1/t_f) * sum_{t=1}^{t_f+1} ln( mu_t * y_t . w_{t-1} )

Verbatim (p.11): "this job is equivalent to maximizing the average logarithmic cumulated return R,
R(...) := (1/t_f) ln(p_f/p_0) = (1/t_f) sum_{t=1}^{t_f+1} ln(mu_t y_t . w_{t-1})" (Eq. 21). Verbatim
(p.4 abstract/intro): "The reward function of the RL framework is the explicit average of the periodic
logarithmic returns."

**Mapping to project:** DIRECT match to the per-step reward contract. The per-step reward is exactly
r_t = ln(mu_t * y_t . w_{t-1}) -- i.e. ln(port_ret_gross) net of the cost factor mu_t computed from
turnover (the |w' - w| trades). This is the project's baseline/risk-neutral reward
(`reward = log(1 + port_ret - cost(turnover))`). DETERMINISTIC + numpy-implementable (mu_t via
fixed-point or the linear turnover approximation). This is the canonical portfolio-RL reward and the
natural risk-neutral comparator against which risk-sensitive rewards are measured.

---

## ALLOCATORS

### 5. DeMiguel, Garlappi & Uppal -- 1/N (Optimal Versus Naive Diversification)

**File:** `H_manual_journal/DeMiguel-1overN__2009.pdf` (this PDF is the **June 2006 working-paper
draft**, not the published version)

**Bibliographic coordinates (verified page 1):**
- Title on draft: "1/N" (earlier circulated as "How Inefficient is the 1/N Asset-Allocation Strategy?")
- Authors: Victor DeMiguel, Lorenzo Garlappi, Raman Uppal
- Draft date: "First draft: March 2005 / This draft: June 2006"
- **Journal coordinates NOT-FOUND in PDF.** (Canonical published cite, sourced externally, NOT off this
  PDF: Review of Financial Studies 22(5):1915--1953, 2009. Do not quote vol/pages as read from this file.)

**1/N rule (Section 2.1, p.5):** w^ew = 1/N in each of N risky assets. Verbatim: "The naive strategy
that we consider involves holding a portfolio weight w^ew_t = 1/N in each of the N risky assets. This
strategy does not involve any optimization or estimation and completely ignores the data."

**Benchmark protocol (p.2; Table 1, p.40):** "We compare the out-of-sample performance of fourteen
different portfolio models relative to that of the 1/N policy across seven empirical datasets of
monthly returns, using the following three performance criteria: (i) the out-of-sample Sharpe ratio;
(ii) the certainty-equivalent return (CEQ) ...; and (iii) the turnover." The 14 models span: classical
mean-variance (mv), Bayesian (bs Bayes-Stein, dm data-and-model), moment-restriction (min minimum-
variance, vw value-weighted, mp missing-factor), constrained variants (mv-c, bs-c, min-c, g-min-c),
and portfolio combinations (mv-min Kan-Zhou three-fund, ew-min).

**Three evaluation metrics (Section 3, formulas confirmed by image render):**
- Out-of-sample Sharpe ratio (Eq. 10, p.11): SR_k = mu_hat_k / sigma_hat_k (mean / std of OOS excess
  returns).
- Certainty-equivalent return (Eq. 12, p.12): CEQ_k = mu_hat_k - (gamma/2) * sigma_hat_k^2 (reported
  with gamma = 1).
- Turnover (Eq. 13, p.12): Turnover = (1/(T-M)) * sum_{t=1}^{T-M} sum_{j=1}^N | w_hat_{k,j,t+1} -
  w_hat_{k,j,t+} |  -- "the average percentage of wealth traded in each period."

**Rolling-window protocol (Section 3, pp.10-11):** "given a T-month long dataset ... we choose an
estimation window of length M = 60 or M = 120 months. In each month t, starting from t = M, we use the
data in the previous M months to estimate the parameters ... compute the return in month t + 1 ...
adding the return for the next period ... and dropping the earliest return." Headline results use M = 120.

**Mapping to project:** 1/N is a REPORT-ONLY allocator baseline (w_i = 1/N, trivially DETERMINISTIC +
numpy). The three metrics (OOS Sharpe, CEQ, turnover Eq. 13) are the project's report-only comparator
metrics; the turnover formula maps directly to the project's `turnover` term. The rolling-window
protocol corroborates the walk-forward evaluation design.

---

### 6. Equal Risk Contribution / Risk Parity -- **FILE MISIDENTIFIED**

**File:** `H_manual_journal/Maillard-RiskParity__2010.pdf`

**CRITICAL FINDING:** This PDF is **NOT** the Maillard-Roncalli-Teiletche paper. The on-disk document
is Cagna & Casuccio, "Equally-weighted Risk Contribution Portfolios: an empirical study using expected
shortfall," CeRP Working Paper 142/14 (2014). The genuine Maillard paper appears only as reference [15]
in its bibliography: "Maillard S., Roncalli T. and Teiletche J., 2009, On the properties of equally
weighted risk contributions portfolios, Journal of Portfolio Management, 37, No. 4" (p.17).

**Maillard formulas (sigma_i = x_i (Sigma x)_i / sqrt(x'Sigma x), the equal-correlation closed form
w_i proportional to 1/sigma_i, the SQP min sum_{i,j}(RC_i - RC_j)^2): NOT-FOUND in this PDF.** They
must be sourced from the actual Maillard paper, which is not on disk under this name.

**What IS in the file (citable as an ES-based ERC extension):**
- Risk-contribution definition (Eq. 1, p.6): RC_i(w) = w_i * d rho(w)/d w_i; ERC condition RC_i = RC_j
  for all i,j.
- ES contribution (Eq. 8, p.7): RC^{ES_alpha}_i(w) = -w_i * E[ R_i | w'R <= VaR_alpha(w) ].
- Gaussian ES closed form (Eq. 5, p.5): ES_alpha(w) = -w'mu - (sqrt(w'Sigma w)/alpha)*phi(Phi^{-1}(alpha)).
- ERC optimization actually solved (Eq. 9, pp.6-7): min_w sum_i sum_j (RC_i(w) - RC_j(w))^2 via SQP
  (Matlab fmincon), long-only, leverage allowed.

**Mapping to project:** ERC / risk-parity is a REPORT-ONLY allocator. The standard-deviation ERC
(min sum (x_i(Sigma x)_i - x_j(Sigma x)_j)^2) is DETERMINISTIC + numpy/scipy-implementable
(`scipy.optimize.minimize(method='SLSQP')` or fixed-point Newton). If citing Maillard's exact
closed forms, source the real paper -- do not cite this file for them.

---

### 7. Lopez de Prado -- Hierarchical Risk Parity (HRP)

**File:** `H_manual_journal/LopezDePrado-HRP__2016.pdf` (31 pp.; **SSRN working-paper version**,
abstract id 2708678)

**Bibliographic coordinates (verified page 1):**
- Title: "Building Diversified Portfolios that Outperform Out-of-Sample"
- Author: Marcos Lopez de Prado (Guggenheim Partners; Lawrence Berkeley National Laboratory)
- Versions: "First version: December 25, 2015 / This version: May 23, 2016"
- **Journal coordinates + DOI NOT-FOUND in PDF** (SSRN preprint; only ssrn.com/abstract=2708678 in
  footer). Published cite (Journal of Portfolio Management, sourced externally) is NOT in this file.

**Three-stage algorithm (verbatim p.4: "Tree clustering, quasi-diagonalization and recursive bisection"):**
- (a) Tree clustering (pp.4-7): correlation-distance d_{i,j} = sqrt( 0.5 * (1 - rho_{i,j}) ); then a
  "distance of distances" d~_{i,j} = sqrt( sum_n (d_{n,i} - d_{n,j})^2 ); cluster the pair minimizing
  d~ via single linkage (nearest-point), recursing N-1 times (scipy `sch.linkage(dist,'single')`).
- (b) Quasi-diagonalization (p.6, Code snippet 1): reorder rows/cols of the covariance matrix by the
  cluster tree so large values sit on the diagonal (no change of basis).
- (c) Recursive bisection (pp.7-8, Code snippet 2): top-down. Split each cluster L_i into halves
  (|L_i^(1)| = int[0.5|L_i|]); within-cluster inverse-variance weights w~ = diag[V]^{-1} / tr(diag[V]^{-1});
  cluster variance V~ = w~' V w~; split factor alpha_i = 1 - V~^(1)/(V~^(1)+V~^(2)); scale the two
  sub-allocations by alpha_i and (1-alpha_i). "solves the allocation problem in deterministic
  logarithmic time, T(n) = O(log2 n)" (p.8).

**Code listings:** Code snippet 1 (getQuasiDiag) p.6; Code snippet 2 (getRecBipart) pp.7-8; full
reproducible example Appendix A.3 (pp.13-15; getIVP, getClusterVar, getQuasiDiag, getRecBipart,
correlDist). **Benchmark (pp.9-10):** Monte Carlo OOS variance sigma^2_CLA=0.1157, sigma^2_IVP=0.0928,
sigma^2_HRP=0.0671; "HRP would improve the out-of-sample Sharpe ratio of a CLA strategy by about 31.3%."

**Mapping to project:** REPORT-ONLY allocator baseline. HRP is explicitly DETERMINISTIC (the paper says
so) + numpy/scipy-implementable using only numpy/pandas/scipy.cluster.hierarchy; does not require
covariance invertibility. Strong diversified comparator alongside 1/N and ERC.

---

### 8. Black & Litterman -- Global Portfolio Optimization (BL posterior)

**File:** `H_manual_journal/BlackLitterman__1992.pdf` (16 pp.; ProQuest/ABI-INFORM scan -- body is image,
formulas transcribed from rendered page images)

**Bibliographic coordinates (verified page 1 / cover):**
- Title: "Global Portfolio Optimization"
- Authors: Fischer Black and Robert Litterman
- Venue: Financial Analysts Journal, Sep/Oct 1992, Vol. 48, No. 5, pp. 28--43
- "Copyright 1991 by Goldman Sachs." printed at foot of p.28. **No DOI printed.**

**KEY FINDING (corrects common belief): the explicit matrix master posterior formula IS printed in this
1992 paper**, in the Appendix item 8 (journal p.42). Verbatim (transcribed from rendered image):

    E[R] = [ (tau*Sigma)^{-1} + P' Omega^{-1} P ]^{-1} [ (tau*Sigma)^{-1} Pi + P' Omega^{-1} Q ]   (App. item 8, p.42)

(The scan's bracketing of the second term has a print artifact -- it renders "tau*Sigma^{-1} Pi" -- but
the canonical reading consistent with item 7 is (tau*Sigma)^{-1} Pi.)

Supporting structure (Appendix, p.42):
- Equilibrium risk premia (item 6): Pi = delta * Sigma * W (reverse optimization from market-cap weights
  W; delta a proportionality constant).
- Views (item 7): P E[R] = Q + epsilon, "P is a known k x n matrix, Q is a k-dimensional vector, and
  epsilon is an unobservable normally distributed random vector with zero mean and a diagonal covariance
  matrix Omega"; the equilibrium prior is centered at Pi with covariance tau*Sigma, "tau is a constant."
- Market weights (item 3): W_i = M_i / sum_i M_i for bonds/equities.

**Mapping to project:** REPORT-ONLY allocator (the BL posterior return vector then feeds a mean-variance
optimizer). The posterior E[R] is closed-form -- DETERMINISTIC + numpy-implementable (`numpy.linalg.inv`,
`@`) given Sigma, tau, Pi (from Pi=delta*Sigma*W), P, Q, Omega. Most input-heavy of the allocators
(requires views P, Q, Omega and a tau choice); best treated as an optional comparator.

---

## EVALUATION / REPORTING

### 9. Agarwal et al. -- rliable / "Statistical Precipice" (IQM, optimality gap, PoI, profiles)

**File:** `H_foundational_canon/rliable-Statistical-Precipice__2108.13264.pdf` (28 pp.)

**Bibliographic coordinates (verified page 1):**
- Title: "Deep Reinforcement Learning at the Edge of the Statistical Precipice"
- Authors: Rishabh Agarwal, Max Schwarzer, Pablo Samuel Castro, Aaron Courville, Marc G. Bellemare
  (Google Research Brain Team; MILA / Universite de Montreal)
- Venue: NeurIPS 2021 (Outstanding Paper Award); arXiv:2108.13264v4 [cs.LG], 5 Jan 2022
- Library: https://github.com/google-research/rliable

**Setup (p.3):** M tasks, N runs/task; normalized scores x_{m,n}; empirical tail distribution
F_hat(tau; y_{1:K}) = (1/K) sum_k 1[y_k > tau].

**Aggregate metrics (all report-only -- NOT rewards):**
- **IQM (Interquartile Mean), p.7:** "25% trimmed mean, IQM discards the bottom and top 25% of the runs
  and calculates the mean score of the remaining 50% runs" over the **combined** MN runs.
- **Optimality Gap, p.7:** "the amount by which the algorithm fails to meet a minimum score of
  gamma = 1.0 ... a score of 1.0 is a desirable target beyond which improvements are not very important."
- **Probability of Improvement, p.7 + Eq. A.2 p.25:** P(X>Y) = (1/M) sum_m P(X_m > Y_m), where the per-task
  Mann-Whitney U-statistic is P(X_m>Y_m) = (1/(NK)) sum_i sum_j S(x_{m,i}, y_{m,j}) with S(x,y)=1 if y<x,
  1/2 if y=x, 0 if y>x. "does not account for the size of improvement." Statistically meaningful if upper
  CI > 0.75.
- **Mean/Median critique, p.3:** mean "Often dominated by performance on outlier tasks"; median "Requires
  large number of runs ... zero scores on nearly half the tasks do not affect it."

**Stratified bootstrap CIs (p.6):** "we re-sample runs with replacement independently for each task to
construct an empirical bootstrap sample with N runs each for M tasks ... and repeat this process many
times." Percentile CIs reliable for N >= 10 runs.

**Performance profiles / score distributions (Eq. 1, p.7):**
    F_hat_X(tau) = (1/M) sum_{m=1}^M (1/N) sum_{n=1}^N 1[x_{m,n} > tau]
"shows the fraction of runs above a certain normalized score"; an outlier run shifts it by at most 1/MN.

**Best-practice recommendations (Table 1, p.3; Discussion p.10):** report interval estimates via
stratified bootstrap CIs; report IQM + average probability of improvement + optimality gap; use
performance profiles; "the problem is not solved by fixing random seeds"; report results for all runs.
Applicable with 3-10 runs/task.

**Mapping to project:** REPORT-ONLY evaluation suite (no reward). These ARE the project's headline
inference tools (per-seed rliable: IQM, optimality gap, probability of improvement, stratified bootstrap
CIs, performance profiles). All DETERMINISTIC + numpy-implementable (the authors ship the `rliable` lib).

---

### 10. Henderson et al. -- Deep Reinforcement Learning that Matters

**File:** `J_additional_relevant/DeepRLThatMatters-Henderson__2018.pdf` (26 pp.; arXiv v3)

**Bibliographic coordinates (verified page 1):**
- Title: "Deep Reinforcement Learning that Matters"
- Authors: Peter Henderson, Riashat Islam, Philip Bachman, Joelle Pineau, Doina Precup, David Meger
  (McGill University; Microsoft Maluuba)
- Venue: AAAI 2018 ("Copyright (c) 2018, AAAI"); arXiv:1709.06560v3 [cs.LG], 30 Jan 2019

**Reporting recommendations (report-only methodology):**
- Number of seeds/trials (p.5): they decline a fixed number -- "there can be no specific number of trials
  specified as a recommendation, ... power analysis methods can be used to give a general idea." Their own
  protocol: "we run five experiment trials for each evaluation, each with a different preset random seed"
  (p.2); they show 5 is often inadequate.
- Cherry-picking warning (p.5): "it is not uncommon for the top-N trials to be selected from among several
  trials ... or averaged over only small number of trials (N < 5). Our experiment with random seeds shows
  that this can be potentially misleading." And: "We demonstrate that the variance between runs is enough
  to create statistically different distributions just from varying random seeds" (two groups of 5 same-
  hyperparameter HalfCheetah runs gave a significant t-test, t=-9.09, p=0.0016).
- Recommended statistical reporting (pp.5-6): bootstrap 95% confidence bounds (Table 3, 10k bootstrap
  iterations); bootstrap power analysis to decide sample size; significance tests -- "2-sample t-test ...
  the Kolmogorov-Smirnov test ... and bootstrap percent differences with 95% confidence intervals."

**Mapping to project:** REPORT-ONLY methodology guidance. Directly licenses the project's multi-seed
design, bootstrap CIs, significance testing, and the refusal to report best-of-k runs. No reward / no
numpy artifact (it is a practices paper).

---

### 11. Fissler & Ziegel -- Higher Order Elicitability and Osband's Principle (joint (VaR,ES))

**File:** `J_additional_relevant/FisslerZiegel-HigherOrderElicitability__2016.pdf` (32 pp.; arXiv v3)

**Bibliographic coordinates (verified page 1):**
- Title: "Higher order elicitability and Osband's principle"
- Authors: Tobias Fissler, Johanna F. Ziegel (University of Bern)
- Dated: October 1, 2015; arXiv:1503.08123v3 [math.ST], 30 Sep 2015; AMS 2010: 62C99, 91B06
- **Journal coordinates (Annals of Statistics 44(4):1680--1707, 2016) NOT-FOUND in PDF** -- preprint only;
  no volume/pages/DOI. Do not quote them as read from this file.

**Main result:** ES alone is NOT elicitable, but the pair (VaR_alpha, ES_alpha) is JOINTLY elicitable
("2-elicitable"). Verbatim (p.17): "ES_alpha fails to be 1-elicitable (Weber, 2006; Gneiting, 2011),
whereas VaR_alpha is 1-elicitable ... the pair (VaR_alpha, ES_alpha): F -> R^2 is 2-elicitable for any
alpha in (0,1) subject to mild conditions." Definitions (p.16): VaR_alpha(Y) = F^{-1}(alpha) =
inf{x : F(x) >= alpha}; ES_alpha(Y) = (1/alpha) integral_0^alpha VaR_u(Y) du.

**Strictly consistent joint scoring family (Corollary 5.5, pp.19-20)**, x_1 = VaR report, x_2 = ES report,
y = realized obs, on A_0 = {x_1 >= x_2}:

    S(x_1, x_2, y) = ( 1{y<=x_1} - alpha ) G_1(x_1) - 1{y<=x_1} G_1(y)
                     + G_2(x_2) ( x_2 - x_1 + (1/alpha) 1{y<=x_1} (x_1 - y) )
                     - script_G_2(x_2) + a(y)

where script_G_2' = G_2. F-consistent if G_1 increasing and G_2 increasing+convex; STRICTLY consistent if
G_2 strictly increasing + strictly convex. Remark 5.3 (p.19): the pair admits only NON-separable strictly
consistent scores (cannot split into a VaR score plus an ES score).

**Mapping to project:** REPORT-ONLY evaluation theory (NOT a reward). It licenses scoring/backtesting the
(VaR, ES) forecasts jointly via the FZ scoring function -- relevant to the H2-Tail (CVaR/ES) co-primary and
to the examiner (Okhrati) profile. The FZ score (Cor. 5.5) is DETERMINISTIC + numpy-implementable for chosen
G_1, G_2 (e.g. the FZ0 / homogeneous-zero choice). Use it as the elicitable tail-forecast scoring rule;
do NOT attribute the EVT/elicitability machinery to Okhrati.

---

## BEAT-THE-HUMAN BENCHMARK PROTOCOL

### 12. Ma et al. -- Eureka: Human-Level Reward Design via Coding LLMs

**File:** `00_core_pillars/Eureka__2310.12931.pdf`

**Bibliographic coordinates (verified page 1):**
- Title: "EUREKA: Human-Level Reward Design via Coding Large Language Models"
- Authors: Yecheng Jason Ma, William Liang, Guanzhi Wang, De-An Huang, Osbert Bastani, Dinesh Jayaraman,
  Yuke Zhu, Linxi "Jim" Fan, Anima Anandkumar (NVIDIA, UPenn, Caltech, UT Austin)
- Venue: "Published as a conference paper at ICLR 2024"; arXiv:2310.12931v2 [cs.RO], 30 Apr 2024

**The beat-the-human protocol:**
- **Human normalized score (p.6):** "we report the human normalized score for EUREKA and L2R,
  (Method - Sparse) / |Human - Sparse|" (confirmed visually). Score 1.0 = parity with the human reward;
  > 1.0 beats human. Dexterity tasks instead report binary success rates. (Appendix F: for the abstract's
  average, scores are clipped to [0,3] per task before averaging over 29 tasks.)
- **Headline result (abstract, p.1):** "EUREKA outperforms human experts on 83% of the tasks, leading to
  an average normalized improvement of 52%."
- **Tasks + human baseline (pp.5-6):** "10 distinct robots and 29 tasks implemented using the IsaacGym
  simulator" (9 Isaac + 20 Bidexterous Manipulation/Dexterity). "Human. These are the original shaped
  reward functions ... written by active reinforcement learning researchers who designed the tasks ...
  represent the outcomes of expert-level human reward engineering."

**Evolutionary search (p.5; Algorithm 1, p.4):** "EUREKA conducts 5 independent runs per environment, and
for each run, searches for 5 iterations with K = 16 samples per iteration." Mutation: take the best reward
from the previous iteration + its reward reflection + the mutation prompt, generate K more i.i.d. rewards.
Backbone: GPT-4 (gpt-4-0314).

**Fitness function (Def. 2.1, p.3; Alg. 1, p.4):** "F : Pi -> R is the fitness function that produces a
scalar evaluation of any policy ... (i.e., evaluate the policy using the ground truth reward function)."
Candidates scored s_1 = F(R_1), ..., s_K = F(R_K); cumulative best kept. F is the task's ground-truth /
sparse metric (binary success on Dexterity; task-specific on Isaac), each reward scored as "the average of
the maximum task metric values achieved from 10 policy checkpoints" over 5 PPO runs.

**Mapping to project:** PROTOCOL template (not a reward). This is the H1 "beat-the-human" benchmark design
the project mirrors: LLM-designed reward vs human-engineered reward, scored by a held-out ground-truth
fitness, with a human-normalized headline statistic. Note for the project's REWARD_CANON H1: adapt the
normalized-score idea to a finance fitness (e.g. Sharpe) and a human-engineered reward baseline; the search
loop (K samples x N iterations + reward reflection) mirrors the project's reflect-on-best campaign engine.
Report-only / methodological; deterministic given a fixed fitness, but the LLM sampling is stochastic.

---

## SUMMARY OF VERIFICATION STATUS

**VERIFIED first-hand (formula + coordinates, ready to cite/implement):**
- Moody & Saffell DSR (Eqs. 14-16, p.878; IEEE TNN 12(4), 2001) -- image-confirmed.
- Markowitz E-V (E = sum X_i mu_i; V = sum_i sum_j sigma_ij X_i X_j, p.81; J. Finance 7(1):77-91, 1952)
  -- image-confirmed.
- Rockafellar & Uryasev CVaR (F_beta Eq. 4 p.5; sample estimator Eq. 9 p.6; Theorem 1-2) -- text-clean.
- Jiang et al. portfolio-RL reward (r_t = ln(mu_t y_t . w_{t-1}) Eq. 10 p.6; mu_t cost Eq. 13 p.7;
  R Eq. 21 p.11; arXiv:1706.10059) -- text-clean.
- DeMiguel 1/N + metrics (SR Eq.10, CEQ Eq.12, Turnover Eq.13; rolling M=120) -- image-confirmed.
- Lopez de Prado HRP (3 stages, distance d=sqrt(0.5(1-rho)), recursive bisection, code snippets 1-2).
- Black & Litterman master posterior (App. item 8, p.42 -- IS printed in the 1992 paper) -- image-confirmed.
- rliable IQM / optimality gap / P(X>Y) Eq. A.2 / score-distribution Eq. 1 / stratified bootstrap.
- Henderson reporting practices (seeds, anti-cherry-pick, bootstrap CIs, significance tests).
- Fissler & Ziegel joint (VaR,ES) scoring family (Cor. 5.5, pp.19-20) -- image-confirmed.
- Eureka human-normalized score (Method-Sparse)/|Human-Sparse| + 83%/52% headline + K=16/N=5 search.

**NOT-FOUND (do not cite as read from these PDFs):**
- Maillard-Roncalli-Teiletche formulas -- the file `Maillard-RiskParity__2010.pdf` is actually
  Cagna & Casuccio (CeRP WP 142/14, 2014). The genuine Maillard closed forms are absent on disk under
  this name. **Action: re-acquire the real Maillard paper, or cite ERC from a correctly-sourced copy.**
- Published journal coordinates / DOIs for: DeMiguel (file is 2006 preprint), HRP (SSRN preprint),
  CVaR (1999 working paper), Fissler-Ziegel (arXiv preprint). The canonical published cites must be
  sourced elsewhere; do not present a volume/page/DOI as if read off these files.

**Top benchmark/protocol items the dissertation should adopt:**
1. Reward comparators with exact citations: Jiang log-return-with-cost (risk-neutral baseline) and
   Moody-Saffell differential Sharpe ratio (online risk-adjusted) -- both DIRECT per-step rewards.
2. Tail-risk reward + metric: Rockafellar-Uryasev sample-CVaR (Eq. 9) for the H2-Tail co-primary; pair
   with Fissler-Ziegel joint (VaR,ES) elicitable scoring for honest tail-forecast evaluation.
3. Allocator baselines (report-only): 1/N (DeMiguel), ERC/risk-parity, HRP (Lopez de Prado), optionally
   Black-Litterman + Markowitz mean-variance -- all deterministic + numpy/scipy.
4. Evaluation protocol: rliable (IQM + optimality gap + probability of improvement + stratified bootstrap
   CIs + performance profiles) as the headline inference; DeMiguel's OOS Sharpe / CEQ / turnover (Eq. 13)
   as report-only metrics; Henderson's multi-seed + significance-testing discipline.
5. Beat-the-human design: mirror Eureka's human-normalized score and ground-truth-fitness search loop for
   the H1 REWARD_CANON benchmark (adapt the normalization to a finance fitness).

