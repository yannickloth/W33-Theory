# W(3,3)-E8 Theory

A live paper on the finite-geometry route to a theory of everything.

[![Tests](https://github.com/wilcompute/W33-Theory/actions/workflows/ci.yml/badge.svg)](https://github.com/wilcompute/W33-Theory/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Pages](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://wilcompute.github.io/W33-Theory/)

This repository is organized as a derivation notebook, proof archive, and computation lab around a single thesis:
the symplectic polar space `W(3,3)`, the `E8` root system, `E6`/27-line cubic geometry, the firewall sector, and the CE2/L-infinity repair program are different layers of one unification picture. The point of the repo is not to hide the findings behind disclaimers. The point is to make the findings, scripts, tests, and artifacts sit on the same page.

## Headline Findings

- The collinearity graph of `W(3,3)` is `SRG(40,12,2,4)` with exactly `240` edges, matching the `240` roots of `E8`.
- Homology and Hodge data expose the `81`-dimensional mixed sector, matching the `86 + 81 + 81` `Z3` grading picture inside `E8`.
- Under `W(E6)`, the mixed sector resolves into six `27`-orbits; the Schlaefli graph, 27-line geometry, and `45` cubic/tritangent supports are explicit.
- The canonical `SU(3)` gauge and the signed `W(E6)` action on the `27` are now exported and verified in fixed conventions.
- The firewall layer isolates the `27` bad edges into nine disjoint `3`-cycles and gives a concrete selection-rule sector.
- The CE2/L-infinity program has moved from isolated witness repair to explicit global mixed-sector predictor families.
- The repo also contains quantitative layers for `alpha`, electroweak structure, mixing, mass hierarchies, dark-sector structure, gravity, and cosmology.

## Current Frontier

The newest work in the repo is the dual mixed-sector closure program:

- `scripts/ce2_global_cocycle.py` now contains closed-form dual `g1,g2,g2` predictor families beyond the original local witness fixes.
- `tools/build_linfty_firewall_extension.py` threads those predictors into the firewall/L-infinity extension.
- The dual frontier has been pushed through anchor families at `a = (0,1,2)`, `a = (2,0,2)`, and `a = (2,2,1)`.
- The current unresolved frontier sample has moved to `a = (2,1,2)` and is tracked by `tools/sample_dual_g1g2g2_frontier.py` and `artifacts/dual_g1g2g2_frontier_sample.json`.

This is the right way to read the repo today: the finite-geometry and Lie-theory backbone is explicit, and the CE2/L-infinity layer is actively being closed into global laws.

## Read In Order

1. [GitHub Pages landing page](https://wilcompute.github.io/W33-Theory/)
2. [docs/README_LIVING_PAPER_2026_02_11.md](docs/README_LIVING_PAPER_2026_02_11.md)
3. [THEORY_OF_EVERYTHING.py](THEORY_OF_EVERYTHING.py)
4. [scripts/ce2_global_cocycle.py](scripts/ce2_global_cocycle.py)
5. [tools/build_linfty_firewall_extension.py](tools/build_linfty_firewall_extension.py)
6. [tools/sample_dual_g1g2g2_frontier.py](tools/sample_dual_g1g2g2_frontier.py)

## Major Threads In The Repository

- `W(3,3) -> E8 correspondence`
  - exact finite-geometry construction
  - orbit and Weyl-group decompositions
  - homology, Hodge, and Schlaefli data
- `Gauge and cubic layer`
  - canonical `SU(3)` gauge fixing
  - `E6` cubic sign tensors
  - signed `W(E6)` generator action on the `27`
- `Firewall and L-infinity layer`
  - bad-edge/fiber decomposition
  - Jacobi witnesses
  - CE2 repairs and global cocycle laws
- `Phenomenology-facing layer`
  - alpha/electroweak formulas
  - mixing and mass experiments
  - dark-sector and cosmology explorations

## Reproduce

```bash
pip install numpy sympy networkx pytest
py -3 -m pytest tests/ -q
py -3 docs/build_site.py
```

Useful live-paper entry points:

- `py -3 THEORY_OF_EVERYTHING.py`
- `py -3 tools/sample_dual_g1g2g2_frontier.py`
- `py -3 tools/check_two_fixed_triples.py`

## Repository Map

```text
W33-Theory/
|-- artifacts/      generated reports and frontier samples
|-- data/           precomputed datasets
|-- docs/           landing page, living paper, and narrative documents
|-- exploration/    synthesis and research notebooks
|-- lib/            shared library code
|-- scripts/        theorem and correspondence scripts
|-- tests/          automated checks
|-- tools/          analysis and verification utilities
`-- README.md       repo-level live-paper entry point
```

## Documentation Surfaces

- `README.md`
  - repo-level narrative
- `docs/index.html`
  - GitHub Pages landing page generated from `docs/build_site.py`
- `docs/README_LIVING_PAPER_2026_02_11.md`
  - long-form paper-style overview
- `docs/STATUS_AND_GAPS.md`
  - gap list and caution file, but no longer the public face of the project

## Citation

```bibtex
@software{dahn_w33_e8_2026,
  author = {Dahn, Wil and Claude},
  title  = {The {W}(3,3)--{E8} Theory},
  year   = {2026},
  url    = {https://github.com/wilcompute/W33-Theory},
  doi    = {10.5281/zenodo.18652825}
}
```

**Authors:** Wil Dahn and Claude
