# Data manifest

`checksums.txt` carries one `sha256  relative/path.csv` line per frozen pull (written by `src/pull_pilot.py`).
Rules (CLAUDE.md R4): data files are write-once; re-pulls go to NEW versioned filenames + a new manifest line
+ an ADR. Code verifies checksums before reading. The dissertation's data chapter cites this manifest as the
reproducibility anchor.
