# W33 Theory of Everything

## Deriving the Standard Model from a Finite Geometry

[![pytest](https://github.com/wilcompute/W33-Theory/actions/workflows/pytest.yml/badge.svg)](https://github.com/wilcompute/W33-Theory/actions/workflows/pytest.yml) [![Sage verification](https://github.com/wilcompute/W33-Theory/actions/workflows/sage-verification.yml/badge.svg)](https://github.com/wilcompute/W33-Theory/actions/workflows/sage-verification.yml) [![Predictions report](https://github.com/wilcompute/W33-Theory/actions/workflows/predictions_report.yml/badge.svg)](https://github.com/wilcompute/W33-Theory/actions/workflows/predictions_report.yml) [![Nightly predictions](https://github.com/wilcompute/W33-Theory/actions/workflows/nightly_predictions.yml/badge.svg)](https://github.com/wilcompute/W33-Theory/actions/workflows/nightly_predictions.yml)

**Author:** Wil Dahn
**Date:** January-February 2026
**Status:** 69 theorems verified, 50+ quantitative predictions

**Canonical definitions:** See `STANDARDIZATION.md` (W(3,3) vs W33, incidence counts, group orders).

---

## What This Is

This repository develops a **theory of everything** (ToE) based on a single
mathematical object: the **W(3,3) generalized quadrangle**, a strongly regular
graph on 40 vertices arising from the symplectic geometry of F\_3^4. The core
claim is that the Standard Model of particle physics --- its gauge group, particle
content, three generations, selection rules, and coupling structure --- is not
postulated but **derived** from W(3,3) embedded in the E8 root system.

The main deliverable is **`tools/toe_unified_derivation.py`**: a self-contained
Python script that proves 69 theorems from first principles, each verified by
exhaustive computation.

---

## The Construction Chain

```
F_3 = {0, 1, 2}               (finite field with 3 elements)
       |
V = F_3^4                     (4-dimensional vector space)
       |
omega(u,v) = symplectic form   (antisymmetric bilinear form)
       |
PG(3,3)                       (40 projective points)
       |
W(3,3) = SRG(40, 12, 2, 4)    (collinearity graph: symplectic GQ)
       |
Aut(W33) = W(E6)              (automorphism group = Weyl group of E6)
       |
E6 subset E8                  (E8 -> E6 x SU(3) branching)
       |
27-rep of E6                  (27 lines on a cubic surface)
       |
Schlafli graph SRG(27,16,10,8) (adjacency at inner product 1)
       |
Double-six -> trinification    (S6 -> S3 x S3 -> SU(3)^3 -> SM)
       |
Firewall selection rules       (9 forbidden triads out of 45)
       |
Standard Model                 (gauge group, 3 generations, Yukawa textures)
```

---

## W(3,3) Graph Parameters

| Parameter | Value | Meaning |
|-----------|-------|---------|
| v (vertices) | 40 | Isotropic points of PG(3,3) |
| k (degree) | 12 | Neighbors per vertex |
| lambda | 2 | Common neighbors (adjacent pair) |
| mu | 4 | Common neighbors (non-adjacent pair) |

**Eigenvalue spectrum:** {12^1, 2^24, (-4)^15}

| Eigenvalue | Multiplicity | Role in the theory |
|------------|--------------|---------------------|
| 12 | 1 | Unique vacuum (ground state) |
| 2 | 24 | First excited multiplet |
| -4 | 15 | Second band |

**Key invariants:**
- |Aut(W33)| = 51840 = |W(E6)| (Weyl group of E6)
- |Edges| = 240 = |Roots of E8|
- Spectral gap = 10 (Fiedler value of Laplacian)

---

## 69 Verified Theorems

The unified derivation (`tools/toe_unified_derivation.py`) proves these theorems:

### Part I: Algebraic Foundations (Thms 1-4)

| # | Theorem | Key Result |
|---|---------|------------|
| 1 | E8 root system | 240 roots, all norm^2 = 2 |
| 2 | W(E6) orbit decomposition | 240 = 72 + 6x27 + 6x1 |
| 3 | Schlafli graph | SRG(27,16,10,8) verified |
| 4 | Double-sixes | 36 double-sixes, S6 x Z2 stabilizer (1440) |

### Part II: Generations and Particle Content (Thms 5-7)

| # | Theorem | Key Result |
|---|---------|------------|
| 5 | Three generations | E8 -> E6 x SU(3): forced, not assumed |
| 6 | 27 = 6+6+15 decomposition | A-sector, B-sector, duad sector |
| 7 | Trinification | SU(3)\_C x SU(3)\_L x SU(3)\_R from S6 -> S3 x S3 |

### Part III: Gauge Geometry and Selection Rules (Thms 8-11)

| # | Theorem | Key Result |
|---|---------|------------|
| 8 | PG(3,2) gauge geometry | 15 points, 35 lines from duad sector |
| 9 | Weinberg angle | sin^2(theta\_W) = 3/8 at GUT scale |
| 10 | 45 cubic triads | Tritangent planes of cubic surface |
| 11 | Firewall partition | 9 forbidden triads, AG(2,3) quotient geometry |

### Part IV: Physical Predictions (Thms 12-19)

| # | Theorem | Key Result |
|---|---------|------------|
| 12 | 3-generation coupling atlas | 1620 total, 324 forbidden, 1296 allowed |
| 13 | Proton decay suppression | Lifetime enhanced ~1.56x by firewall |
| 14 | Spacetime from W(3,3) | 10 blocks x 4 states = 40 |
| 15 | Hypercharge quantization | Y = n/6 from Coxeter Z6 phase |
| 16 | Chevalley certificate | E6 Cartan + Serre relations in 27-rep |
| 17 | CKM mixing structure | Diagonal dominance from IP asymmetry |
| 18 | SM field decomposition | 27 = 16+10+1 under SO(10) |
| 19 | W(E6) equivariance | 45 triads form single orbit; 40 vacua |

### Part V: Quantitative GUT Physics (Thms 20-25)

| # | Theorem | Key Result |
|---|---------|------------|
| 20 | Gauge coupling unification | M\_GUT ~ 10^15.8 GeV with trinification |
| 21 | Yukawa texture | Firewall creates asymmetric up/down survival |
| 22 | Cabibbo angle structure | Geometric mixing ratio from IP matrix |
| 23 | Proton lifetime | tau\_p ~ 10^36.8 yr, consistent with Super-K |
| 24 | Dark matter candidate | D/Dbar exotic sector from 10 of SO(10) |
| 25 | Anomaly cancellation | Tr(Y) = Tr(Y^3) = 0 verified |

### Part VI: Structural Depth (Thms 26-30)

| # | Theorem | Key Result |
|---|---------|------------|
| 26 | N\_c = 3 forced | Double-six geometry requires 3 colors |
| 27 | B-L quantization | B-L in 1/3 units, anomaly-free |
| 28 | Neutrino seesaw | m\_nu ~ 0.005 eV from M\_GUT |
| 29 | Doublet-triplet splitting | 1.5x firewall asymmetry |
| 30 | Vacuum landscape | SRG(40,12,2,4) transition graph |

### Part VII: The Jacobi-or-Die Test (Thm 31)

| # | Theorem | Key Result |
|---|---------|------------|
| 31 | Z3-graded E8 Jacobi | 118,944 triples checked, 0 failures |

### Part VIII: Structural Completeness (Thms 32-35)

| # | Theorem | Key Result |
|---|---------|------------|
| 32 | Bracket surjectivity | [g1,g1]->g2, [g2,g2]->g1, [g1,g2]->g0 all surjective |
| 33 | E8 Dynkin recovery | Cartan matrix det=1, degree-3 branch node |
| 34 | Z3 cyclic fusion | Generation number conserved mod 3 |
| 35 | Qutrit Heisenberg | Firewall holonomy = commutator curvature |

### Part IX: Deep Structure (Thms 36-45)

| # | Theorem | Key Result |
|---|---------|------------|
| 36 | Killing form | kappa = 60\*I\_8, dual Coxeter g\*=30, E8 semisimple |
| 37 | 36 double-sixes | = 36 positive E6 root pairs (Schlafli 1858) |
| 38 | Sp(4,F3) construction | W(3,3) built from symplectic form ab initio |
| 39 | Kissing number | 240 = optimal in 8D (Viazovska 2016) |
| 40 | E6 Casimir | C\_2(27)=26/3, Dynkin index I(27)=3 |
| 41 | Exceptional Jordan algebra | dim J3(O) = 27 = E6 fundamental |
| 42 | AG(2,3) rewrite rules | 12 lines x 3 Z3 lifts = 36 allowed triads |
| 43 | E8 branching rule | 240 = 72 + 6 + 162 verified exactly |
| 44 | SM quantum numbers | Complete E6->SM branching, all anomalies cancel |
| 45 | Vacuum spectral gap | Gap=10, Fiedler=10, Ramanujan expander |

### Part X: The Discrete Root Engine (Thms 46-55)

| # | Theorem | Key Result |
|---|---------|------------|
| 46 | W33 self-duality | Line graph ≅ point graph ≅ SRG(40,12,2,4) |
| 47 | Coxeter A2 hexagons | 240 roots = 40 × 6 A2 hexagons from c^5 orbits |
| 48 | Circle closes | Coxeter orbit adjacency = SRG(40,12,2,4) = W33 |
| 49 | Z6 hexagon law | Inner product depends only on (p-q) mod 6 |
| 50 | Inter-orbit fusion | Coupled orbits bracket into exactly 2 orbits (2×6) |
| 51 | 3-type IP model | 780 orbit pairs: orthogonal (36,0,0) or coupled (12,12,12) |
| 52 | Exceptional chain | E8 ⊃ E7 ⊃ E6 ⊃ F4 ⊃ G2 with all branchings |
| 53 | W33 uniqueness | The ONLY self-dual GQ(3,3) (Payne-Thas 1984) |
| 54 | E8 fiber bundle | W33 base, A2 fibers, Z6 structure group |
| 55 | Grand Closure | W33 ↔ E8 ↔ SM is a complete mathematical equivalence |

### Part XI: Firewall as State-Space Law (Thms 56-59)

| # | Theorem | Key Result |
|---|---------|------------|
| 56 | Firewall superselection | 27 affine sections Lie-consistent under 36-triad filter |
| 57 | Section stabilizer | D4 ⊕ u(1)^2 (dim 30) inside E6 |
| 58 | D4 triality decomposition | 27 = 8 ⊕ 8 ⊕ 8 ⊕ 1 ⊕ 1 ⊕ 1 |
| 59 | 2-qutrit Pauli geometry | W33 = Pauli commutation graph, 36 spreads, MUBs |

### Part XII: The Coupling Atlas (Thms 60-69)

| # | Theorem | Key Result |
|---|---------|------------|
| 60 | AG(2,3) affine duality | 9 forbidden triads = AG(2,3), Z3 kernel, 4 parallel classes |
| 61 | Coupling census | 1620 total, 324 (20%) forbidden, uniform across 6 orbit pairs |
| 62 | Yukawa texture classification | 9 SM field-type classes, 2 fully safe channels |
| 63 | Affine interaction dictionary | 4 parallel classes × 3 lines × 108 couplings = 1296 allowed |
| 64 | Forbidden fraction hierarchy | Top Yukawa 33%, gauge 17%, lepton 50%, Higgs 0% |
| 65 | Color-singlet structure | All 9 triad types conserve SU(3)\_c |
| 66 | E6 weight-basis commutators | 5/15 nonzero, all match root operators (overlap=1.0) |
| 67 | Phase diagram alignment | Emergent charges match canonical E6 Cartan directions |
| 68 | Backbone vs coset | All commutators irreducibly mixed (D6 + coset entangled) |
| 69 | Grand coupling atlas | AG(2,3) × Z3 × SU(3)\_fam controls all 1620 couplings |

---

## What's New vs. Standard E6 GUTs

This framework differs from textbook E6 grand unification in several ways:

1. **E6 is derived, not postulated.** The gauge group emerges from Aut(W33) = W(E6).
2. **Three generations are forced.** E8 -> E6 x SU(3) requires exactly 3 copies of 27.
3. **N\_c = 3 is derived.** The double-six geometry admits only 3 colors.
4. **Firewall selection rules are new.** 9 of 45 cubic triads are forbidden --- this has
   no analogue in standard GUTs and constrains proton decay, Yukawa couplings, and
   doublet-triplet splitting.
5. **The vacuum landscape is geometric.** 40 vacua = 40 W(3,3) vertices, with
   SRG(40,12,2,4) transition graph and spectral gap = 10.
6. **Gauge-gravity duality.** The same group W(E6) = GSp(4,3) controls both the gauge
   sector (E6) and spacetime (W33).
7. **Quantum information structure.** The firewall quotient AG(2,3) is isomorphic to
   qutrit phase space, with holonomy = Heisenberg commutator curvature.
8. **Octonionic origin.** The 27-dimensional fundamental of E6 is the exceptional
   Jordan algebra J\_3(O), connecting the theory to octonions and the Freudenthal-Tits
   magic square.
9. **E8 Jacobi identity verified exhaustively.** 118,944 root triples, 0 failures.
10. **Circle closed --- both directions.** W33 -> E8 (via Coxeter embedding) AND
    E8 -> W33 (via Coxeter orbit adjacency). They are dual descriptions.
11. **W33 self-duality.** The line graph of W(3,3) is isomorphic to its point graph.
    This is the discrete analogue of electric-magnetic duality.
12. **E8 = fiber bundle over W33.** 40 A2 fibers over W33 with Z6 structure group.
    The Lie bracket is encoded by transition functions between fibers.
13. **W33 uniqueness (Payne-Thas 1984).** W(3,3) is the ONLY self-dual GQ with s=t=3.
    Combined with the bidirectional W33-E8 link, E8 is uniquely determined.
14. **Zero free parameters.** All of particle physics follows from a single integer: s=3.

---

## Quantitative Predictions

| # | Prediction | Value | Source |
|---|-----------|-------|--------|
| 1 | sin^2(theta\_W) at M\_GUT | 3/8 = 0.375 | Thm 9 |
| 2 | Number of generations | 3 (exact) | Thm 5 |
| 3 | Proton lifetime | ~10^36.8 yr | Thm 23 |
| 4 | M\_GUT (trinification) | ~10^15.8 GeV | Thm 20 |
| 5 | Hypercharge quantization | Y = n/6 | Thm 15 |
| 6 | Number of colors | 3 (exact) | Thm 26 |
| 7 | B-L quantization | 1/3 units | Thm 27 |
| 8 | Neutrino mass scale | ~0.005 eV | Thm 28 |
| 9 | Number of vacua | 40 | Thm 30 |
| 10 | Dual Coxeter number | g\*=30 | Thm 36 |
| 11 | Double-sixes | 36 | Thm 37 |
| 12 | Kissing number (8D) | 240 | Thm 39 |
| 13 | E6 Casimir C\_2(27) | 26/3 | Thm 40 |
| 14 | Spectral gap | 10 | Thm 45 |
| 15 | W33 self-duality | line graph ≅ point graph | Thm 46 |
| 16 | A2 hexagons | 40 (from c^5 orbits) | Thm 47 |
| 17 | Circle closes | orbit adj = W33 | Thm 48 |
| 18 | Free parameters | 0 | Thm 53, 55 |
| 19 | Firewall superselection | 27 affine sections on 3^9 total | Thm 56 |
| 20 | Section stabilizer | D4 ⊕ u(1)^2 (dim 30) | Thm 57 |
| 21 | D4 triality | 27 = 8+8+8+1+1+1 | Thm 58 |
| 22 | W33 spreads | 36 (= MUB sets for 2-qutrit) | Thm 59 |
| 23 | AG(2,3) parallel classes | 4 | Thm 60 |
| 24 | Total cubic couplings | 1620 = 45 × 36 | Thm 61 |
| 25 | Forbidden couplings | 324 (20% exactly) | Thm 61 |
| 26 | Yukawa texture classes | 9 distinct SM types | Thm 62 |
| 27 | Safe Higgs channel | H\_d H\_u S: 0% forbidden | Thm 64 |
| 28 | Top Yukawa suppression | H\_u Q u^c: 33% forbidden | Thm 64 |
| 29 | All couplings color-singlet | verified all 9 types | Thm 65 |
| 30 | E6 commutators matched | 5/15 nonzero, overlap=1.0 | Thm 66 |
| 31 | Backbone+coset entangled | All irreducibly mixed | Thm 68 |

---

## Running the Derivation

```bash
# Create virtual environment and install dependencies
python -m venv .venv_test
.venv_test/Scripts/pip install numpy   # Windows
# .venv_test/bin/pip install numpy     # Linux/macOS

# Run all 69 theorems (takes ~15 minutes due to exhaustive Jacobi check)
.venv_test/Scripts/python -X utf8 tools/toe_unified_derivation.py

# Run tests
.venv_test/Scripts/python -m pytest tests/ -q
```

Output is saved to `artifacts/toe_unified_derivation.json`.

---

## Repository Structure

```
tools/
  toe_unified_derivation.py     # Main deliverable: 69 theorems
  compute_double_sixes.py       # E8 root construction + W(E6) orbits
  e8_lattice_cocycle.py         # Deterministic cocycle for structure constants
  e8_e6_a2_fusion.py            # E8 -> E6 + A2 decomposition
  verify_e8_jacobi_cocycle.py   # Jacobi identity random sampling
  solve_canonical_su3_gauge_and_cubic.py  # SU(3) gauge + cubic invariant
  chevalley_normalize_e6_from_basis_export.py  # E6 Chevalley basis
  ... (70+ additional analysis tools)

artifacts/
  toe_unified_derivation.json   # Machine-readable theorem results
  canonical_su3_gauge_and_cubic.json  # SU(3) gauge data
  e6_basis_export_chevalley_27rep.json  # E6 basis certificate
  e6_cubic_tensor_from_e8.json  # Cubic invariant from E8

tests/
  test_toe_new_results.py       # Core theorem verification tests
  test_e8_roots.py              # E8 root system tests
  test_schlafli_graph.py        # Schlafli graph SRG tests
  ... (25+ test files)

More New Work/                  # Incremental analysis bundles (ChatGPT)
```

---

## Theoretical Background

### The W(3,3) Generalized Quadrangle

W(3,3) is the symplectic generalized quadrangle of order (3,3). It arises as the
incidence geometry of totally isotropic subspaces of a 4-dimensional symplectic
space over F\_3. Its collinearity graph is the unique strongly regular graph with
parameters (40, 12, 2, 4).

### The E8 Connection

The 240 edges of the W(3,3) collinearity graph correspond to the 240 roots of the
E8 root system. The automorphism group Aut(W33) = GSp(4,3) is isomorphic to the
Weyl group W(E6), which is a subgroup of W(E8). This gives a natural embedding of
the W(3,3) combinatorics into the E8 Lie algebra.

### The 27 Lines on a Cubic Surface

Under W(E6), the 240 E8 roots decompose as 72 + 6x27 + 6x1. Each 27-element orbit
forms the Schlafli graph SRG(27,16,10,8) --- the intersection graph of the 27 lines
on a general cubic surface. The 6 copies paired by SU(3) weights give 3 generations
of matter (27 + 27-bar).

### The Firewall

Among the 45 cubic triads (tritangent planes of the cubic surface), exactly 9 form
a vertex-disjoint partition of the 27 vertices. This "firewall" partition defines
selection rules that forbid certain Yukawa couplings, creating asymmetric textures
that seed the fermion mass hierarchy.

### The Octonionic Connection

The 27-dimensional fundamental representation of E6 is isomorphic to the exceptional
Jordan algebra J\_3(O) of 3x3 Hermitian matrices over the octonions. The cubic
invariant det(X) on J\_3(O) corresponds to the E6 cubic form, whose 45 terms are
our 45 tritangent planes. This places the theory within the Freudenthal-Tits magic
square: E6 = L(C, O), E7 = L(H, O), E8 = L(O, O).

---

## References

1. Coxeter, H.S.M. - "The polytope 2\_21"
2. Conway & Sloane - "Sphere Packings, Lattices and Groups"
3. Baez, J.C. - "The Octonions" (Bull. AMS, 2002)
4. Particle Data Group (2024) - Review of Particle Physics
5. Viazovska, M. - "The sphere packing problem in dimension 8" (Annals of Math, 2017)
6. Payne & Thas - "Finite Generalized Quadrangles" (2nd ed.)
7. Adams, J.F. - "Lectures on Exceptional Lie Groups"

---

## Developer Notes

- Use `utils.json_safe.dump_json` to write result files (handles Sage/numpy types).
- Quick checks:
  - Run `make check-json` to validate JSON serialization policy.
  - CI workflow `json-serialization-check` runs `tests/test_json_serialization.py`.
- Verification digest:
  - `python3 tools/build_verification_digest.py`
  - Outputs `artifacts/verification_digest.md` and `artifacts/verification_digest.json`.
- Running tests locally:
  - **Windows:** `scripts\run_local_tests.bat` or `.venv_test\Scripts\python -m pytest tests/ -q`
  - **Unix/macOS:** `./scripts/generate_summary.sh` or `.venv_test/bin/python -m pytest tests/ -q`

---

## License

MIT License - Academic and educational use.

---

## Contact

**Wil Dahn**
GitHub: [@wilcompute](https://github.com/wilcompute)
Repository: [W33-Theory](https://github.com/wilcompute/W33-Theory)
