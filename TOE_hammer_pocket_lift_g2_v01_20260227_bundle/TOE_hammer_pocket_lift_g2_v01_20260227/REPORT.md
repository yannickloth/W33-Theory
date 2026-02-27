# TOE hammer: pocket→octonion completion and g₂ lift (v01, 2026-02-27)

This bundle does three things:

1. Uses the **correct “standard positive G₂ 3-form” sign pattern** (not a naive all-`+` Fano orientation) to build a true octonion multiplication table whose derivation algebra is **dim 14**.
2. Fits a **W33-derived 7-pocket** (from your 36-vertex E6-antipode SRG triangle algebra) to that octonion table by solving a finite constraint system.
3. Extracts an explicit basis split  
   \(\mathfrak g_2 = \mathfrak{sl}_3 \oplus (3\oplus \bar 3)\)  
   where the “missing +6” are literal **axis movers**.

## Paper anchor (Wilmot)
Springer OA record: DOI **10.1007/s00006-025-01423-5** (Advances in Applied Clifford Algebras, 2026). citeturn0search0

Key abstract sentence (short paraphrase): Spin(7) calibration terms relate to an ideal with **three idempotents** and provide a direct construction of **G₂** for each of the **480** octonion representations. citeturn0search0

## A) Fixing the “Der=6” bug (metric mismatch)
If you build octonions using an arbitrary oriented-Fano tensor and simultaneously assume the basis is orthonormal (so scalar parts vanish for i≠j), you can accidentally enforce the *wrong* metric and end up with a smaller stabilizer (dim 6).

We instead use the **standard positive G₂ form** convention:

- positive triples: [(1, 2, 7), (3, 4, 7), (5, 6, 7), (1, 3, 5)]
- negative triples: [(1, 4, 6), (2, 3, 6), (2, 4, 5)]

and define \(e_i e_j = -\delta_{ij} + \varphi_{ijk} e_k\).
With that sign pattern:
- stabilizer in \(\mathfrak{so}(7)\) is **dim 14**
- derivation equations on the full 8D algebra give **dim 14**

## B) Completing a real W33 pocket to a full octonion table
Base pocket (global 36-vertex labels): **[0, 1, 2, 14, 15, 17, 27]** with silent axis **27**.

From the W33-derived oriented triangle multiplication (720 defined ordered products on 36), we restrict to this pocket and collect **24** signed constraints of the form
\[
a\cdot b = \pm c.
\]

We solve for:
- a bijection \(\phi:\{0..6\}\to\{1..7\}\) (7! choices),
- sign flips on the basis (2⁷ choices),

such that the pocket constraints match the octonion table.

**Result for this pocket:**
- \(#\phi\text{-solutions}= 168\)
- \(#(\phi,\text{sign})\text{-solutions}= 2688\)
- **unique induced octonion tables on pocket labels = 2** (the two ± octonion classes)

Each induced table has **Der dimension 14**.

## C) Explicit g₂ basis and the “+6 axis movers”
For one completed table, we compute the full derivation space by solving
\[
D(xy)=D(x)y + xD(y)
\]
over \(\mathbb Q\) on the 8D octonion algebra (scalar+7 imag).

We output in `RESULTS.json`:
- `g2_derivations_basis_14`: 14 basis derivation matrices (8×8)
- `g2_sl3_axis_fix_basis_8`: 8 basis matrices with **column(axis)=0** (these form \(\mathfrak{sl}_3\))
- `g2_axis_movers_basis_6`: 6 additional basis matrices spanning the complement

In this basis, the 6 movers map the axis basis vector to **each of the 6 active directions individually** (see `axis_movers_images_of_axis_column`).

## D) Transport/orbit sanity check inside PSp(4,3)
Using the 10 generators on 36 vertices (`sp43_generators_on_e6pairs_36.json`), the group order is **25920**.

Transporting the completed pocket table as a labeled object gives:
- completion orbit size **4320**
- stabilizer size **6**
- **8 completions per pocket** across the 540-pocket orbit

---

## Files
- `RESULTS.json` — counts + the 14/8/6 derivation matrices.
- `scripts/hammer_g2_pocketlift.py` — end-to-end reproduction script.
