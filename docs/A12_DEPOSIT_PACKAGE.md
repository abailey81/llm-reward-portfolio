# A12 — the public pre-registration deposit, assembled and ready to submit

**Status: EVERYTHING IS PREPARED. What remains is an account action only Tamer can take (~10 minutes).**

This closes the gap between "a registered obligation that appears unmet" and "one form to fill in". It
does **not** duplicate any bound file into the repo: the bundle is produced on demand from the signed
freeze tag, so what gets deposited is provably the frozen design and not a copy that could drift.

---

## 1. What is registered, verbatim

`config/preregistration.yaml → freeze_day_checklist_additions.public_deposit`:

> *"at the v2 freeze: deposit the prereg bundle PUBLICLY (OSF or Zenodo, DOI'd) — the public timestamp
> anchor referees can verify (the private-repo tag/bundle/OpenTimestamps remain the internal chain)"*

So the deposit is the **pre-registration bundle**, not the code base and not the licensed data. That
matters: the Refinitiv panel is licensed and **must never be deposited**.

## 2. What goes in — the nine hash-bound files, and nothing else

The canonical freeze hash is computed over exactly these, in this order:

| # | file | what it binds |
|---|---|---|
| 1 | `PREREGISTRATION.md` | the human-readable prose record |
| 2 | `config/preregistration.yaml` | the machine record (freeze state stripped before hashing) |
| 3 | `config/inference.yaml` | splits, embargo, testing family (m=6), multiplicity, SESOI, DSR |
| 4 | `config/environment.yaml` | lookback, vol windows, action projection, costs, cash rate |
| 5 | `config/data.yaml` | splits, embargo days |
| 6 | `config/arms.yaml` | the per-arm feedback spec — the manipulated variable's wiring |
| 7 | `prompts/system.txt` | the reward-design contract shown to every arm |
| 8 | `prompts/initial_generation.txt` | the generation-0 instruction shown to every arm |
| 9 | `src/feedback/schema.py` | **renders** the fed numbers — the treatment surface itself (#97) |

| | |
|---|---|
| canonical SHA-256 | `3ca6f01ab7724d47bd5d01bc9e73b4d3150c049e1048dd86a864b400a230432f` |
| tag | `prereg-v2.1` (annotated), seal commit `b9c2be5`, 2026-07-28 16:17 +0100 |
| predecessor anchor | v2.0 = `4f90ecc4…`, tag `prereg-v2.0` — preserved, never overwritten |

## 3. Build the bundle (one command, reproducible by anyone with the repo)

```
git archive --format=zip --prefix=prereg-v2.1/ -o prereg-v2.1-bundle.zip prereg-v2.1 \
  PREREGISTRATION.md config/preregistration.yaml config/inference.yaml \
  config/environment.yaml config/data.yaml config/arms.yaml \
  prompts/system.txt prompts/initial_generation.txt src/feedback/schema.py
sha256sum prereg-v2.1-bundle.zip
python scripts/freeze.py --check          # must print RC=0 and "[MATCHES]" before you deposit
```

**VERIFIED 2026-07-30:** the command above was run and produces exactly the nine files (plus directory
entries), `rc=0`.

Deposit the zip **plus** the manifest below as a plain-text file. Do **not** advertise the zip's own
sha256 as the anchor — `git archive` output is not byte-stable across git versions. The **per-file**
hashes are, and the canonical freeze hash is re-derivable by anyone from the repo's own
`scripts/freeze.py`:

```
canonical freeze SHA-256 : 3ca6f01ab7724d47bd5d01bc9e73b4d3150c049e1048dd86a864b400a230432f
git tag                  : prereg-v2.1 (annotated)   seal commit: b9c2be5   2026-07-28 16:17 +0100

a453ed9d18d9f0094333437657e5abfaf9b6310101fa69917280b8a3c1b0d6a2  PREREGISTRATION.md
fe1f3874f2fb76b6c404bfbb2d3141fa0aca0e33ff2037e6e155b48ebf169cd0  config/preregistration.yaml
371eb9ed7f0a323de045465c59e2263deb0c5c3f70180a382fe889f0e8d1d5f1  config/inference.yaml
a5a20b26af38424aa9ac1324a4fe138c98bcd53db1f7b45c3b3e9a6ee9e0d183  config/environment.yaml
c178b0d911948597f16fbdac98b7857ec81bd139406727ed56a3c61384ba2d81  config/data.yaml
c5db9c6c92136dc25e9ee86ac512c4e3ed9bb7849597694c6c5f89744ca7919b  config/arms.yaml
bc1f365a617595e334580949b994ee8e538579717b2be23f2552dcef9e82ebfc  prompts/system.txt
2c2d23fb9019c39b030faba782523366af8515aa01805d5a6f13705cc2527ebe  prompts/initial_generation.txt
bb8574b2edc21436a445863f95a3299f6dae440a43f5664a4a0253cd58974a3c  src/feedback/schema.py
```

## 4. Paste-ready deposit metadata

| field | value |
|---|---|
| **Title** | Pre-registration bundle v2.1 — *Does richer tail information change the reward an LLM writes?* A pre-registered study of LLM-authored reward code for risk-sensitive portfolio reinforcement learning |
| **Authors** | Atesyakar, Tamer (UCL) |
| **Resource type** | Preprint / Project → *Pre-registration* |
| **Publication date** | the freeze date, **2026-07-28** (state it explicitly; the DOI's own timestamp is the anchor) |
| **License** | CC BY 4.0 for the bundle text; note that the code file it contains is under the repository `LICENSE` |
| **Keywords** | pre-registration; reinforcement learning; reward design; large language models; risk-sensitive control; CVaR; portfolio optimisation; reproducibility |
| **Description** | Pre-registration bundle for a study testing whether the tail information fed to an LLM changes the reward function it authors for a risk-sensitive portfolio RL agent. Five treatment arms (`distributional`, `scalar`, `scalar_cvar5`, `placebo`, `placebo_shuffled`) plus four derivative-free optimiser arms; only the fed feedback block differs across arms. Hypotheses, estimands, multiplicity control (BH q=0.05 over m=6), SESOI (0.05 DSR), equivalence margins, the seed ladder and the stopping rule are all fixed in advance. Canonical SHA-256 of the bundle: `3ca6f01a…0432f`; git tag `prereg-v2.1`, seal commit `b9c2be5`. Amendments R1–R115 are recorded in the bundle and were all made **before** any confirmatory data existed. |
| **Related identifiers** | the GitHub repository URL (as *"is supplemented by"*), and the eventual dissertation/preprint DOI once it exists |

⚠ **Do NOT upload:** the Refinitiv gold panel, any `outputs/` tree, or API keys. The bundle command
above cannot pick them up, which is why it is written as an allow-list rather than an exclude-list.

## 5. The click path

1. **Zenodo** (recommended — DOI issued instantly, versioned, and it accepts a GitHub link):
   log in → *New upload* → drop `prereg-v2.1-bundle.zip` and the hash text file → set *Resource type =
   Preprint* (or *Other → pre-registration*) → paste the metadata from §4 → *Publish*.
   OSF works equally well (*Registrations → Preregistration*) if a registry framing is preferred.
2. Copy the DOI back into: `CITATION.cff`, `paper/FRONT_MATTER.md`, the Reproducibility section, and
   `config/preregistration.yaml`'s checklist row — **the yaml edit is a bound file, so it happens at the
   next unfreeze/re-freeze, not live.** Record the DOI in `docs/HANDOFF.md` §1 immediately.
3. Tell this session the DOI and it will wire every non-bound reference in one pass.

## 6. Why it is worth the ten minutes

The rubric's publishability yardstick rewards a verifiable public timestamp, and a pre-registration
that a referee can check *independently of us* is the difference between "they say it was
pre-registered" and "here is the DOI, dated before the first confirmatory record". It is the cheapest
grade-bearing action left on the board, and the one thing here that cannot be done on Tamer's behalf.
