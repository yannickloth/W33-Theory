# W33 480 Spectral Action → Alpha Closure (v02)

This bundle pushes the TOE work **one notch closer to a derivation** by
removing a key “why this denominator?” mystery in the α formula.

## What you get

1) A *forced* 480-state transport layer (directed edges) with the non-backtracking operator B.
2) A verified Ihara–Bass reduction that explains why (k−1) is canonical.
3) A canonical regulated vertex propagator M that makes the α fractional term **exactly**
   the constant-mode susceptibility 1ᵀM^{-1}1.
4) A clean identity showing the **137 integer part** is a norm-square in W33:
   k² − 2μ + 1 = (k−1)² + μ² = 11² + 4² (unique to s=t=3).

## Files

- `build_w33_core.py`
  - Constructs W33 in its symplectic GF(3) model, plus edges, directed edges, lines, and B.
- `ihara_bass_and_M_bridge.py`
  - Verifies Ihara–Bass numerically; shows the M operator and the exact 40/1111 identity;
    connects M to the Ihara vertex factor Q(u) at a specific complex fugacity u.
- `spectral_action_one_loop.py`
  - Shows the Gaussian integral derivation of 1ᵀM^{-1}1, and the norm-square identity for 137.
- `DERIVATION_ALPHA_FROM_480.md`
  - Human-readable derivation writeup.

## Run

```bash
python ihara_bass_and_M_bridge.py
python spectral_action_one_loop.py
```
