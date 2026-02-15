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

*Created automatically to track the MiniMOG parity investigation.*