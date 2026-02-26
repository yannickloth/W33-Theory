# Test C — CE2 tables from one normal-form law (executed)

This run was executed **inside the attached `W33-Theory-master (4).zip` repo**.

## 0) Unblocked the pipeline (no Sage)
The repo’s `tools/verify_e6_cubic_affine_heisenberg_model.py` expects:
- `artifacts/sage_h27_to_schlafli_effective_triads_conjugacy.json`
- `artifacts/firewall_bad_triads_mapping.json`

Both were missing in the zip, so I rebuilt them from repo-native artifacts/tools:

1. **H27 ↔ Schläfli mapping** (no Sage):  
   `tools/build_schlafli_e6id_to_w33_h27_mapping.py` → `artifacts/schlafli_e6id_to_w33_h27.json`  
   Inverted `maps.e6id_to_h27local` to produce `h27_local_to_schlafli_e6id` and wrote the expected file.

2. **WE6 signed action + channel dictionary + selection rules**:  
   - `tools/export_we6_signed_action_on_27.py`  
   - `tools/build_channel_dictionary_from_we6_generators.py`  
   - `tools/generate_selection_rules_report.py`

3. **Firewall bad triads mapping**:  
   `tools/map_firewall_bad_triangles_to_cubic_triads.py` → `artifacts/firewall_bad_triads_mapping.json`

4. **E6 cubic affine Heisenberg model**:
   - `tools/solve_canonical_su3_gauge_and_cubic.py`
   - `tools/verify_e6_cubic_affine_heisenberg_model.py`  
   → `artifacts/e6_cubic_affine_heisenberg_model.json`

## 1) CE2 closed-form validity (all 864 keys)
Using `scripts/ce2_global_cocycle.py`:
- loaded `committed_artifacts/ce2_simple_family_sign_map.json` (864 triples)
- loaded the generated `artifacts/e6_cubic_affine_heisenberg_model.json`
- verified that the closed-form rule (constant-line branch + metaplectic/Weil branch) is consistent with the sign-map invariants.

## 2) Tables are *constraints*, not magic
From the sign map + Heisenberg coords, for each (t,d,s,w) we computed:
- either **constant-line**: sign independent of z-data, or
- variable: fitted unique `(eps,c0)` satisfying `sign = eps * chi(zm+zo+c0)`.

Then we checked:

- For every `(t,d)` and every variable `(s,w)`, the committed polynomial  
  `_SIMPLE_FAMILY_WEIL_C0_COEFF[t][d]` evaluates to the fitted `c0(s,w)`.

- For every `(t,d)` and every variable `(s,w)`, the committed polynomial  
  `_SIMPLE_FAMILY_WEIL_E_COEFF[t][d]` satisfies `chi(e(s,w)) = eps(s,w)`.

**Result:** all constraints are satisfied; mismatches = 0.

## 3) Non-uniqueness at constant-line points (important)
On constant-line points, `c0(s,w)` is not determined (because the sign no longer depends on `zm+zo+c0`).  
So `c0` and `e` polynomials are only determined **up to adding** polynomials that vanish on the variable locus.

Your repo’s tables correspond to a consistent canonical gauge choice (fixed by the fit scripts), and the checks above confirm they match the empirical constraints *exactly*.

---

**Artifacts generated in this run:**
- `artifacts/sage_h27_to_schlafli_effective_triads_conjugacy.json` (Python-derived)
- `artifacts/we6_signed_action_on_27.json`
- `artifacts/we6_channel_dictionary.json`
- `artifacts/selection_rules_report.json` (+ `.md`)
- `artifacts/firewall_bad_triads_mapping.json` (+ `.md`)
- `artifacts/e6_cubic_affine_heisenberg_model.json` (+ `.md`)
