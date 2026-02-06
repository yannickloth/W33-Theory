Add GF(2) parity proof, explicit certificate, generator, and tests.

Changes:
- `docs/gf2_parity_proof.md`: compact, formal GF(2) parity proof with explicit 10-triad certificate.
- `tools/generate_gf2_certificate.py`: generates `artifacts/gf2_certificates.json` from extracted unsat cores.
- `tests/test_gf2_parity_proof.py`: tests the certificate (A·v=0 and d·v=1), checks minimal hitting-set includes [0,20,23], and asserts all small odd null vectors (w≤10) include (0,20,23). Tests auto-generate artifacts when missing.

Why:
Provides a rigorous, reproducible GF(2) contradiction certificate and documents a canonical repair (forbid `(0,20,23)`) which fixes the observed parity obstruction. This PR includes a generator script and tests to make CI robust.

How to reproduce locally:
- `python tools/generate_gf2_certificate.py`
- `python -m pytest tests/test_gf2_parity_proof.py`

Tests passed locally (3 passed).

Notes: draft PR; please review docs and tests. If you prefer I can mark this PR ready for review and include CI badges or additional explanatory diagrams.
