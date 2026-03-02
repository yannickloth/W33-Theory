# Pillar 90: Tomotope Automorphisms and Triality

Following the matched‑pair analysis of Pillar 85, we now probe the internal
symmetries of the 192‑flag tomotope itself.  The four involutions
$r_0,r_1,r_2,r_3$ define a 4‑coloured maniplex on 192 vertices; any
permutation of the flags which preserves the colouring is an automorphism of
the maniplex.

A brief computation using NetworkX shows that the automorphism group has order
**96**.  In other words, there are exactly 96 distinct colour‑preserving
permutations of the tomotope.  This cardinality coincides with the order of
the $P_0$ factor appearing in the Zappa–Szép decomposition
$\Gamma = N\cdot P_0$ (see Pillar 85).  The correspondence is not a
coincidence: the automorphism group is isomorphic to $P_0$, while the
normal regular subgroup $N$ (which acts transitively on the 192 flags) is the
kernel of this action.

> **Note on triality.**  The phenomenon above ties into the classical notion
> of *triality*.  The Dynkin diagram $\mathrm{D}_4$ admits an outer
> automorphism group isomorphic to $S_3$, permuting the three 8‑dimensional
> irreducible representations of $\mathrm{Spin}(8)$.  Geometrically this
> triality manifests in the tomotope as the three Sylow‑2 subgroups of $N$ and
> in the splitting $192=3\cdot64$ exhibited in Pillar 85.  A readable account
> of these ideas can be found in the Wikipedia article on [Triality]
> (https://en.wikipedia.org/wiki/Triality).

## Computations performed

- built the edge‑coloured graph from the $r_i$ permutations in
  `TOE_tomotope_true_flag_model_v02_20260228_bundle.zip`;
- enumerated all colour‑preserving graph automorphisms using NetworkX;
- recorded the cycle structure of each automorphism; the action is not
  regular, confirming that the automorphism group is strictly smaller than
  $\Gamma$.

The script `THEORY_PART_CXCVI_TOMOTOPE_AUTOMORPHISMS.py` implements these
steps, writes a JSON summary and provides basic validation.  All of the
results are replicated in the accompanying tests.

The automorphism data will be used in subsequent pillars when comparing the
$P_0$ action to other symmetry groups and when establishing uniqueness of the
tomotope structure.
