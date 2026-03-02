# G2 / Clifford paper bridge (and what to test next)

Your repo already logged a Google Scholar synthesis that cites:

> **Wilmot (arXiv:2505.06011, May 2025)**  
> *"Construction of exceptional Lie algebra G2 and non-associative algebras using Clifford algebra"*  
> Key quote recorded there: *"The 4-form calibration terms of Spin(7) are related to an ideal with three idempotents and provides a direct construction of G2 for each of the 480 representations of the octonions."*  
> It also highlights the numerology **728 = 480 + 248** and **728 = 14 × 52 = dim(G2)×dim(F4)**.

(See `docs/archive/GOOGLE_SCHOLAR_FEB2026.md` in the W33-Theory repo.)

## What we *already have* that matches this structure

1) **Three idempotents / triple structure**  
Our explicit WE6-even ↔ W33 bridge maps each W33 edge to an **oriented triple of E6 antipode-pairs**.
That is literally a “3-idempotent packet” stabilized by an index-2 character (the Z2 flip cocycle).

2) **480 showing up naturally**
- W33 has **240** isotropic edges.
- If you orient each edge (u→v vs v→u) you get **480** oriented edges.
This matches the “480 octonion representations” count recorded in the repo synthesis.

3) **Spin(7)/calibration ↔ constant face curvature**
On the derived SRG(36,20,10,12) triangle complex, the Z2 “curvature” is **constant on faces**
(when you pull back orientation from the 240 cover). This is exactly the kind of “calibration-like”
uniform cochain you’d expect to be the discrete shadow of a continuous calibration form.

## The next concrete tests to link our discrete algebra to G2

### Test A: Build a non-associative algebra from the triangle presentation
Let the 36 antipode-pairs be basis elements e_i.
For adjacent i~j, define a product e_i * e_j = ± e_k where {i,j,k} is the unique decomposition triangle containing edge (i,j),
and the sign is taken from a consistent local orientation lifted from the 240 cover.
For nonadjacent pairs define product 0 (or leave undefined and study the partial magma).

Then compute:
- associator distribution ( (x*y)*z + x*(y*z) over GF(2) or over Z )
- automorphism group of the multiplication table
- derivations (linear maps D with D(x*y)=D(x)*y+x*D(y))

If a 7-dimensional subalgebra closes and the derivations are 14-dimensional, you've hit a genuine G2 signature.

### Test B: Find “octonion pockets” (7-element closures) in the 36-vertex partial product
We already proved the SRG clique number is 5, so you won’t get a literal Fano STS(7) as a subdesign on vertices.
But you *can* look for 7-element sets closed under the **partial** product induced by adjacent pairs.
That’s the right discrete analogue of “octonion pockets” inside larger nonassociative algebras.

### Test C: 728 = 480 + 248 as an *operator-level* decomposition
Interpret:
- **480** = oriented edge space (W33 / E6-pair transport sector)
- **248** = adjoint E8 sector (your root/holonomy/Bargmann invariants sector)

Then test whether the combined operator algebra on these two sectors closes to a 728-dim algebra
(with a natural G2×F4 grading suggested by 14×52).

I’ve left stubs for these tests in the next bundle we’ll produce (see below).

