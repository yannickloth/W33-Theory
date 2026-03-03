#!/usr/bin/env python3
"""Update docs for checks 226-239: GQ Axiomatics, Ihara Zeta & Absolute Bounds."""

# ── Update index.html ──
with open('docs/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('225/225', '239/239')

gq_section = """
  <h3>GQ Axiomatics, Ihara Zeta &amp; Absolute Bounds (Checks 226&ndash;239)</h3>

  <h4>GQ(q,q) Axiomatics: Everything from q = 3</h4>
  <p>The generalized quadrangle GQ(q,q) has collinearity graph SRG with:</p>
  <div class="math-block">
    <span class="eq">&lambda; = q &minus; 1 = 2, &ensp; &mu; = q + 1 = 4</span><br>
    <span class="eq">k = q&middot;&mu; = q(q+1) = 12, &ensp; v = (q+1)(q&sup2;+1) = 40</span>
  </div>
  <p><strong>Self-dual:</strong> points = lines = v = 40 (point-line democracy).</p>
  <p><strong>Overlap product:</strong> &mu;&lambda; = (q+1)(q&minus;1) = q&sup2;&minus;1 = <strong>8 = rank(E&#8328;)</strong>.</p>
  <p><strong>Uniqueness:</strong> &mu;&minus;&lambda; = &lambda; requires 2 = q&minus;1, i.e., <strong>q = 3 is the ONLY self-referencing
  field size</strong>. The SRG parameters are locked in a self-referential loop.</p>

  <h4>Graph-Theoretic Riemann Hypothesis</h4>
  <p>The <strong>Ihara zeta function</strong> &zeta;<sub>G</sub>(u) of W(3,3) has all non-trivial poles
  lying <strong>exactly on the critical circle</strong> |u| = 1/&radic;(k&minus;1) = 1/&radic;11:</p>
  <table>
    <tr><th>Eigenvalue</th><th>Poles</th><th>|u|&sup2;</th><th>Count</th></tr>
    <tr><td>r = 2</td><td>(1&plusmn;i&radic;10)/11</td><td>1/11</td><td>48 = 2f</td></tr>
    <tr><td>s = &minus;4</td><td>(&minus;2&plusmn;i&radic;7)/11</td><td>1/11</td><td>30 = 2g</td></tr>
    <tr><td colspan="3"><strong>Total complex poles</strong></td><td><strong>78 = dim(E&#8326;)!</strong></td></tr>
  </table>
  <p>This is the <strong>graph-theoretic Riemann Hypothesis</strong>: W(3,3) is maximally Ramanujan.</p>
  <p>The pole discriminants encode the graph: |disc<sub>r</sub>| = 40 = v,
  |disc<sub>s</sub>| = 28 = v&minus;k = dim(SO(8)), and their difference = k = 12.</p>
  <p>Total Ihara zeros = 2(E&minus;v) + 2v = 2E = <strong>480 = directed edges</strong>.</p>

  <h4>Delsarte Absolute Bounds &amp; Monster Connection</h4>
  <div class="math-block">
    <span class="eq">f(f+3)/2 = 24 &times; 27 / 2 = <strong>324 = &mu; &times; b&#8321; = 196884 &minus; 196560</strong></span>
  </div>
  <p>The Delsarte absolute bound = Monster&ndash;Leech gap = spacetime &times; Betti!
  And f+3 = 27 = k' (complement degree), g+3 = 18 = &lambda;' (complement overlap).
  <strong>The absolute bounds are built from complement parameters.</strong></p>
  <p>Krein condition margins: k(k&minus;1) = 132 and 2f = 48 &mdash; both comfortably positive.</p>
"""

html = html.replace(
    '<section id="status">',
    gq_section + '\n<section id="status">'
)

with open('docs/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("index.html updated to 239/239")

# ── Update COMPLETE_SUMMARY.md ──
with open('docs/COMPLETE_SUMMARY.md', 'r', encoding='utf-8') as f:
    md = f.read()

md = md.replace('225/225', '239/239')
md = md.replace('225 checks', '239 checks')

gq_md = """
## GQ Axiomatics, Ihara Zeta & Absolute Bounds (Checks 226-239)

### GQ(q,q) Axiomatics (Checks 226-229)
The generalized quadrangle GQ(q,q) completely determines the SRG from q alone:
- λ = q-1 = 2, μ = q+1 = 4
- v = (q+1)(q²+1) = 40, k = q(q+1) = 12
- **Self-dual:** points = lines = v = 40
- **μλ = q²-1 = 8 = rank(E₈)** (overlap product = E₈ lattice rank)
- **UNIQUENESS: μ-λ = λ ⟺ q = 3** (only self-referencing field size!)

### Graph-Theoretic Riemann Hypothesis (Checks 230-236)
The Ihara zeta function ζ_G(u) of W(3,3):
- Cycle rank ρ = E-v = 200 = v(k-r)/2
- **ALL poles lie on critical circle |u| = 1/√(k-1) = 1/√11**
- This is the graph-theoretic Riemann Hypothesis!
- Complex Ihara poles = 2f+2g = 2(v-1) = **78 = dim(E₆)**
- Total Ihara zeros = 2E = 480 = directed edges
- r-pole |discriminant| = 40 = v
- s-pole |discriminant| = 28 = v-k = dim(SO(8))
- Discriminant difference = k = 12

### Delsarte Absolute Bounds (Checks 237-238)
**f(f+3)/2 = 24×27/2 = 324 = μ×b₁ = Monster-Leech gap!**
- f+3 = 27 = k' (complement degree)
- g+3 = 18 = λ' = μ' (complement overlap)
- The absolute bounds are built from complement parameters!

### Krein Parameters (Check 239)
- Krein margin 1 = k(k-1) = 132
- Krein margin 2 = 2f = 48
"""

if '## Summary' in md:
    md = md.replace('## Summary', gq_md + '\n## Summary')
elif '## Conclusion' in md:
    md = md.replace('## Conclusion', gq_md + '\n## Conclusion')
else:
    md += '\n' + gq_md

with open('docs/COMPLETE_SUMMARY.md', 'w', encoding='utf-8') as f:
    f.write(md)
print("COMPLETE_SUMMARY.md updated to 239/239")
print("Done!")
