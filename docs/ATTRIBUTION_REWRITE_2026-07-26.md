# History rewrite, 2026-07-26 — removal of AI co-author attribution

**What happened.** Every commit reachable from this repository's refs was rewritten to remove
AI-attribution trailers. `CLAUDE.md` carries an absolute rule that this is a single-author MSc
dissertation and that Claude must never appear as an author, co-author, contributor or collaborator
— but commits made *before* that rule was written already carried
`Co-Authored-By: Claude … <noreply@anthropic.com>` trailers, and that trailer is precisely what
GitHub reads to render a co-author on a commit. Tamer directed on 2026-07-26 that it must not say
contributed or co-authored by Claude **anywhere**, so the trailers were stripped from history rather
than only from new commits.

**What changed, exactly.** Commit *messages* only — the attribution lines and nothing else. Verified
mechanically over all 365 commits before anything was pushed:

| check | result |
|---|---|
| commits reachable from the remote refs | 365 |
| commits whose message carried attribution | 174 |
| tree mismatches (file contents changed) | **0** |
| author identity / author-date mismatches | **0** |
| attribution remaining after the rewrite | **0** |

File contents, authorship, and dates are untouched: every rewritten commit keeps a **byte-identical
tree**, which is what makes this a message-only edit and not a change to the work. The pre-rewrite
state was bundled first (`outputs/attribution_rewrite_backup/pre_rewrite_*.bundle`), and the rewrite
ran in an isolated clone so that three concurrently-running sessions' uncommitted work was never at
risk. All six remote branches were force-pushed with `--force-with-lease`; the local branch, the
local `main`, and both tags were then re-anchored onto the same rewritten commits so that no future
push can re-introduce the trailers. The annotated tag `prereg-v1.0` was rebuilt with its **original
tagger identity and timestamp**, so re-anchoring it is not a re-dating.

**Why the citations were NOT rewritten.** `CHANGELOG.md`, `HANDOFF.md`, `DECISIONS.md` and the
session cursor cite ~141 distinct commit SHAs (344 occurrences), and those SHAs changed. They were
deliberately left as they are, for two reasons:

1. **They are true as written.** A CHANGELOG line saying "committed `8c5a022`" records what that
   commit *was called at the time*. Rewriting it to the post-rewrite SHA would retroactively alter
   the record of what happened, which is the opposite of the honesty this project holds itself to.
2. **A blind find-and-replace would have been dangerous.** The docs also record **SHA-256 digests**
   — the pre-registration freeze hashes (`ce5db62c…`, `68c0a4ff…`, `b8993600a4d53a09…`) — in the same
   short-hex, backticked style as commit SHAs. A regex sweep could not reliably tell them apart, and
   corrupting a recorded freeze hash would damage the scientific record far more than a stale link.

**How to resolve an old SHA.** `ATTRIBUTION_REWRITE_SHA_MAP.tsv` in this directory is the complete,
verified translation table (365 rows, `old_sha<TAB>new_sha`). To look one up:

```bash
grep ^8c5a022 docs/ATTRIBUTION_REWRITE_SHA_MAP.tsv     # -> the post-rewrite SHA
```

This is the same commit-map convention `git filter-repo` emits, and it is why the old identifiers in
the historical documents remain fully resolvable.

**Standing rule from here.** No commit, PR, tag, or release note gets an AI-attribution trailer —
see the absolute rule at the top of `CLAUDE.md`. AI assistance is disclosed exactly once, where UCL
policy requires it: the AI-assistance disclosure in the dissertation front matter. That disclosure is
required and stays; it is a statement of tool use under the author's direction, not authorship. The
paper likewise describes the language models as *"the object of study, not authorship aids"*, which
is a claim about the experiment and is also unaffected by any of the above.
