# Reproducibility section (draft for paper §4.8) — 2026-07-25

> The honest three-layer statement, verified first-hand against the repo. Replaces the current
> two-regime §4.8. Grade-A claims + the NEEDS-A-FIX list are at the bottom. Citations marked
> [VERIFY] must clear the pre-submission sweep.

## 4.8 Reproducibility

Reproducibility here is not one guarantee but three, at descending strength, and the usual error is to
advertise the strongest as if it covered the whole pipeline. We answer the study against the NeurIPS/TMLR
machine-learning reproducibility checklist (Pineau et al. 2021 [VERIFY]; see
`docs/REPRODUCIBILITY_CHECKLIST.md`), and because reproducibility in machine learning is empirically
fragile (Gundersen & Kjensmo 2018 [VERIFY]) and quantitative backtests are especially prone to
non-reproducible overfitting (López de Prado 2018; Bailey & López de Prado 2014), we separate three
layers and state each with its exact scope *and* its honest boundary.

**Layer 1 — the analysis replays deterministically from the archive.** Given the archived generations,
every number recomputes: the *generative artifacts* — every rendered prompt, the reward source, and the
panel — reproduce **hash-exact**, and the *trained* numbers reproduce to a tight tolerance (relative 1e-4)
on a fixed device (they are not bit-identical, because floating-point reductions are non-associative). The
full stochastic stack is seeded from a single run seed —
Python `random`, NumPy, PyTorch and cuDNN — with `PYTHONHASHSEED` fixed and `CUBLAS_WORKSPACE_CONFIG=:4096:8`
set *before the first CUDA op* so cuBLAS matmul is deterministic (`src/utils/seeding.py`). The environment
is pinned by exact version in `requirements.lock` (`==` pins, not artifact-hash `--hash` pins) — the notorious source of irreproducible RL numbers,
the PyTorch/CUDA build, is fixed at `torch==2.6.0+cu124` (with `stable-baselines3==2.8.0`) against
interpreter `3.11.9`. The campaign's parallel execution path is proven byte-identical to the serial one by
a behaviour test (`tests/test_test_leg_equivalence.py`), so throughput optimisation cannot move a result.
A continuous-integration job and a pre-commit hook both run `freeze.py --check` on every touch to a design
file, so the analysis cannot silently drift from the frozen specification. The honest boundary: this
determinism holds *on a fixed device* (and even there the trained numbers match to a tight tolerance,
not bit-for-bit). Across a CPU↔GPU boundary, across different GPUs, or across
PyTorch releases, floating-point non-associativity makes training only *statistically* reproducible —
which is exactly why every headline is an interquartile mean with bootstrap error bars over a seed ladder,
never a single run (Henderson et al. 2018).

**Layer 2 — the protocol is re-runnable by anyone.** The entire design — hypotheses, arms, candidate and
seed budgets, splits and embargo, the frozen tail-diagnostic vector, the benchmark suite and the analysis
plan — is bound by a single canonical SHA-256 hash over eight files: the pre-registration prose, its
machine-readable mirror, three executed configuration files (inference, environment, data) and three
treatment files (the per-arm feedback specification and the two loaded prompts). The *manipulated variable
itself* is therefore inside the hash, not merely the prose describing it (`scripts/freeze.py`). The
licensed Refinitiv/LSEG panel is the one artifact we cannot ship, and we say so plainly: the repository
carries SHA-256 checksums, the full acquisition pipeline, and a shape-identical synthetic panel, so an
unentitled reader runs the entire machinery end-to-end on synthetic data while an entitled one rebuilds
the exact panel and verifies it against the checksums. The freeze is deliberately unstamped at the time of
writing (`frozen: false`): it executes at launch, together with the campaign-run approval, so the
immutable hash coincides with — rather than merely precedes — the first sealed-leg evaluation.

**Layer 3 — the experiment is anchored in open weights.** A single frontier closed model (Claude Opus 5)
is the confirmatory reward-author, chosen for capability; but a closed model is a reproducibility
liability — it is eventually deprecated and its exact weights withdrawn, at which point the generative
step becomes historically irreproducible. We mitigate on two fronts. First, ten replication legs re-run
the identical protocol, five open-weight and pinned by Hugging Face repository *and commit hash*
(`model_suite.hf_pins_recorded`), because a hosted API route is transient whereas a weights commit is
permanent — anyone can re-host the pinned artifact. That commit is bound into the freeze
(`assert_leg_roster_match`), so the permanence anchor cannot drift post-freeze. Second, we disclose what
was *served*, not what was *requested*: the Qwen legs are served fp8 by one pinned provider, so the
authoring artifact is the fp8-served variant of the bf16-pinned weights — the pin, provider and
quantisation *together* define the executed author, and we never claim the bf16 weights authored the code.
For the closed legs and the confirmatory author we archive the provider-reported `served_model`,
`served_provider` and `request_id` at each call and rely on the vendor's stated weight-preservation
commitment; the residual deprecation exposure is disclosed, not hidden.

*The self-hosted-leg question, answered honestly.* We scope Layer 3 to what the artifact **demonstrates
today: re-hostable pinned weights — replication, not bit-reproduction of the generation.** Every open-weight
leg is served through a hosted router (the registered `qwen3.5-9b` leg is served fp8 by a pinned provider),
so the permanence guarantee is that anyone can re-host the pinned `repo@commit`, not that the generation is
bit-identical. The single upgrade that would close the remaining distance — authoring one leg from the exact
HF-commit-pinned bf16 weights on known UCL Myriad hardware, the one configuration whose *generation* is
bit-reproducible — is **built and turnkey** (`scripts/serve_qwen_selfhost.py`) but **not yet executed and not
yet a registered suite leg**; we name it as the next step and claim no self-hosted author the run has not
produced.

**Why the generation cannot be regenerated.** Language-model inference is non-deterministic even at fixed
model and temperature: floating-point non-associativity under concurrent execution yields different
completions for the same prompt on commodity hardware (Yuan et al. 2025), and versions drift beneath
fixed identifiers. We therefore adopt a replay-from-archive contract — every rendered prompt, raw
response, resolved and served model id, token usage and stop reason is written to an append-only
provenance ledger at generation time (`ProvenanceRecord`, `src/llm/client.py`), and all downstream results
replay from that archive; the model is never re-queried. A pre-freeze audit hardened the weakest part of
this contract. Reasoning ("thinking") pins were previously *asserted* to function but never *measured*, so
a silently-ignored pin was indistinguishable from a live one — the failure mode that let several legs
author empty code under an unpinned thinking default. The client now captures the reasoning-token count
and served provider on every call, and the leg gate renders a direction-aware, three-state verdict: an
*enable* pin returning zero reasoning tokens on a real authoring call is flagged FICTIONAL, a *disable*
pin returning positive tokens is flagged IGNORED, and an absent field is honestly reported UNVERIFIED
rather than passed (`scripts/leg_gates.py`). A pin is now evidence, not a promise.

**Reproducibility limitations, foregrounded.** (i) Bit-exact replay is device-conditional (Layer 1). (ii)
The confirmatory author is a closed model under a currently *undated* identifier; we archive the served
id and request id at the first live call, but a dated snapshot would be stronger and deprecation exposure
remains. (iii) The provenance ledger is append-only JSONL flushed per call — crash-consistent and
complete, but not cryptographically tamper-evident; a signed manifest would harden it. Reasoning
round-trip evidence is captured for the OpenRouter legs via the usage field; the Anthropic legs expose no
equivalent reasoning-token count, so their thinking posture is disclosed rather than round-trip-measured.
None of these touches the analysis layer, which replays deterministically given the archive (hash-exact
generative artifacts; tolerance-exact trained numbers on a fixed device).

### Table 4.x — Reproducibility artifacts
| Artifact | What it pins | Where |
|---|---|---|
| `.python-version` | Interpreter `3.11.9` | repo root |
| `requirements.lock` | Exact **version** pins (`torch==2.6.0+cu124`, `sb3`/`sb3-contrib==2.8.0`, `anthropic==0.111.0`, `openai==2.42.0`); `==` pins, not `--hash` artifact pins | repo root |
| `src/utils/seeding.py` | Single-seed determinism: RNGs, `PYTHONHASHSEED`, `CUBLAS_WORKSPACE_CONFIG` | `src/utils/` |
| Canonical SHA-256 freeze hash | 8 design files (prereg prose + yaml, 3 configs, 3 treatment/prompt files) | `scripts/freeze.py` |
| CI + pre-commit `freeze.py --check` | Design-drift guard on every commit/push | `.github/workflows/ci.yml`, `.pre-commit-config.yaml` |
| `tests/test_test_leg_equivalence.py` | Parallel ≡ serial byte-identity (fixed device) | `tests/` |
| Checksums + pipeline + synthetic panel | Byte-exact panel verification / license-free method replay | `data/manifest/manifest.jsonl` + `data/**/*.provenance.json` (checksums), `data_pipeline/`, `src/data/synthetic.py::make_synthetic_panel` |
| `ProvenanceRecord` → `llm_calls.jsonl` | Per-call prompt, response, usage (+`reasoning_tokens`), stop reason, `served_model`/`served_provider`, `request_id` | `src/llm/client.py` |
| `hf_pins_recorded` + `assert_leg_roster_match` | Open-leg weights `repo@commit` (5 legs), bound into the freeze | `preregistration.yaml`, `legs.yaml`, `freeze.py` |

## Claims split
**GRADE-A (verified first-hand in-repo):** seeded stack + hash-seed + CUBLAS config before first CUDA op
(`seeding.py:38-63`); exact pins (`requirements.lock`, `.python-version`); parallel≡serial byte-identity
test; freeze = SHA-256 over 8 files incl. the two prompts + `arms.yaml`; drift guard in BOTH CI + pre-commit
(`ci.yml:22-27`, `.pre-commit-config.yaml:34-36`); replay `ProvenanceRecord`; R103 reasoning round-trip
REAL (`client.py:196-201,276`) + three-state leg-gate verdict (`leg_gates.py:215-242`) + hf_pin-COMMIT
freeze binding (`freeze.py:988-1001`); 5 open legs HF-commit-pinned; served-variant fp8 disclosure;
device-conditional determinism stated; FP-nondeterminism already cited (`yuan2025nondeterminism`, `CH4:318`).

**✅ WORDING OVERCLAIMS CORRECTED 2026-07-26 (deep reproducibility audit).** Four falsifiable claims fixed in
this doc: "bit-exact replay" → "hash-exact generative artifacts + tolerance-exact (1e-4) trained numbers,
fixed-device"; "byte-level pins" → "exact-version `==` pins (not `--hash`)"; `data/**/*.sha256` → the actual
`manifest.jsonl` + `*.provenance.json` checksums; and the self-hosted dual framing → the honest **re-hostable**
scope (self-host named as built-but-unexecuted). The items below are now EXECUTION/artifact gaps, not wording.

**NEEDS-A-FIX (close before deposit):** (1) self-hosted leg — EXECUTE the Myriad Qwen-9B-bf16 self-host (A5)
+ register it as a suite leg to upgrade Layer 3 from re-hostable to bit-reproducible (the framing is now
consistent everywhere). (2)
Regenerate the STALE `MODEL_CARD.md` + `REPRODUCIBILITY_CHECKLIST.md` (30 seeds/50k/laptop-only → the
ladder→568, B*=400k, Myriad-primary). (3) Replace the current 2-regime CH4 §4.8 with this 3-layer version.
(4) Confirmatory `claude-opus-5` is dateless — archive served_model+request_id at first call (already in
client.py), pin a dated snapshot if published. (5) Soften "byte-level tamper-evidence" (it's append-only
JSONL) or add a signed manifest. (6) Reconcile the "2000+ tests" vs "611" count to the live number.
