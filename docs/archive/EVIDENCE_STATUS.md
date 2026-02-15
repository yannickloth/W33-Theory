# Evidence Status (Math Certificates vs. Phenomenology)

This repo mixes two kinds of work:

1. **Mathematical / computational certificates**: reproducible statements about finite geometry, Lie data, and algebraic identities that can be re-run from repo artifacts.
2. **Phenomenology / interpretation**: mappings from the discrete structures to Standard Model parameters and physical constants. These may include **hard-coded experimental values** and **ad-hoc correction factors** and should be treated as exploratory unless separately derived.

This file is a “truth table” to keep the project honest while still moving fast.

---

## A. High-confidence certificates (reproducible)

### W33 / finite-geometry layer
- `tools/compute_double_sixes.py` → `artifacts/double_six_results.json`
  - E8 has 240 roots.
  - Coxeter `c^5` partitions 240 roots into 40 orbits of size 6 (W33 vertices).
  - W(E6) orbit split: `72 + 6×27 + 6×1`.
  - Each 27-orbit induces a Schläfli graph SRG(27,16,10,8) and contains 36 double-sixes.
- `tools/verify_toe_bridge.py` → `artifacts/toe_bridge_verification.json`
  - Builds W33 from `F3^4` and verifies SRG structure and line structure.
  - Verifies the “firewall split” on `H27`: non-orth pairs `243 = 27 (bad) + 216 (kernel)`.
- `tools/compute_w33_incidence_code_ranks.py` → `artifacts/w33_incidence_code_ranks.json/.md`
  - Computes the rank of the 40×40 point-line incidence matrix over GF(2) and GF(3).
  - Current certificate: `rank = 25`, so `k = 15` in both characteristics; GF(2) code has `d_min = 8`.
- `tools/verify_w33_two_qutrit_pauli_geometry.py` → `artifacts/w33_two_qutrit_pauli_geometry.json/.md`
  - Identifies W(3,3) with the commutation geometry of the **2-qutrit** Pauli group (dim 9).
  - Verifies `SRG(40,12,2,4)` from symplectic orthogonality, and commutation ⇔ orthogonality under the Pauli mapping.
  - Verifies 40 lines (size 4), 36 spreads (10 disjoint lines covering all points), and a stabilizer MUB certificate on one spread (max overlap deviation ~ `1e-15`).

### E6 (27-rep) algebra layer
- `artifacts/e6_basis_export_chevalley_27rep.json`
  - Certified Cartan recovery and Dynkin type `E6`, root decomposition, and Serre checks (within tolerance).
- `artifacts/e6_27rep_basis_export/E6_basis_78.npy`, `artifacts/e6_27rep_basis_export/Cartan_mats.npy`
  - Concrete 27×27 matrix basis for the 78-dim algebra and a commuting rank-6 Cartan.

### Z3-graded E8 bracket layer (trinification)
- `tools/toe_e8_z3graded_bracket_jacobi.py`
  - Implements the Z3-graded bracket and checks Jacobi for the **full 45-triad** cubic.
- `tools/test_gauge_covariance_firewall.py`
  - Confirms `g0 = e6 ⊕ sl3` acts by derivations on the **full** 45-triad bracket, and fails after deleting the 9 fiber triads.

### Firewall: “delete 9 fiber triads” is not Lie globally
- `tools/compute_firewall_jacobiator_tensor.py` → `artifacts/firewall_jacobiator_tensor.json/.md`
  - Computes the Jacobiator structure after deleting the 9 fiber triads.
- `tools/diagnose_mixed_grade_homotopy.py`
  - Shows which grade-combinations require the missing triads to restore Jacobi.

### Firewall: superselection resolution (affine section sectors)
- `tools/verify_firewall_filtered_trinification_section_sectors.py`
  → `artifacts/firewall_filtered_trinification_section_sectors.json/.md`
  - Among all `3^9 = 19683` “one-per-fiber” sections, exactly **27** are closed and Jacobi-consistent under the **36-triad filtered** bracket.
  - These 27 are exactly the graphs of affine maps `z(x,y)=ax+by+c` over `F3`.
- `tools/sage_verify_firewall_affine_sections.py` → `artifacts/sage_firewall_affine_sections.json/.md`
  - Sage (Docker) cross-check of the same 27 affine sections.

### Symmetry breaking on an affine sector
- `tools/verify_e6_affine_section_stabilizer_d4_u1u1.py`
  → `artifacts/e6_affine_section_stabilizer_d4_u1u1.json/.md`
  - Stabilizer inside `e6` of an affine sector has dim **30**, derived dim **28**, center dim **2** ⇒ `D4 ⊕ u(1)^2`.
- `tools/verify_e6_affine_section_d4_triality_decomposition.py`
  → `artifacts/e6_affine_section_d4_triality_decomposition.json/.md`
  - Under that stabilizer, `27 = 8 ⊕ 8 ⊕ 8 ⊕ 1 ⊕ 1 ⊕ 1` (triality pattern).

### Unified derivation artifact (now includes firewall superselection)
- `tools/toe_unified_derivation.py` → `artifacts/toe_unified_derivation.json`
  - Contains 59 theorem blocks; the last four include the affine-sector firewall certificates and the 2-qutrit Pauli/MUB certificate.

---

## B. Exploratory / phenomenology (needs separate derivations)

Many “parameter-free prediction” scripts hard-code experimental numbers, include correction factors, or choose O(1) coefficients.

To avoid arguing by vibe, run:
- `python3 tools/audit_prediction_scripts.py` → `artifacts/prediction_script_audit.md`

That audit flags (mechanically):
- scripts that mention “Experimental”,
- scripts containing common physical-constant literals (e.g., `246`, `1.22e19`, `137.036`, `0.1179`),
- scripts containing “correction factor” / “fit” / “calibrate” language.

**Rule of thumb:** treat these as *hypothesis generators*, not proofs, until they can be re-derived from the certified algebra/geometry without importing experimental constants.

---

## C. Immediate next “breakthrough-grade” tasks

1. **Make firewall physics precise**: decide whether the firewall is best modeled as
   - a global L∞-style higher bracket (complete the mixed-grade homotopy story), or
   - a state-space law (superselection to the 27 affine sectors), or both.
2. **Connect sectors to dynamics**: compute how the 27 affine sectors transform under the relevant symmetry groups (e.g., `W(E6)` action), and whether sector-to-sector transitions match any physical selection rule.
3. **Upgrade quantum-info claims into certificates**: if “qutrit code on W33” is a claim, compute actual code parameters (rank/distance) over `F3` and write artifacts (no narrative-only results).
