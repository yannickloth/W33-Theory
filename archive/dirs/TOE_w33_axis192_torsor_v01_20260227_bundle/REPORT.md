TOE — W33 axis-fixed 192 torsor aligned to Wilmot stabilizer

This bundle constructs, from your W33-derived 7-pocket constraints, the explicit
set of axis-fixed completion embeddings of size 192 and proves (computationally)
that it is a *free transitive torsor* for the octonion axis-line stabilizer of size 192
inside the signed-permutation stabilizer of size 1344.

Key inputs (extracted from your uploaded bundles)
- SRG36 oriented triangles from:
  TOE_holonomy_Z2_flatZ3_v01_20260227_bundle.zip
    • TOE_edge_to_oriented_rootpairs_v01_20260227_bundle.zip
    • TOE_E6pair_SRG_triangle_decomp_v01_20260227_bundle.zip
- Octonion stabilizer (size 1344) from:
  TOE_pocket_transport_glue_orbit480_v01_20260227_bundle.zip
    • octonion_stabilizer_1344.json
  (built from the canonical Fano triples used in recompute_octonion_orbit_480.py):
    [(1, 2, 3), (1, 4, 5), (1, 7, 6), (2, 4, 6), (2, 5, 7), (3, 4, 7), (3, 6, 5)]

What we compute
1) Build the SRG36 multiplication table (720 oriented products) from the 120 oriented triangle blocks.
2) Restrict to your base pocket (vertices):
   [0, 1, 2, 14, 15, 17, 27]
   This yields exactly 24 internal constraints of the form:
     v_x · v_y = ± v_z.
3) Solve the completion-to-octonion embedding problem:
   Unknowns:
     • φ : local labels {0..6} → imag units {1..7}  (a permutation)
     • bits : local signs (7 bits)
   Constraints:
     • oct_mul(φ[x],φ[y]) has output φ[z]
     • sign parity matches the pocket sign

Results (matches your hammer bundle counts)
- φ solutions: 168
- total (φ,bits) embedding solutions: 2688
- these split into exactly 2 induced local multiplication tables (enc0, enc1),
  each with 1344 embeddings.

Axis-fixed 192 and the stabilizer alignment
- Fix the pocket silent vertex (local index 6) to map to axis unit 7:
    φ[6] = 7
  For each induced table class, this slice has size 192 (= 1344 / 7).

- From octonion_stabilizer_1344.json, define the axis-line stabilizer subgroup:
    H = { g in stabilizer : g sends unit 7 → ± unit 7 }
  In the file’s representation, this is exactly:
    perm[6] == 7
  and |H| = 192.

Main torsor statement (verified)
For each table class (enc0 and enc1):
- Let E be the 192 embeddings with φ[6]=7 in that class.
- Let H be the 192 axis-line stabilizer elements.
- Pick any base embedding e0 ∈ E.
Then the action:
    (perm,signs) ⋅ (φ,bits)  =  (perm∘φ,  bits ⊕ sign-flips-on-φ)
is free and transitive:
    H·e0 = E, and the map H → E is a bijection.

Files
- SUMMARY.json
- local_table_encodings.json              (the two induced tables enc0/enc1)
- embeddings_enc0_1344.csv                (all embeddings for table class enc0)
- embeddings_enc1_1344.csv
- axis_fixed_enc0_192.csv                 (the axis-fixed slice φ[6]=7)
- axis_fixed_enc1_192.csv
- axis_line_stabilizer_192.json           (the subgroup H ⊂ stabilizer_1344)
- torsor_enc0_axis7_192.json              (explicit bijection stab_index ↔ embedding)
- torsor_enc1_axis7_192.json
- recompute_w33_axis192_torsor.py         (end-to-end recompute)

Interpretation / why this matters for the weld
This is the cleanest possible meaning of your identity:

    192 = 1344 / 7

The W33 pocket completion problem does not merely “match counts” — it reconstructs
a canonical 192-object *torsor* that is literally the axis-line stabilizer of the
octonion table under signed permutations.

This gives a rigid coordinate system you can now transport:
- across pockets (via overlap gluing),
- across Sp/PSp lifts (the central Z2 deck),
- and ultimately into the 480 orbit classification.


Bonus: we extracted an explicit bridge from pocket symmetries → octonion axis stabilizer
-----------------------------------------------------------------

Inside PSp(4,3) acting on SRG36, the *set stabilizer* of the base pocket has size 48,
but only 6 elements preserve the *oriented pocket multiplication* exactly (no cocycle needed).
(This is the “stabilizer_size = 6” you saw in the hammer bundle.)

Those 6 elements induce only 3 distinct permutations σ of the 7 local labels (a C3 action fixing the silent index 6),
and—crucially—using the 192 torsor coordinate we can identify the corresponding octonion automorphisms:

  σ = identity                 ↔  r = identity  (stab_index 7)
  σ = (1 3 0)(2 5 4) on locals  ↔  r in H of order 3 (stab_index 399)
  σ = (3 0 1)(4 2 5) on locals  ↔  r in H of order 3 (stab_index 246)

This is the first *explicit* “W33 pocket symmetry → signed-permutation octonion symmetry” map we’ve extracted.

Files:
  pocket_mult_stabilizer_PSp43_size6.json
  pocket_mult_stabilizer_to_octonion_axis192.json
