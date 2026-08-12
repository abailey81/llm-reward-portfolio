<!-- ⚠ THIS FILE IS NOT YET WIRED INTO THE BUILD, so it does NOT appear in the compiled PDF.
     TO WIRE IT: add, as the LAST entry of `APPENDICES` in scripts/build_paper.py:
         "appendices/F_prompts_and_authored_code.md",
     Appending LAST takes the next free letter (F), so nothing renumbers. It must NOT be added to
     `word_budget.BODY_CHAPTERS` — its heading says "(word-excluded)", exactly like Appendix D.
     It was left unwired on 2026-08-01 because scripts/** Was drift-fenced during a live
     confirmatory campaign and a non-owner edit turns that run RED.
     REGENERATE, don't hand-edit: this file is produced from the real frozen sources by
     paper/appendices/gen_F_prompts_and_authored_code.py, which prints every path it reads. -->

# Appendix F — The prompts, and the code the model actually wrote (word-excluded)

This appendix prints the manipulation and its output verbatim. It exists because the surrounding
literature treats this as the standard of evidence and the two closest financial neighbours do not
meet it: of seven directly comparable systems, all seven print their prompts, five print
model-authored artefacts, and the two finance papers print neither authored code nor a worked
iteration. A reader cannot otherwise check that the loop did what the method section claims.

Every block below is reproduced from the artefact it names. The two prompt files are bound by the
design freeze, so what is printed here is what the campaign executed. Lines too long for the page
are hard-wrapped with a hanging indent. Nothing is elided, and no line is edited.

## F.1 The system prompt (`prompts/system.txt`, hash-bound)

Identical for every arm and every model, in every generation.

\begingroup\footnotesize

```text
You design REWARD FUNCTIONS (Python) for a reinforcement-learning
    portfolio-allocation agent.

You receive ANONYMIZED numeric arrays only — no asset names, no dates, no
    identifiers. You cannot
and must not reference any specific company, market event, or time period; you only
    see numbers.

Your reward MUST follow this contract exactly:

    def reward(weights, returns, prev_weights, port_ret, info):
        # weights:      np.ndarray, current simplex weights over assets + cash
        # returns:      np.ndarray, per-asset returns realized this step
        # prev_weights: np.ndarray, previous weights (for turnover/cost)
        # port_ret:     float, realized portfolio return this step (gross - cost)
        # info:         dict; info["reward_state"] carries YOUR state across steps
            (or None at reset)
        # RETURN: (total: float, components: dict[str, float], reward_state)
        ...
        return total, components, reward_state

Rules:
- numpy only (available as `np`); no imports beyond numpy; no file/network/OS
    access; no dates.
- The agent maximizes `total`. `components` is logged only (for interpretability).
    `reward_state`
  is round-tripped via `info` so you can write stateful rewards (e.g. an online
      Sharpe).
- Optimize RISK-ADJUSTED performance — weigh return against its risk (you are
    selected on a
  risk-adjusted score). The feedback after each attempt tells you HOW to weigh it;
      do not assume.
- After each attempt you receive feedback; revise the function to improve
    out-of-sample
  risk-adjusted performance. Respond with a single Python code block containing ONLY
      the
  function definition — no prose or explanation before or after the code.
```

\endgroup

<!-- The filename is forced onto its own line. Section headings are set JUSTIFIED, so an
     \allowbreak inside the \texttt run is not enough: breaking early would leave a first line
     needing 73pt of stretch across four spaces, which TeX scores as infeasible, so it took the
     overfull line instead and 53.2pt of the path ran off the page. \newline is not subject to
     that trade-off. F.1's path is short enough to fit and is left alone. -->

## F.2 The generation-0 prompt\newline(`prompts/initial_generation.txt`, hash-bound)

Used once per arm, before any feedback exists.

\begingroup\footnotesize

```text
Here is the environment interface and the reward contract.

{ENV_INTERFACE}        # observation/action shapes, the step semantics, the contract
    signature

Write a reward function for the portfolio-allocation agent. Think about:
  - risk-adjusted return (not raw return alone),
  - turnover/transaction cost.
The feedback you receive after each attempt is what should steer how you shape risk.

A trivial example that satisfies the contract:

    def reward(weights, returns, prev_weights, port_ret, info):
        return float(port_ret), {"port_ret": float(port_ret)}, None

Respond with a single Python code block containing ONLY your reward function
    definition — no
prose before or after the code.
```

\endgroup

## F.3 The reflection turn

Every generation after the first opens with a single fixed sentence, composed in code rather than
from a template file, and the arm's feedback block is appended directly beneath it.

\begingroup\footnotesize

```text
Reflect on the previous candidate's results and propose an improved reward function.
    Feedback from the previous candidate:
```

\endgroup

The five feedback blocks that may follow that sentence are printed in Listing 1.1 of the
Introduction, and are the whole of what differs across the language-model arms. `prompts/reflection.txt`
exists in the repository but is dead and is deliberately not loaded, a fact recorded here because
a reader inspecting the repository would otherwise reasonably assume it was the live template.

## F.4 What the model actually wrote

A complete authored reward program, exactly as archived, from the registered inference line's
`distributional` arm at generation 0. It was written from the contract alone, before the model
had seen any feedback.

\begingroup\footnotesize

```python
def reward(weights, returns, prev_weights, port_ret, info):
    """
    Tail-risk (CVaR) normalized reward with drawdown control and turnover damping.

    Design notes (distinct from vol/Sharpe-ratio style designs):
      * risk is measured by the EMPIRICAL LOWER-TAIL (CVaR_10%) of a 120-step
        rolling buffer of realized portfolio returns, blended with an EWMA
        downside semi-deviation (fast reaction) -> robust, asymmetric risk.
      * gain is measured in LOG space (compounding aware) and is charged an
        EXTRA implicit turnover fee on top of the environment's 10 bps.
      * an explicit underwater (drawdown) penalty keeps the equity path smooth.
      * a mild concentration penalty discourages all-in single-asset bets.
    """
    w = np.asarray(weights, dtype=np.float64).ravel()
    pw = np.asarray(prev_weights, dtype=np.float64).ravel()
    r = float(port_ret)
    if not np.isfinite(r):
        r = 0.0
    r = float(np.clip(r, -0.5, 0.5))

    NBUF = 120
    WARM = 20

    st = info.get("reward_state") if isinstance(info, dict) else None
    if st is None:
        st = {
            "buf": np.zeros(NBUF, dtype=np.float64),
            "n": 0,
            "idx": 0,
            "ds_var": 1e-4,      # EWMA downside variance
            "cum_log": 0.0,      # cumulative log wealth
            "peak": 0.0,         # running max of cum_log
            "steps": 0,
        }

    buf = st["buf"]
    n = int(st["n"])
    idx = int(st["idx"])
    ds_var = float(st["ds_var"])
    cum_log = float(st["cum_log"])
    peak = float(st["peak"])
    steps = int(st["steps"]) + 1

    # ---- log gain -------------------------------------------------------
    g = float(np.log1p(max(r, -0.9)))

    # ---- turnover (one-way, undrifted approximation) --------------------
    m = min(w.size, pw.size)
    turnover = 0.5 * float(np.sum(np.abs(w[:m] - pw[:m])))
    turnover = float(np.clip(turnover, 0.0, 1.0))

    # ---- update rolling buffer ------------------------------------------
    buf[idx] = r
    idx = (idx + 1) % NBUF
    n = min(n + 1, NBUF)

    # ---- EWMA downside semi-variance (fast) -----------------------------
    lam = 0.94
    neg = min(r, 0.0)
    ds_var = lam * ds_var + (1.0 - lam) * (neg * neg)
    ds_dev = float(np.sqrt(max(ds_var, 1e-10)))

    # ---- empirical CVaR of lower 10% tail (slow, robust) ----------------
    if n >= 10:
        hist = buf[:n] if n < NBUF else buf
        k = max(2, int(np.ceil(0.10 * n)))
        worst = np.sort(hist)[:k]
        cvar = -float(np.mean(worst))          # positive when tail is negative
        cvar = max(cvar, 0.0)
    else:
        cvar = ds_dev

    # ---- drawdown state -------------------------------------------------
    cum_log += g
    peak = max(peak, cum_log)
    underwater = max(0.0, peak - cum_log)      # in log units

    # ---- blended risk denominator ---------------------------------------
    risk = 0.55 * cvar + 0.45 * (1.3 * ds_dev)
    risk = float(np.clip(risk, 2.5e-3, 0.12))
    if steps <= WARM:
        # blend toward a neutral scale before statistics are meaningful
        a = steps / float(WARM)
        risk = (1.0 - a) * 0.012 + a * risk

    # ---- concentration (only penalize extreme bets) ---------------------
    hhi = float(np.sum(w * w))
    conc_pen = max(0.0, hhi - 0.22)

    # ---- assemble -------------------------------------------------------
    adj_gain = g - 0.0020 * turnover           # extra 20 bps implicit fee
    core = adj_gain / risk                     # tail-risk normalized gain
    core = float(np.clip(core, -6.0, 6.0))

    dd_pen = 6.0 * underwater + 25.0 * underwater * underwater
    dd_pen = float(min(dd_pen, 4.0))

    total = core - dd_pen - 0.8 * conc_pen - 0.35 * turnover

    # small bonus for staying in a low-tail-risk regime (path smoothness)
    total += 0.15 * float(np.exp(-risk / 0.010))

    if not np.isfinite(total):
        total = 0.0
    total = float(np.clip(total, -10.0, 10.0))

    components = {
        "log_gain": g,
        "core_risk_adj": core,
        "cvar10": cvar,
        "ds_dev": ds_dev,
        "risk_den": risk,
        "turnover": turnover,
        "underwater": underwater,
        "dd_pen": dd_pen,
        "hhi": hhi,
        "conc_pen": conc_pen,
        "total": total,
    }

    st = {
        "buf": buf,
        "n": n,
        "idx": idx,
        "ds_var": ds_var,
        "cum_log": cum_log,
        "peak": peak,
        "steps": steps,
    }
    return total, components, st
```

\endgroup

## F.5 The iteration ladder

<!-- THE 64-LINE UNIFIED DIFF THAT SAT HERE WAS REPLACED ON 2026-08-11 BY THE PART OF IT THAT CARRIES
     THE ARGUMENT, and the replacement is honest about being one. The diff was ALREADY elided (159 of
     its lines were cut, with the elision stated inside the block), so what shipped was never the whole
     object either. What the exhibit exists to show is that the same candidate slot changes under a
     single tail-feedback block, and the two docstrings plus the state dictionaries show that more
     legibly than sixty lines of context. The complete pair of sources is in the reproduction archive,
     and F.4 above prints one of the two entire. -->

The same arm and candidate slot one generation later, after a single tail-feedback block. This is the
exhibit the lineage uses to show that the loop is doing something: the *same object* changing under
feedback, rather than a final artefact presented alone. The design intent the model states at the head of
the program is rewritten wholesale between the two generations.

What the diff below shows is a wholesale replacement rather than a tuning. The rolling-buffer
conditional value-at-risk block of generation 0 becomes an exponentially-weighted partial-moment block,
and the state the program carries between steps grows from seven keys to nine. The two function bodies
run to 130 lines and 111, are not reproduced here, and both sit in the reproduction archive, while F.4
prints one of them entire.

\begingroup\footnotesize

```diff
--- generation 0 (no feedback yet)
+++ generation 1 (after tail feedback)
     """
-    Tail-risk (CVaR) normalized reward with drawdown control and turnover damping.
-      * risk = EMPIRICAL LOWER-TAIL (CVaR_10%) of a 120-step rolling buffer of
-        realized returns, blended with an EWMA downside semi-deviation.
-      * gain in LOG space, charged an EXTRA implicit turnover fee.
-      * an explicit underwater (drawdown) penalty keeps the equity path smooth.
+    Rolling Sortino-flavoured reward with Omega (partial-moment ratio) tilt,
+    convex deep-loss penalty, log-drawdown control and turnover friction.
+      * risk denominator = EWMA downside semi-deviation (long memory, ~35 steps)
+      * separate EWMA upside / downside partial moments -> log-Omega tilt
+      * drawdown measured in LOG-wealth units, both level and increment penalised
+      * convex (power 1.5) penalty only on losses beyond half a semi-deviation
     """
@@ the carried state, at the foot of the same function @@
-    st = {"buf", "n", "idx", "ds_var", "cum_log", "peak", "steps"}
+    new_state = {"n", "m", "d2", "up", "dn", "cum", "peak", "dd_prev", "dd_ewma"}
```

\endgroup
