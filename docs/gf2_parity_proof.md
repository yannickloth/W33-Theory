# GF(2) parity proof (compact)

This short note formalizes the computational certificate into a succinct proof.

Definitions
- Let A ∈ GF(2)^{27×36} be the incidence matrix whose columns are the 36 affine E6 triads (each column has three 1s corresponding to the triad's node indices 0..26).
- Let d ∈ GF(2)^{36} be the D_BITS vector (1 for sign −1, 0 for +1) as in `artifacts/e6_cubic_sign_gauge_solution.json`.

Claim
There exists v ∈ GF(2)^{36} such that A v = 0 and d · v = 1 (mod 2). Concretely, v can be taken as the indicator vector of the 10 triads:

T = { [0,18,25], [0,20,23], [3,10,25], [3,13,23], [5,12,22], [5,16,18], [8,9,22], [8,10,20], [9,16,17], [12,13,17] }.

Proof (computational step, short):
1) Compute node parity: sum_{t in T} column_t(A) = 0 in GF(2) (XOR of the 10 columns is zero).  (See `tools/generate_gf2_certificate.py`.)
2) Compute d parity: sum_{t in T} d_t = 1 in GF(2) (the D_BITS sum is odd).

Combining (1) and (2) yields 0 = 1 in GF(2), a contradiction. Therefore any mapping that matches all triads in T cannot be sign-consistent.

Remarks
- The computation is reproducible; scripts and artifacts referenced above contain the explicit arrays and JSON artifacts.
- The obstruction is local: enumerating nullspace vectors up to small weight reveals that every odd-parity null vector contains triad (0,20,23), yielding a canonical forbid.

QED
