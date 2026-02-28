# Pillar 91: Normaliser of the Tomotope Automorphism Group

Pillar 90 established that the tomotope maniplex has exactly 96
colour‑preserving automorphisms; these coincide with the $P_0$ factor in the
matched‑pair decomposition \(\Gamma = N\cdot P_0\) of the tomotope
monodromy group.  A natural question is how this subgroup sits inside the
full group: is $P_0$ normal, self‑normalising, or something in between?

We answer this by computing the orbit of the automorphism subgroup under
conjugation by elements of \(\Gamma\).  Elements of \(\Gamma\) are
readily obtained as the closure of the four involutive generators
$r_0,r_1,r_2,r_3\) from the true‑flag model (size 18 432).  Conjugating the
96 automorphisms by each element of \(\Gamma\) produces a set of subgroups
(the conjugacy class of $P_0$).  The size of this set equals the index of the
normaliser $N_\Gamma(P_0)$.

**Result (T1).**  The conjugacy class contains a *single* subgroup; i.e.
$P_0$ is invariant under conjugation by all of \(\Gamma\).  Consequently
the normaliser has full order 18 432.  In group‑theoretic language
$P_0\triangleleft\Gamma$.

This is a striking complement to the matched‑pair picture: although the
factorisation was presented as a general Zappa–Szép product, the $P_0$ factor
is in fact a normal subgroup.  The regular subgroup $N$ therefore provides a
coset decomposition of the normaliser; there are exactly 192 distinct cosets
corresponding to the 192 elements of $N$.

**Additional statistics (T2).**  We accumulated the cycle lengths of every
automorphism encountered in the conjugacy orbit (in this case, just the
original 96).  The total distribution remains

```text
1:192, 2:2592, 3:2048, 4:1728
```

matching the data from Pillar 90 and underscoring the uniformity of the
subgroup under the larger group action.

The script `THEORY_PART_CXCVII_AUT_NORMALISER.py` performs the above
computations; `tests/test_aut_normaliser.py` verifies them and ensures that
the necessary summary and report files are produced.

The normality of $P_0$ will simplify later arguments that compare the
monodromy and automorphism groups, and it clarifies the role of triality:  the
full symmetry of the tomotope decomposes as a direct product
$N\times P_0$, with $P_0$ controlling the outer automorphisms.  Future
pillars will exploit this normality when aligning the $N$‑action with the
Heisenberg quotient and when constructing explicit isomorphisms between
various quotient structures.
