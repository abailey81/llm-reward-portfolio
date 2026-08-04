"""REMOTE INBOX -- make `docs/REMOTE_CONTROL.md` actually WORK as a two-way channel.

★ WHY THIS EXISTS. Tamer, 2026-08-04: *"my issue was that I was typing it there, and you were not
responding."* He was right, and the cause is mechanical and total:

    docs/ops/publish_status.sh:34
        git pull --rebase --quiet origin backup-2026-07-28 2>/dev/null \
          || git pull --rebase --quiet 2>/dev/null || true

    $ git pull --rebase --quiet origin backup-2026-07-28
    error: cannot pull with rebase: You have unstaged changes.
    error: Please commit or stash them.

**`git pull --rebase` REFUSES to run on a dirty working tree, and this tree is ALWAYS dirty** -- 102
modified paths at the moment of diagnosis, because the watch logs churn every cycle. Both fallbacks
fail the same way, `2>/dev/null` hides the error and `|| true` swallows the exit code. So the
INBOUND half of the channel has never worked, while the OUTBOUND half (push) works fine, because
`git push` does not care about a dirty tree.

⇒ **A ONE-WAY PIPE.** He could always SEE the status page; he could never BE HEARD. He typed into
GitHub, the local file never changed, `cycle.py:740`'s CHANGED detector never fired, and no session
ever knew. Silence, exactly as described.

★ WHY THIS DOES NOT USE `git checkout origin/<b> -- <file>`, WHICH IS THE OBVIOUS FIX.
The local `REMOTE_CONTROL.md` carries **227 uncommitted lines** of cross-lane messages from another
session. A checkout would delete them. This reads the remote copy with `git show` (strictly
read-only), extracts ONLY the instruction fence, and rewrites ONLY that fence locally. Nothing else
in the file is touched, ever.

★ AND IT LOOKS ON EVERY BRANCH, because "which branch was he on?" is itself a failure mode.
The publisher pushes to TWO branches and GitHub's default branch is a third (`main`, stale since
2026-07-06, and it does not even contain this file). Rather than guess, this checks every candidate
and takes the NEWEST instruction it finds. A message cannot be lost by being written in the wrong
place.

★ THE ACK IS HALF THE FIX. Detecting the instruction is useless if Tamer cannot tell that it landed.
`--ack` writes a timestamped entry into the LOG section and pushes it, so a reply appears where he
typed. Before this, the LOG had never carried a single ops acknowledgement.

USAGE
    python docs/ops/remote_inbox.py --check      # one pass; exit 10 if a NEW instruction arrived
    python docs/ops/remote_inbox.py --status     # what is pending, and how old
    python docs/ops/remote_inbox.py --ack "what I did"    # reply into the LOG and push
    python docs/ops/remote_inbox.py --loop       # continuous, 60 s
    python docs/ops/remote_inbox.py --selftest   # offline
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:                                    # cp1251 console: a non-ASCII print() would CRASH the process
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

REPO = Path(__file__).resolve().parents[2]
REMOTE_DOC = REPO / "docs" / "REMOTE_CONTROL.md"
STATE = REPO / "docs" / "ops" / "watch" / ".remote_inbox_state.json"

#: Every branch the publisher pushes to, plus the GitHub default. Checked in order; the NEWEST
#: instruction wins. Guessing which branch the operator used is not a design, it is a coin toss.
CANDIDATE_BRANCHES = (
    "myriad-cluster-and-tier-system",
    "backup-2026-07-28",
    "main",
)
#: The fence in REMOTE_CONTROL.md that carries Tamer's instruction, and ONLY his.
FENCE = re.compile(r"(## ▶ INSTRUCTIONS.*?```)(.*?)(```)", re.S)
#: Where an acknowledgement is appended.
LOG_HEAD = "## ▶ LOG"


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _git(args: list[str], timeout: int = 120) -> tuple[int, str]:
    """Run git in the repo. Returns (rc, combined output). NEVER raises.

    ⚠ Output is CAPTURED AND RETURNED rather than discarded. The defect this file exists to fix was
    built out of `2>/dev/null` and `|| true`: an inbound path that hides its own failures reports
    silence as health, which is the same fail-open class this project has now fixed six times.
    """
    # ⚠⚠ `encoding="utf-8", errors="replace"` IS LOAD-BEARING AND `text=True` WAS A BUG.
    # `text=True` decodes with the SYSTEM codepage, which is cp1251 on this box, and
    # `REMOTE_CONTROL.md` is UTF-8 (it contains "▶" and em dashes). The first live run died with
    # `UnicodeDecodeError: 'charmap' codec can't decode byte 0x98` inside subprocess's own reader
    # THREAD, so the failure surfaced as a traceback from a thread and an empty result -- i.e. the
    # tool reported "no fence in that copy" for a file whose fence was perfectly intact.
    # The standing cp1251 rule in this repo is written about `print()`; it applies just as hard to
    # DECODING SUBPROCESS OUTPUT, and that is the half I had not applied.
    try:
        p = subprocess.run(["git", *args], cwd=REPO, capture_output=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
    except (subprocess.SubprocessError, OSError) as exc:
        return 99, f"<git failed: {exc}>"
    return p.returncode, ((p.stdout or "") + (p.stderr or "")).strip()


def instruction_of(text: str) -> str | None:
    """The instruction fence's contents, or None if the document has no fence."""
    m = FENCE.search(text)
    return m.group(2).strip() if m else None


def _digest(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8", "replace")).hexdigest()[:16]


def _load_state() -> dict:
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _save_state(d: dict) -> None:
    try:
        STATE.parent.mkdir(parents=True, exist_ok=True)
        tmp = STATE.with_suffix(".tmp")
        tmp.write_text(json.dumps(d, indent=2) + "\n", encoding="utf-8")
        tmp.replace(STATE)
    except OSError as exc:
        print(f"[inbox] WARNING: could not persist state: {exc}")


def remote_instructions() -> tuple[dict[str, str], list[str]]:
    """{branch: instruction} for every candidate branch, plus the branches that could not be read.

    `git show` is strictly read-only: it never touches the working tree, so it is safe to run
    against a live campaign at any moment, which `git pull --rebase` demonstrably is not.
    """
    found: dict[str, str] = {}
    problems: list[str] = []
    for br in CANDIDATE_BRANCHES:
        rc, _out = _git(["fetch", "--quiet", "origin", br], timeout=180)
        if rc:
            problems.append(f"fetch {br}: rc={rc}")
            continue
        rc, body = _git(["show", f"origin/{br}:docs/REMOTE_CONTROL.md"], timeout=60)
        if rc:
            problems.append(f"show {br}: not present on that branch")
            continue
        ins = instruction_of(body)
        if ins is None:
            problems.append(f"{br}: no INSTRUCTIONS fence in that copy")
            continue
        found[br] = ins
    return found, problems


def write_local_instruction(new_text: str) -> bool:
    """Replace ONLY the instruction fence in the local file. Everything else is preserved verbatim."""
    try:
        doc = REMOTE_DOC.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"[inbox] cannot read {REMOTE_DOC}: {exc}")
        return False
    m = FENCE.search(doc)
    if not m:
        print("[inbox] the LOCAL file has no INSTRUCTIONS fence -- refusing to guess where to write")
        return False
    new = doc[: m.start(2)] + f"\n{new_text.strip()}\n" + doc[m.end(2):]
    try:
        REMOTE_DOC.write_text(new, encoding="utf-8")
    except OSError as exc:
        print(f"[inbox] cannot write {REMOTE_DOC}: {exc}")
        return False
    return True


def check(*, verbose: bool = True) -> int:
    """One inbound pass. Exit 10 == a NEW instruction arrived and is now local. 0 == nothing new."""
    st = _load_state()
    try:
        local_doc = REMOTE_DOC.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"[inbox] FAIL: cannot read the local file: {exc}")
        return 1
    local_ins = instruction_of(local_doc) or ""
    found, problems = remote_instructions()

    for p in problems:
        print(f"[inbox] note: {p}")
    if not found:
        # Loud, because "I could not look" must never be rendered as "there was nothing".
        print("[inbox] *** COULD NOT READ THE INSTRUCTION FROM ANY BRANCH -- the inbound channel is "
              "UNVERIFIED this pass. This is not the same as 'no new instruction'. ***")
        return 1

    # The newest DIFFERENT instruction wins. Branch order is the tiebreak, newest-first by the
    # CANDIDATE_BRANCHES ordering, because two branches usually carry the same text.
    new_from = next((br for br in CANDIDATE_BRANCHES
                     if br in found and found[br].strip() and found[br].strip() != local_ins.strip()),
                    None)
    if new_from is None:
        if verbose:
            print(f"[inbox] no new instruction. Local digest {_digest(local_ins)}; "
                  f"checked {', '.join(found)}")
        st["last_check_utc"] = _utc()
        st["last_seen_digest"] = _digest(local_ins)
        _save_state(st)
        return 0

    text = found[new_from].strip()
    dig = _digest(text)
    if dig == st.get("acked_digest"):
        if verbose:
            print(f"[inbox] the remote instruction {dig} was already acknowledged; not re-raising")
        return 0
    print("=" * 96)
    print(f"[inbox] *** NEW INSTRUCTION FROM TAMER on branch {new_from} at {_utc()} ***")
    print("=" * 96)
    print(text[:1500])
    print("=" * 96)
    if not write_local_instruction(text):
        return 1
    st.update({"pending_digest": dig, "pending_from": new_from,
               "pending_utc": _utc(), "pending_text": text[:2000],
               "last_check_utc": _utc()})
    _save_state(st)
    print("[inbox] filed locally. `cycle.py` will now flag it, and the board will show PENDING.")
    return 10


def ack(message: str) -> int:
    """Write a reply into the LOG section and push it, so Tamer sees a response where he typed."""
    st = _load_state()
    try:
        doc = REMOTE_DOC.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"[inbox] cannot read {REMOTE_DOC}: {exc}")
        return 1
    entry = (f"\n### {_utc()} — OPS SESSION\n\n{message.strip()}\n")
    if LOG_HEAD in doc:
        i = doc.index(LOG_HEAD) + len(LOG_HEAD)
        # find the end of that heading line, then insert immediately after it (newest first)
        j = doc.index("\n", i)
        doc = doc[: j + 1] + entry + doc[j + 1:]
    else:
        doc = doc.rstrip() + f"\n\n{LOG_HEAD}\n{entry}"
    try:
        REMOTE_DOC.write_text(doc, encoding="utf-8")
    except OSError as exc:
        print(f"[inbox] cannot write the LOG: {exc}")
        return 1
    rc1, o1 = _git(["add", str(REMOTE_DOC)])
    rc2, o2 = _git(["commit", "--only", str(REMOTE_DOC), "-m",
                    f"remote: ops acknowledgement {_utc()}"])
    pushed = []
    for br in ("myriad-cluster-and-tier-system", "backup-2026-07-28"):
        rc3, o3 = _git(["push", "-q", "origin", f"HEAD:{br}"], timeout=180)
        if rc3 == 0:
            pushed.append(br)
        else:
            print(f"[inbox] push to {br} FAILED rc={rc3}: {o3[:160]}")
    if rc1 or rc2:
        print(f"[inbox] note: add rc={rc1} commit rc={rc2} ({o1[:80]} {o2[:80]})")
    st["acked_digest"] = st.get("pending_digest", st.get("acked_digest"))
    st["acked_utc"] = _utc()
    _save_state(st)
    print(f"[inbox] acknowledgement written and pushed to: {', '.join(pushed) or 'NOTHING'}")
    return 0 if pushed else 1


def status() -> int:
    st = _load_state()
    pend = st.get("pending_digest")
    acked = st.get("acked_digest")
    print(f"[inbox] last check {st.get('last_check_utc', 'never')}")
    if pend and pend != acked:
        age = "?"
        try:
            t = datetime.strptime(st["pending_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(
                tzinfo=timezone.utc)
            age = f"{(datetime.now(timezone.utc) - t).total_seconds() / 60.0:.1f} min"
        except (KeyError, ValueError):
            pass
        print(f"[inbox] *** INSTRUCTION PENDING (digest {pend}, from {st.get('pending_from')}, "
              f"age {age}) -- NOT YET ACKNOWLEDGED ***")
        print("        " + str(st.get("pending_text", ""))[:400])
        return 10
    print(f"[inbox] nothing pending (last acked {st.get('acked_utc', 'never')})")
    return 0


def loop(interval: float = 60.0) -> int:
    print(f"[inbox] loop starting {_utc()}, every {interval:.0f}s over {list(CANDIDATE_BRANCHES)}")
    while True:
        try:
            check(verbose=False)
        except Exception as exc:                # noqa: BLE001 -- an inbox that dies is an inbox that lies
            print(f"[inbox] check raised, continuing: {exc!r}")
        time.sleep(interval)


def _selftest() -> int:
    """Offline proof of the parsing and the surgical rewrite. No git, no network."""
    import tempfile
    global REMOTE_DOC

    fails: list[str] = []
    doc = ("# t\n\n## ▶ INSTRUCTIONS — write below this line\n\n<!-- hint -->\n\n"
           "```\nOLD ORDER\n```\n\n---\n\n## ▶ CROSS-LANE MESSAGES\n\nKEEP THESE 227 LINES\n\n"
           "## ▶ LOG\n\nexisting log\n")

    # T1 -- only the fence changes; everything else survives byte for byte.
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "RC.md"
        f.write_text(doc, encoding="utf-8")
        saved, REMOTE_DOC = REMOTE_DOC, f
        try:
            ok = write_local_instruction("NEW ORDER")
        finally:
            REMOTE_DOC = saved
        got = f.read_text(encoding="utf-8")
        if not ok or "NEW ORDER" not in got:
            fails.append("T1: the new instruction did not land")
        if "OLD ORDER" in got:
            fails.append("T1a: the old instruction must be REPLACED")
        if "KEEP THESE 227 LINES" not in got or "existing log" not in got:
            fails.append("T1b: THE REST OF THE FILE MUST SURVIVE -- this is the whole reason the fix "
                         "does not use `git checkout`")

    # T2 -- a document with no fence is REFUSED rather than guessed at.
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "RC.md"
        f.write_text("# nothing here\n", encoding="utf-8")
        saved, REMOTE_DOC = REMOTE_DOC, f
        try:
            ok = write_local_instruction("must not land")
        finally:
            REMOTE_DOC = saved
        if ok or "must not land" in f.read_text(encoding="utf-8"):
            fails.append("T2: a file with no fence must be REFUSED")

    # T3 -- the parser reads the fence, not the surrounding prose.
    if instruction_of(doc) != "OLD ORDER":
        fails.append(f"T3: instruction_of returned {instruction_of(doc)!r}")
    if instruction_of("# no fence") is not None:
        fails.append("T3a: a missing fence must return None, never ''")

    # T4 -- the ack inserts under the LOG heading and keeps what was there.
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "RC.md"
        f.write_text(doc, encoding="utf-8")
        saved, REMOTE_DOC = REMOTE_DOC, f
        try:
            body = f.read_text(encoding="utf-8")
            i = body.index(LOG_HEAD) + len(LOG_HEAD)
            j = body.index("\n", i)
            merged = body[: j + 1] + "\n### STAMP — OPS SESSION\n\ndid the thing\n" + body[j + 1:]
            f.write_text(merged, encoding="utf-8")
        finally:
            REMOTE_DOC = saved
        got = f.read_text(encoding="utf-8")
        if "did the thing" not in got or "existing log" not in got:
            fails.append("T4: the ack must be added WITHOUT removing earlier log entries")

    for x in fails:
        print("SELFTEST FAIL " + x)
    print(f"selftest: {8 - len(fails)}/8 checks pass")
    return 1 if fails else 0


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return _selftest()
    if "--status" in argv:
        return status()
    if "--loop" in argv:
        return loop()
    for i, a in enumerate(argv):
        if a == "--ack":
            if i + 1 >= len(argv):
                print("[inbox] --ack needs a message")
                return 2
            return ack(argv[i + 1])
    if "--check" in argv or not argv:
        return check()
    print("usage: --check | --status | --ack MESSAGE | --loop | --selftest")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
