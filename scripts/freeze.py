"""Pre-registration freeze (FINAL_PLAN Phase 1.E; punch-list Rank 9).

Purpose
-------
Lock the experimental design before any results are seen. The freeze is a GATE:
``PREREGISTRATION.md`` (the human-readable prose record) and
``config/preregistration.yaml`` (its machine-readable mirror) must agree on every
freeze-relevant field, Phase 0 must have passed, and only then is a single canonical
SHA-256 over the pre-registration artifacts AND the executed load-bearing configs
recorded as the immutable design hash.

The canonical hash
------------------
SHA-256 over the **LF-normalized UTF-8 bytes** of the hashed artifacts concatenated in a
FIXED, documented order (``norm`` = strip-BOM + CRLF/CR -> LF; ``strip_state`` = blank the
two MUTABLE ``frozen``/``freeze_hash`` lines so the hash is INVARIANT to the freeze act)::

    canonical_bytes = norm(PREREGISTRATION.md)
                      + b"\n" + strip_state(norm(config/preregistration.yaml))
                      + b"\n" + norm(config/inference.yaml)        # if present  ┐ _BOUND_CONFIGS
                      + b"\n" + norm(config/environment.yaml)      # if present  │ (executed knobs)
                      + b"\n" + norm(config/data.yaml)             # if present  ┘
                      + b"\n" + norm(config/arms.yaml)             # if present  ┐ _BOUND_TREATMENT
                      + b"\n" + norm(prompts/system.txt)           # if present  │ (the manipulated
                      + b"\n" + norm(prompts/initial_generation.txt) # if present┘  variable itself)

i.e. **prose, THEN the freeze-state-stripped prereg yaml, THEN the three bound configs, THEN the three
bound treatment files** (see ``_BOUND_CONFIGS`` + ``_BOUND_TREATMENT``) — each joined by a single ``\n``
(LF) record separator. The bound configs are the EXECUTED knobs the campaign reads (splits/embargo/
lookback/family); the bound treatment is the per-arm feedback spec + the two loaded prompts (the
manipulated variable's text, R62). Binding both stops the frozen DESIGN drifting from the IMPLEMENTED
design (critical-review 2026-06-20; treatment added 2026-06-28). A bound file absent on a minimal root is
skipped, so a two-file (prose + prereg-yaml) root still hashes — this module is the single definition of
that order; nothing else may re-define it.

The prose<->YAML gate (the assertion)
-------------------------------------
Both files are parsed and asserted to agree on the freeze-relevant fields:

  - seed count                         -> ``len(yaml['seeds'])`` vs the prose "5->30 / [0..29]"
  - ``inference.testing_family.m``     -> the union size (6) vs the enumerated member rows; the two
                                          co-primary IUT sub-families (H2-RA m=3, H2-Tail m=3; R25) must
                                          partition it, and every prose "m = <N>" must be a declared size
                                          ({3, 6}) so a stray "m = 9" still fails
  - ``inference.difference_tests``     -> each label has its prose anchor (R11 relabel)
  - ``inference.sesoi``                -> vs the prose "SESOI = 0.05 validation-DSR units"
  - ``inference.equivalence_margin``   -> vs the prose "symmetric TOST ... +/-0.05 DSR"
  - top-level ``cost_sweep.grid_bps``  -> vs the prose "grid_bps = [0, 5, 10, 25, 50]"

Any mismatch raises :class:`FreezeConsistencyError` with a clear message naming the field.

Phase-0 precondition
--------------------
The freeze REFUSES unless ``phase0_smoke_passed_log_id`` is set in the YAML (the smoke
GATE must have gone GREEN/AMBER first — CLAUDE.md keystone). A missing/blank marker raises
:class:`FreezePreconditionError`.

Modes
-----
  --check   Recompute the hash + re-run every assertion WITHOUT writing anything (CI/drift
            guard). Exit code 0 == consistent + Phase-0 met; non-zero on any drift/failure.
  (default) The real freeze (the write path): set ``frozen: true`` + ``freeze_hash`` in the
            YAML, append the hash + UTC + git SHA to ``docs/DECISION_LOG.md`` (the ADR-005
            slot), create a signed git tag ``prereg-v1.0`` (best-effort), and OpenTimestamp
            the hash (best-effort). This path is implemented but MUST be run only by the user.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

# scripts/ is not a package; make ``src`` importable when run as a file.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.utils.provenance import git_commit, sha256_bytes  # noqa: E402

# --------------------------------------------------------------------------- #
# Paths (repo-root relative; resolved robustly)                                #
# --------------------------------------------------------------------------- #
PREREG_MD = "PREREGISTRATION.md"
PREREG_YAML = "config/preregistration.yaml"
#: The EXECUTED load-bearing config the campaign actually reads — bound into the freeze hash so the frozen
#: DESIGN cannot silently drift from the IMPLEMENTED knobs (splits/embargo/lookback/family live HERE, not in
#: the prereg yaml; the hash previously covered only the prereg, so 'nothing frozen can drift' was false at
#: the config layer — critical-review 2026-06-20). Missing files (a minimal test root) are skipped.
_BOUND_CONFIGS: tuple[str, ...] = (
    "config/inference.yaml",   # splits, embargo, testing_family (m=6), multiplicity, sesoi, dsr
    "config/environment.yaml", # lookback, vol windows, action projection/bound, costs, cash_daily_rate
    "config/data.yaml",        # splits, embargo_days
)

#: The DESIGN-DEFINING treatment text — the per-arm feedback spec (``config/arms.yaml``) and the human-
#: authored prompt templates LOADED at run time (``prompts/system.txt`` + ``prompts/initial_generation
#: .txt``). These literally constitute the manipulated variable: distributional-vs-scalar feedback is
#: rendered through them, yet the original canonical hash bound NEITHER — so the treatment could be
#: edited post-freeze without tripping ``--check`` (deep-audit 2026-06-28, amendment R62). Binding their
#: CONTENT closes that gap. ``arms.yaml`` is ALSO roster-checked (``_ARM_ROSTER_CONFIGS``); hashing its
#: bytes here is independent of, and complementary to, that key-level guard. ``prompts/reflection.txt`` is
#: deliberately EXCLUDED: it is dead (no runtime path loads it — the reflection turn is built in-code from
#: ``src/llm/prompts._REFLECTION_PREAMBLE`` + ``src/feedback/schema.build_block``) and is archived (R63).
#: The IN-CODE treatment surface (``schema.build_block``, the preamble) is pinned by the git SHA recorded
#: at the freeze, not by this content hash. A file absent on a minimal test root is skipped.
_BOUND_TREATMENT: tuple[str, ...] = (
    "config/arms.yaml",               # the per-arm feedback spec (the manipulated variable's wiring)
    "prompts/system.txt",             # the reward-design contract shown to every arm
    "prompts/initial_generation.txt", # the generation-0 instruction shown to every arm
)

#: Executed configs whose ``arms`` roster must AGREE with the frozen prereg roster (V1 cross-file guard,
#: 2026-06-26). These are deliberately NOT bound into the canonical hash — operational compute knobs in
#: ``campaign.yaml`` (gpu, budget, resume, ...) must stay amendable post-freeze without a design amendment —
#: but their ARM LIST is asserted equal to the frozen design's ``arms`` so the campaign can never silently
#: run a DIFFERENT roster than the one frozen (the ``placebo_shuffled`` 6-vs-7 drift, DEEP_AUDIT V1/V2).
#: ``arms.yaml`` carries the roster as the KEYS of its ``arms`` mapping; ``campaign.yaml`` as a list. Either
#: file absent on a minimal test root is skipped (the prereg-only fixture still verifies).
_ARM_ROSTER_CONFIGS: tuple[str, ...] = (
    "config/campaign.yaml",    # the executed campaign roster (list under `arms:`)
    "config/arms.yaml",        # the per-arm feedback spec (roster = keys of the `arms:` mapping)
)
DECISION_LOG = "docs/DECISION_LOG.md"

#: The annotated/signed git tag stamped at the freeze.
FREEZE_TAG = "prereg-v1.0"

#: The marker line in ``docs/DECISION_LOG.md`` whose body the freeze fills (ADR-005 slot).
_DECISION_LOG_FREEZE_HEADER = "### FREEZE — pre-registration content hash"


def repo_root() -> Path:
    """Repository root (the directory holding ``config/`` + ``pyproject.toml``)."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "config").is_dir() and (parent / "pyproject.toml").is_file():
            return parent
    raise RuntimeError("could not locate repo root (no parent has both config/ and pyproject.toml)")


# --------------------------------------------------------------------------- #
# Errors                                                                       #
# --------------------------------------------------------------------------- #
class FreezeError(RuntimeError):
    """Base class for any freeze-gate failure."""


class FreezePreconditionError(FreezeError):
    """A precondition for freezing is not met (e.g. Phase-0 not recorded)."""


class FreezeConsistencyError(FreezeError):
    """PREREGISTRATION.md prose and preregistration.yaml disagree on a frozen field."""


# --------------------------------------------------------------------------- #
# Canonical bytes + hash                                                       #
# --------------------------------------------------------------------------- #
def _normalize_bytes(raw: bytes) -> bytes:
    """LF-normalize UTF-8 bytes: strip a leading BOM, rewrite CRLF/CR -> LF.

    Makes the content hash invariant to OS line endings / a BOM-prefixed checkout, so the
    same logical artifact hashes identically on Windows-dev and the Linux campaign box.
    """
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    # Collapse ANY run of CR(s) + an optional trailing LF to a single LF — invariant not only to CRLF/CR
    # but to a doubled `\r\r\n` (a CRLF checkout re-rewritten as CRLF, e.g. the line-ending test). Identical
    # output to the prior replace-chain for real LF/CRLF files (canonical hash UNCHANGED), and idempotent.
    return re.sub(rb"\r+\n?", b"\n", raw)


def _strip_freeze_state(yml_text: str) -> str:
    """Blank out the two MUTABLE freeze-state fields so the canonical hash is invariant to the act of
    freezing. ``_set_yaml_frozen`` flips ``frozen: false->true`` and ``freeze_hash: null-><digest>`` IN the
    hashed file; hashing those raw bytes made ``--check`` report DRIFT forever post-freeze (it recorded the
    PRE-flip digest then re-hashed the POST-flip file). We hash the frozen DESIGN content, not the
    freeze-state bookkeeping, by normalising both lines to a fixed placeholder (critical-review 2026-06-20).
    """
    import re

    out = re.sub(r"(?m)^(frozen:\s*).*$", r"\1<FREEZE_STATE>", yml_text, count=1)
    out = re.sub(r"(?m)^(freeze_hash:\s*).*$", r"\1<FREEZE_STATE>", out, count=1)
    return out


def canonical_bytes(root: Path | None = None) -> bytes:
    """Return the canonical byte string the freeze hashes (FIXED order; see the module docstring).

    Order: ``norm(PREREGISTRATION.md)``, then the freeze-state-stripped prereg yaml (the two MUTABLE
    ``frozen``/``freeze_hash`` fields blanked so the hash is INVARIANT to the freeze act), then each of
    ``_BOUND_CONFIGS`` (inference/environment/data), then each of ``_BOUND_TREATMENT`` (arms.yaml +
    the two loaded prompts) that is present — joined by a single ``\\n`` record separator so each boundary
    is unambiguous and order-sensitive (bound configs added 2026-06-20; bound treatment added 2026-06-28).
    """
    root = root or repo_root()
    md = _normalize_bytes((root / PREREG_MD).read_bytes())
    yml_text = _strip_freeze_state(_normalize_bytes((root / PREREG_YAML).read_bytes()).decode("utf-8"))
    parts: list[bytes] = [md, yml_text.encode("utf-8")]
    # Bind the EXECUTED load-bearing config (skip any absent on a minimal root, so the prereg-only hash
    # is preserved for tests that supply just the two prereg files).
    for rel in _BOUND_CONFIGS:
        p = root / rel
        if p.exists():
            parts.append(_normalize_bytes(p.read_bytes()))
    # Then bind the treatment-defining text (per-arm feedback spec + the two loaded prompts) in a fixed,
    # documented order AFTER the configs, so the frozen DESIGN includes the manipulated variable itself
    # (R62). Absent on a minimal root -> skipped, preserving the prereg-only hash for the freeze tests.
    for rel in _BOUND_TREATMENT:
        p = root / rel
        if p.exists():
            parts.append(_normalize_bytes(p.read_bytes()))
    return b"\n".join(parts)


def canonical_hash(root: Path | None = None) -> str:
    """SHA-256 hex digest of :func:`canonical_bytes` (the frozen design hash).

    Covers up to EIGHT files in fixed order — prose, freeze-state-stripped prereg yaml, the
    three bound configs (inference/environment/data), then the three bound treatment files
    (arms.yaml + prompts/system.txt + prompts/initial_generation.txt), each only if present;
    see the module docstring, ``_BOUND_CONFIGS`` and ``_BOUND_TREATMENT`` (R62, 2026-06-28).
    """
    return sha256_bytes(canonical_bytes(root))


# --------------------------------------------------------------------------- #
# Parsing                                                                      #
# --------------------------------------------------------------------------- #
def load_yaml(root: Path | None = None) -> dict[str, Any]:
    """Parse ``config/preregistration.yaml`` (LF-normalized) into a plain dict."""
    root = root or repo_root()
    text = _normalize_bytes((root / PREREG_YAML).read_bytes()).decode("utf-8")
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise FreezeConsistencyError(f"{PREREG_YAML} did not parse to a mapping")
    return data


def load_prose(root: Path | None = None) -> str:
    """Read ``PREREGISTRATION.md`` (LF-normalized UTF-8 text)."""
    root = root or repo_root()
    return _normalize_bytes((root / PREREG_MD).read_bytes()).decode("utf-8")


def _prose_floats(prose: str, pattern: str) -> list[float]:
    """Every float captured by ``pattern`` (one capturing group) in ``prose``."""
    return [float(m) for m in re.findall(pattern, prose)]


def _prose_grid(prose: str) -> list[int] | None:
    """The cost-sweep bps grid as written in the prose: ``grid_bps = [0, 5, 10, 25, 50]``."""
    m = re.search(r"grid_bps\s*=\s*\[([0-9,\s]+)\]", prose)
    if not m:
        return None
    return [int(x) for x in re.findall(r"\d+", m.group(1))]


# --------------------------------------------------------------------------- #
# The gate: prose <-> yaml consistency on the freeze-relevant fields           #
# --------------------------------------------------------------------------- #
def _require(condition: object, message: str) -> None:
    if not condition:
        raise FreezeConsistencyError(message)


def assert_prose_matches_yaml(yml: dict[str, Any], prose: str) -> list[str]:
    """Assert the PROSE record agrees with the YAML mirror on every frozen field.

    Returns a list of human-readable "checked + agreed" lines (for the report); raises
    :class:`FreezeConsistencyError` naming the first field that disagrees.
    """
    checked: list[str] = []
    inf = yml.get("inference") or {}

    # 1) Seed count -------------------------------------------------------- #
    seeds = yml.get("seeds")
    if not isinstance(seeds, list) or not seeds:
        raise FreezeConsistencyError("yaml 'seeds' must be a non-empty list")
    n_seeds = len(seeds)
    _require(
        seeds == list(range(n_seeds)),
        f"yaml 'seeds' must be the contiguous [0..{n_seeds - 1}] block, got {seeds!r}",
    )
    # Prose binds the headline count via amendment D2 ("5->30", "[0..29]", "headline seed count 30").
    prose_seed_counts = {
        int(x)
        for x in re.findall(r"5\s*(?:->|→)\s*(\d+)", prose)
        + re.findall(r"headline seed count\s+(\d+)", prose)
        + re.findall(r"target\s+\*\*(\d+)\*\*", prose)
    }
    prose_high = max(prose_seed_counts) if prose_seed_counts else None
    _require(
        prose_high == n_seeds,
        f"seed count mismatch: yaml has {n_seeds} seeds ([0..{n_seeds - 1}]) but the prose "
        f"amendment states a headline count of {prose_high}",
    )
    # The "[0..N-1]" literal is also written in the prose; check it agrees.
    prose_ranges = re.findall(r"\[0\.\.(\d+)\]", prose)
    if prose_ranges:
        _require(
            all(int(hi) == n_seeds - 1 for hi in prose_ranges),
            f"seed range mismatch: yaml is [0..{n_seeds - 1}] but prose writes [0..{prose_ranges}]",
        )
    checked.append(f"seeds: yaml [0..{n_seeds - 1}] (n={n_seeds}) == prose 5->{prose_high} / [0..{n_seeds - 1}]")

    # 1b) Arm roster: every frozen arm is named in the prose, and §3's count word matches len(arms).
    # (V1 reconcile 2026-06-26: the frozen roster silently dropped `placebo_shuffled` — the headline
    # structure-vs-content control — while the campaign ran 7 arms; this guard makes that drift fail loud.)
    arms = yml.get("arms")
    if not isinstance(arms, list) or not arms:
        raise FreezeConsistencyError("yaml 'arms' must be a non-empty list")
    n_arms = len(arms)
    missing_arms = [a for a in arms if str(a) not in prose]
    _require(
        not missing_arms,
        f"arm roster mismatch: yaml lists {arms} but the prose never names {missing_arms}",
    )
    _ARM_WORD = {5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine"}
    arm_word = _ARM_WORD.get(n_arms)
    _require(
        arm_word is not None and re.search(rf"##\s*3\.\s*The\s+{arm_word}\s+arms", prose) is not None,
        f"arm count mismatch: yaml has {n_arms} arms but §3 prose does not read 'The {arm_word} arms'",
    )
    checked.append(f"arms: yaml n={n_arms} ({list(arms)}) all named in prose; §3 == 'The {arm_word} arms'")

    # 2) inference.testing_family: the m=6 union + the two co-primary IUT sub-families (R25) ----- #
    fam = inf.get("testing_family") or {}
    m_yaml = fam.get("m")
    members = fam.get("members") or []
    if not isinstance(m_yaml, int):
        raise FreezeConsistencyError("yaml 'inference.testing_family.m' must be an int")
    _require(
        len(members) == m_yaml,
        f"yaml testing_family.m={m_yaml} but {len(members)} members are enumerated",
    )
    # R25: the headline gate is TWO co-primary intersection-union tests (H2-RA on Sharpe, H2-Tail on
    # CVaR-5%). Validate the `families` block: each sub-family's m equals its member count, the two are
    # DISJOINT, and together they partition the m=6 union. `declared_sizes` is the set of family sizes
    # the prose may legitimately reference (each sub-family's m + the union m).
    families = fam.get("families") if isinstance(fam.get("families"), dict) else {}
    declared_sizes = {m_yaml}
    if families:
        def _member_key(mem: dict[str, Any]) -> tuple[str, str, str, object]:
            return (str(mem["arm_a"]), str(mem["arm_b"]), str(mem["metric"]), mem.get("level"))

        union_keys = {_member_key(mem) for mem in members}
        sub_union: set[tuple[str, str, str, object]] = set()
        for sub_name, sub in families.items():
            sub_m = sub.get("m")
            sub_members = sub.get("members") or []
            if not isinstance(sub_m, int):
                raise FreezeConsistencyError(
                    f"yaml 'inference.testing_family.families.{sub_name}.m' must be an int"
                )
            _require(
                len(sub_members) == sub_m,
                f"yaml testing_family.families.{sub_name}.m={sub_m} but {len(sub_members)} members enumerated",
            )
            keys = {_member_key(mem) for mem in sub_members}
            _require(
                sub_union.isdisjoint(keys),
                f"testing_family co-primary sub-families overlap at {sorted(map(str, sub_union & keys))} "
                "(the two IUTs must be DISJOINT; R25)",
            )
            sub_union |= keys
            declared_sizes.add(sub_m)
        _require(
            sub_union == union_keys,
            "testing_family.families do not partition the m=6 union (R25): "
            f"sub-only {sorted(map(str, sub_union - union_keys))}, "
            f"union-only {sorted(map(str, union_keys - sub_union))}",
        )
        _require(
            sum(int(families[s]["m"]) for s in families) == m_yaml,
            f"testing_family sub-family sizes {[families[s]['m'] for s in families]} do not sum to m={m_yaml}",
        )
    prose_m = re.findall(r"\bm\s*=\s*\*{0,2}(\d+)\*{0,2}", prose)
    _require(bool(prose_m), "prose does not state the testing-family size 'm = <N>'")
    # Every prose 'm = <N>' must be one of the DECLARED family sizes (the union 6 + each IUT's 3); a stray
    # 'm = 9' (or any undeclared size) still fails the gate, exactly as the single-m check did.
    _require(
        all(int(v) in declared_sizes for v in prose_m),
        f"testing_family m mismatch: prose states m={set(prose_m)} but the declared family sizes are "
        f"{sorted(declared_sizes)} (union m={m_yaml}; R25 co-primary IUTs)",
    )
    _require(
        m_yaml in {int(v) for v in prose_m},
        f"testing_family union size m={m_yaml} is not stated in the prose (found m={set(prose_m)})",
    )
    checked.append(
        f"inference.testing_family.m: yaml union {m_yaml} (== {len(members)} members) + IUT sub-families "
        f"{sorted(declared_sizes - {m_yaml})} == prose m={sorted(set(int(v) for v in prose_m))}"
    )

    # 3) inference.difference_tests (R11 relabel) -------------------------- #
    diff = inf.get("difference_tests")
    if not isinstance(diff, list) or not diff:
        raise FreezeConsistencyError("yaml 'inference.difference_tests' must be a non-empty list")
    # Each frozen label must have its prose anchor (so a silent relabel in one file is caught).
    diff_anchors = {
        "sharpe_recentred_bootstrap": r"re-?centred basic",
        "cvar_difference": r"CVaR-?difference",
    }
    for label in diff:
        anchor = diff_anchors.get(label)
        if anchor is None:
            # Unknown label: require it to appear verbatim somewhere in the prose.
            _require(
                label.replace("_", " ") in prose or label in prose,
                f"difference_tests label '{label}' has no anchor in the prose record",
            )
        else:
            _require(
                re.search(anchor, prose) is not None,
                f"difference_tests label '{label}' present in yaml but its prose anchor "
                f"/{anchor}/ is absent (a silent relabel?)",
            )
    checked.append(f"inference.difference_tests: {diff} — each label anchored in prose")

    # 4) inference.sesoi --------------------------------------------------- #
    sesoi = inf.get("sesoi")
    if not isinstance(sesoi, (int, float)):
        raise FreezeConsistencyError("yaml 'inference.sesoi' must be numeric")
    prose_sesoi = _prose_floats(prose, r"SESOI\s*=\s*\*{0,2}([0-9]*\.?[0-9]+)")
    _require(bool(prose_sesoi), "prose does not state 'SESOI = <x>'")
    _require(
        all(abs(v - float(sesoi)) < 1e-12 for v in prose_sesoi),
        f"SESOI mismatch: yaml sesoi={sesoi} but prose states SESOI={prose_sesoi}",
    )
    checked.append(f"inference.sesoi: yaml {sesoi} == prose SESOI={prose_sesoi[0]}")

    # 5) inference.equivalence_margin (symmetric TOST +/- margin) ---------- #
    margin = inf.get("equivalence_margin")
    if not isinstance(margin, (int, float)):
        raise FreezeConsistencyError("yaml 'inference.equivalence_margin' must be numeric")
    prose_margin = _prose_floats(prose, r"(?:±|\+/-|\+-)\s*\*{0,2}([0-9]*\.?[0-9]+)\s*DSR")
    _require(bool(prose_margin), "prose does not state the symmetric TOST margin '±<x> DSR'")
    _require(
        all(abs(v - float(margin)) < 1e-12 for v in prose_margin),
        f"equivalence_margin mismatch: yaml equivalence_margin={margin} but prose states "
        f"±{prose_margin} DSR",
    )
    checked.append(f"inference.equivalence_margin: yaml {margin} == prose ±{prose_margin[0]} DSR")

    # 6) cost_sweep.grid_bps (top-level) ----------------------------------- #
    cost_sweep = yml.get("cost_sweep") or {}
    grid_yaml = cost_sweep.get("grid_bps")
    if not isinstance(grid_yaml, list) or not grid_yaml:
        raise FreezeConsistencyError("yaml 'cost_sweep.grid_bps' must be a non-empty list")
    grid_prose = _prose_grid(prose)
    _require(grid_prose is not None, "prose does not state 'grid_bps = [...]'")
    _require(
        [int(x) for x in grid_yaml] == grid_prose,
        f"cost_sweep.grid_bps mismatch: yaml {grid_yaml} vs prose {grid_prose}",
    )
    checked.append(f"cost_sweep.grid_bps: yaml {grid_yaml} == prose {grid_prose}")

    # 7) 2026-06-24 amendments: lambda_cvar (λ=0), agent_numerics.tf32, search.reflect_protocol ---- #
    # The prose for these is verbose, so we assert the YAML carries the frozen VALUES + that the prose
    # NAMES each amendment (robust value-side checks), extending the gate to the three newest frozen items
    # without a fuzzy free-text regex that could false-fail the freeze.
    lam = (yml.get("fitness") or {}).get("lambda_cvar")
    _require(
        isinstance(lam, (int, float)) and abs(float(lam)) < 1e-12,
        f"fitness.lambda_cvar must be 0.0 (the frozen lambda=0 selection, amendment R22); yaml has {lam!r}",
    )
    _require(("lambda" in prose.lower()) or ("λ" in prose), "prose does not name the lambda=0 amendment (R22)")
    checked.append(f"fitness.lambda_cvar: yaml {lam} == prose lambda=0 (R22)")

    tf32 = (yml.get("agent_numerics") or {}).get("tf32")
    _require(tf32 is True, f"agent_numerics.tf32 must be true (frozen uniform precision, R23); yaml has {tf32!r}")
    _require("tf32" in prose.lower(), "prose does not name the TF32 amendment (R23)")
    checked.append(f"agent_numerics.tf32: yaml {tf32} == prose §11 (R23)")

    reflect = (yml.get("search") or {}).get("reflect_protocol_default")
    _require(
        bool(reflect),
        "search.reflect_protocol_default must be set (the headline reflection-protocol record, R21)",
    )
    _require(
        ("reflect-on-best" in prose.lower()) or ("reflect-on-last" in prose.lower()),
        "prose does not name the reflect-protocol amendment (R21)",
    )
    checked.append(f"search.reflect_protocol_default: yaml {reflect!r} present (R21)")

    return checked


def assert_phase0_recorded(yml: dict[str, Any]) -> str:
    """Refuse the freeze unless the Phase-0 pass marker is recorded.

    Returns the marker string; raises :class:`FreezePreconditionError` if absent/blank.
    """
    marker = yml.get("phase0_smoke_passed_log_id")
    if not isinstance(marker, str) or not marker.strip():
        raise FreezePreconditionError(
            "Phase-0 precondition NOT met: config/preregistration.yaml "
            "'phase0_smoke_passed_log_id' is missing/blank. The smoke GATE "
            "(scripts/smoke_test.py) must go GREEN/AMBER and be recorded before freezing."
        )
    return marker


def _config_arm_roster(rel: str, text: str) -> set[str]:
    """The arm roster declared by an executed config (``_ARM_ROSTER_CONFIGS`` member).

    ``arms.yaml`` declares the roster as the KEYS of its ``arms:`` mapping; ``campaign.yaml`` as a
    list under ``arms:``. Raise :class:`FreezeConsistencyError` if neither shape is present.
    """
    data = yaml.safe_load(text)
    arms_field = (data or {}).get("arms") if isinstance(data, dict) else None
    if isinstance(arms_field, dict):
        return {str(k) for k in arms_field}
    if isinstance(arms_field, list) and arms_field:
        return {str(a) for a in arms_field}
    raise FreezeConsistencyError(
        f"{rel} declares no usable 'arms' roster (a non-empty list or mapping); got "
        f"{type(arms_field).__name__}"
    )


def assert_executed_arms_match(yml: dict[str, Any], root: Path) -> str | None:
    """Cross-file V1 guard: every executed config's arm roster must equal the FROZEN prereg roster.

    The frozen design's ``arms`` (``config/preregistration.yaml``, already in the canonical hash and
    cross-checked against the §3 prose by :func:`assert_prose_matches_yaml`) is the source of truth. This
    asserts the EXECUTED configs the campaign actually reads (``_ARM_ROSTER_CONFIGS``) declare exactly that
    roster, so the campaign cannot silently run a different arm set than the one frozen — the ``placebo_
    shuffled`` 6-vs-7 drift the DEEP_AUDIT (V1/V2) flagged. These configs are NOT in the hash (compute knobs
    must stay amendable), so this assertion — not the hash — is what binds their roster.

    Returns a "checked + agreed" line naming the configs verified, or ``None`` when none is present (a
    minimal prereg-only test root). Raises :class:`FreezeConsistencyError` naming the first config that
    disagrees.
    """
    prereg_arms = yml.get("arms")
    if not isinstance(prereg_arms, list) or not prereg_arms:
        raise FreezeConsistencyError("yaml 'arms' must be a non-empty list")
    frozen = {str(a) for a in prereg_arms}
    checked: list[str] = []
    for rel in _ARM_ROSTER_CONFIGS:
        p = root / rel
        if not p.exists():
            continue
        roster = _config_arm_roster(rel, _normalize_bytes(p.read_bytes()).decode("utf-8"))
        _require(
            roster == frozen,
            f"executed arm roster in {rel} {sorted(roster)} != frozen prereg arms {sorted(frozen)} "
            f"(missing {sorted(frozen - roster)}, extra {sorted(roster - frozen)}); the campaign must "
            "run EXACTLY the frozen roster (V1: the placebo_shuffled 6-vs-7 drift)",
        )
        checked.append(rel)
    if not checked:
        return None
    return f"executed arms: {checked} rosters == frozen prereg arms (n={len(frozen)}: {sorted(frozen)})"


# --------------------------------------------------------------------------- #
# Verification (shared by --check and the real freeze)                         #
# --------------------------------------------------------------------------- #
@dataclass
class FreezeStatus:
    """The result of verifying the pre-registration (no side effects)."""

    hash: str
    phase0_marker: str
    checks: list[str]
    already_frozen: bool
    recorded_hash: str | None


def verify(root: Path | None = None) -> FreezeStatus:
    """Run every freeze precondition + the prose<->yaml gate; compute the hash. No writes.

    Raises :class:`FreezePreconditionError` / :class:`FreezeConsistencyError` on any failure.
    """
    root = root or repo_root()
    yml = load_yaml(root)
    prose = load_prose(root)

    phase0_marker = assert_phase0_recorded(yml)
    checks = assert_prose_matches_yaml(yml, prose)
    # V1 cross-file guard: the EXECUTED configs (campaign.yaml/arms.yaml) must declare exactly the frozen
    # roster. Not part of the hash (compute knobs stay amendable); this assertion is what binds their roster.
    arms_check = assert_executed_arms_match(yml, root)
    if arms_check is not None:
        checks.append(arms_check)
    digest = canonical_hash(root)

    return FreezeStatus(
        hash=digest,
        phase0_marker=phase0_marker,
        checks=checks,
        already_frozen=bool(yml.get("frozen")),
        recorded_hash=yml.get("freeze_hash"),
    )


# --------------------------------------------------------------------------- #
# The WRITE path (real freeze only — never run by an agent / by --check)        #
# --------------------------------------------------------------------------- #
def _set_yaml_frozen(root: Path, digest: str) -> None:
    """Flip ``frozen: false -> true`` and ``freeze_hash: null -> <digest>`` IN PLACE.

    A line-level edit (not a YAML round-trip) so every comment, amendment note, and the
    exact byte layout of the mirror are preserved — only the two scalar values change.
    """
    path = root / PREREG_YAML
    text = _normalize_bytes(path.read_bytes()).decode("utf-8")

    new_text, n_frozen = re.subn(
        r"(?m)^(frozen:\s*)false\b", r"\g<1>true", text, count=1
    )
    if n_frozen != 1:
        raise FreezeError(f"could not flip 'frozen: false' in {PREREG_YAML} (already frozen?)")

    new_text, n_hash = re.subn(
        r"(?m)^(freeze_hash:\s*)null\b", rf"\g<1>{digest}", new_text, count=1
    )
    if n_hash != 1:
        raise FreezeError(f"could not set 'freeze_hash: null' in {PREREG_YAML} (already set?)")

    path.write_text(new_text, encoding="utf-8", newline="\n")


def _utc_now_iso() -> str:
    """UTC timestamp, ISO-8601, second precision, 'Z' suffix."""
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _append_decision_log(root: Path, digest: str, when: str, git_sha: str | None) -> None:
    """Record the hash + UTC + git SHA into ``docs/DECISION_LOG.md`` (the ADR-005 slot).

    Fills the existing ``### FREEZE — pre-registration content hash (TO FILL)`` block by
    appending a dated completion entry beneath the ``<!-- amendments appended ... -->``
    marker, so the append-only audit log stays append-only.
    """
    path = root / DECISION_LOG
    text = _normalize_bytes(path.read_bytes()).decode("utf-8")
    sha = git_sha or "(no git SHA)"
    entry = (
        f"\n### FREEZE-DONE — pre-registration content hash recorded ({when[:10]})\n"
        f"**Decision:** PREREGISTRATION.md + config/preregistration.yaml FROZEN.\n"
        f"- **Content hash (SHA-256):** `{digest}`\n"
        f"- **Frozen at (UTC):** {when}\n"
        f"- **Git commit:** `{sha}`\n"
        f"- **Phase-0 precondition:** met (see the PHASE-0 GREEN entry above).\n"
        f"- **Tag:** `{FREEZE_TAG}` (signed; OpenTimestamps proof beside it if `ots` was present).\n"
        f"**Status:** frozen; any post-freeze change requires a dated, user-approved amendment.\n"
    )
    marker = "<!-- amendments appended below this line -->"
    if marker in text:
        text = text.replace(marker, marker + "\n" + entry, 1)
    else:  # pragma: no cover - the marker is present in the live file
        text = text.rstrip() + "\n" + entry
    path.write_text(text, encoding="utf-8", newline="\n")


def _git_tag_signed(root: Path, digest: str, when: str) -> str:
    """Create the freeze tag. Try a SIGNED tag first; fall back to annotated + warn.

    Returns a short status string for the report. Best-effort: never raises.
    """
    message = f"Pre-registration freeze {FREEZE_TAG}\nSHA-256 {digest}\nUTC {when}"
    try:
        subprocess.run(
            ["git", "tag", "-s", FREEZE_TAG, "-m", message],
            cwd=root, capture_output=True, text=True, check=True,
        )
        return f"signed tag {FREEZE_TAG} created"
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        detail = getattr(exc, "stderr", "") or str(exc)
        print(f"[freeze] WARN: signed tag failed ({detail.strip()}); falling back to annotated tag.")
    try:
        subprocess.run(
            ["git", "tag", "-a", FREEZE_TAG, "-m", message],
            cwd=root, capture_output=True, text=True, check=True,
        )
        return f"annotated tag {FREEZE_TAG} created (UNSIGNED — `-s` unavailable)"
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:  # pragma: no cover
        detail = getattr(exc, "stderr", "") or str(exc)
        print(f"[freeze] WARN: annotated tag also failed ({detail.strip()}); skipping tag.")
        return "tag SKIPPED (git tag failed)"


def _ots_stamp(root: Path, digest: str) -> str:
    """OpenTimestamp the hash (best-effort). Skip + warn if `ots` is absent. Never raises."""
    proof = root / "docs" / f"{FREEZE_TAG}.sha256"
    try:
        proof.write_text(f"{digest}  PREREGISTRATION+yaml ({FREEZE_TAG})\n", encoding="utf-8", newline="\n")
        subprocess.run(
            ["ots", "stamp", str(proof)],
            cwd=root, capture_output=True, text=True, check=True,
        )
        return f"ots stamped {proof.name} (.ots proof beside it)"
    except FileNotFoundError:
        print("[freeze] WARN: `ots` (opentimestamps-client) not found — skipping the timestamp proof.")
        return "ots SKIPPED (client absent)"
    except subprocess.CalledProcessError as exc:  # pragma: no cover
        print(f"[freeze] WARN: `ots stamp` failed ({(exc.stderr or '').strip()}); skipping.")
        return "ots SKIPPED (stamp failed)"


def do_freeze(root: Path | None = None) -> FreezeStatus:
    """The REAL freeze (the write path). Verifies, then writes the hash, log, tag, ots.

    NB: this MUTATES the repo (YAML + DECISION_LOG + a git tag). It must be run ONLY by the
    user at the Phase-1 freeze, never by an agent or in CI. ``--check`` never calls this.
    """
    root = root or repo_root()
    status = verify(root)
    if status.already_frozen:
        raise FreezeError(
            f"{PREREG_YAML} is already frozen (frozen: true, freeze_hash={status.recorded_hash}). "
            "Re-freezing is forbidden; post-freeze changes go through a dated amendment."
        )

    when = _utc_now_iso()
    git_sha = git_commit()

    # Order: stamp the design into the YAML, then record it, then tag, then timestamp.
    _set_yaml_frozen(root, status.hash)
    # Recompute the hash AFTER flipping frozen/freeze_hash would change it — so the RECORDED
    # hash is the PRE-flip canonical hash (the design content), which is what `verify` returns
    # and what `--check` re-derives. The two scalar-state flips are deliberately NOT part of
    # the hashed design (see ADR-005 freeze-record note).
    _append_decision_log(root, status.hash, when, git_sha)
    tag_status = _git_tag_signed(root, status.hash, when)
    ots_status = _ots_stamp(root, status.hash)

    print(f"[freeze] FROZEN. SHA-256 {status.hash}")
    print(f"[freeze]   UTC {when}  git {git_sha or '(none)'}")
    print(f"[freeze]   {tag_status}")
    print(f"[freeze]   {ots_status}")
    return status


# --------------------------------------------------------------------------- #
# CLI                                                                          #
# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Freeze / verify the pre-registration (FINAL_PLAN Phase 1.E; Rank 9).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify prose<->yaml + Phase-0 + recompute the hash; NO writes. Non-zero exit on drift.",
    )
    return parser


def _print_check(status: FreezeStatus) -> None:
    print("[freeze] --check — verifying the pre-registration (no writes):")
    print(f"  Phase-0 precondition MET: {status.phase0_marker}")
    print("  prose<->yaml consistency:")
    for line in status.checks:
        print(f"    OK  {line}")
    print(f"  canonical SHA-256: {status.hash}")
    if status.recorded_hash:
        match = "MATCHES" if status.recorded_hash == status.hash else "DRIFT!"
        print(f"  recorded freeze_hash: {status.recorded_hash}  [{match}]")
    else:
        print("  recorded freeze_hash: null (not yet frozen — expected pre-freeze)")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = repo_root()

    if args.check:
        try:
            status = verify(root)
        except FreezeError as exc:
            print(f"[freeze] --check FAILED: {exc}", file=sys.stderr)
            return 1
        _print_check(status)
        # On a frozen repo, --check is also a DRIFT guard: the recorded hash must match.
        if status.recorded_hash and status.recorded_hash != status.hash:
            print(
                f"[freeze] --check FAILED: recorded freeze_hash {status.recorded_hash} != "
                f"current {status.hash} (the frozen artifacts changed).",
                file=sys.stderr,
            )
            return 1
        return 0

    # Default == the REAL freeze (write path). Implemented; gated to the user.
    status = do_freeze(root)
    return 0 if status else 1


if __name__ == "__main__":
    raise SystemExit(main())
