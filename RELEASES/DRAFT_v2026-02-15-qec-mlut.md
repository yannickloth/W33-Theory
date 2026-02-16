Release: Pillar-45 — GF(3) QEC primitives + MLUT decoder (draft)

Tag: v2026-02-15-qec-mlut (suggested)

**Correction notice (2026-02-15):** The published GitHub Release body previously displayed character-encoding (mojibake). The canonical, corrected release notes are maintained in `docs/outreach/pillar-45-qec.md`; the README badge points there. The Release on GitHub is being refreshed to match this canonical text and preserve DOI/assets.

Overview
- This release introduces reproducible GF(3) (qutrit) quantum‑error‑correction primitives derived from the W(3,3) finite geometry. It provides encoder/decoder implementations, exact and approximate MLUT (table‑lookup) decoders, coverage analytics, a fully executed demo notebook, deterministic tests, and CI-driven benchmarks.

What’s included
- `scripts/w33_quantum_error_correction.py` — GF(3) encoder/decoder API, syndrome helpers, MLUT builders (exact + approximate), coverage/statistics helpers.
- `notebooks/w33_qec_demo.ipynb` — executed demonstration showing encode/decode, MLUT construction and coverage visualizations.
- `tests/test_e8_embedding.py` — deterministic unit & property tests for QEC primitives (seeded RNGs where applicable).
- `.github/workflows/qec.yml` — CI workflow that runs the demo notebook, targeted QEC tests, and MLUT micro‑benchmarks.

Why this matters
- Connects the W(3,3) finite geometry to practical qutrit QEC tools and provides a small, reproducible codebase for experimentation and benchmarking.

Verify (quick)
- Run unit tests: `pytest -q tests/test_e8_embedding.py::TestQuantumErrorCorrection`
- Execute demo notebook: `jupyter nbconvert --to notebook --execute --inplace notebooks/w33_qec_demo.ipynb`
- Run the MLUT benchmark via CI (see Actions → QEC CI badge).

DOI & publishing
- Zenodo DOI: [10.5281/zenodo.18652825](https://doi.org/10.5281/zenodo.18652825)
- Automated Zenodo deposition is triggered by the `release_to_zenodo` workflow when this GitHub Release is published (requires `ZENODO_TOKEN`).

Changelog (high level)
- Add: GF(3) encoder/decoder, syndrome + MLUT decoders
- Add: approximate MLUT sampler, coverage analytics
- Add: demo notebook, deterministic tests, CI workflow
- Perf: fast‑syndrome helper and MLUT optimizations

Contributors
- Wilj D. (author), reviewers & contributors

Notes
- This is a draft release; please review the demo and tests and open issues/PRs for corrections or follow‑ups.
