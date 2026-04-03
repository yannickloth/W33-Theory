"""Update docs to 295/295 — PART VII-D: Leech Lattice, Partition & Information."""
import pathlib

root = pathlib.Path(r"c:\Repos\Theory of Everything\docs")

# ── index.html ──
html_path = root / "index.html"
html = html_path.read_text(encoding="utf-8")
html = html.replace("281/281", "295/295")
html = html.replace("281 checks", "295 checks")

new_html_section = """
        <div class="result-card">
            <h3>&#9733; PART VII-D: Leech Lattice, Partition Function &amp; Information Theory (checks 282-295)</h3>
            <p><strong>Leech lattice &Lambda;<sub>24</sub></strong> lives in &Ropf;<sup>f</sup> = &Ropf;<sup>24</sup>.
               Kissing number 196560 = E&middot;q&sup2;&middot;&Phi;<sub>3</sub>&middot;&Phi;<sub>6</sub>
               = 240&times;9&times;13&times;7.
               Monster&ndash;Leech gap = 196884&minus;196560 = 324 = &mu;&middot;b<sub>1</sub> = Delsarte bound.</p>
            <p><strong>Shannon capacity</strong> &Theta;(G) = &alpha; = v/&chi; = 10 (tight Lov&aacute;sz).</p>
            <div class="highlight">
            <strong>Partition numbers from SRG parameters:</strong><br>
            p(k) = p(12) = 77 = dim(E<sub>6</sub>)&minus;1<br>
            p(g) = p(15) = 176 = (k&minus;1)(k+&mu;)<br>
            p(f) = p(24) = 1575 = g&sup2;&middot;&Phi;<sub>6</sub><br><br>
            <strong>Ramanujan tau function:</strong><br>
            &tau;(q) = &tau;(3) = 252 = E+k = k&middot;dim(C<sub>3</sub>)<br>
            &tau;(&lambda;) = &tau;(2) = &minus;24 = &minus;f<br><br>
            <strong>Modular forms:</strong><br>
            &eta;<sup>f</sup> = &eta;<sup>24</sup> = &Delta;, weight(&Delta;) = k = 12<br>
            E<sub>4</sub>: weight = &mu; = 4, leading coeff = E = 240<br>
            E<sub>6</sub>: weight = k/&lambda; = 6, coeff = &minus;k(v+&lambda;) = &minus;504
            </div>
        </div>
"""
html = html.replace("</main>", new_html_section + "\n        </main>")
html_path.write_text(html, encoding="utf-8")
print("index.html updated to 295/295")

# ── COMPLETE_SUMMARY.md ──
md_path = root / "COMPLETE_SUMMARY.md"
md = md_path.read_text(encoding="utf-8")
md = md.replace("281/281", "295/295")
md = md.replace("281 checks", "295 checks")

new_md_section = """
---

## PART VII-D: Leech Lattice, Partition Function & Information Theory (checks 282-295)

### Leech Lattice Λ₂₄
- Lives in **ℝ^f = ℝ^24** — the unique even unimodular rootless lattice
- **Kissing number = 196560 = E·q²·Φ₃·Φ₆** = 240×9×13×7
- Leech/v = 4914 = λ·q³·Φ₆·Φ₃
- Monster–Leech gap: 196884 − 196560 = **324 = μ·b₁ = Delsarte abs bound**

### Shannon Capacity
- **Θ(G) = α = v/χ = 10** — tight Lovász bound achieved

### Partition Numbers
| p(n) | Value | W(3,3) expression |
|------|-------|--------------------|
| p(k)=p(12) | 77 | dim(E₆) − 1 |
| p(g)=p(15) | 176 | (k−1)(k+μ) |
| p(f)=p(24) | 1575 | g²·Φ₆ |

### Ramanujan Tau Function
- **τ(q) = τ(3) = 252 = E + k** = k·dim(C₃) from magic square
- **τ(λ) = τ(2) = −24 = −f**

### Modular Forms
- **η^f = η²⁴ = Δ**, weight(Δ) = k = 12
- **E₄**: weight = μ = 4, leading coeff = E = 240
- **E₆**: weight = k/λ = 6, coeff = −k(v+λ) = −504

"""

md += new_md_section
md_path.write_text(md, encoding="utf-8")
print("COMPLETE_SUMMARY.md updated to 295/295")
