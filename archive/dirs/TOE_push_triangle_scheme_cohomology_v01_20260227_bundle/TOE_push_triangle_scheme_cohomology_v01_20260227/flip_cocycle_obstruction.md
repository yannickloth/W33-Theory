# Z2 flip cocycle on the 120-block action: obstruction + interpretation

From `edgepair_transport_D6.csv` we have, for each generator g_i and block x:

- image block y = g_i(x)
- flip bit f_i(x) in Z2, describing how the canonical 2-lift (240 edges) twists over the 120-block base.

A global gauge would be a function s(x)∈Z2 such that:
    f_i(x) = s(x) ⊕ s(g_i(x))
for all i,x.

This is equivalent to requiring every cycle in the Schreier graph have zero Z2 holonomy.

We solve the constraints and find they are **inconsistent** (nontrivial Z2 curvature already on 2-step loops).
The smallest witnesses are length-2 loops g_j∘g_i returning to the base with holonomy 1; see `nontrivial_len2_loops.csv`.

Group-theoretic meaning:
- The stabilizer of a block in the 120-action has order 216.
- The stabilizer of a lift (an edge in the 240 cover) has order 108.
- The Z2 flip is exactly the nontrivial index-2 character on the 216 stabilizer distinguishing the two lifts.

Adding the global deck involution (swap both lifts in every fiber) produces a group of order 51840 = 2×25920.
