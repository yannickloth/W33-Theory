# Comparison: Anchor CP‑SAT outcomes for singleton forbids

Summary: both singleton forbids `[0,18,25]` and `[0,20,23]` were tried as repairs to the opt mapping GF(2) contradiction; for the default sign-consistent W set (0,4,5,6,7,8,9,10,11,12,13,14,15) each forbid yields **FEASIBLE** anchored CP‑SAT solutions with `matched=19` for all W's (reports: `reports/anchor_forbid_0-18-25.md`, `reports/anchor_forbid_0-20-23.md`).

Implication: both singleton forbids are effective canonical repair candidates; next step is to pick a canonical tie-breaker (e.g., lexicographic, geometric, or choose smallest Schläfli id) and run final anchored verification + GF(2) certificate generation for the chosen forbid across the full W list.

Suggested next actions:
- If you prefer **quick canonical choice**, pick one of the singleton forbids (I can default to `[0,20,23]` since we used it earlier), and I will run the full anchored verification + GF(2) certificate and add formal test artifacts.
- If you prefer **geom/automorphism-informed choice**, I can compute orbit representatives and prefer the forbid with the smallest canonical representative across automorphisms.
- Or I can **keep both** and add both canonical repairs to the repo as alternate valid solutions (with notes).

Which direction should I take next?
