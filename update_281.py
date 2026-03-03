"""Update docs to 281/281 — PART VII-C: Golay Code, E₈ Lattice & Ramanujan Bound."""
import pathlib

root = pathlib.Path(r"c:\Repos\Theory of Everything\docs")

# ── index.html ──
html_path = root / "index.html"
html = html_path.read_text(encoding="utf-8")
html = html.replace("267/267", "281/281")
html = html.replace("267 checks", "281 checks")

new_html_section = """
        <div class="result-card">
            <h3>&#9733; PART VII-C: Golay Code, E&#x2088; Lattice &amp; Ramanujan Bound (checks 268-281)</h3>
            <p>The <strong>E&#x2088; lattice kissing number = 240 = E</strong> (edges of W(3,3)).
               The 240 roots decompose as D&#x2088; roots + half-spinor:
               2&middot;rank(E&#x2088;)&middot;&Phi;<sub>6</sub> + 2<sup>&Phi;<sub>6</sub></sup>
               = 2&times;8&times;7 + 2<sup>7</sup> = 112 + 128 = 240.</p>
            <p><strong>Ramanujan:</strong> max(|r|,|s|) = 4 &lt; 2&radic;(k&minus;1) = 6.633 &mdash;
               W(3,3) is an <em>optimal expander</em>.</p>
            <p><strong>Lov&aacute;sz &theta; bounds (TIGHT):</strong> &theta;(G)=10=&alpha;,
               &theta;(&#x1D53E;)=4=&omega;=&chi; &mdash; Lov&aacute;sz sandwich equality both
               sides!</p>
            <div class="highlight">
            <strong>&#9733; Extended binary Golay code [24,12,8] = [f, k, rank(E&#x2088;)] &#9733;</strong><br>
            The densest known code has: length = f = 24, dimension = k = 12,
            min distance = rank(E&#x2088;) = 8 = k&minus;&mu;.<br>
            |Golay| = 2<sup>k</sup> = 4096 codewords.
            Steiner system S(5,8,24) = S(q+r, k&minus;&mu;, f) with
            759 = q&middot;(k&minus;1)&middot;(f&minus;1) = 3&times;11&times;23 blocks.<br>
            <strong>M&#x2082;&#x2084; prime factors</strong> = {&lambda;, q, q+r, &Phi;<sub>6</sub>, k&minus;1, f&minus;1}
            = {2,3,5,7,11,23}.<br>
            Catalan C<sub>q</sub> = C<sub>3</sub> = 5 = q + r.<br>
            von Staudt&ndash;Clausen: denom(B<sub>f</sub>) =
            &lambda;&middot;q&middot;(q+r)&middot;&Phi;<sub>6</sub>&middot;&Phi;<sub>3</sub> = 2730.<br>
            dim(D&#x2084;) = SO(8) = 28 = v&minus;k; D&#x2084; triality: 3&times;8 = 24 = f.
            </div>
        </div>
"""
html = html.replace("</main>", new_html_section + "\n        </main>")
html_path.write_text(html, encoding="utf-8")
print("index.html updated to 281/281")

# ── COMPLETE_SUMMARY.md ──
md_path = root / "COMPLETE_SUMMARY.md"
md = md_path.read_text(encoding="utf-8")
md = md.replace("267/267", "281/281")
md = md.replace("267 checks", "281 checks")

new_md_section = """
---

## PART VII-C: Golay Code, E₈ Lattice & Ramanujan Bound (checks 268-281)

### E₈ Lattice
- **Kissing number = 240 = E** — sphere packing in dim rank(E₈)=8
- Root decomposition: E = 2·rank(E₈)·Φ₆ + 2^Φ₆ = 112 + 128 (D₈ + half-spinor)

### Ramanujan & Lovász
- **Ramanujan:** max(|r|,|s|) = 4 < 2√(k−1) ≈ 6.633 → optimal expander
- **θ(G) = α = 10** (tight Lovász bound)
- **θ(Ḡ) = ω = χ = 4** (Lovász sandwich equality both sides!)

### ★ Extended Golay Code [24, 12, 8] = [f, k, rank(E₈)] ★

The densest known binary code has parameters that ARE the W(3,3) parameters:
| Parameter | Golay | W(3,3) |
|-----------|-------|--------|
| Length | 24 | f (multiplicity of r) |
| Dimension | 12 | k (degree) |
| Min distance | 8 | rank(E₈) = k−μ |
| Codewords | 4096 | 2^k |

### Steiner System & Mathieu Group
- S(5,8,24) = S(q+r, k−μ, f) — the unique Steiner 5-design
- 759 blocks = q·(k−1)·(f−1) = 3×11×23
- M₂₄ prime factors = {λ, q, q+r, Φ₆, k−1, f−1} = {2,3,5,7,11,23}

### Additional Identities
- Catalan C_q = C₃ = 5 = q + r
- von Staudt–Clausen: denom(B_f) = λ·q·(q+r)·Φ₆·Φ₃ = 2730
- dim(D₄) = SO(8) = 28 = v−k (non-neighbours per vertex)
- D₄ triality: 3 reps × dim 8 = q × rank(E₈) = 24 = f

"""

md += new_md_section
md_path.write_text(md, encoding="utf-8")
print("COMPLETE_SUMMARY.md updated to 281/281")
