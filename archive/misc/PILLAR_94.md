# Pillar 94: Correlating N with Heisenberg Coordinates

The regular subgroup \(N\subset\Gamma\) obtained in Pillar 93 comes with a
canonical labelling of the 192 tomotope flags: the element of \(N\) assigned
to a flag is the unique element sending the base flag (chosen as 0) to that
flag.  The 270‑edge transport data of Pillar 89 assign to each qid a triple
\((x,y,z)\in\mathbb Z_3^3\) which we regard as the Heisenberg coordinate of
the corresponding pocket and hence of the flag occupying that pocket.  By
composing these two bijections we obtain a map
\(\delta:N\to\mathbb Z_3^3\) given by

\[
\delta(n)=\mathrm{coords}(n\cdot0)-\mathrm{coords}(0)\in\mathbb Z_3^3.
\]

The script `THEORY_PART_CXCV_CORRELATE_N_HEIS.py` performs the following
computations:

* reads `edges_270_transport.csv` to build the qid→coordinate table (27
distinct Heisenberg points);
* reads `K54_54sheet_coords.csv` to map canonical flags to qids;
* loads `N_subgroup.json` and `N_flag_map.json` from Pillar 93;
* tabulates the delta vector associated to every element of \(N\);
* counts occurrences of each triple (there are exactly 27, matching the qid
  set);
* examines the failure of \(\delta\) to be a group homomorphism and verifies
  that mismatches always lie in the central \(\{0\}\times\{0\}\times\mathbb Z_3\)
  subgroup, as expected for a Heisenberg cocycle.

The produced summary file (`N_heis_correlation_summary.json`) includes
statistics on the delta distribution and a small sample of cocycle mismatches;
the accompanying report simply dumps the JSON for human reading.  The
associated tests re‑compute the data and assert the key facts above.

## Consequences

- We now have an explicit realisation of the translation part of the
  Heisenberg group inside \(\Gamma\): the map \(N\to\mathbb Z_3^3\) is a
  surjection whose kernel is a central subgroup of order \(192/27=\) not an
  integer, but its failure to be a homomorphism is exactly a central 2‑cocycle.
- Together with Pillar 92 this demonstrates that the full symmetry group
  contains a copy of the Heisenberg extension of \(\mathbb F_3^2\) by Z3,
  providing a natural algebraic bridge to the constructions in Section …
  (future text).
- Practically, computations on \(N\) may now be interpreted as translations in
  Heisenberg space; this greatly simplifies reasoning about the 270‑edge
  transport law and will be used in the next pillars when analysing the
  remaining bundles.

Further work could try to identify a specific generating pair of
\(N\) whose delta vectors correspond to the standard basis of F3² together
with a central lift, making the Heisenberg presentation fully concrete.
