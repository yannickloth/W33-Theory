# Conjugacy certificate: WE6_true-even coset action ↔ PSp(4,3) line normal form
This bundle contains an explicit conjugator σ ∈ S₄₀ such that for each generator g in the WE6 coset action,
    σ ∘ g ∘ σ^{-1} ∈ ⟨PSp(4,3) line generators⟩.

## Rare elements used to pin down σ
- Chosen element a12 in WE6 coset action: order 12, cycle type 2^2 6^2 12^2
- Chosen element a9  in WE6 coset action: order 9, cycle type 1 3 9^4
- Matched element b12 in PSp line action: order 12, cycle type 2^2 6^2 12^2
- Matched element b9  in PSp line action: order 9, cycle type 1 3 9^4

Pair invariants (must match for a viable pairing):
- ord_p: A=12  B=12
- ord_q: A=9  B=9
- ord_pq: A=9  B=9
- ord_comm: A=9  B=9

## Verification
Run `python verify_conjugacy.py` to check σ conjugates all 10 WE6 coset generators into the PSp line group.
