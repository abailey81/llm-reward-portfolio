#!/bin/bash
# Emits ONE line only when Tamer's instruction block in docs/REMOTE_CONTROL.md actually CHANGES.
# The publisher loop does the `git pull` every 5 min, so this only has to read the local file.
# Keyed on CONTENT, not on file mtime: a pull that rewrites the file with identical text is silent.
set -u
REPO=/c/Users/User/Desktop/dissertation_papers/llm-reward-portfolio
F="$REPO/docs/REMOTE_CONTROL.md"

# the instruction is the first fenced block after the "INSTRUCTIONS" heading
extract() {
  awk '/^## . INSTRUCTIONS/,0' "$F" 2>/dev/null \
    | awk '/^```/{n++; next} n==1' \
    | sed 's/[[:space:]]*$//' | grep -v '^$' | tr '\n' ' '
}

prev=$(extract)
echo "remote-control watcher armed; current instruction: [${prev:-<empty>}]"
while true; do
  sleep 60
  cur=$(extract)
  if [ "$cur" != "$prev" ]; then
    echo "TAMER INSTRUCTION CHANGED -> [${cur:-<empty>}]"
    prev="$cur"
  fi
done
