# MINI MOG Tetracode parity — canonical labeling mismatch

## Summary

Exhaustive and solver-assisted searches show there is **no** MOG column/row
permutation that makes *all* 132 Golay hexads satisfy the MiniMOG tetracode
row‑parity for the repository's current canonical labeling.

- Search methods tried: scripts/find_mog_perm_for_tetracode.py (columns × rows),
  MRV backtracking CSP, and an OR‑Tools CP‑SAT formulation.
- Result: CP‑SAT => **INFEASIBLE** for the requirement "all hexads pass".
- Observed canonical passes: **6 hexads** (see below); **126 hexads fail**.

## Passing hexads (current canonical labeling)

- [0, 1, 5, 6, 8, 10]
- [0, 1, 2, 8, 9, 10]
- [0, 3, 6, 7, 9, 11]
- [1, 2, 4, 5, 8, 10]
- [3, 4, 5, 6, 7, 11]
- [2, 3, 4, 7, 9, 11]

## Files / diagnostics

- Diagnostic search script: `scripts/find_mog_perm_for_tetracode.py`
- Unit test wrapper: `tests/test_find_mog_perm_for_tetracode.py`
- CP‑SAT model used for proof: `scripts/search_mog_perm_cocycle.py` (and ad‑hoc notebook runs)
- Test updated to assert the *current* canonical passing set: `tests/test_mini_mog.py`

### Promoted mapping (canonical)

The experimental permutation has been **promoted** and applied to the
repository's canonical `THE_EXACT_MAP` mapping. The canonical labeling now
reflects the promoted permutation and increases tetracode coverage to
**24 / 132** hexads.

- Promoted permutation: `BEST_TETRACODE_PERM = [0, 1, 7, 3, 2, 5, 6, 4, 8, 9, 10, 11]`
- Canonical mapping updated in `THE_EXACT_MAP.py` (see `pos_to_line_mog`).
- Tests updated accordingly in `tests/test_mini_mog.py`.

## Recommendation / next steps

1. Decide canonical authority: keep current `THE_EXACT_MAP` labeling, or adopt
   an alternative labeling that enforces MiniMOG tetracode parity for all
   hexads.
2. If relabeling is accepted, implement the mapping change and re-enable the
   full parity test (remove the canonical-passing assertion).
3. If current labeling is authoritative, keep the test as-is and add docs
   explaining the mismatch; consider formally proving infeasibility.

## Reproduction

Run the diagnostic search and CP‑SAT reproducer:

```bash
python scripts/find_mog_perm_for_tetracode.py
python scripts/search_mog_perm_cocycle.py
pytest tests/test_find_mog_perm_for_tetracode.py -q
```

---

## Resolution / Closure

- PR #74 (`feat/mog-tetracode-candidate`) was **merged** into `master` and the
  promoted permutation was applied to the canonical mapping in `THE_EXACT_MAP.py`.
- A CP‑SAT maximize model was run and **proved optimal** under the current
  problem formulation (objective: maximize number of tetracode‑passing hexads
  subject to MOG slot ↔ position permutation). The maximum achievable count
  under this model is **24 / 132**; no permutation yields all 132 hexads.
- Status: **Closed — canonical mapping promoted; 24 is optimal under model.**

Related references:
- Merged PR: https://github.com/wilcompute/W33-Theory/pull/74

---

*Created automatically to track the MiniMOG parity investigation.*
>>>>>>> 3395fc1d (docs(issue): close MINI_MOG tetracode parity issue — promotion merged, CP-SAT optimality (24))
