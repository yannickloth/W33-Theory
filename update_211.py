#!/usr/bin/env python3
"""Update docs for checks 198-211: Chromatic Structure, Seidel Spectrum & Exceptional Tower."""

# ── Update index.html ──
with open('docs/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('197/197', '211/211')

# Add exceptional tower section before status
tower_section = """
  <h3>Chromatic Structure, Seidel Spectrum &amp; Exceptional Tower</h3>

  <h4>The Spectral-Combinatorial Lock</h4>
  <p>W(3,3) satisfies the extraordinary identity <strong>k = &mu;(&lambda;+1) = 4&times;3 = 12</strong>,
  which forces the eigenvalues to equal the overlap parameters: &lambda; = r = 2 and &mu; = &minus;s = 4.
  Spectral and combinatorial information are <em>locked together</em>.</p>

  <h4>Perfect Graph Partition</h4>
  <table>
    <tr><th>Invariant</th><th>Value</th><th>Equals</th><th>Meaning</th></tr>
    <tr><td>&alpha; (independence)</td><td>10</td><td>k &minus; r</td><td>Ovoids of GQ(3,3)</td></tr>
    <tr><td>&chi; (chromatic)</td><td>4</td><td>&omega; = &mu;</td><td>Spacetime dimension</td></tr>
    <tr><td>&chi; &times; &alpha;</td><td>40</td><td>v</td><td>Perfect graph!</td></tr>
    <tr><td>&Theta; (Shannon)</td><td>10</td><td>&alpha;</td><td>Zero-error channel capacity</td></tr>
  </table>
  <p>Both Lov&aacute;sz theta bounds are <strong>tight</strong>: &vartheta;(G) = 10 = &alpha;,
  &vartheta;(&#x1D43E;) = 4 = &chi;, and &vartheta;(G)&middot;&vartheta;(&#x1D43E;) = 40 = v.</p>

  <h4>Seidel Matrix &amp; E&#8328; (Again!)</h4>
  <p>The Seidel matrix S = J &minus; I &minus; 2A (governing equiangular lines and two-graphs)
  has eigenvalues {g, &minus;(q+&lambda;), &Phi;&#8326;} = {15, &minus;5, 7}.</p>
  <div class="math-block">
    <span class="eq">Seidel energy = |15| + 24&times;|&minus;5| + 15&times;|7| = 15 + 120 + 105 = <strong>240 = E&#8328; roots</strong></span>
  </div>
  <p>The Seidel matrix independently encodes E&#8328; through its energy!</p>

  <h4>Kirchhoff Spanning Trees</h4>
  <div class="math-block">
    <span class="eq">&tau; = (1/v)&middot;(k&minus;r)<sup>f</sup>&middot;(k&minus;s)<sup>g</sup> = 2<sup>81</sup> &middot; 5<sup>23</sup></span>
  </div>
  <p>Exponent of 2: <strong>81 = q&sup4; = b&#8321;</strong> (first Betti number).<br>
  Exponent of 5: <strong>23 = f &minus; 1</strong> (Golay code length, Leech lattice dimension minus 1).</p>

  <h4>The Complete Exceptional Tower</h4>
  <p>Every exceptional Lie algebra dimension emerges as a <strong>simple SRG formula</strong>:</p>
  <table>
    <tr><th>Algebra</th><th>SRG Formula</th><th>dim</th></tr>
    <tr><td>G&#8322;</td><td>k + &mu; &minus; &lambda;</td><td><strong>14</strong></td></tr>
    <tr><td>F&#8324;</td><td>v + k</td><td><strong>52</strong></td></tr>
    <tr><td>E&#8326;</td><td>2v &minus; &lambda;</td><td><strong>78</strong></td></tr>
    <tr><td>E&#8327; (fund)</td><td>v + k + &mu;</td><td><strong>56</strong></td></tr>
    <tr><td>E&#8327;</td><td>vq + &Phi;&#8323;</td><td><strong>133</strong></td></tr>
    <tr><td>E&#8328;</td><td>E + k &minus; &mu;</td><td><strong>248</strong></td></tr>
  </table>
  <p>The full G&#8322; &rarr; F&#8324; &rarr; E&#8326; &rarr; E&#8327; &rarr; E&#8328; tower is contained in W(3,3)!</p>

  <h4>The Grand Identity</h4>
  <div class="math-block">
    <span class="eq">|Aut(W(3,3))| = q &times; E<sub>graph</sub> &times; E<sub>complement</sub> = 3 &times; 120 &times; 144 = <strong>51840 = |W(E&#8326;)|</strong></span>
  </div>
  <p>The automorphism group order = generations &times; graph energy &times; complement energy.
  This connects symmetry, spectral theory, and complement duality in a single equation.</p>
"""

html = html.replace(
    '<section id="status">',
    tower_section + '\n<section id="status">'
)

with open('docs/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("index.html updated to 211/211")

# ── Update COMPLETE_SUMMARY.md ──
with open('docs/COMPLETE_SUMMARY.md', 'r', encoding='utf-8') as f:
    md = f.read()

md = md.replace('197/197', '211/211')
md = md.replace('197 checks', '211 checks')

tower_md = """
## Chromatic Structure, Seidel Spectrum & Exceptional Tower (Checks 198-211)

### The Spectral-Combinatorial Lock (Check 198)
W(3,3) satisfies k = mu(lam+1) = 4x3 = 12, forcing lam = r = 2 and mu = -s = 4.

### Perfect Graph & Shannon Capacity (Checks 199-200)
- Independence number alpha = 10 = k-r (ovoids of GQ)
- Chromatic number chi = omega = mu = 4 (spacetime dimension!)
- chi x alpha = 40 = v (perfect graph partition)
- Lovász theta(G) = 10, theta(complement) = 4 = mu, product = v = 40 (BOTH TIGHT)
- Shannon capacity Theta = alpha = 10

### Seidel Matrix (Checks 201-202)
The Seidel matrix S = J - I - 2A has eigenvalues {15, -5, 7} = {g, -(q+lam), Phi_6}.
**Seidel energy = 15 + 120 + 105 = 240 = E = E_8 roots!**

### Kirchhoff Spanning Trees (Check 203)
tau = 2^81 * 5^23 where:
- 81 = q^4 = b_1 (first Betti number)
- 23 = f-1 (Golay code length, Leech lattice dim - 1)

### Signless & Normalized Laplacians (Checks 204-205)
- Signless Laplacian: {2k, k+r, k+s} = {24=f, 14=dim(G2), 8=k-mu}
- Normalized Laplacian: {0, 5/6 = kappa1+kappa2, 4/3 = C_F(QCD)}

### Graph Determinant (Check 206)
det(A) = -q * 2^56 = -3 * 2^56, where 56 = v+k+mu = dim(E7 fundamental)

### THE EXCEPTIONAL TOWER (Checks 207-209)

| Algebra | SRG Formula | dim |
|---------|-------------|-----|
| G2 | k + mu - lam | **14** |
| F4 | v + k | **52** |
| E6 | 2v - lam | **78** |
| E7 (fund) | v + k + mu | **56** |
| E7 | vq + Phi_3 | **133** |
| E8 | E + k - mu | **248** |

ALL five exceptional Lie algebra dimensions emerge from simple SRG parameter formulas!

### Cross-Parameter Identities (Check 210)
- kr = klam = f = 24 (gauge multiplicity = degree x eigenvalue)
- v|s| = T = 160 (triangles = vertices x |neg eigenvalue|)

### The Grand Identity (Check 211)
|Aut(W(3,3))| = q * E_graph * E_complement = 3 x 120 x 144 = **51840 = |W(E6)|**
The automorphism group = generations x graph energy x complement energy!
"""

if '## Summary' in md:
    md = md.replace('## Summary', tower_md + '\n## Summary')
elif '## Conclusion' in md:
    md = md.replace('## Conclusion', tower_md + '\n## Conclusion')
else:
    md += '\n' + tower_md

with open('docs/COMPLETE_SUMMARY.md', 'w', encoding='utf-8') as f:
    f.write(md)
print("COMPLETE_SUMMARY.md updated to 211/211")
print("Done!")
