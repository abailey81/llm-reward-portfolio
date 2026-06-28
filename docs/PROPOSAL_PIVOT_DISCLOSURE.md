# Scope disclosure — change of research question

**DRAFT — requires Dr Okhrati's written sign-off before submission.**

> Intended placement: dissertation Introduction (scope/contribution statement). This is an
> examiner-facing disclosure of a deliberate, supervisor-approved **change of research question**
> relative to the approved proposal. It is not a confession of drift; it is the record of a design
> decision taken openly at the outset. The paragraph below is the text to be inserted; this header
> and the verification note are not part of the dissertation.

> **Why this is worded as a "change of research question," not a "narrowing."** A first-hand reading
> of the approved proposal (`UCL_Deep_RL_Dissertation_Proposal_v2.docx`, Feb 2026, ~2,970 words)
> establishes that the dissertation is a **near-total replacement** of the proposal's programme, not a
> subset of it, so the candid word is *change*, not *narrowing*. The proposal's contribution was an
> explicit **ten-component framework** answering **seven research questions (RQ1–RQ7)** — DreamerV3
> world-model, Mamba state-space encoder, graph-attention (GAT) cross-asset encoder, HMM regime
> detector, IQN-SAC distributional critic, multi-objective Pareto RL, MAML meta-learning, conformal
> prediction, and a double-machine-learning (DML) causal layer — in which the **LLM appears only as
> Component 1: a FinBERT/BERTopic news-SENTIMENT encoder** turning text into probability features. A
> full-text search of the proposal returns **zero** occurrences of *eureka*, *reward design*, *reward
> function*, *reward code*, *reward-function code*, *distributional feedback*, or *reward shaping*. The
> only genuine overlap with the present work is thematic and shallow — both care about CVaR / tail risk
> in a portfolio RL setting — but even there the mechanism is opposite: in the proposal CVaR lives
> *inside* an IQN-SAC critic (Wang distortion on the quantile function, an architecture); in the
> present work the realised-return tail is *fed back to an LLM* as a reflection signal (a feedback
> loop). Describing this as a "narrowing" or "de-scoping" would mis-state the record — the new question
> is not contained in the old seven. Calling it what it is — a change of question — reads as
> independence and judgement, not weakness. **(Verify the term counts and component list against the
> docx before relying on this paragraph in the submitted PDF; the supervisor co-authored corpus
> material and a loose characterisation is easily checked.)**

---

With my supervisor's agreement, this dissertation pursues a **different research question** from the
one set out in my originally approved MSc proposal. The approved proposal advanced an ambitious
ten-component architecture as its contribution — a DreamerV3 world-model, a Mamba state-space
backbone, a graph-attention (GAT) cross-asset encoder, an HMM regime detector, an IQN-SAC
distributional agent, multi-objective Pareto reinforcement learning, MAML-style meta-learning,
conformal risk guarantees, and a double-machine-learning causal-inference layer — organised around
seven research questions, with a large language model used in a single peripheral role: a
FinBERT-style news-sentiment encoder feeding the state representation. On reflection, and after
discussion with Dr Okhrati, that programme was judged unsound *as a dissertation* on an
**identifiability** ground rather than an effort one: with ten interacting novel components, no single
finding could be cleanly attributed to any one of them, and a negative or ambiguous result — the
likeliest outcome for any one module under MSc time and compute — would have been uninterpretable. A
ten-way integration cannot answer a sharp scientific question; it can only report whether a large
bespoke system happened to work.

We therefore changed the question. The work now asks a single, sharply defined one — **whether an LLM
reward-designer, embedded in an Eureka-style reflection loop, is a Bayes-responsive user of risk
information**: does feeding the model the realised-return *tail* (a multi-level tail-risk signal:
several CVaR levels, left-tail mass, and robust skew) rather than a scalar performance number
measurably change the risk profile of the resulting policies? This is not a sub-question of the
original seven; it promotes the LLM from a peripheral sentiment encoder to the central object of
study, holds the RL agent fixed and simple (a single SB3 SAC learner, not a ten-module stack), and
manipulates exactly one variable — the feedback channel. That makes the study **identifiability-clean**
(one manipulated cause against a fixed agent at matched compute), it is **pre-registered and
hash-frozen** before any confirmatory result is seen, and it yields a **bankable, decision-relevant**
outcome whether the effect is positive or null. I disclose this openly as a change made at the
outset and approved by my supervisor, not a silent drift away from the registered plan; the
components of the original framework are recorded as future work, and the one substantive point of
contact between the two designs — the centrality of tail risk (CVaR) to a risk-sensitive portfolio
agent — is retained and, indeed, sharpened into the dissertation's central manipulation.
