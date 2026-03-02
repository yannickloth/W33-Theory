Release: Pillars 58–60 — p‑Adic AdS/CFT, String Worldsheet, Topological QFT (draft)

Summary
-------
This release documents and verifies **Pillars 58–60** added to the W(3,3)→E8 project:
- Pillar 58 — p‑Adic AdS/CFT (`scripts/w33_padic_ads_cft.py`) — W(3,3) as a finite quotient of the Bruhat‑Tits tree; 3‑adic holography; conformal dimensions from Hodge spectrum; MERA embedding.
- Pillar 59 — String Worldsheet & Modular Invariance (`scripts/w33_string_worldsheet.py`) — modular invariant partition function, E8 theta = E4, Z3 orbifold and three generations, Hagedorn analysis.
- Pillar 60 — Topological Quantum Field Theory (`scripts/w33_tqft.py`) — Frobenius/Bose–Mesner algebra, Dijkgraaf–Witten counts for PSp(4,3), state‑sum checks and cobordism pairing.

Suggested tag
-------------
- `v2026-02-16-pillars-58-60`

Changelog (high level)
----------------------
- Added `scripts/w33_padic_ads_cft.py` — p‑adic holography diagnostics, conformal dimension table, Green's function comparison, MERA interpretation.
- Added `scripts/w33_string_worldsheet.py` — modular partition function checks, E8 theta verification, Z3 orbifold sectoring and Hagedorn analysis.
- Added `scripts/w33_tqft.py` — Bose–Mesner / Frobenius algebra extraction, simple state‑sum counts (GF(2)/GF(3)), Dijkgraaf–Witten evaluations for simple manifolds.
- Tests: added canonical smoke tests for Pillars 58–60 to `tests/test_e8_embedding.py` (3 new test methods), bringing the canonical suite to 280 tests.
- Docs & metadata: README, RELEASES and `CITATION.cff` already reflect the 60 pillars; this draft provides release notes for CI/Zenodo publishing.

Verification
------------
Run the pillar verifications locally or via CI:

```bash
# quick checks (Pillars 58–60 only)
python -m pytest tests/test_e8_embedding.py -k "PAdic or Worldsheet or TQFT" -q

# canonical suite (recommended)
python -m pytest tests/test_e8_embedding.py -q

# run full suite (long-running)
python -m pytest -q
```

Publishing notes
----------------
- Create GitHub Release with the suggested tag above; CI (`release_to_zenodo`) will deposit to Zenodo (requires `ZENODO_TOKEN`).
- After Zenodo DOI is minted, use `scripts/zenodo_sync.py --apply` to inject the DOI into the README and release notes.

References / PRs
----------------
- Pillar 58 implementation: PR #110
- Pillar 59 implementation: PR #111
- Pillar 60 implementation: PR #112

Next steps (recommended)
------------------------
1. Run CI and create GitHub Release `v2026-02-16-pillars-58-60` once tests pass.
2. Publish Zenodo deposition via CI (requires `ZENODO_TOKEN`).
3. Draft short outreach post summarizing the p‑adic/Worldsheet/TQFT connections for the release notes.
