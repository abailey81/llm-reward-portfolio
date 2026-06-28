"""Load the frozen REAL gold panel (Refinitiv) into the engine's :class:`Panel`.

The gold panel in ``data/gold/`` is the survivorship-free, point-in-time research data built by
``data_pipeline/`` (ADR-019…022): ``returns_panel_univ3.parquet`` (5,283 sessions × 953 RICs,
2005–2025), ``cash_features_univ3.parquet`` (``vol20``, ``vol20_over_vol60``, ``vix`` = FRED VIXCLS —
CBOE ``.VIX`` is not licensed), and ``top30_selection_univ3.parquet`` (the point-in-time top-30 RICs at
each window start). This module slices a single window's top-30 into a finite, **anonymised** ``Panel``
the environment can train on.

Two invariants are enforced here so the contamination defence (N3, FINAL_PLAN B.8) and the env's
finiteness contract hold:

1. **Anonymisation.** The ``Panel`` carries only integer ``asset_ids`` (``0..N-1``) — **no RICs, no
   tickers, no dates ever reach a reward**. The RIC↔id mapping is returned *separately* (opt-in) for
   provenance/analysis only and must never be passed into a reward or the LLM.

2. **Finiteness via an explicit delisting policy.** A survivorship-free top-30 contains names that die
   mid-window (e.g. Wachovia ``WB.N^A09`` delists 2009; Dell ``DELL.OQ^J13`` goes private 2013), so the
   raw slice has NaNs after delisting. The env *rejects* non-finite rows (``environment_spec_v1``), so a
   policy is required. The default, ``on_missing="liquidate_to_cash"``, sets post-event / missing returns
   to ``0.0`` (proceeds held flat ≈ cash) — the standard survivorship-correct treatment that preserves
   the dead names rather than dropping them (dropping would silently re-introduce survivorship bias).

   ⚠ **PROVISIONAL — needs preregistration sign-off (see DECISIONS.md ADR-024).** The intra-window
   delisting mechanic is a frozen-design decision the env does not yet model explicitly; ``liquidate_to_cash``
   is a defensible default for the prototype, not a ratified choice for the headline result.
"""
from __future__ import annotations

import ast
import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Any, Literal

import numpy as np
import pandas as pd

from .panel import Panel

__all__ = ["load_gold_panel", "GoldLoadResult", "embargoed_val_start", "gold_suffix"]

_LOG = logging.getLogger(__name__)

# Repo-root-relative default location of the frozen gold artifacts.
_GOLD_DIR = Path(__file__).resolve().parents[2] / "data" / "gold"

# Gold-panel suffix selector. ``univ3`` is the LIVE default **and the FROZEN headline panel**
# (R44, 2026-06-26; ADR-021 canonical research panel; ``_univ``/``_univ2`` are superseded). The
# headline campaign runs on this default with **NO** ``LLM_RP_GOLD_SUFFIX`` override — leaving the
# env var unset keeps every loader (headline, dev, suite) on ``univ3``. The selector is still
# SWITCHABLE for the sensitivity band only: setting ``LLM_RP_GOLD_SUFFIX=univ4`` points a loader at
# the Shumway-STYLE delisting panel (BUILT: data_pipeline build_universe(suffix="_univ4",
# apply_delisting=True); R33), and a switch to a missing suffix fails loudly in ``_read``.
#   ⚠ univ4 is the M&A-CONTAMINATED HEAVY END of the delisting-return sensitivity band, **NOT the
#   headline** (R39/R44 reverse R33's earlier univ4-headline choice; data-integrity audit
#   2026-06-25): the frozen vault carries no delisting reason/terminal, so the −30/−55% surcharge
#   hits 100% of delistings incl. premium M&A (DELL/TWX/ABMD...) — training a tail-risk study on
#   fabricated tail losses is indefensible. The honest tail is the band d∈{0,−30,−55,−100%}
#   (analyze_campaign.delisting_band) with univ3 (zero-fill / ``liquidate_to_cash``, no fabrication)
#   at the too-light 0% end and univ4 the −30/−55 heavy end; the full sweep moves pooled test
#   CVaR-5% only ~2%, so the H2 ordering is invariant across the band. The correct-on-re-pull ideal
#   is the reason-gated ``univ4r`` (docs/DATA_REPULL_DELISTING.md). Screened research panel (integrity
#   flags wired into build_universe): ``univ3s`` (returns byte-identical to univ3; flag-report sidecar).
_DEFAULT_SUFFIX = "univ3"


def gold_suffix() -> str:
    """The active gold suffix: ``$LLM_RP_GOLD_SUFFIX`` if set (stripped of a leading
    ``_``), else ``univ3``. Read at call time so a sensitivity-band sweep can switch panels via the
    environment without a code edit — the live default ``univ3`` is **the frozen headline panel**
    (R44), so the headline campaign runs with **NO** ``LLM_RP_GOLD_SUFFIX`` set. The override exists
    only for the band: ``LLM_RP_GOLD_SUFFIX=univ4`` selects the M&A-contaminated heavy END of the
    delisting band (R39/R44 supersede R33's earlier univ4-headline choice — see the suffix selector
    note above and ``analyze_campaign.delisting_band``)."""
    override = os.environ.get("LLM_RP_GOLD_SUFFIX", "").strip().lstrip("_")
    return override or _DEFAULT_SUFFIX


_SUFFIX = gold_suffix()  # module-level snapshot for back-compat; prefer gold_suffix() live
# The freeze manifest (config/data.yaml: freeze.checksum == sha256). One JSON object per line,
# carrying a repo-root-relative ``relpath`` and its frozen ``sha256`` (ADR-014; data_pipeline/vault).
_MANIFEST = Path(__file__).resolve().parents[2] / "data" / "manifest" / "manifest.jsonl"
_HASH_CHUNK = 1 << 20  # 1 MiB read blocks for streaming the SHA-256

# Split ends (inclusive) from the frozen preregistration §data_splits. Used only to bound a window when
# an explicit ``end`` is not given; kept here as a documented default, not a source of truth.
_DEV_END = "2014-12-31"  # train split end (val begins 2015)

# The materialized split table (``data/gold/splits_univ3.parquet``) carries a single ``splits_json``
# cell whose ``development.validation_post_embargo`` boundary records the 21-session EMBARGO floor
# (val begins 2015-02-03 = train_end + 21 trading days). R18 NOTE: the EXECUTED val start is
# ``max(boundary, train_end + max(embargo, lookback))``; with the production lookback=60 the lookback
# purge dominates, so execution begins ~2015-03-31 (boundary + 39) — the parquet records the embargo,
# not the executed start. ``embargo_trading_days`` (=21) is exposed alongside as the fallback knob.
_SPLITS_NAME = "splits"  # -> splits_univ3.parquet via the _SUFFIX convention

OnMissing = Literal["liquidate_to_cash", "ffill_then_zero", "error"]


class GoldLoadResult:
    """A loaded panel plus its (non-reward) provenance mapping.

    ``panel`` is the anonymised, finite :class:`Panel` for the environment. ``ric_by_id`` maps each
    integer ``asset_id`` back to its Refinitiv RIC — **for provenance/analysis only**; it must never be
    handed to a reward function or the LLM (contamination defence).
    """

    def __init__(self, panel: Panel, ric_by_id: dict[int, str], window: str) -> None:
        self.panel = panel
        self.ric_by_id = ric_by_id
        self.window = window


def _file_sha256(path: Path) -> str:
    """Stream ``path`` and return its lowercase hex SHA-256 (memory-safe for large parquet)."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(_HASH_CHUNK), b""):
            h.update(block)
    return h.hexdigest()


def _expected_sha256(path: Path, manifest_path: Path = _MANIFEST) -> str | None:
    """Return the frozen SHA-256 for ``path`` from the freeze manifest, or ``None`` if unknown.

    The manifest (``data/manifest/manifest.jsonl``) keys artifacts by a repo-root-relative POSIX
    ``relpath``; we match on that, falling back to a basename match so a relocated ``gold_dir`` still
    resolves. Returns ``None`` (rather than raising) when no manifest or no matching entry exists, so
    verification can SKIP gracefully on installs that ship without the manifest.
    """
    if not manifest_path.is_file():
        return None
    target_name = path.name
    target_rel = None
    try:
        # Repo-root-relative POSIX path (manifest convention), e.g. "data/gold/returns_panel_univ3.parquet".
        # The manifest lives at <repo>/data/manifest/manifest.jsonl, so the repo root is parents[2]
        # (parents[0]=data/manifest, parents[1]=data, parents[2]=<repo>) — parents[1] yielded a
        # data/-relative path ("gold/…") that never matched the data/-prefixed relpaths, so only the
        # basename fallback fired (Rank 18 fix).
        target_rel = path.resolve().relative_to(manifest_path.resolve().parents[2]).as_posix()
    except ValueError:  # gold_dir lives outside the repo root — fall back to basename matching.
        target_rel = None
    by_name: str | None = None
    with manifest_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:  # pragma: no cover - tolerate a stray manifest line
                continue
            sha = entry.get("sha256")
            if not sha:
                continue
            relpath = entry.get("relpath", "")
            if target_rel is not None and relpath == target_rel:
                return sha  # exact relpath match wins
            if Path(relpath).name == target_name or entry.get("name") == target_name:
                by_name = sha
    return by_name


def _verify_checksum(path: Path) -> None:
    """Verify ``path`` against its frozen manifest SHA-256 (opt-in; ``freeze.checksum: sha256``).

    Raises :class:`ValueError` on mismatch (tamper / wrong build). If no expected checksum is
    configured for the file (no manifest, or the file is absent from it), logs at INFO and returns —
    so callers/tests without the manifest are never broken (graceful skip).
    """
    expected = _expected_sha256(path, _MANIFEST)
    if expected is None:
        _LOG.info("checksum verification skipped for %s (no manifest entry / no manifest)", path.name)
        return
    actual = _file_sha256(path)
    if actual != expected:
        raise ValueError(
            f"gold artifact checksum mismatch for {path.name}: "
            f"expected {expected[:12]}…, got {actual[:12]}… — the frozen file has changed "
            f"(tamper or wrong build). Re-pull via data_pipeline/ or restore the frozen artifact."
        )
    _LOG.debug("checksum OK for %s (%s…)", path.name, expected[:12])


def _read(name: str, gold_dir: Path, *, verify_checksum: bool = False) -> pd.DataFrame:
    path = gold_dir / f"{name}_{gold_suffix()}.parquet"
    if not path.exists():
        raise FileNotFoundError(
            f"gold artifact not found: {path}. Build it via data_pipeline/ (needs Refinitiv creds) "
            f"or check data/gold/. (Active suffix {gold_suffix()!r} — set LLM_RP_GOLD_SUFFIX to switch.)"
        )
    if verify_checksum:
        _verify_checksum(path)
    return pd.read_parquet(path)


def _window_rics(
    top30: pd.DataFrame, phase: str, window_start: str | pd.Timestamp | None = None
) -> tuple[list[str], pd.Timestamp]:
    rows = top30[top30["phase"] == phase]
    if rows.empty:
        raise KeyError(f"phase {phase!r} not in top30_selection (have {sorted(top30['phase'].unique())})")
    if window_start is not None:
        # Disambiguate a multi-window phase (walk_forward has many rows) by point-in-time start, so a
        # PIT-universe robustness re-evaluation can pick e.g. the 2018-01-02 top-30 (#13). Without it the
        # first row is used (back-compatible).
        ws = pd.Timestamp(window_start)
        match = rows[pd.to_datetime(rows["window_start"]) == ws]
        if match.empty:
            avail = sorted(str(pd.Timestamp(x))[:10] for x in rows["window_start"])
            raise KeyError(f"phase {phase!r} window_start {ws.date()} not found (have {avail})")
        row = match.iloc[0]
    else:
        row = rows.iloc[0]
    sel = row["selection"]
    if not isinstance(sel, (list, tuple, np.ndarray)):
        sel = ast.literal_eval(sel)
    return list(sel), pd.Timestamp(row["window_start"])


def _seed_leading_vix(vix_s: pd.Series, cash: pd.DataFrame, start: Any) -> pd.Series:
    """Fill a window's VIX gaps WITHOUT leaking the future (data-1 fix 2026-06-20).

    ``ffill`` carries the last PAST close into interior/trailing gaps (leakage-free). A LEADING NaN cannot
    be ffill'd, so a bare ``.bfill()`` would pull it BACKWARD from a LATER session — a future leak at the
    agent's first decision-day obs (the window is vix_prelagged, so row ``t`` holds the ``t-1`` close).
    Instead seed a leading gap from PAST data only: the last valid VIX STRICTLY BEFORE ``start`` in the
    FULL ``cash`` frame (so a walk-forward window's ``start`` seeds from its genuine ``t-1`` close, e.g.
    2018-01-02, not from ``t+1``). ``bfill`` is the last resort ONLY when no prior observation exists
    anywhere — i.e. ``start`` is the global-first session (the dev window's 2005-01-03, where ``cash``
    itself begins); that lone boundary cell is genuinely unknowable, not a silent leak. Extracted from
    ``load_gold_panel`` so this leakage-critical rule is unit-tested directly (tests/test_loaders.py).
    """
    vix_s = vix_s.ffill()
    if pd.isna(vix_s.iloc[0]):
        prior_vix = cash.loc[cash.index < start, "vix"].ffill()
        seed = prior_vix.iloc[-1] if len(prior_vix) and not pd.isna(prior_vix.iloc[-1]) else np.nan
        vix_s = vix_s.fillna(seed) if not pd.isna(seed) else vix_s.bfill()
    return vix_s


def load_gold_panel(
    phase: str = "development",
    *,
    end: str | pd.Timestamp | None = None,
    window_start: str | pd.Timestamp | None = None,
    gold_dir: Path | str = _GOLD_DIR,
    on_missing: OnMissing = "liquidate_to_cash",
    verify_checksum: bool = False,
    validate: bool = False,
) -> GoldLoadResult:
    """Load one window's point-in-time top-30 into a finite, anonymised :class:`Panel`.

    Parameters
    ----------
    phase
        A window label in ``top30_selection_univ3`` (``"development"`` or a ``"walk_forward"`` start).
        For ``"walk_forward"`` there are several rows; pass an explicit ``end`` to disambiguate the span.
    end
        Inclusive last session. Defaults to the train-split end (``2014-12-31``) for ``"development"``;
        for walk-forward windows an explicit ``end`` is required (no silent guess).
    on_missing
        Delisting / missing-return policy (see module docstring). ``"liquidate_to_cash"`` (default) →
        fill NaN with ``0.0``; ``"ffill_then_zero"`` → forward-fill INTERIOR gaps only, then zero BOTH the
        leading gaps AND the post-last-valid DEAD TAIL (so a delisted name never repeats its final daily
        return — final-audit #20); ``"error"`` → raise if any NaN remains (continuously-alive universe only).
    verify_checksum
        Opt-in freeze check (``config/data.yaml: freeze.checksum: sha256``). When ``True``, each gold
        parquet's SHA-256 is verified against the frozen value in ``data/manifest/manifest.jsonl`` before
        it is read; a mismatch raises :class:`ValueError`. If no manifest entry exists for a file (e.g. a
        synthetic-only install) the check is SKIPPED with an INFO log, so existing callers are unaffected.
        Defaults to ``False`` to preserve the prior load behaviour.
    validate
        Opt-in data-contract (``src.data.validation.validate_panel``): assert the semantic + leakage
        invariants of the built panel (strictly-increasing dates, returns ``>= -1.0`` and not implausibly
        large, non-negative finite VIX, unique integer ``asset_ids``, non-negative market caps, no all-zero
        column) and raise :class:`~src.data.validation.PanelContractError` on violation. Defaults to ``False``.
    """
    gold_dir = Path(gold_dir)
    returns = _read("returns_panel", gold_dir, verify_checksum=verify_checksum)
    cash = _read("cash_features", gold_dir, verify_checksum=verify_checksum)
    top30 = _read("top30_selection", gold_dir, verify_checksum=verify_checksum)

    rics, start = _window_rics(top30, phase, window_start)
    if end is None:
        if phase == "development":
            end = pd.Timestamp(_DEV_END)
        else:
            raise ValueError(f"phase {phase!r} needs an explicit `end` (walk-forward span is ambiguous).")
    end = pd.Timestamp(end)

    missing_rics = [r for r in rics if r not in returns.columns]
    if missing_rics:
        raise KeyError(f"top-30 RICs absent from returns panel: {missing_rics}")

    sub = returns.loc[start:end, rics].copy()
    vix_s = cash.loc[start:end, "vix"].copy()
    if sub.empty:
        raise ValueError(f"empty window {start}..{end} for phase {phase!r}")

    # --- finiteness via the delisting policy ---
    if on_missing == "liquidate_to_cash":
        sub = sub.fillna(0.0)
    elif on_missing == "ffill_then_zero":
        # Forward-fill INTERIOR gaps only, then zero the DEAD TAIL: never propagate a return past a
        # name's last valid observation (final-audit #20 — a bare .ffill() repeated the final daily
        # return on every post-delisting session, fabricating compounding wealth on a dead name). The
        # post-last-valid tail and any leading gap become 0.0, identical to liquidate_to_cash there.
        last_valid = {col: sub[col].last_valid_index() for col in sub.columns}
        sub = sub.ffill()
        for col, lv in last_valid.items():
            if lv is not None:
                sub.loc[sub.index > lv, col] = 0.0
        sub = sub.fillna(0.0)
    elif on_missing == "error":
        if sub.isna().any().any():
            bad = sub.columns[sub.isna().any()].tolist()
            raise ValueError(f"NaNs present under on_missing='error' (names: {bad[:5]}…)")
    else:  # pragma: no cover - guarded by Literal
        raise ValueError(f"unknown on_missing={on_missing!r}")
    # VIX must be knowable at every obs; fill gaps leakage-free (ffill past closes; a leading gap is seeded
    # from the genuine pre-``start`` session, never bfill'd from a future in-window session). The rule is
    # extracted to _seed_leading_vix so the leakage-critical leading-gap branch is unit-tested in isolation.
    vix_s = _seed_leading_vix(vix_s, cash, start)

    returns_arr = sub.to_numpy(dtype=float)
    vix_arr = vix_s.to_numpy(dtype=float)
    # Normalize VIX to conventional POINTS (~9..83). The gold cash_features currently store VIX as a
    # FRACTION (FRED VIXCLS / 100 — e.g. 0.0914..0.8269 over 2005-2025); a future rebuild may store
    # points. Detect by magnitude (a real VIX is never < ~5 points; a fraction is never > ~2) and
    # rescale the fractional convention up by 100 so the WHOLE system speaks one unit: the regime
    # thresholds (config/regimes.yaml calm<15 / stress>25), the synthetic panel (~10-50), and the
    # trainer's documented obs range (~10-80). Without this the VIX-threshold rule labelled EVERY gold
    # date calm (all vix < 15) and the independent-regime count COLLAPSED to 1 — the vix-units bug
    # (2026-06-19). The env obs is scale-agnostic (VecNormalize, ADR), so this only corrects regime
    # stratification; the frozen parquet is untouched (transform on read; magnitude-guarded so a points
    # gold is never double-scaled). NB (final-audit #19): POINTS is the canonical LIVE unit — the env
    # obs, the regime thresholds, and the synthetic panel all speak points; the pipeline's /vix_scale
    # FRACTION is its internal storage convention, deliberately reconciled here on read (NOT a silent
    # revert). The env feeds BOTH the obs (scale-agnostic under VecNormalize) and regime labelling from
    # this one array, so a single canonical unit is the correct design, not a conflation.
    # Detect the unit (fraction vs points) from the FIRST ~2 years only — always inside TRAIN (2005-2014).
    # The unit is a GLOBAL data-format property of the frozen parquet, so the head detects it identically
    # to a panel-wide median while never reading the sealed test span (leakage audit 2026-06-20, #11).
    if vix_arr.size:
        head = vix_arr[: min(vix_arr.size, 504)]
        if float(np.nanmedian(head)) < 2.0:
            vix_arr = vix_arr * 100.0
    dates_arr = sub.index.to_numpy()  # datetime64[ns]; never enters a reward
    n_assets = returns_arr.shape[1]
    asset_ids = np.arange(n_assets, dtype=int)  # ANONYMISED — no RICs in the Panel

    if not np.isfinite(returns_arr).all():
        raise ValueError("returns still non-finite after the missing-data policy — investigate the slice")
    if not np.isfinite(vix_arr).all():
        raise ValueError("vix non-finite after fill — check cash_features.vix over the window")

    # vix_prelagged=True: the gold cash_features.vix is ALREADY shift(1)-lagged at build time
    # (data_pipeline/src/features.py: row t holds the t-1 close), so the env must NOT lag it again
    # (final-audit #7). The synthetic panel leaves this False (contemporaneous) and the env lags it.
    panel = Panel(
        returns=returns_arr, vix=vix_arr, dates=dates_arr, asset_ids=asset_ids, vix_prelagged=True
    )
    if validate:
        # Opt-in data-contract (src/data/validation.py): assert the semantic + leakage invariants
        # (strictly-increasing dates, sane returns, non-negative vix, unique integer asset_ids, ...).
        # Default off to preserve prior load behaviour; raises PanelContractError on violation.
        from .validation import validate_panel

        validate_panel(panel, strict=True)
    ric_by_id = {i: ric for i, ric in enumerate(rics)}  # provenance ONLY — never to a reward/LLM
    return GoldLoadResult(panel=panel, ric_by_id=ric_by_id, window=phase)


def _materialized_val_post_embargo(
    phase: str, gold_dir: Path
) -> tuple[pd.Timestamp | None, int | None]:
    """Return ``(validation_post_embargo_start, embargo_trading_days)`` from the frozen split table.

    Reads ``data/gold/splits_<suffix>.parquet`` (one ``splits_json`` cell) and pulls the
    materialized post-embargo validation boundary for ``phase`` (only ``"development"`` carries one).
    Returns ``(None, embargo)`` when the boundary is absent and ``(None, None)`` when the table or
    its embargo field cannot be read — so callers fall back gracefully (Rank 18).
    """
    path = gold_dir / f"{_SPLITS_NAME}_{gold_suffix()}.parquet"
    if not path.exists():
        return None, None
    try:
        cell = pd.read_parquet(path)["splits_json"].iloc[0]
        splits = json.loads(cell) if isinstance(cell, str) else dict(cell)
    except (KeyError, IndexError, ValueError, TypeError):  # pragma: no cover - corrupt/odd table
        return None, None
    embargo = splits.get("embargo_trading_days")
    embargo_i = int(embargo) if isinstance(embargo, (int, float)) else None
    block = splits.get(phase)
    if isinstance(block, dict):
        vpe = block.get("validation_post_embargo")
        if isinstance(vpe, (list, tuple)) and vpe:
            try:
                return pd.Timestamp(vpe[0]), embargo_i
            except (ValueError, TypeError):  # pragma: no cover - malformed date
                return None, embargo_i
    return None, embargo_i


def embargoed_val_start(
    dates: np.ndarray,
    train_end: str | pd.Timestamp,
    *,
    phase: str = "development",
    embargo_days: int = 21,
    lookback: int = 0,
    gold_dir: Path | str = _GOLD_DIR,
) -> int:
    """Index into ``dates`` of the FIRST validation session that respects the purge (R18).

    Resolves ``val_start = max(materialized_boundary, train_end + 1 + max(embargo_days, lookback))``:

    1. **Materialized embargo boundary (a FLOOR).** ``development.validation_post_embargo[0]`` from
       ``data/gold/splits_<suffix>.parquet`` (= ``2015-02-03`` = train_end + 21 sessions for the dev
       split) is read as the embargo floor. **R18 NOTE:** with a feature ``lookback`` (production = 60),
       the lookback purge ``train_end + 1 + max(embargo, lookback)`` DOMINATES this +21 boundary, so the
       EXECUTED val starts ~2015-03-31 (boundary + 39), NOT 2015-02-03 — the materialized parquet records
       only the 21-session EMBARGO, while execution applies the larger feature-lookback purge. (With
       ``lookback=0`` the boundary is honoured exactly, e.g. in the legacy embargo-only unit tests.)
    2. **Fallback (no split table).** Purge ``max(embargo_days, lookback)`` TRADING sessions after
       ``train_end`` — used on a synthetic-only install. ``lookback=0`` reduces this to the embargo.

    Parameters
    ----------
    dates:
        The panel's session index (``datetime64[ns]``), ascending.
    train_end:
        Inclusive last TRAIN session (the boundary the embargo is measured from).
    phase, embargo_days, gold_dir:
        The split phase to read, the fallback embargo in trading days, and the gold dir.

    Returns
    -------
    int
        The val-start index. Always ``> searchsorted(dates, train_end)`` (a non-empty embargo gap),
        clamped to ``len(dates)``.
    """
    d = np.asarray(dates)
    train_idx = int(np.searchsorted(d, np.datetime64(pd.Timestamp(train_end))))  # last-train position
    abut = train_idx + 1  # the OLD (no-embargo) val start, kept as the floor

    boundary, materialized_embargo = _materialized_val_post_embargo(phase, Path(gold_dir))
    # The purge must cover the FEATURE LOOKBACK, not merely the embargo: every observation reads
    # returns[t-lookback:t], so a gap of only ``embargo``(21) < ``lookback``(60) leaves the val
    # window's first (lookback - embargo) observations reading TRAIN returns — a López de Prado
    # purge-insufficiency (leakage audit 2026-06-20, PREREGISTRATION R18). The effective purge is
    # max(embargo, lookback). ``lookback=0`` (the default) preserves the legacy embargo-only behaviour.
    emb_resolved = int(materialized_embargo) if materialized_embargo is not None else int(embargo_days)
    purge = max(emb_resolved, int(lookback))
    lookback_floor = abut + purge  # drop ``purge`` post-train sessions so no val feature reaches train

    if boundary is not None:
        idx = int(np.searchsorted(d, np.datetime64(boundary)))
        # Honour the materialized boundary only if it sits AFTER the abutting start (a real embargo),
        # but never let it under-purge the lookback.
        if idx > abut:
            return min(max(idx, lookback_floor), len(d))

    return min(max(abut + 1, lookback_floor), len(d))
