# ATLAS matrix reps (vendored snapshots)

This folder vendors small **public** matrix-representation snippets from the
ATLAS of Group Representations so the repo’s verification scripts/tests can run
fully offline.

## 2.Suz over GF(3), dim 12

Files:
- `2SuzG1-f3r12B0.m1`
- `2SuzG1-f3r12B0.m2`

Source:
- ATLAS matrep landing page: `https://brauer.maths.qmul.ac.uk/Atlas/v3/matrep/2SuzG1-f3r12B0`
- Direct MeatAxe-text endpoints:
  - `https://brauer.maths.qmul.ac.uk/Atlas/spor/Suz/mtx/2SuzG1-f3r12B0.m1`
  - `https://brauer.maths.qmul.ac.uk/Atlas/spor/Suz/mtx/2SuzG1-f3r12B0.m2`

Format:
- Single-line “text MeatAxe” format: `1 3 12 12 <row1> ... <row12>`, where each
  `<row>` is a 12-character string over `{0,1,2}` representing entries in `GF(3)`.
