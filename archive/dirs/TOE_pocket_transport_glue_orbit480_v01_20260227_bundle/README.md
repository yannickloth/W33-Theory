# TOE pocket transport glue & orbit480 bundle v01 (2026-02-27)

This package collects the results of the ``pocket-glue`` and ``orbit 480``
computations described in the conversation.  It is intended to provide a
reproducible record of the two counts that appeared in Wilmot’s paper:

* every 7-pocket completion glue must carry a global sign, giving exactly 2
  glue solutions across the 540-pocket overlap graph;
* the orbit of octonion multiplication tables under signed permutations has
  size 480.

Files:

* `pocket_glue_summary.json` – statistics of the pocket-overlap graph and
  glue solution count (connectivity, edges of size 4/6, components, #solutions).
* `orbit_480_summary.json` – group order / stabilizer / orbit calculations.
* `recompute.py` – small script reproducing both summaries from existing
  outputs in the workspace.
* `REPORT.md` – human-readable narrative of the computation.

To regenerate the summaries yourself, run `python recompute.py` in a
workspace where `pocket_geometry.json` and `octonion_rep_stats.json` exist.