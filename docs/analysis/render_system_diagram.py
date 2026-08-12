#!/usr/bin/env python3
"""⚠ SUPERSEDED entry point for Figure 1.1 / 4.1 -- forwards to ``render_schematics_legible``.

WHAT THIS FILE USED TO DO. It called the fenced ``src.viz.schematics.system_diagram`` and moved one
edge label ("fed each gen"), which the fenced code centred on a 26.5 pt gap inside an opaque white
patch, so that in the built PDF the label covered the entire arrow it named and overprinted the
FEEDBACK CHANNEL box border (measured on p.77, 2026-08-10).

WHY IT NO LONGER DOES IT. A second, larger defect in the same figure -- every label arriving on the
page at 5.3-7.8 pt against the IFTE0008 guideline of >= 10 pt, because the figure was authored 8.12 in
wide for a 453.5 pt column -- cannot be repaired by moving artists. At 10 pt the diagram's top row
needs its labels re-wrapped and its boxes re-sized, which is the layout itself. That re-layout lives in
:mod:`docs.analysis.render_schematics_legible`, which also places this edge label clear of its arrow by
construction, so the repair here is subsumed rather than lost.

This file stays only so that anything already invoking it writes the CORRECTED figure rather than
silently restoring the small one to ``outputs/figures/F1_system_diagram.pdf``. Prefer calling
``render_schematics_legible`` directly; both should be deleted, and both layouts folded back into
``src/viz/schematics.py``, when the ``src/**`` fence lifts.

Usage:
    python docs/analysis/render_system_diagram.py   # -> outputs/figures/F1_system_diagram.{png,pdf}
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

OUT = REPO / "outputs" / "figures" / "F1_system_diagram.png"


def main() -> int:
    from docs.analysis.figure_typeface import use_document_typeface
    from docs.analysis.render_schematics_legible import system_diagram

    use_document_typeface()
    canvas = system_diagram()
    canvas.save(OUT)
    print(f"wrote {OUT} (+ .pdf) via render_schematics_legible.system_diagram")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
