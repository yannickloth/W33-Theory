#!/usr/bin/env python3
"""Update docs for checks 212-225: Hodge Firewall & Moonshine Chain."""

# ── Update index.html ──
with open('docs/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('211/211', '225/225')

# Add Hodge/Moonshine section before </section id="status">
hodge_moon_section = """
  <h3>Hodge Firewall &amp; Moonshine Chain (Checks 212&ndash;225)</h3>

  <h4>The E&#8326; Firewall (Operator-Level Statement)</h4>
  <p>The Hodge decomposition of the 1-cochain space (dim = E = 240) gives:</p>
  <div class="math-block">
    <span class="eq">C&sup1; = im(d&#8320;) &oplus; im(&delta;&#8322;) &oplus; &Eta;&sup1;</span><br>
    <span class="eq">240 = 39 + 120 + 81 = (v&minus;1) + E/2 + q&sup4;</span>
  </div>
  <p>The <strong>harmonic subspace</strong> &Eta;&sup1; = ker(L&#8321;) has dimension <strong>81 = 27 &times; 3</strong>
  = (E&#8326; fundamental) &times; (generations).</p>
  <p>Gauge transformations A &rarr; A + d&#8320;&chi; only move the exact component im(d&#8320;).
  The harmonic sector is <strong>gauge-invariant</strong>, protected by the Hodge projector
  P = I &minus; d&#8320;&Delta;&#8320;&#8314;&delta;&#8321; &minus; &delta;&#8322;&Delta;&#8322;&#8314;d&#8321;.</p>
  <div class="math-block">
    <span class="eq"><strong>E&#8326; acts on gauge-invariant harmonic 1-forms, protected from gauge redundancy by the Hodge projector.</strong></span>
  </div>

  <h4>The Moonshine Chain</h4>
  <p>Every constant in the chain W(3,3) &rarr; E&#8328; &rarr; &Theta; &rarr; j &rarr; Monster is a W(3,3) invariant:</p>
  <table>
    <tr><th>Moonshine Object</th><th>Value</th><th>W(3,3) Parameter</th></tr>
    <tr><td>&Theta;<sub>E&#8328;</sub> first coefficient</td><td><strong>240</strong></td><td>E = edge count = |E&#8328; roots|</td></tr>
    <tr><td>&eta; exponent in j = E&#8324;&sup3;/&eta;&sup2;&sup4;</td><td><strong>24</strong></td><td>f = gauge multiplicity = &chi;(K3)</td></tr>
    <tr><td>Number of E&#8328; copies</td><td><strong>3</strong></td><td>q = generations</td></tr>
    <tr><td>j constant term</td><td><strong>744</strong></td><td>q &times; dim(E&#8328;) = 3 &times; 248</td></tr>
    <tr><td>Leech lattice dimension</td><td><strong>24</strong></td><td>f = rank(E&#8328;&sup3;) = 3 &times; 8</td></tr>
    <tr><td>Central charge c</td><td><strong>24</strong></td><td>f (Monster VOA / Leech CFT)</td></tr>
  </table>

  <h4>The Monster&ndash;Leech Gap Identity</h4>
  <div class="math-block">
    <span class="eq">196884 &minus; 196560 = 324 = &mu; &times; b&#8321; = 4 &times; 81 = 18&sup2; = (&lambda;')&sup2;</span>
  </div>
  <p>The gap between the Monster module weight-2 dimension and the Leech kissing number equals
  <strong>spacetime dimension &times; first Betti number</strong> = <strong>(complement overlap parameter)&sup2;</strong>.</p>
  <p>Thompson decomposition: 196883 = 196560 + &mu;&middot;b&#8321; &minus; 1 = Leech + spacetime&times;matter &minus; vacuum.</p>

  <h4>The Hodge&ndash;Moonshine Bridge</h4>
  <p>b&#8321; = 81 = q&sup4; is the <strong>hinge</strong> connecting four independent mathematical domains:</p>
  <ol>
    <li><strong>DEC/Hodge theory:</strong> dim(&Eta;&sup1;) = 81 (gauge-invariant harmonic 1-forms)</li>
    <li><strong>E&#8326; representation theory:</strong> 81 = 27 &times; 3 (E&#8326; fundamental &times; generations)</li>
    <li><strong>Kirchhoff spectral theory:</strong> &tau; = 2<sup>81</sup> &middot; 5&sup2;&sup3; (spanning tree 2-exponent)</li>
    <li><strong>Monstrous moonshine:</strong> 196884 &minus; 196560 = &mu; &times; 81 = 324</li>
  </ol>
"""

html = html.replace(
    '<section id="status">',
    hodge_moon_section + '\n<section id="status">'
)

with open('docs/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("index.html updated to 225/225")

# ── Update COMPLETE_SUMMARY.md ──
with open('docs/COMPLETE_SUMMARY.md', 'r', encoding='utf-8') as f:
    md = f.read()

md = md.replace('211/211', '225/225')
md = md.replace('211 checks', '225 checks')

hodge_moon_md = """
## Hodge Firewall & Moonshine Chain (Checks 212-225)

### The E₆ Firewall (Checks 212-215)

The Hodge decomposition of C¹ (dim = E = 240):
```
C¹ = im(d₀) ⊕ im(δ₂) ⊕ H¹
240 = 39 + 120 + 81 = (v-1) + E/2 + q⁴
```

**H¹ = ker(L₁) = 81 = 27 × 3 = dim(E₆ fund) × generations**

This is the **E₆ Firewall**: gauge transformations A → A + d₀χ only move the exact
component im(d₀). The harmonic sector H¹ is **gauge-invariant**, protected by the
Hodge projector P = I − d₀Δ₀⁺δ₁ − δ₂Δ₂⁺d₁.

> E₆ acts on the gauge-invariant harmonic 1-form sector, protected from gauge
> redundancy by the Hodge projector.

### The Moonshine Chain (Checks 216-224)

Every constant in the chain W(3,3) → E₈ → Θ → j → Monster is a W(3,3) invariant:

| Object | Value | W(3,3) Parameter |
|--------|-------|-------------------|
| Θ_{E₈} coeff₁ | 240 | E = edges |
| η exponent | 24 | f = gauge multiplicity |
| E₈ copies | 3 | q = generations |
| j constant | 744 | q × dim(E₈) = 3 × 248 |
| Leech dim | 24 | f = rank(E₈³) |
| Central charge | 24 | f (Monster VOA) |

**The Monster-Leech Gap:**
```
196884 − 196560 = 324 = μ × b₁ = 4 × 81 = 18² = (λ')²
```
= spacetime dimension × first Betti number = complement parameter squared!

### The Hodge-Moonshine Bridge (Check 225)

b₁ = 81 = q⁴ connects FOUR independent domains:
1. **DEC**: dim(H¹) = 81 (gauge-invariant matter)
2. **E₆**: 81 = 27 × 3 (E₆ fund × generations)
3. **Kirchhoff**: τ = 2^81 · 5²³ (spanning tree exponent)
4. **Monster**: 196884 − 196560 = μ × 81 = 324
"""

if '## Summary' in md:
    md = md.replace('## Summary', hodge_moon_md + '\n## Summary')
elif '## Conclusion' in md:
    md = md.replace('## Conclusion', hodge_moon_md + '\n## Conclusion')
else:
    md += '\n' + hodge_moon_md

with open('docs/COMPLETE_SUMMARY.md', 'w', encoding='utf-8') as f:
    f.write(md)
print("COMPLETE_SUMMARY.md updated to 225/225")
print("Done!")
