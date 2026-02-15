# Pillar‑45 — GF(3) qutrit QEC primitives + MLUT (2026-02-15)

**DOI:** https://doi.org/10.5281/zenodo.18652825

## TL;DR

Pillar‑45 adds a complete, reproducible GF(3) qutrit quantum‑error‑correction toolchain to the W33→E8 repository: encoder/decoder, syndrome & MLUT decoders, approximate MLUT sampling, deterministic tests, and an executed demo notebook.

## Background

The W(3,3) finite geometry maps naturally to ternary code structures. Over recent months we've formalized a stack of correspondences connecting W(3,3) incidence structures to E8 embeddings and — unexpectedly — to practical qutrit QEC primitives useful for both theorists and experimentalists.

## What we built

- GF(3) encoder & syndrome decoder (`scripts/w33_quantum_error_correction.py`)
- Exact and approximate MLUT (table‑lookup) decoders with a fast‑syndrome helper
- Coverage analytics and deterministic unit/property tests with seeded RNGs
- Executable demo: `notebooks/w33_qec_demo.ipynb`
- CI that runs tests, executes the notebook, and runs MLUT benchmarks

## Highlights

- Practical qutrit QEC primitives suitable for experimentation and benchmarking
- Reproducibility‑first: tests, CI notebook execution, and citable release (DOI)

## Reproduce

- Run QEC tests:

  ```bash
  pytest -q tests/test_e8_embedding.py::TestQuantumErrorCorrection
  ```

- Execute the demo notebook:

  ```bash
  jupyter nbconvert --to notebook --execute --inplace notebooks/w33_qec_demo.ipynb
  ```

- Release & DOI:
  - GitHub release: https://github.com/wilcompute/W33-Theory/releases/tag/v2026-02-15-qec-mlut
  - Zenodo DOI: https://doi.org/10.5281/zenodo.18652825

## Citation (BibTeX)

```
@misc{wilcompute_pillar45_2026,
  author = {Wilj D.},
  title = {Pillar-45 — GF(3) QEC primitives + MLUT (v2026-02-15-qec-mlut)},
  year = {2026},
  howpublished = {Zenodo},
  doi = {10.5281/zenodo.18652825},
  url = {https://github.com/wilcompute/W33-Theory/releases/tag/v2026-02-15-qec-mlut}
}
```

## Call to action

Try the demo, run the MLUT benchmarks, and open issues or discussion items for feedback and replication requests.

---

*Posted 2026-02-15 — automated release & DOI insertion via CI.*
