# W(3,3)-E8 Research Program

Finite geometry, Lie theory, and reproducible computation around the `W(3,3) <-> E8` correspondence.

[![Tests](https://github.com/wilcompute/W33-Theory/actions/workflows/ci.yml/badge.svg)](https://github.com/wilcompute/W33-Theory/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Pages](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://wilcompute.github.io/W33-Theory/)

This repository does not currently establish a complete physical theory of everything. It does contain a large, explicit computational program linking the symplectic polar space `W(3,3)`, `E8` root combinatorics, `W(E6)` symmetry, Schlaefli geometry on 27 lines, cubic-support data, and a set of reproducible artifacts around those correspondences.

The canonical status boundary for the project is:

- Solved here: exact finite-geometry and Lie-theoretic constructions, orbit decompositions, gauge-fixing artifacts, sign data, and verification scripts.
- Not solved here: a complete Lagrangian, chirality, mass spectra, RG flow, Lorentzian gravity, or experimentally validated TOE phenomenology.

## What Is Computationally Verified

- The `E8` root system is constructed explicitly with `240` roots.
- Coxeter data yields a `40 x 6` orbit model used as the `W(3,3)` vertex picture in this repo.
- Under `W(E6)`, the root data decomposes into `72 + 6 x 27 + 6 x 1`.
- Each `27`-orbit carries the Schlaefli graph `SRG(27,16,10,8)` with its double-six and tritangent structure.
- The firewall split exposes `243 = 216 + 27`, with the `27` bad edges organizing into nine disjoint 3-cycles.
- The repo includes a deterministic 27-state dynamics harness on the Schlaefli kernel plus firewall edges.
- A canonical `SU(3)` gauge and `E6` cubic sign tensor are computed and verified in fixed conventions.
- Generator actions, channel dictionaries, and selection-rule reports are exported as reproducible artifacts.

Primary source for this boundary: [docs/STATUS_AND_GAPS.md](docs/STATUS_AND_GAPS.md)

## What Remains Open

Before this becomes an actual physical TOE, the repo still needs:

- A principled action or Hamiltonian with equations of motion.
- A chirality mechanism and anomaly-complete field content.
- Masses, mixing, CP violation, and RG running from concrete couplings.
- A derivation of spacetime and gravity with observational outputs.
- Quantitative, falsifiable predictions with uncertainties.

In other words: the mathematics program is substantial, but the physics program is still open.

## Entirety, Stated Precisely

If the goal is to "solve the theory of everything in entirety," the strongest defensible statement this repository currently supports is:

1. The finite-geometry and Lie-theory side is far enough along to be treated as an explicit computational research program.
2. The bridge from that structure to a complete physical TOE is not finished.
3. The honest end-to-end task, today, is to keep those two layers separated and reproducible.

That separation is now the default stance of the README and landing page.

## Selected Workstreams

- `tools/` and `src/` contain the main finite-geometry, root-system, and algebraic-construction code.
- `artifacts/` stores generated reports and certificates from major verification runs.
- `docs/STATUS_AND_GAPS.md` is the best short statement of what is actually established.
- `docs/index.html` is the generated public landing page, built from `docs/build_site.py`.
- `README.md` is the repo-level contract for what the project claims.

## Quick Start

```bash
pip install numpy sympy networkx pytest
python -m pytest tests/ -q        # or: py -3 -m pytest tests/ -q
python docs/build_site.py         # or: py -3 docs/build_site.py
```

## Repository Map

```text
W33-Theory/
|-- artifacts/      generated reports and certificates
|-- data/           precomputed datasets
|-- docs/           site source and narrative documents
|-- exploration/    research and scratch investigations
|-- lib/            shared library code
|-- src/            source modules
|-- tests/          automated tests
|-- tools/          analysis and verification scripts
`-- README.md       repo-level status and navigation
```

## Citation

```bibtex
@software{dahn_w33_e8_2026,
  author = {Dahn, Wil and Claude},
  title  = {The {W}(3,3)--{E8} Correspondence:
            Finite Geometry and Standard Model Structure},
  year   = {2026},
  url    = {https://github.com/wilcompute/W33-Theory},
  doi    = {10.5281/zenodo.18652825}
}
```

**Authors:** Wil Dahn and Claude
