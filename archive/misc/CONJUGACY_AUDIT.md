# Conjugacy Audit: Edgepair vs E6×A2‑graded Line Actions

This note documents a pure-Python verification of the impossibility of a
single `S_{120}` conjugator between the two 120‑point permutation
representations of \(PSp(4,3)\) that appear in the repository.

## Representations under consideration

1. **edgepair action** – generators read from
   `artifacts/sp43_edgepair_generators.json`.  The resulting group is
   transitive on 120 points and has order 25920.

2. **E6×A2‑graded line action** – generators read from
   `SP43_TO_WE6_TRUE_FIXED_BUNDLE_v01_2026-02-25/sp43_line_perms_fixed.json`.
   This action is *not* transitive: its orbit sizes are
   \([36,27,27,27,1,1,1]\), reflecting the decomposition of E₈ lines under
the \(E_6	imes A_2\) subgroup.  The full group also has order 25920.

## Invariants computed

The following invariants were extracted for both actions and are saved in
`action_conjugacy_obstruction.json`.

* Group order (same in both cases).
* Element‑order spectrum (identical).
* For each order, the multiset of fixed-point counts of elements of that
  order.
* Orbit decompositions of the two actions.

## Obstruction to conjugacy

Although the spectra agree, the fixed-point distributions differ for order‑5
elements:

* **edgepair:** every order‑5 element fixes **0 points** (24 disjoint
  5‑cycles).
* **line action:** every order‑5 element fixes **10 points** along with
  22 5‑cycles and the remaining points broken into orbits of length 5.

Fixed-point counts are invariant under conjugation in the symmetric group, so
no element of \(S_{120}\) can map one action to the other.  This provides a
rigid, group-theoretic obstruction: there is *no* 120‑point permutation that
conjugates the two representations.

## Consequences

* The search for a single explicit conjugator between these two specific
  actions is futile; any such conjugator would have to map a transitive
  representation to an intransitive one, which is impossible.
* If a conjugator is still desired, one must choose a different pair of
  120‑actions (for example, two transitive coset actions arising from
  different index‑120 subgroups).

## Contents of this bundle

* `action_conjugacy_obstruction.json` – machine readable data used in the
  analysis.
* `tools_pure_python_conjugacy_audit_template.py` – a python template that
  reproduces the computations performed here; drop-in replacement for earlier
  Sage/GAP methods.

(See `REPORT.md` inside the WE6_TRUE_FIXED bundle for the corresponding
Sage computation that hinted at this obstruction.)

---
*Generated 2026‑02‑27 by automated audit tools.*
