"""Live dashboard for a (possibly backgrounded / remote-headless) prototype/campaign run.

Reads ``<run_dir>/progress.json`` (the atomically-rewritten state from :class:`src.utils.monitoring.RunMonitor`)
and tails ``events.jsonl`` / ``anomalies.jsonl`` to render a precise, real-time picture: multi-level progress
(arms ▸ candidates ▸ training steps), the latest training metrics, GPU/CPU/RAM telemetry, ETA, an error
tracker (anomalies grouped by category), live LLM token-spend + estimated cost, a **silent-hang detector**
(loud STALE banner when ``progress.json`` stops being rewritten while the run is still "running"), and any
anomalies — so anything even slightly off is visible at a glance, **without attaching to the training
process**. This watcher is strictly READ-ONLY: it parses on-disk artefacts and never touches the run, so a
crash here can never affect the frozen campaign or its byte-identical replay.

Usage::

    python scripts/monitor.py outputs/prototype                       # live dashboard (~2 Hz refresh)
    python scripts/monitor.py outputs/prototype --once                # one plain-text snapshot (scriptable)
    python scripts/monitor.py outputs/prototype --interval 1
    python scripts/monitor.py outputs/prototype --stale-secs 600      # tune the silent-hang threshold
    # Remote, unattended (rented GPU over SSH): push a phone alert on done/error/stall. OFF by default;
    # stdlib urllib only (no new dep); a pure observation side-channel — sends run STATUS, never data.
    python scripts/monitor.py outputs/campaign --notify https://ntfy.sh/<your-private-topic>
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any

# Default silence threshold: ``RunMonitor._flush`` rewrites progress.json on every candidate AND every idle
# pump tick (~0.3 s in the parallel path), so no update for minutes means the run has genuinely hung
# (deadlocked worker, wedged CUDA call, OOM-killed driver) rather than merely being between candidates.
_DEFAULT_STALE_SECS = 300.0

# LLM list price per 1M tokens (Anthropic, Jan 2026) — matched by substring against the logged model id, so
# the dashboard shows a running USD estimate for the reward-authoring spend. Report-only; over-estimates
# slightly because it ignores prompt-cache reads (which bill ~0.1x). Update if Anthropic re-prices.
_PRICES_PER_MTOK: dict[str, tuple[float, float]] = {
    "fable-5": (10.0, 50.0),
    "opus-4-8": (5.0, 25.0),
    "opus-4-7": (5.0, 25.0),
    "opus-4-6": (5.0, 25.0),
    "sonnet-4-6": (3.0, 15.0),
    "haiku-4-5": (1.0, 5.0),
}

# Rotating-circle spinner frames (user-requested "circles") — advanced through on each refresh tick.
_SPINNER = "◐◓◑◒"

# ---- small read-only cache: re-parse a JSONL only when its (mtime,size) changes ------------------------- #
_CACHE: dict[str, tuple[tuple[float, int], list[dict[str, Any]]]] = {}


def read_state(run_dir: Path) -> dict[str, Any] | None:
    p = run_dir / "progress.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None  # mid-write race; the next tick re-reads the atomic replacement


def _read_jsonl_cached(path: Path) -> list[dict[str, Any]]:
    """Parse a JSONL file, caching by (mtime, size) so the ~2 Hz refresh doesn't re-read an unchanged file."""
    if not path.exists():
        return []
    try:
        stt = path.stat()
        key = (stt.st_mtime, stt.st_size)
    except Exception:
        return []
    hit = _CACHE.get(str(path))
    if hit is not None and hit[0] == key:
        return hit[1]
    out: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        try:
            out.append(json.loads(line))
        except Exception:
            pass
    _CACHE[str(path)] = (key, out)
    return out


def tail_jsonl(path: Path, n: int) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    out: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines()[-n:]:
        try:
            out.append(json.loads(line))
        except Exception:
            pass
    return out


# ---- liveness / silent-hang detection ------------------------------------------------------------------ #
def state_age_seconds(st: dict[str, Any] | None, now_epoch: float) -> float | None:
    """Seconds since ``progress.json`` was last rewritten, or None if unknown/unparseable.

    Uses the monitor's own ``updated`` wall-clock stamp (``%Y-%m-%dT%H:%M:%S``, local time), so it measures
    *writer* liveness independent of this watcher's clock drift within the same host.
    """
    if not st:
        return None
    ts = st.get("updated")
    if not isinstance(ts, str):
        return None
    try:
        wrote = time.mktime(time.strptime(ts, "%Y-%m-%dT%H:%M:%S"))
    except Exception:
        return None
    return max(0.0, now_epoch - wrote)


def is_stale(st: dict[str, Any] | None, now_epoch: float, threshold: float) -> bool:
    """True when the run *should* be advancing but ``progress.json`` has gone silent past ``threshold``.

    A terminal phase (``done``/``error``) is never stale — the writer has intentionally stopped.
    """
    if not st or st.get("phase") in ("done", "error", "starting"):
        return False
    age = state_age_seconds(st, now_epoch)
    return age is not None and age > threshold


# ---- error tracker + token/cost accounting (read-only over the structured logs) ------------------------- #
def anomaly_counts(run_dir: Path) -> dict[str, int]:
    """Anomalies grouped by ``kind`` (critic_explosion, ram_pressure_*, failure_wave, …) — the error tracker."""
    c: Counter[str] = Counter()
    for rec in _read_jsonl_cached(run_dir / "anomalies.jsonl"):
        c[str(rec.get("kind", "?"))] += 1
    return dict(c.most_common())


def _resolve_price(model: str | None) -> tuple[float, float] | None:
    if not model:
        return None
    m = model.lower()
    for key, price in _PRICES_PER_MTOK.items():
        if key in m:
            return price
    return None


def token_spend(run_dir: Path) -> dict[str, Any]:
    """Aggregate LLM token usage + estimated USD cost from the ``llm_call`` records in ``events.jsonl``.

    Returns ``{calls, in_tok, out_tok, usd, costed_calls}``. ``usd`` sums only calls whose model id matches
    the price table (``costed_calls``); list price, cache reads ignored ⇒ a conservative upper bound.
    """
    calls = in_tok = out_tok = costed = 0
    usd = 0.0
    for rec in _read_jsonl_cached(run_dir / "events.jsonl"):
        if rec.get("event") != "llm_call":
            continue
        calls += 1
        it = rec.get("in_tok")
        ot = rec.get("out_tok")
        it = int(it) if isinstance(it, (int, float)) else 0
        ot = int(ot) if isinstance(ot, (int, float)) else 0
        in_tok += it
        out_tok += ot
        price = _resolve_price(rec.get("model"))
        if price is not None:
            usd += it / 1e6 * price[0] + ot / 1e6 * price[1]
            costed += 1
    return {"calls": calls, "in_tok": in_tok, "out_tok": out_tok, "usd": round(usd, 4), "costed_calls": costed}


# ---- remote alert (opt-in, fail-safe, stdlib only; a pure side-channel) --------------------------------- #
def build_alert(st: dict[str, Any] | None, reason: str, run_dir: Path) -> str:
    """One-line status message for a push notification. Carries run STATUS only — never data/returns/code."""
    if not st:
        return f"[{run_dir.name}] {reason}: no progress.json yet"
    a, c = st.get("arms", {}), st.get("candidates", {})
    an = st.get("anomalies", {})
    tok = token_spend(run_dir)
    return (
        f"[{st.get('title', run_dir.name)}] {reason.upper()} | phase={st.get('phase')} "
        f"arms {a.get('done', '?')}/{a.get('total', '?')} cand {c.get('run_done', '?')}/{c.get('run_total', '?')} "
        f"anomalies={an.get('count', 0)} llm_usd≈{tok['usd']}"
    )


def post_alert(url: str, message: str, *, timeout: float = 10.0) -> bool:
    """POST ``message`` to ``url`` (ntfy.sh-compatible). Best-effort: swallows every error, never raises."""
    try:
        req = urllib.request.Request(
            url, data=message.encode("utf-8"),
            headers={"Content-Type": "text/plain", "Title": "campaign-monitor"},
        )
        urllib.request.urlopen(req, timeout=timeout).read()  # noqa: S310 - operator-supplied alert URL
        return True
    except Exception:
        return False


def _bar(done: int, total: int, width: int = 30) -> str:
    # ASCII fill so the plain-text snapshot prints on ANY console codepage (e.g. Windows cp1251);
    # rich renders these fine too.
    total = max(int(total or 0), 1)
    frac = min(max(done / total, 0.0), 1.0)
    fill = int(frac * width)
    return f"[{'#' * fill}{'-' * (width - fill)}] {done}/{total} ({frac * 100:4.1f}%)"


def _fmt_secs(s: float | None) -> str:
    if not s or s <= 0:
        return "?"
    s = int(s)
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    return f"{h}h{m:02d}m" if h else f"{m}m{sec:02d}s"


def snapshot_text(st: dict[str, Any], run_dir: Path | None = None, *, stale_secs: float = _DEFAULT_STALE_SECS) -> str:
    a, c, tr, r = st["arms"], st["candidates"], st.get("training", {}), st.get("resources", {})
    an = st.get("anomalies", {})
    gpu = f"GPU {r.get('gpu_util', '?')}% {r.get('gpu_mem_mib', ['?', '?'])[0]}/{r.get('gpu_mem_mib', ['?', '?'])[1]}MiB {r.get('gpu_temp', '?')}C"
    age = state_age_seconds(st, time.time())
    lines = []
    if is_stale(st, time.time(), stale_secs):
        lines.append(f"  !!! STALE — no progress.json update for {_fmt_secs(age)} (silent hang? check the run)")
    lines += [
        f"{st.get('title')} [{st.get('model')}]  phase={st.get('phase')}  elapsed={_fmt_secs(st.get('elapsed_s'))}  ETA={_fmt_secs(st.get('eta_s'))}  age={_fmt_secs(age)}",
        f"  Arms       {_bar(a['done'], a['total'])}  current={a.get('current')}",
        f"  Candidates {_bar(c['run_done'], c['run_total'])}  in-arm {c['in_arm_done']}/{c['in_arm_total']}",
        f"  Training   {_bar(tr.get('step', 0), tr.get('total', 1))}  "
        f"fps={_g(tr.get('fps'))} critic={_g(tr.get('critic_loss'))} actor={_g(tr.get('actor_loss'))} ent={_g(tr.get('ent_coef'))} rew={_g(tr.get('ep_rew_mean'))}",
        f"  {gpu}  CPU {r.get('cpu_pct', '?')}%  RAM {r.get('ram_pct', '?')}%  RSS {r.get('proc_rss_mib', '?')}MiB",
        f"  best_fitness={st.get('best_fitness')}",
        f"  ANOMALIES={an.get('count', 0)}",
    ]
    if run_dir is not None:
        by_kind = anomaly_counts(run_dir)
        if by_kind:
            lines.append("    by kind: " + ", ".join(f"{k}×{v}" for k, v in by_kind.items()))
        tok = token_spend(run_dir)
        if tok["calls"]:
            lines.append(
                f"  LLM        {tok['calls']} calls  in={tok['in_tok']:,} out={tok['out_tok']:,} tok  est≈${tok['usd']}"
            )
    for rec in an.get("recent", []):
        lines.append(f"    ! {rec.get('kind')}: {rec.get('detail')}")
    return "\n".join(lines)


def _g(v: Any) -> str:
    return f"{v:.4g}" if isinstance(v, (int, float)) and v == v else "?"


def render(st: dict[str, Any] | None, run_dir: Path, *, stale_secs: float = _DEFAULT_STALE_SECS, tick: int = 0) -> Any:
    from rich.console import Group
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text

    if st is None:
        return Panel(Text("waiting for progress.json …", style="yellow"), title=str(run_dir))

    now = time.time()
    stale = is_stale(st, now, stale_secs)
    age = state_age_seconds(st, now)
    a, c, tr, r = st["arms"], st["candidates"], st.get("training", {}), st.get("resources", {})
    an = st.get("anomalies", {})
    t = Table.grid(padding=(0, 1))
    t.add_column(justify="right", style="bold cyan")
    t.add_column()
    if stale:
        t.add_row("STALE", Text(f"no update for {_fmt_secs(age)} — silent hang? the run may be wedged", style="bold red"))
    t.add_row("phase", f"{st.get('phase')}   elapsed {_fmt_secs(st.get('elapsed_s'))}   ETA {_fmt_secs(st.get('eta_s'))}   age {_fmt_secs(age)}")
    t.add_row("Arms", _bar(a["done"], a["total"]) + f"   {a.get('current') or ''}")
    t.add_row("Candidates", _bar(c["run_done"], c["run_total"]) + f"   in-arm {c['in_arm_done']}/{c['in_arm_total']} gen{c.get('gen', 0)}")
    t.add_row("Training", _bar(tr.get("step", 0), tr.get("total", 1)))
    t.add_row("", f"fps={_g(tr.get('fps'))}  critic={_g(tr.get('critic_loss'))}  actor={_g(tr.get('actor_loss'))}  ent={_g(tr.get('ent_coef'))}  rew={_g(tr.get('ep_rew_mean'))}")
    gpu_mem = r.get("gpu_mem_mib", ["?", "?"])
    t.add_row("GPU", f"{r.get('gpu_util', '?')}%  {gpu_mem[0]}/{gpu_mem[1]} MiB  {r.get('gpu_temp', '?')}C")
    t.add_row("Host", f"CPU {r.get('cpu_pct', '?')}%  RAM {r.get('ram_pct', '?')}%  RSS {r.get('proc_rss_mib', '?')} MiB")
    t.add_row("best", str(st.get("best_fitness")))
    # LLM token-spend + estimated USD (reward-authoring cost) — read from events.jsonl.
    tok = token_spend(run_dir)
    if tok["calls"]:
        t.add_row("LLM", f"{tok['calls']} calls  {tok['in_tok']:,} in / {tok['out_tok']:,} out tok  est≈${tok['usd']}")
    # Candidate-parallel: a row per concurrently-training candidate.
    active = st.get("active") or []
    if active:
        t.add_row("active", f"{len(active)} training concurrently")
        for w in active[:8]:
            t.add_row(
                "  > " + str(w.get("arm", ""))[:13],
                f"{w.get('cand', '')} {_bar(w.get('step', 0), w.get('total', 1), 16)} "
                f"fps={_g(w.get('fps'))} critic={_g(w.get('critic_loss'))}",
            )

    nan = int(an.get("count", 0))
    anbody = Text(f"anomalies: {nan}", style="bold red" if nan else "green")
    by_kind = anomaly_counts(run_dir)
    if by_kind:
        anbody.append("  [" + ", ".join(f"{k}×{v}" for k, v in by_kind.items()) + "]", style="red")
    for rec in an.get("recent", []):
        anbody.append(f"\n ! {rec.get('kind')}: {rec.get('detail')}", style="red")

    ev = Text("recent events", style="dim")
    for e in tail_jsonl(run_dir / "events.jsonl", 8):
        style = "red" if e.get("event") == "ANOMALY" else ("yellow" if e.get("level") == "WARNING" else "dim")
        ev.append(f"\n {e.get('ts', '')[-8:]} {e.get('event')} {e.get('msg', '')[:80]}", style=style)

    spin = _SPINNER[tick % len(_SPINNER)] if st.get("phase") not in ("done", "error") else "●"
    title = f"{spin} {st.get('title')} [{st.get('model')}]  pid {st.get('pid')}"
    border = "red" if (nan or stale) else ("green" if st.get("phase") == "done" else "cyan")
    return Panel(Group(t, anbody, ev), title=title, border_style=border)


def main() -> None:
    ap = argparse.ArgumentParser(description="Live, read-only dashboard for a prototype/campaign run.")
    ap.add_argument("run_dir", help="the run output dir (contains progress.json)")
    ap.add_argument("--once", action="store_true", help="print one plain-text snapshot and exit")
    ap.add_argument("--interval", type=float, default=2.0, help="refresh seconds (default 2)")
    ap.add_argument("--stale-secs", type=float, default=_DEFAULT_STALE_SECS,
                    help=f"silent-hang threshold in seconds (default {_DEFAULT_STALE_SECS:g})")
    ap.add_argument("--notify", metavar="URL", default=None,
                    help="opt-in push URL (e.g. https://ntfy.sh/<topic>): POST a STATUS line on done/error/stall. "
                         "OFF by default; stdlib only; a read-only side-channel that never touches the run.")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]  # safe unicode on any console codepage
    except Exception:
        pass
    run_dir = Path(args.run_dir)

    if args.once:
        st = read_state(run_dir)
        print(snapshot_text(st, run_dir, stale_secs=args.stale_secs) if st else f"no progress.json under {run_dir} yet")
        return

    try:  # beautiful, locals-capturing tracebacks if the dashboard itself errors (advanced error tracking)
        from rich.traceback import install as _install_tb

        _install_tb(show_locals=False)
    except Exception:
        pass

    from rich.console import Console
    from rich.live import Live

    console = Console()
    sent: set[str] = set()  # dedupe push notifications: one per (done|error|stall)

    def _maybe_notify(st: dict[str, Any] | None) -> None:
        if not args.notify or st is None:
            return
        phase = st.get("phase")
        reason = "done" if phase == "done" else "error" if phase == "error" else (
            "stall" if is_stale(st, time.time(), args.stale_secs) else None
        )
        if reason and reason not in sent:
            sent.add(reason)
            post_alert(args.notify, build_alert(st, reason, run_dir))

    tick = 0
    with Live(render(read_state(run_dir), run_dir, stale_secs=args.stale_secs), console=console,
              refresh_per_second=2, screen=False) as live:
        while True:
            try:
                tick += 1
                st = read_state(run_dir)
                live.update(render(st, run_dir, stale_secs=args.stale_secs, tick=tick))
                _maybe_notify(st)
                if st is not None and st.get("phase") in ("done", "error"):
                    time.sleep(args.interval)
                    live.update(render(read_state(run_dir), run_dir, stale_secs=args.stale_secs, tick=tick))
                    break
                time.sleep(args.interval)
            except KeyboardInterrupt:
                break


if __name__ == "__main__":
    main()
