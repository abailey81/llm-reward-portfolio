# Your Dissertation, Explained From Zero

> **⚠ DESIGN SUPERSESSION (2026-07-20/21 — read this first).** This document describes the **v1**
> design (frozen 2026-07-18 at `ce5db62c`). On 2026-07-20, after industry-supervisor feedback
> (NatWest AI R&D), the registration was UNFROZEN **pre-data** (ADR-059; legitimate — no campaign
> data existed) and revised to **v2**: the same confirmatory core (Opus 5, 7 arms, m=6, SESOI,
> the E1 seed ladder) now wrapped by **9 report-only replication legs** (DeepSeek V4-Pro, GLM-5.2,
> the Qwen 27B/9B open pair, Haiku 4.5 + Sonnet 4.6 closed ladder, GPT-5.6 Luna, Nemotron 3
> Super, Gemini 3.5 Flash stretch seat) + a ~25-model reading-link survey + a pre-registered
> cross-model synthesis + an advisory $30 spend ledger. Everything below about the core science
> remains accurate; single-model/frozen-state statements are superseded. Authority:
> `docs/V2_MASTER_PLAN_2026-07-20.md`, `docs/MODEL_SWEEP_2026-07-20_v2.md`, PREREGISTRATION §14,
> CHANGELOG [2026-07-20/21].


> **Who this is for.** Someone with *no* background in finance, machine learning, statistics, or AI.
> Every idea is built up from scratch, in order, each on top of the last. By the end you will
> understand exactly what this dissertation does, why it is designed the way it is, and why its
> most likely result — "no difference" — is actually the point.
>
> Companion documents: `DISSERTATION_MASTER_OVERVIEW.md` (the precise, technical version of
> everything here), `PREREGISTRATION.md` (the frozen scientific plan), and the paper chapters in
> `paper/`. Nothing here contradicts them — this is the same project told gently.

---

## Part 0 — The whole thing in three paragraphs

Imagine you hire a very smart assistant (an AI language model — the same kind of technology as
ChatGPT or Claude) and give it an unusual job: **write the "rules of motivation" for a robot
trader**. The robot trader learns by trial and error — it tries things, gets a score after each
step, and gradually does more of whatever raises its score. Those scoring rules are called a
**reward function**, and whoever writes them effectively decides what the robot cares about. Write
"maximise profit" and you may get a robot that makes money most days but occasionally loses
catastrophically. The scoring rules are the single most important — and hardest — part of the whole
setup.

Now the actual question of the dissertation. After each attempt, the assistant is shown how its
last set of rules performed, and asked to write a better one. **What should we show it?** Option A:
a single number ("your rules scored 0.83"). Option B: that same number **plus a detailed readout of
the worst days** — how bad the bad days were, at several levels of badness. Intuitively, option B
seems obviously better: more information about disasters should help the assistant write rules that
avoid disasters. But does the assistant actually *use* that extra information? Nobody has ever
tested this properly, with controls, in a fair experiment. That test is this dissertation.

The twist — and the intellectually honest heart of the project — is that there are good reasons to
predict the extra information will make **no measurable difference**, because AI language models
are known to be surprisingly bad at reading and comparing small, similar-looking numbers (is
−0.0577 worse than −0.0582?). The dissertation is built so that either answer is a genuine
discovery: if the tail readout helps, that's new; if it doesn't, the experiment is instrumented to
pinpoint *where* the information got lost — and "we located exactly where the chain breaks" is a
real scientific finding, not a failure.

---

## Part 1 — The background, one piece at a time

### 1.1 Investing basics: portfolios and returns

A **stock** is a small piece of ownership of a company. Its price moves every day. A **portfolio**
is a collection of stocks you hold at once — instead of betting everything on one company, you
spread money across many.

A **return** is the percentage change in your money over some period. If you have £100 today and
£101 tomorrow, your daily return is +1%. If you drop to £98, it's −2%. Over years, small daily
returns compound into large differences.

Managing a portfolio means deciding, each day, **what fraction of your money to put in each
stock** — the **weights**. 10% in stock A, 5% in stock B, …, and perhaps some in **cash** (holding
money uninvested, the safe do-nothing option). This dissertation's setup trades the **30 biggest US
stocks plus a cash option**, re-deciding the weights every trading day.

One realistic detail matters: changing your holdings costs money (fees, the gap between buy and
sell prices). This is a **transaction cost** — here modelled as a small fee proportional to how
much you trade. A strategy that frantically rearranges its portfolio every day bleeds money in
costs. So the robot has to weigh "better positioning" against "cost of moving."

### 1.2 Risk — and specifically the "tail"

Two portfolios can have the same *average* return and be wildly different in how it feels — and how
dangerous it is — to hold them. One earns a steady +0.03% most days. The other alternates +2% and
−1.9%. Same average; totally different risk.

Now the crucial concept of this whole dissertation. Picture a bar chart of all your daily returns
over years: most days cluster near zero, fewer days are moderately good or bad, and a very few days
are extreme. Statisticians call the far ends of this chart the **tails**. The **left tail** is the
collection of your *worst* days.

Why obsess over the left tail? Because in real markets it behaves much, much worse than naive
theory predicts. From this project's own data (21 years of the biggest US stocks):

- Extreme daily crashes that a textbook "bell-curve" model says should almost *never* happen (a
  "five-sigma" move) actually occur **about ten thousand times more often** than the bell curve
  predicts.
- On ordinary days, about 3% of stocks might have a terrible day at once. On the market's *worst*
  days, **nearly one stock in five crashes together** — exactly when you most need diversification,
  it evaporates.
- Even more subtle: how bad the tail is *relative to the bell-curve prediction* actually
  **reverses** as you go deeper into it — moderate bad days are slightly *less* bad than the bell
  curve says, but extreme days are far *worse*. A single risk number, measured at one depth, is
  mathematically incapable of describing a tail that flips like this. You need readings at
  *several* depths. **Keep this fact — it is the entire justification for the experiment's
  "option B."**

The standard measure of tail badness is **CVaR** ("conditional value-at-risk"), which sounds
technical but is a simple idea: *"take your worst 5% of days — what was the average loss on those
days?"* That's CVaR at the 5% level. You can also ask it of the worst 10%, worst 25%, or worst 1% —
readings at different depths of the tail. CVaR is the professional's preferred measure because it
behaves sensibly (a mathematically-grounded family called **coherent risk measures** — for
instance, unlike a cruder measure called VaR, it never punishes you for diversifying).

### 1.3 What reinforcement learning is

**Machine learning** is getting computers to improve at tasks from data rather than from hand-written
instructions. **Reinforcement learning (RL)** is the branch that works like training a dog:

1. The **agent** (the dog / the trading robot) observes the situation.
2. It takes an **action** (sit / choose today's portfolio weights).
3. It receives a **reward** — a number meaning "good" or "bad" (a treat / a score).
4. Over many, many repetitions, it adjusts its behaviour to earn more reward.

The agent isn't told *how* to act. It's told what *counts as good*, and it discovers behaviour
that scores well — often behaviour its designers never anticipated. In this project the agent is a
well-established, off-the-shelf RL algorithm called **SAC** (Soft Actor-Critic — the specific
flavour doesn't matter for understanding; think "a standard, respected learning engine"). Each
training run lets it practise on years of historical market data for **400,000 learning steps** —
a number chosen by careful measurement, as you'll see later.

One term you'll meet: the agent contains a **critic** — its internal estimate of "how good is my
situation?" that guides learning. Keep that word in mind; the dissertation deliberately does *not*
touch the critic.

### 1.4 The reward function — the hardest part

The reward function is the small piece of code that computes the score after every step. It is the
*steering wheel* of the entire system: the agent will optimise **exactly** what the reward says,
including its loopholes, and nothing else.

- Reward = "daily profit" → the agent may learn profitable-but-reckless behaviour: great average,
  horrifying worst days. The reward never mentioned worst days, so the agent doesn't care.
- Add "…minus a penalty for risk" → *which* risk? Volatility? Worst-case loss? Over what window?
  Weighted how much? Every choice changes the behaviour you get.

Designing rewards is so notoriously tricky that it has a name — **reward engineering** — and a
famous failure mode, **reward hacking**: the agent finds a way to score highly that defeats the
purpose (like a student gaming a mark scheme instead of learning). In finance the stakes are sharp:
a mis-specified reward produces exactly the "profitable on average, ruinous in the tail" portfolio
from §1.2.

### 1.5 Enter the language model

A **large language model (LLM)** — like Claude or ChatGPT — is an AI trained on enormous amounts of
text, able to write fluent prose *and working computer code* on request.

In 2023, researchers (a system called **Eureka**, from NVIDIA) had an idea: since reward design is
a bottleneck done by human experts through trial and error, why not have an LLM do it?

1. Ask the LLM to **write a reward function** (actual Python code).
2. Train the RL agent with that reward. Measure how it did.
3. **Show the LLM the results** and ask it to write an improved reward.
4. Repeat.

This loop — propose, test, reflect, improve — worked impressively in robotics, sometimes beating
human-designed rewards. Step 3 is called **reflection**, and the information shown to the LLM is the
**feedback**.

Here is the gap this dissertation lives in. In Eureka and everything since, that feedback is
essentially **a scalar** — one summary number (or a short list of component scores). Nobody
tells the LLM about the *shape of outcomes* — the tail. And notably, Eureka's own authors showed
that removing the feedback step entirely cost about a third of the performance, so the feedback
*channel* clearly matters. What nobody has tested is whether the feedback's *content* — scalar
versus a rich tail readout — matters. In a risk-sensitive domain, where the tail is provably
impossible to summarise in one number (§1.2), that untested question is exactly the right one to
ask.

---

## Part 2 — The question, asked properly

### 2.1 The question in plain words

> **When an AI language model writes the reward code for a trading agent, does *showing it the
> downside* — a multi-level readout of the worst days — change the code it writes? And if it does,
> does that change flow all the way through training into a genuinely safer trading strategy?**

### 2.2 Why you can't just try it once

Suppose you run the loop once with a tail readout and it produces a great strategy. Proves nothing.
Maybe you got lucky. Maybe *any* extra text in the prompt — even meaningless text — nudges the LLM
to be more careful. Maybe the improvement came from the one summary number, not the tail. Training
runs are noisy; two identical setups can differ just from randomness.

Science's answer is the **controlled experiment** — the logic of drug trials:

- **Treatment and control groups** that differ in *exactly one thing*, so any difference in outcome
  is attributable to that one thing.
- A **placebo** — an inert version of the treatment (the sugar pill) — because *receiving
  something* can itself change behaviour. If the drug doesn't beat the sugar pill, the drug's
  chemistry isn't doing anything.
- **Repetition**, because single results can be flukes.
- **Statistics**, to say honestly whether a difference is real or noise.
- And, in the best modern practice, **pre-registration**: publicly committing to your hypotheses
  and analysis *before* seeing results, so you can't fool yourself afterwards (more in Part 6).

This dissertation is, to the best of a very thorough literature search, **the first time anyone has
subjected LLM reward-design feedback to this full experimental treatment** — treatment, controls,
placebo, repetition, pre-registered statistics. That "first" is a core part of its claim to
originality.

### 2.3 The one manipulated variable

In this experiment, the *only* thing that differs between groups is **what the LLM is shown about
its previous attempt**. Everything else — the learning agent, its settings, the data, the training
budget, the base instructions, the number of attempts — is held rigidly identical. The project
calls this the **identification principle**: if only the feedback varies, then only the feedback
can explain any difference.

What exactly is the rich feedback? **Six numbers describing the left tail** of the daily returns
the trained agent actually produced:

1. Average loss on the worst 5% of days (CVaR 5%),
2. …worst 10% of days,
3. …worst 25% of days,
4. …worst 1% of days (flagged to the LLM as a noisy estimate — few days that extreme exist),
5. How often really bad days occur (the fraction of days worse than two standard deviations),
6. A robust measure of how lopsided the outcomes are (is the bad side stretched further than the
   good side?).

Multi-level on purpose: remember §1.2 — the tail's badness *reverses* across depths relative to the
bell curve, so no single number can carry its shape. Several depths can. (There is also real
mathematics behind the choice — this six-number family is drawn from the "coherent risk" class that
modern risk theory says is the right vocabulary — but the intuition above is the substance.)

---

## Part 3 — The experiment: seven groups

Each **group** (the project calls them **arms**) runs the same discovery loop: the LLM writes 30
candidate reward functions over 6 rounds of reflection; each candidate trains the same agent on the
same data for the same 400,000 steps. The arms differ **only** in the feedback block shown at
reflection time.

| # | Arm | What the LLM sees after each attempt | The question it answers |
|---|-----|--------------------------------------|--------------------------|
| 1 | **distributional** | The score **plus all six tail numbers** | The treatment — does the downside readout help? |
| 2 | **scalar** | The score **only** | The baseline — the status quo of the field |
| 3 | **placebo** | The score plus six lines of **explicitly inert filler** ("reference value 1: +0.000"…), matched in length | The sugar pill: is it *information*, or does any extra block of text help? |
| 4 | **scalar_cvar5** | The score plus **exactly one** tail number (the worst-5% average) | Is the multi-level *shape* needed, or is one downside number enough? |
| 5 | **placebo_shuffled** | The **exact tail-readout format** — but the six real values **scrambled across the labels** | The subtlest control: does the LLM use the *content*, or just react to something that *looks like* a risk table? |
| 6 | **random_search** | No LLM at all — random tries within a sensible menu of reward formulas | Is the LLM smarter than blind guessing at the same budget? |
| 7 | **bayes_opt** | No LLM — a classical smart-tuning algorithm adjusting the dials of a fixed reward formula | Is free-form code-writing worth more than expertly tuning a fixed template? |

Read the comparisons like a detective:

- If **distributional beats scalar** — extra tail information helped. But *why*?
- …and also **beats placebo** — it wasn't just "more text in the prompt."
- …and also **beats scalar_cvar5** — the multi-level *shape* mattered, not merely "a downside
  number was present."
- …and also **beats placebo_shuffled** — the LLM used the actual *values*, not the look of the
  table. (If distributional and placebo_shuffled tie, the LLM is reacting to the *costume* of risk
  information, not its content — a fascinating finding in itself.)

Two design details make this fair in ways an expert would immediately probe:

- **The placebo's filler is labelled "inert" on purpose.** Six lines of "0.000" *without* a label
  would look like real diagnostics of a miraculously riskless strategy — actively misleading, which
  would be a worse experiment. Labelling it inert is disclosed, and it makes the placebo *easier*
  for the treatment to beat only in the direction that works *against* the researcher's hoped-for
  effect — a conservative choice.
- **The base instructions never mention tails.** The standing prompt tells every arm to optimise
  "risk-adjusted performance — the feedback after each attempt tells you HOW to weigh it; do not
  assume." Not one tail-related word (no "CVaR," no "drawdown," no "tail") appears in any shared
  prompt — this is *mechanically enforced* by an automated check. Why so strict? An early pilot
  made exactly this mistake: the shared prompt mentioned tails, so *every* arm wrote tail-aware
  code and the experiment measured nothing. The fix means the experiment now measures the pure
  effect of the *fed information*, not of a hint in the instructions.

---

## Part 4 — One cycle of the machine, step by step

Here's what actually happens for one candidate in, say, the distributional arm:

1. **Prompt.** The LLM receives the standing instructions (the rules of the job: write a Python
   function with an exact signature; use only the numerical library `numpy`; you'll see anonymised
   numbers only) plus — after the first round — the reflection message: *"Reflect on the previous
   candidate's results and propose an improved reward function. Feedback from the previous
   candidate:"* followed by that arm's feedback block.
2. **The LLM writes code.** An actual Python function: given today's portfolio weights, the day's
   returns, yesterday's weights, and the day's net portfolio return, produce a score.
3. **Safety screening.** The LLM's code is *untrusted* — treated like a stranger's USB stick. A
   **sandbox** examines the code's structure before running it, rejecting anything that touches
   files, the network, the operating system, or known escape tricks; then runs it once in a
   quarantined throwaway process on dummy data with a strict timeout. Only clean, working code
   proceeds. (Security folks: it's an allowlist-based static gate — only known-safe numerical
   operations are permitted — plus a killable child process. Failed candidates are logged and
   skipped, never crash the experiment.)
4. **Training.** The standard agent trains with this reward for 400,000 steps on the training
   years of market data.
5. **Report card.** The trained agent is evaluated on a *separate* slice of years it never trained
   on (why separate — next Part), producing its held-out score.
6. **Tail measurement.** The six tail numbers are computed from the daily returns the trained agent
   actually produced during training.
7. **Feedback block.** Score + (for this arm) the six tail numbers are formatted into the next
   reflection message.
8. **Everything is archived** — the exact prompt, the exact code, the exact feedback, the scores —
   so any result can be re-derived later from disk, exactly. Then the loop repeats.

After 30 candidates, the arm's **winner** is the candidate with the best held-out score. The
winners are what the arms ultimately compare.

An honest subtlety, stated up front in the dissertation rather than buried: the six tail numbers
are measured on the returns of the agent trained under *that candidate's own reward*. The
measurement is therefore **entangled with the thing it steers** — a feedback loop, not an outside
thermometer. That's not a flaw to hide; the comparison "scalar-fed loop vs tail-fed loop" is
precisely the real-world object of interest. But it forbids a certain overclaim ("this measurement
is independent of the agent") — and the dissertation is careful never to make it.

---

## Part 5 — Keeping score fairly

### 5.1 Three slices of time, one of them sealed

All of this runs on **21 years of real daily market data (2005 – mid-2026)** for the largest US
stocks — professional-grade licensed data, built the careful way: it includes companies that later
went bankrupt or were delisted (excluding them — "survivorship bias" — would paint history rosier
than it was, precisely erasing the disasters a tail study needs), and every data point is
"point-in-time" (only information actually available on that date). The stocks are shown to the
system as anonymous numbered series — no names, no dates — so the LLM can't recognise "this is
Lehman in 2008" from its vast reading of history.

The years are split into three roles:

- **Training (2005–2016).** The agent practises here. The tail feedback is measured here.
- **Validation (2017–2019).** The report card for *choosing* winners. The agent never trained on
  it, so scoring here punishes memorisation.
- **Test (2020 – mid-2026), SEALED.** Touched exactly once, at the very end, for the final verdict.
  During the experiment it is physically unreachable — the evaluation objects for the search stage
  are built without it, so peeking isn't just forbidden, it's impossible.

Why so ceremonial about the third slice? Because "choosing what looks best" quietly overfits
whatever data you choose on. Validation absorbs that selection pressure; the sealed test then gives
one clean, untouched answer. Buffer gaps of sixty trading days separate the slices so information
can't leak across the boundary through overlapping calculation windows.

### 5.2 The two report-card numbers

- **Sharpe ratio** — the standard "return per unit of bumpiness" measure: how much reward you got
  for the rollercoaster you endured. Higher is better. The project actually uses the **Deflated**
  Sharpe ratio — a modern correction that discounts the score for how many candidates you tried
  (try 30 things and pick the best; the best *looks* good partly by luck — DSR subtracts that
  luck) and for non-bell-curve returns.
- **CVaR-5%** — the tail measure itself (§1.2): the average loss on the worst 5% of days, computed
  on the sealed test years. This is where a tail-feedback advantage should show up if it exists.

The headline comparison (called **H2** in the paper) is judged on *both*, as two co-equal families:
performance (Sharpe) and safety (CVaR). To be declared supported, the distributional arm must beat
**all three** relevant comparison arms (scalar, placebo, scalar_cvar5) on that family's measure —
a deliberately strict "beat everything or it doesn't count" rule (statisticians call it an
intersection–union test, and its strictness is itself the multiple-testing correction).

There are three further, smaller questions, each with its own comparison: **H1** — do LLM-written
rewards beat four classic human-designed ones (descriptive interest only)? **H3** — does the
*iterative reflection* loop actually beat just asking for 30 candidates in one shot (does the
conversation matter at all)? **H4** — does the LLM beat the two no-LLM search methods?

### 5.3 Why many repeats, and what "statistically significant" means here

Training is genuinely random (randomised starting conditions), so the same reward can produce
different results twice. One comparison proves nothing. The design therefore re-trains each arm's
*winner* many times with different random **seeds** — matched pairwise across arms so randomness
cancels fairly — climbing a pre-planned ladder of repetition counts (30 → 100 → … → up to 568,
with ~400 as the primary target; how high it climbs is decided by available computer time and the
deadline, *never* by peeking at results — peeking-to-stop is a classic way to fool yourself).

Then, the single most important statistical idea in the dissertation:

**Failing to find a difference is not the same as showing there is no difference.** A sloppy
experiment finds nothing because it's sloppy. To claim "these two are equivalent," you must do
something stronger: pre-declare the **smallest difference that would matter** (here: 0.05 in
deflated-Sharpe units — anything smaller is agreed, in advance, to be practically negligible), and
then demonstrate statistically that the true difference sits **inside** that ±0.05 band. That's an
**equivalence test** (the method is called TOST). It turns "we found nothing" into the far stronger
"we actively bounded the effect: whatever it is, it is smaller than anything anyone should care
about." And if the data are too noisy even for that, the pre-registered rules force the honest
verdict **"inconclusive"** — never quietly dressing weakness up as equivalence. A Bayesian
companion analysis asks the same question from a second school of statistics ("how much do these
data actively *favour* no-difference?"), so the null is corroborated from two independent
directions.

---

## Part 6 — The promise made in advance: pre-registration

Here is a quiet crisis of modern science: analyse data enough different ways and something will
look "significant" by chance. Researchers — honestly, unconsciously — drift toward the analysis
that flatters their result. The community's strongest fix is **pre-registration**: write down your
hypotheses, measures, group sizes, and analysis rules *before* the data exist, then follow the plan.

This dissertation pre-registers to an unusual, arguably frontier, standard:

- A long formal document fixes everything: the four hypotheses, the seven arms, the 30-candidate
  budget, the seed ladder, the data slices, the six tail numbers, the exact statistical tests, the
  0.05 threshold — even the *wording templates* for each possible outcome.
- The plan is **cryptographically frozen**. A digital fingerprint (a SHA-256 hash — think of a wax
  seal that shatters if the document changes by even one letter) is computed over the plan and the
  eight files that define the experiment (including the exact prompt texts — the treatment itself).
  The fingerprint, beginning `ce5db62c…`, is recorded, git-tagged, and timestamped.
- **The software enforces the seal.** The campaign launcher re-computes the fingerprint and
  *refuses to run* if anything has drifted. Roughly twenty automated cross-checks verify the prose,
  the machine-readable config, and the executing code all agree (same seven arms, same budget, same
  thresholds…). Even the tail-neutrality of the prompts (§Part 3) is checked mechanically at
  freeze time.
- Changes after freezing are still possible — science needs that — but only as **dated, explicitly
  approved amendments**, each logged. The plan carries 77 such logged amendments from its
  development, each with its reason. Post-freeze, silent edits are impossible.
- One charming quirk you may notice: the frozen plan's own header still says "PRE-FREEZE." Fixing
  that word would *break the seal* (change the fingerprint), so it stays, and the official freeze
  record lives in a separate log. The seal matters more than the label.

Why go this far for a master's dissertation? Because the expected result is a **null** — and an
unregistered null is worthless ("you probably just did it wrong"), while a pre-registered null with
frozen hypotheses, controls, placebo, equivalence bounds, and sealed test data is **evidence**. The
pre-registration is what converts "we found nothing" into "there is (bounded) nothing to find, and
here is where it goes missing."

### 6.1 A pilot's cautionary tale — why all this rigour is earned, not decorative

Before the real experiment, a cheap pilot run (with a smaller LLM) produced an exciting-looking
result: the tail-fed arm seemed to have significantly better tail outcomes (p ≈ 0.004!). The
project *dissected* its own result instead of celebrating, and it fell apart three separate ways:
the statistical unit was wrong (one training run's time series, not repeated runs); the effect
**reversed against the placebo** (the arm fed *no* tail information at all had the safest tail of
everything — the "effect" tracked general risk-return positioning, not tail information); and the
direct measure of "does the code respond to the fed numbers?" came out *negative*. So the pilot's
lesson was the opposite of its headline: it exposed exactly the traps the final design now guards
against, and its defects map one-to-one onto the final design's controls. For this reason the
dissertation follows an iron rule: **no number from the pilot appears anywhere as evidence.** The
pilot validated the machinery; the frozen campaign produces the science.

---

## Part 7 — The most interesting part: why "no difference" is the expected — and valuable — answer

### 7.1 The envelope: what mathematics guarantees, and what it doesn't

There's real theory in the dissertation (its Chapter 3), and its punchline is understandable
without any formulas.

The scalar that the control arm sees is *literally a piece of* what the treatment arm sees (same
score line, minus the six tail lines). Information theory (a classical result of David Blackwell,
1950s) then guarantees: **an *ideal* decision-maker can never do worse with the extra information**
— whatever it could do with less, it can do with more, by ignoring the extra. So "more information
can't hurt" is a *theorem*…

…about an **ideal** user. And that's the whole point. The theorem is an **envelope** — a ceiling on
what's achievable — not a prediction about a real, finite, quirky language model feeding a real,
finite learning agent. The dissertation's actual empirical question is: **how much of that
theoretical ceiling does today's frontier AI actually realise?** Measuring the gap between the
envelope and reality is a legitimate scientific measurement *whatever the answer is*.

### 7.2 Three specific places the chain can break

For the extra information to show up as safer trading, a three-link chain must hold:

> **Link 1 — Reading:** the fed tail numbers must actually change the code the LLM writes.
> **Link 2 — Transmission:** the changed code must change the trained agent's behaviour.
> **Link 3 — Realisation:** the changed behaviour must survive into out-of-sample results.

Each link has a concrete, documented reason it might fail:

- **Link 1 — the numeracy bottleneck (the headline suspect).** LLMs, for all their brilliance with
  words and code, are *measurably unreliable at comparing close small numbers* — published
  research puts frontier models at 50–70% accuracy on tasks like "which is smaller, −0.0577 or
  −0.0582?", the failures traceable to how models chop numbers into tokens. Now look at the fed
  tail block: it is *precisely* a list of close small decimals. The information may arrive and
  simply never be read. (Elegant twist: the experiment includes a pre-registered probe that
  re-renders the *same* numbers legibly — as whole basis points with rank tags — to test whether
  legibility, not capacity, is the barrier.)
- **Link 2/3 — a deep structural fact about the agent.** There's a known mathematical obstruction:
  an agent that maximises the *average* of a step-by-step reward cannot, in general, be made to
  exactly optimise a *tail* property of its overall outcome distribution — encoding tail-optimality
  properly requires machinery (augmented state, non-standard policies) that this experiment's fixed
  agent deliberately doesn't have (it's held fixed for fairness — the identification principle).
  So even a perfectly tail-aware reward might not fully transmit.
- **And the selection stage is deliberately tail-blind.** Winners are picked purely on the
  (deflated) Sharpe score — no tail term — so that any tail improvement is attributable to the
  *feedback*, not to the experimenter quietly selecting for tails. Conservative by design; also one
  more reason a tail advantage is hard to realise.

Because several independent reasons all point the same way, the pre-registered prediction table has
three branches — **Strict** (tail feedback works: better tail outcomes, responsive code), **Weak**
(partial, inconclusive-and-bounded), **Null** (no difference anywhere, unresponsive code) — and the
project openly predicts the **Null branch**. Notice something elegant: the theory predicts that
even in the *success* branch there's no Sharpe advantage (the tail-blind selection stage sees to
that) — the branches separate only on the tail measures and the code-level instruments. The
pilot's directional evidence (negative responsiveness; the placebo reversal) points the same way.

### 7.3 The detective kit: locating the break

This is the dissertation's claimed originality — not the win/lose verdict, but the **instrumented
autopsy** (its "mechanism audit"):

- **Responsiveness (Link 1):** statistically, do movements in the fed tail numbers correlate with
  changes in the authored code?
- **Mediation (Link 2):** a standard statistical decomposition asking how much of any outcome
  difference flows *through* the code changes. If Link 1 is dead (fed numbers don't move the code),
  then arithmetic forces the whole indirect path to zero — and the null is *explained*, not just
  observed.
- **The code taxonomy (fingerprinting what was written):** every authored reward function is
  classified by its structural skeleton — the shape of its code, with all names and numbers
  stripped away. This matters because an LLM might *mention* "cvar_05" in a variable name without
  computing anything tail-related — words are cheap. The skeleton view separates *echoing the
  vocabulary* from *changing the computation*. It also answers a lovely question: do differently-fed
  arms write different *kinds* of programs, or the same kinds with different decoration?
- **The controls as probes:** the scrambled-values arm (does the model respond to a plausible
  risk-table *costume*?) and the one-number arm (is the multi-level *shape* used at all?) each pin
  down a specific alternative story.
- **The legibility probe:** same information, friendlier format — if responsiveness jumps, the
  bottleneck is *reading*, and there's a concrete, cheap fix for the whole field ("render your
  feedback legibly"), which would be a genuinely useful practical discovery extracted from a null.

So the final report will not say "no effect, sorry." It will say something like: *the information
was present (theorem), the code did not track it (Link 1 severed — here's the correlation, here's
the code fingerprint evidence), the equivalence is bounded (±0.05), and the leading explanation is
numeric legibility (here's the format probe).* That's a mechanism, a boundary, and an agenda —
from a null.

**Why anyone beyond one degree committee cares:** the AI world is racing to put LLMs inside
automated discovery loops (writing rewards, objectives, even whole research pipelines), and
evaluates them almost entirely by demonstrations — "look, it worked." This dissertation is a
carefully-built counterexample culture: a controlled, sealed, pre-registered test of one loudly
plausible assumption ("richer feedback helps"), with the result that richer feedback **is not
self-acting** — information you feed an LLM is not automatically information it *uses*. Anyone
building such systems needs to know exactly this, and the experimental template is reusable for
any of the field's other untested assumptions.

### 7.4 "But why expect the LLM to fail? Isn't that pessimistic?"

The most natural objection — so let's meet it head-on. The null prediction is **not pessimism**; it
is a calibrated best guess from four independent sources, made inside a design where honesty costs
nothing:

1. **We already looked.** The pilot ran this exact loop, and the direct measurement of "does the
   authored code track the fed tail numbers?" came out *negative* — and the apparent tail advantage
   reversed against the placebo. The machine's own evidence points to the null; predicting success
   against your own measurement would be the dishonest move.
2. **There's a documented mechanism.** Published research shows frontier LLMs are only 50–70%
   accurate at comparing close small numbers — and the fed block is precisely a list of close small
   negative decimals. A narrow, specific, *testable* reading bottleneck — not "LLMs are dumb."
3. **The design deliberately handicaps the effect, for fairness.** Tail-neutral prompts (only the
   *marginal* value of tail-specificity is measured — subtle by construction), tail-blind winner
   selection (so selection can't fake a tail effect — but also doesn't reward one), and a genuine
   mathematical obstruction at the agent stage (a mean-maximising agent cannot exactly optimise a
   tail property — a theorem, not an opinion).
4. **"Null" does not mean "the LLM fails at its job."** It still writes working — sometimes
   excellent — reward code; whether it beats human rewards or dumb search are separate questions it
   may well win. The prediction is only that the *extra six numbers* don't change what it writes:
   the channel fails to add value, not the author.

And the deeper logic: the experiment is built so that **we don't need the LLM to succeed for the
research to succeed**. If tail feedback works, that's the pre-registered Strict branch — the first
controlled evidence that feedback *content* matters, and nothing in the design suppresses it. If it
doesn't, the instruments locate *where* the information is lost, the statistics *bound* the effect,
and the legibility probe extracts a practical fix for the field. Because both branches are valuable,
there is no incentive to spin — which is exactly what frees the prediction to be honest. And a
hard-to-love prediction committed in advance, under seal, is what makes *any* outcome a genuine
test: being wrong in the happy direction would be the most convincing possible version of a positive
result.

### 7.5 "But it worked in Eureka — shouldn't it work here?"

Careful — two different claims are being blended. What Eureka established is that (a) an LLM can
write reward code that beats human designs, and (b) the feedback **loop** matters (removing
reflection entirely cost ~28.6%). What Eureka *never tested* is whether the feedback's **content**
matters — its feedback was scalar-flavoured throughout, and its famous ablation compared feedback
against *silence*, never one kind of feedback against another. Our H1 and H4 (LLM vs human rewards,
LLM vs dumb search) *are* the Eureka result transplanted to finance, and there the precedent
genuinely supports optimism. The null prediction lives only in **H2** — the content contrast Eureka
never ran. And the analogy weakens exactly there, four ways: our contrast is a *margin*
(scalar vs scalar-plus-tail) rather than Eureka's all-or-nothing ablation; Eureka's feedback was
*labelled, actionable component scores* the LLM could read like a code review, while ours is six
close small decimals — the documented LLM weak spot; robotics simulators have loud signals and big
headroom while markets are noisy; and Eureka's selector rewarded task-aligned improvements while
ours is deliberately tail-blind for fairness. Finally: the study's novelty is the **question and the
instrument**, not a new method that ought to win — it is novel precisely *because* the field has
been assuming the answer instead of testing it. If we were confident it worked, the study would be
less interesting, not more.

---

## Part 8 — The practical machinery (in passing, but worth knowing)

- **Scale.** 7 arms × 30 candidates × 400,000 training steps, then the winners re-trained across
  the seed ladder — thousands of training runs. It runs on **UCL's Myriad supercomputing cluster**
  (with the author's own GPU laptop certified as a fallback that produces bit-for-bit identical
  science — the cluster is speed, not a dependency).
- **Why 400,000 steps?** Measured, not guessed. A learning curve was mapped across budgets from
  small to 1.6 million steps (under a rule *pre-committed before the data came in* — the same
  anti-fooling discipline as everything else), and 400,000 is the measured "knee": ~90% of the
  attainable performance at a fraction of the compute, applied identically to every arm.
- **Determinism and replay.** Same seed → same result, bit for bit; every LLM interaction archived
  at call time. LLMs themselves are *not* deterministic — ask twice, get different code — so the
  scientific object is the archive: any analysis re-runs exactly from disk. A suite of **~2,100
  automated tests** guards the whole machine, including deliberately adversarial ones (e.g. corrupt
  all "future" data and verify the agent's observations don't change — proving it can't peek
  ahead).
- **Cost sanity.** The LLM writing the rewards is Claude Opus 5 (a frontier model, pinned to a
  dated version for reproducibility); authoring the whole campaign's rewards costs on the order of
  tens of dollars. The expensive part is the GPU training time, hence the cluster.
- **The data are licensed** (LSEG/Refinitiv) and can't be redistributed — so the repository ships
  the *recipe* (the exact pipeline plus checksums so an entitled person can rebuild and verify the
  identical dataset byte-for-byte) and a synthetic stand-in dataset on which all the code runs.

---

## Part 9 — The dissertation as a document

- It's an MSc dissertation at **UCL**, graded **on the PDF alone** — no oral defence — by the
  supervisor **Dr Ramin Okhrati** (a probability theorist who works on risk measures and on LLM
  risk behaviour — the theory chapter's rigour and the honest-null framing are pitched precisely
  at that readership) plus a second marker who may be from any discipline (hence: everything must
  also be clear to a non-specialist — the spirit of this very document).
- Main text is capped at **10,000 words** (figures, mathematics, appendices excluded), in a fixed
  16-section structure. Deadline **1 September 2026**.
- Chapter map: introduction and question → related work (where the novelty sits) → theory (the
  envelope) → methods (Parts 3–6 here) → the pilot (machinery-validation only — no pilot number is
  evidence) → results (currently a fully pre-built skeleton whose every number reads
  `[FROM CAMPAIGN]`, awaiting the frozen campaign) → discussion, limitations, conclusion.
- The grading rubric prizes exactly what the design leans into: independence of thought,
  unquestionable originality, publishable significance, faultless communication — and the
  examiner's known tastes: intuition before machinery, depth over breadth, honesty over spin,
  motivate-the-method-with-data. The work is also being prepared for real publication afterwards
  (journal track: TMLR; conference track: ICAIF).
- Status at the time of writing: design frozen (2026-07-18), machinery certified, campaign awaiting
  final launch; then the results chapters get their numbers and the writing month begins.

---

## Part 10 — Plain-words glossary

| Term | Plain meaning |
|---|---|
| **Agent** | The learning trading program (here: a standard algorithm called SAC, held identical everywhere) |
| **Arm** | One experimental group; seven in total, differing only in feedback shown to the LLM |
| **Backtest** | Evaluating a strategy on historical data as if it had traded then |
| **CVaR (x%)** | "Average loss across your worst x% of days" — the tail-badness measure |
| **Coherent risk measure** | A risk measure passing sanity axioms (e.g. never punishing diversification); CVaR qualifies |
| **Critic** | The agent's internal "how good is my situation?" estimator; deliberately untouched here |
| **Deflated Sharpe (DSR)** | Sharpe ratio with the luck of trying-many-candidates subtracted |
| **Equivalence test (TOST)** | Statistics for *actively showing* a difference is smaller than a pre-set "smallest difference that matters" |
| **Feedback / reflection** | What the LLM is shown about its last attempt before writing the next |
| **Freeze / hash** | The cryptographic wax seal on the pre-registered plan (`ce5db62c…`); software refuses to run if broken |
| **Left tail** | Your worst days, as a group |
| **LLM** | Large language model — AI that writes text and code (here: Claude Opus 5) |
| **Null result** | "No difference found" — here, predicted, pre-registered, bounded, and explained |
| **Placebo** | An inert stand-in for the treatment, to separate "got something" from "got information" |
| **Portfolio weights** | The fraction of money in each stock (plus cash), re-chosen daily |
| **Pre-registration** | Publicly fixing hypotheses and analysis before results exist |
| **Reward function** | The scoring code that defines what the agent tries to maximise — here, written by the LLM |
| **Reward hacking** | The agent exploiting the letter of the reward against its spirit |
| **Seed** | The starting random state; different seeds → different runs; matched seeds → fair comparisons |
| **Sealed test set** | The final years of data, untouched until the single final verdict |
| **SESOI** | "Smallest effect size of interest" — the pre-declared ±0.05 band defining practical equivalence |
| **Sharpe ratio** | Return earned per unit of bumpiness endured |
| **Survivorship bias** | The rosy distortion from silently dropping companies that died; this dataset keeps them |
| **Transaction cost** | The price of changing holdings; charged on every trade here |

---

*Written 2026-07-19 from the frozen state of the project (seal `ce5db62c…`). Best read alongside
`DISSERTATION_MASTER_OVERVIEW.md`, which states everything here with full technical precision.*
