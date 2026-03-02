# CE2 ⇄ Weil bridge via point-parabolic in Ω(5,3) and the outer spinor-norm twist

## What we proved computationally
- Ω(5,3) (order 25920) acts transitively on the 40 projective points of PG(3,3).
- The stabilizer of a point has order 648.
- Inside this stabilizer there is a **normal Heisenberg 3-group U** of order 27 with center Z of order 3.
- The quotient action on U/Z is exactly SL(2,3) (24 elements).
- We located explicit elements inducing the CE2 generator matrices:
  - S = [[0,2],[1,0]]
  - T = [[1,0],[1,1]]

## Recovering the CE2 μ cochain directly from conjugation
For each n in the stabilizer, conjugation sends (a,b,c) -> (A(a,b), c + μ_n(a,b)).
We recovered μ for the above S and T and solved the unique gauge correction:
- scale center by s=2 and add linear coboundary l(a,b)=2a,
giving canonical μ_S(a,b)=2ab and μ_T(a,b)=2a^2 (mod 3).

## The outer twist and χ(2) = -1
We constructed an element n = h^{-1} g_out that normalizes the point stabilizer but lies outside Ω (spinor class 2).
Its induced action on U/Z is a GL(2,3) matrix with det = 2 (= -1), so the quadratic character gives χ(det)=χ(2)=-1.
This is the exact origin of the extra ± sign when you extend from SL(2,3) to the full similitude/outer coset.

Run `python verify_bridge.py` to re-check all invariants.
