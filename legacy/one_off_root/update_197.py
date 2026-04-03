#!/usr/bin/env python3
"""Update docs for checks 184-197: Spectral Invariants & Complement Duality."""

import re

# ── Update index.html ──
with open('docs/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update count: 183 → 197 everywhere
html = html.replace('183/183', '197/197')
html = html.replace('ALL 183 claims', 'ALL 197 claims')
html = html.replace('183 checks</strong>', '197 checks</strong>')

# 2. Update banner to include complement duality
html = html.replace(
    '197 checks</strong>',
    '197 checks • complement duality</strong>'
)

# 3. Add complement duality narrative section before </section id="curvature">
complement_section = """
  <h3>Complement Duality & Spectral Energy</h3>
  <p>The complement of W(3,3) — connecting every <em>non-collinear</em> pair — is itself a strongly regular graph
  with astonishing physical content:</p>
  <div class="math-block">
    <span class="eq">W(3,3)&#x0305; = SRG(40, 27, 18, 18)</span><br>
    <span class="eq">k' = v−k−1 = 27 = q³ = dim(E₆ fund) — the MATTER SHELL</span><br>
    <span class="eq">λ' = μ' = 18 = 2q² (pseudo-conference: totally democratic)</span>
  </div>
  <p>The complement spectrum is <strong>balanced</strong>: eigenvalues {27, +q, −q} = {27, +3, −3},
  with |r'| = |s'| = q = 3 — the number of generations. From the matter perspective,
  physics is <strong>CP-symmetric</strong>. The original graph breaks this: |r|=2 ≠ |s|=4.</p>

  <h4>Graph Energy Identities</h4>
  <table>
    <tr><th>Quantity</th><th>Formula</th><th>Value</th><th>Equals</th></tr>
    <tr><td>Graph energy</td><td>k + f|r| + g|s| = 12+48+60</td><td><strong>120</strong></td><td>E/2 (half the edges!)</td></tr>
    <tr><td>Complement energy</td><td>k' + f'|r'| + g'|s'| = 27+45+72</td><td><strong>144</strong></td><td>k² (bare coupling²)</td></tr>
    <tr><td>Ratio</td><td>120/144</td><td><strong>5/6</strong></td><td>κ₁+κ₂ (Ollivier-Ricci sum!)</td></tr>
    <tr><td>Difference</td><td>144−120</td><td><strong>24</strong></td><td>f = gauge multiplicity = χ(K3)</td></tr>
    <tr><td>Sum</td><td>120+144</td><td><strong>264</strong></td><td>(k−1)×f = 11×24</td></tr>
  </table>
  <p>The energy ratio bridges <strong>spectral graph theory ↔ discrete Riemannian geometry</strong>:
  graph energy / complement energy = sum of Ollivier-Ricci curvatures at both distance scales.</p>

  <h4>Eigenvalue Equation</h4>
  <p>The non-trivial eigenvalues satisfy x² − (λ−μ)x − (k−μ) = 0, with discriminant:</p>
  <div class="math-block">
    <span class="eq">Δ = (λ−μ)² + 4(k−μ) = 4 + 32 = 36 = (2q)² = 6²</span>
  </div>
  <p><strong>Perfect square</strong> → eigenvalues are guaranteed integers. This is a stringent constraint
  selecting q = 3 among all possible field sizes.</p>

  <h4>Tight Hoffman Clique Bound</h4>
  <p>The clique number ω = q+1 = 4 = μ achieves the Hoffman bound 1−k/s = 1−12/(−4) = 4 with <strong>equality</strong>.
  The K₄ lines (cliques) = maximal cliques = spacetime dimension.</p>

  <h4>Global Graph Invariants</h4>
  <table>
    <tr><th>Invariant</th><th>Value</th><th>Physical Meaning</th></tr>
    <tr><td>Diameter</td><td>2</td><td>Exactly 2 distance classes (SRG defining property)</td></tr>
    <tr><td>Girth</td><td>3</td><td>Triangles exist (λ > 0); encode Yang-Mills cubic vertex</td></tr>
    <tr><td>Vertex connectivity</td><td>12 = k</td><td>Maximally connected; all k links are load-bearing</td></tr>
    <tr><td>Spectral gap</td><td>10 = k−r</td><td>= dim(SO(10) vector); governs expansion rate</td></tr>
    <tr><td>E + E'</td><td>780 = C(40,2)</td><td>Graph + complement partition K₄₀ = dim(Sp(40))</td></tr>
  </table>
"""

# Insert before the closing </section> after curvature content
html = html.replace(
    '<section id="status">',
    complement_section + '\n<section id="status">'
)

# 4. Update the status table entry for verification count
html = html.replace(
    'spectral dimension flow</strong></strong></td></tr>',
    'spectral dimension flow, complement duality (SRG(40,27,18,18)), graph energy identities, Hoffman tight bound, spectral gap = dim(SO(10))</strong></strong></td></tr>'
)

with open('docs/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html updated to 197/197")

# ── Update COMPLETE_SUMMARY.md ──
with open('docs/COMPLETE_SUMMARY.md', 'r', encoding='utf-8') as f:
    md = f.read()

md = md.replace('183/183', '197/197')
md = md.replace('183 checks', '197 checks')

# Add new section for complement duality
complement_md = """
## Spectral Invariants & Complement Duality (Checks 184-197)

The graph complement of W(3,3) reveals a profound duality:

| Property | W(3,3) | Complement |
|----------|--------|------------|
| Parameters | SRG(40,12,2,4) | SRG(40,27,18,18) |
| Non-trivial eigs | {2, -4} | {+3, -3} = {±q} |
| Energy | 120 = E/2 | 144 = k² |
| Degree | 12 = gauge | 27 = matter |

**Key identities:**
- Energy ratio: 120/144 = 5/6 = κ₁+κ₂ (sum of Ollivier-Ricci curvatures!)
- Energy difference: 144−120 = 24 = f = gauge multiplicity
- Energy sum: 120+144 = 264 = (k−1)×f = 11×24
- Complement is CP-symmetric: |r'| = |s'| = q = 3
- Eigenvalue discriminant = (2q)² = 36 → integer eigenvalues forced
- Clique number ω = q+1 = 4 = μ (Hoffman bound TIGHT)
- Spectral gap = k−r = 10 = dim(SO(10) vector)
- Diameter = 2, girth = 3, vertex connectivity = k = 12
- E + E' = 240 + 540 = 780 = C(40,2) = dim(Sp(40))
"""

# Insert before the final summary section
if '## Summary' in md:
    md = md.replace('## Summary', complement_md + '\n## Summary')
elif '## Conclusion' in md:
    md = md.replace('## Conclusion', complement_md + '\n## Conclusion')
else:
    md += '\n' + complement_md

with open('docs/COMPLETE_SUMMARY.md', 'w', encoding='utf-8') as f:
    f.write(md)

print("COMPLETE_SUMMARY.md updated to 197/197")
print("Done!")
