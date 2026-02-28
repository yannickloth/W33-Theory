# Tomotope matched-pair push (repo synthesis)

This bundle ties together three objects already present in your repo/bundles:

- **Tomotope monodromy** Γ on 192 flags with Coxeter-type local orders {3,12,4} (from the true flag model).
- The **axis-line 192 group** H (octonion stabilizer axis-line subgroup).
- The **K-locus triality weld** giving a Z3-valued cocycle on the 54-pocket orbit.

---

## 1) Exact factorization inside tomotope monodromy

We use the computed exact factorization:

- |Γ| = 18432
- Γ = N · P0 with |N|=192, |P0|=96, N∩P0={1} (Zappa–Szép / matched pair)
- N is regular on flags (identifies flags with N-elements)

### P0 acts on N/[N,N] ≅ V4 with image of size 2
Concretely the induced permutations on the 4 cosets are:

[(0, 1, 2, 3), (0, 1, 3, 2)]

So P0 does **not** realize full Aut(V4)=S3; it only flips a single pair of sheets.

See: `matched_pair_V4_image_of_P0.json`.

---

## 2) The (3, 12, 4) “12-step rotation” decomposes as 4 steps + triality

Let t := r1·r2 in Γ. Then ord(t)=12.

The key fact (and the cleanest bridge to your “triality weld”):

- t^4 has **order 3**
- t^4 lies purely in the P0 factor (its N-part is identity)

So every 4 steps of the 12-cycle, you pick up a triality element.

See full factorization of t^k: `rotation_r1r2_factor_powers.json`.

---

## 3) Triality action on the 192-translation layer

Let p := t^4 (order 3 in P0). Its matched-pair left action on the 192 N-elements has cycle type:

- 96 fixed points
- 32 cycles of length 3

See: `triality_element_t4_action_on_N.json`.

---

## 3.5) Internal triality inside N: three Sylow-2 subgroups (3×64)

N is not a 2-group; it has exactly **three** distinct Sylow-2 subgroups of order 64.
An element of order 3 in N conjugates one Sylow-2 to the next, cycling all three.
So N has a natural *triality decomposition*:

- 192 = 3 × 64
- the C3 permutes the three 64-state Sylow-2 sectors.

See: `N_sylow2_triality.json`.

## 4) Axis-192 H versus Tomotope-192 N

Order spectra comparison:

- Axis H has 48 elements of order 8 (octonionic “quarter-turn spin”).
- Tomotope N has **no order 8**, and instead has 48 additional elements of order 4.

Everything else matches exactly (orders 1,2,3,6).

This is a *very sharp* explanation of why “axis-192 is a shadow”: tomotope needs the same 192-sized skeleton but with the spin-8 collapsed to spin-4.

See: `H_vs_N_order_spectra.json`.

---

## 5) K-locus Z3 cocycle sanity

Using the Z3 cocycle exported in the triality-weld bundle:

- 200 random words followed by group-theoretic inverse words returned to base with total voltage 0 in **200/200** cases.

(This checks the cocycle is behaving like a genuine stabilizer-valued cocycle, as expected.)

See: `K_Z3_cocycle_sanity.json`.

---

## Next computation (to “solve further”)

You now have the right primitives to build the **Z12** structure behind ord(r1r2)=12:

- the Z3 triality from the K-weld (pocket stabilizer),
- the V4 sheet action from P0 ↷ N/[N,N],
- and the fact that t^4 is exactly triality.

Next: construct an explicit voltage model on the 48 incidence-pair base where the fiber is **(V4 ⋊ Z3)** (or a Z12 quotient),
and verify it reproduces the tomotope r1–r2 rotation algebraically.

