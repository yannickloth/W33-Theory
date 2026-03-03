#!/usr/bin/env python3
"""Update docs for checks 240-253: Modular Residues & Representation Fusion."""

# ── Update index.html ──
with open('docs/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('239/239', '253/253')

modular_section = """
  <h3>Modular Residues &amp; Representation Fusion (Checks 240&ndash;253)</h3>

  <h4>Cyclotomic Residue Table</h4>
  <p>The SRG parameters mod the cyclotomic primes &Phi;&#8323; = 13 and &Phi;&#8326; = 7
  reproduce physical constants:</p>
  <table>
    <tr><th>Residue</th><th>Value</th><th>Equals</th><th>Meaning</th></tr>
    <tr><td>v mod k</td><td>40 mod 12</td><td><strong>4 = &mu;</strong></td><td>Spacetime dimension</td></tr>
    <tr><td>E mod &Phi;&#8323;</td><td>240 mod 13</td><td><strong>6 = q!</strong></td><td>Generations factorial</td></tr>
    <tr><td>E mod &Phi;&#8326;</td><td>240 mod 7</td><td><strong>2 = &lambda;</strong></td><td>Overlap parameter</td></tr>
    <tr><td>v mod &Phi;&#8323;</td><td>40 mod 13</td><td><strong>1 = b&#8320;</strong></td><td>Connected components</td></tr>
    <tr><td>v mod &Phi;&#8326;</td><td>40 mod 7</td><td><strong>5 = q+r</strong></td><td>Field + eigenvalue</td></tr>
    <tr><td>k mod &Phi;&#8326;</td><td>12 mod 7</td><td><strong>5 = v mod &Phi;&#8326;</strong></td><td>k &equiv; v (mod &Phi;&#8326;)!</td></tr>
  </table>

  <h4>Eigenvalue Multiplicity Algebra</h4>
  <table>
    <tr><th>Identity</th><th>Value</th><th>Equals</th></tr>
    <tr><td>f &middot; g</td><td>24 &times; 15</td><td><strong>360 = |A&#8326;|</strong> (alternating group)</td></tr>
    <tr><td>f &minus; g</td><td>24 &minus; 15</td><td><strong>9 = q&sup2;</strong> (field size squared)</td></tr>
    <tr><td>(f&minus;g)&sup2;</td><td>9&sup2;</td><td><strong>81 = b&#8321; = q&sup4;</strong> (first Betti number!)</td></tr>
    <tr><td>f/g</td><td>24/15 = 8/5</td><td><strong>rank(E&#8328;)/(q+r)</strong></td></tr>
  </table>
  <p>The squared multiplicity gap = harmonic 1-form dimension = matter sector!</p>

  <h4>&#x1F525; Check 248 = dim(E&#8328;) — META-SELF-REFERENCE</h4>
  <div class="math-block">
    <span class="eq"><strong>CHECK NUMBER 248 = dim(E&#8328;) = E + k &minus; &mu; = 240 + 12 &minus; 4 = 248</strong></span>
  </div>
  <p>The theory is literally <strong>self-referencing at E&#8328;</strong>: the check that verifies
  E&#8328; IS numbered 248.</p>

  <h4>Spectral Gap Product &amp; Triple Lock</h4>
  <div class="math-block">
    <span class="eq">(k&minus;&lambda;)(k&minus;&mu;) = 10 &times; 8 = <strong>80 = 2v</strong> (spectral gap product = 2&times;vertices)</span><br>
    <span class="eq">&lambda;&middot;&mu;&middot;k = 2&times;4&times;12 = <strong>96 = f&middot;&mu;</strong> (triple SRG product = gauge&times;spacetime)</span><br>
    <span class="eq">(v&minus;1)(k&minus;1) = 39&times;11 = <strong>429 = q&middot;(k&minus;1)&middot;&Phi;&#8323;</strong></span>
  </div>
"""

html = html.replace(
    '<section id="status">',
    modular_section + '\n<section id="status">'
)

with open('docs/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("index.html updated to 253/253")

# ── Update COMPLETE_SUMMARY.md ──
with open('docs/COMPLETE_SUMMARY.md', 'r', encoding='utf-8') as f:
    md = f.read()

md = md.replace('239/239', '253/253')
md = md.replace('239 checks', '253 checks')

modular_md = """
## Modular Residues & Representation Fusion (Checks 240-253)

### Cyclotomic Residue Table
| Residue | Value | Equals | Meaning |
|---------|-------|--------|---------|
| v mod k | 40 mod 12 | **4 = μ** | Spacetime dimension |
| E mod Φ₃ | 240 mod 13 | **6 = q!** | Generations factorial |
| E mod Φ₆ | 240 mod 7 | **2 = λ** | Overlap parameter |
| v mod Φ₃ | 40 mod 13 | **1 = b₀** | Connected components |
| v mod Φ₆ | 40 mod 7 | **5 = q+r** | Field + eigenvalue |
| k mod Φ₆ | 12 mod 7 | **5 = v mod Φ₆** | k ≡ v (mod Φ₆)! |

### Eigenvalue Multiplicity Algebra
- **f·g = 360 = |A₆|** (alternating group on 6 letters)
- **f−g = 9 = q²** (multiplicity gap = field size squared)
- **(f−g)² = 81 = b₁ = q⁴** (gap squared = first Betti number!)
- **f/g = 8/5 = rank(E₈)/(q+r)**

### CHECK 248 = dim(E₈) — META-SELF-REFERENCE!!!
Check number 248 = dim(E₈) = E+k−μ = 240+12−4 = 248.
The theory is SELF-REFERENCING at E₈.

### Spectral Gap Product & Triple Lock
- (k−λ)(k−μ) = 10×8 = **80 = 2v** (spectral gap product = 2×vertices)
- λ·μ·k = 2×4×12 = **96 = f·μ** (triple SRG product = gauge×spacetime)
- (v−1)(k−1) = 39×11 = **429 = q·(k−1)·Φ₃**
"""

if '## Summary' in md:
    md = md.replace('## Summary', modular_md + '\n## Summary')
elif '## Conclusion' in md:
    md = md.replace('## Conclusion', modular_md + '\n## Conclusion')
else:
    md += '\n' + modular_md

with open('docs/COMPLETE_SUMMARY.md', 'w', encoding='utf-8') as f:
    f.write(md)
print("COMPLETE_SUMMARY.md updated to 253/253")
print("Done!")
