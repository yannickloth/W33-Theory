TOE / W33-Theory — WE6-even ↔ PSp(4,3) action sanity + E6×A2 split

This bundle is designed to be dropped into the W33-Theory repo root.

Contents
- docs/WE6_line_action_decomposition.md
- scripts/verify_orbit_decompositions.py
- scripts/classify_e8_roots_dotpair.py
- scripts/classify_w33_edges_by_rootclass.py
- PUSH_TO_MASTER.md

What it does (high level)
1) Verifies that the SP(4,3)-derived 120-line action is INTRANSITIVE with orbits:
   36 + 27 + 27 + 27 + 1 + 1 + 1
   while the 120-edgepair action is TRANSITIVE (single orbit of size 120).
   => these two degree-120 permutation representations cannot be conjugate in S_120.

2) Extracts the canonical E8→E6×A2 dot-pair decomposition already encoded in
   artifacts/explicit_bijection_decomposition.json:
   - 72 roots in the (0,0) class  (E6 roots)
   - 6 roots in six singleton classes (A2 roots)
   - 162 remaining roots in six 27-classes, pairing into three 54-sets (27 lines each)

3) Uses the explicit W33→E8 bijection to classify W33 edges by root class.

Prereqs
- Python 3.10+
- Run from the repo root.

Run
  python scripts/verify_orbit_decompositions.py
  python scripts/classify_e8_roots_dotpair.py
  python scripts/classify_w33_edges_by_rootclass.py

