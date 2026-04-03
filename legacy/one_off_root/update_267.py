"""Update docs to 267/267 — PART VII-B: Freudenthal-Tits Magic Square."""
import pathlib, re

root = pathlib.Path(r"c:\Repos\Theory of Everything\docs")

# ── index.html ──
html_path = root / "index.html"
html = html_path.read_text(encoding="utf-8")
html = html.replace("253/253", "267/267")
html = html.replace("253 checks", "267 checks")

new_html_section = """
        <div class="result-card">
            <h3>&#9733; PART VII-B: Freudenthal-Tits Magic Square (checks 254-267)</h3>
            <p>The 4&times;4 Freudenthal-Tits magic square M(A,B) for composition algebras
               A,B &isin; {&Ropf;,&Copf;,&Hopf;,&Oopf;} generates <strong>every</strong>
               exceptional Lie algebra. We show all 10 unique entries are closed-form
               expressions of W(3,3) SRG parameters:</p>
            <table style="margin:0.5em auto;border-collapse:collapse;text-align:center">
            <tr><th></th><th>&Ropf;</th><th>&Copf;</th><th>&Hopf;</th><th>&Oopf;</th></tr>
            <tr><td>&Ropf;</td><td>A<sub>1</sub>(3)=q</td><td>A<sub>2</sub>(8)=k&minus;&mu;</td>
                <td>C<sub>3</sub>(21)=C(&Phi;<sub>6</sub>,2)</td><td>F<sub>4</sub>(52)=v+k</td></tr>
            <tr><td>&Copf;</td><td>A<sub>2</sub>(8)</td><td>A<sub>2</sub>&oplus;A<sub>2</sub>(16)=k+&mu;=s&sup2;</td>
                <td>A<sub>5</sub>(35)=C(&Phi;<sub>6</sub>,3)</td><td>E<sub>6</sub>(78)=2v&minus;&lambda;</td></tr>
            <tr><td>&Hopf;</td><td>C<sub>3</sub>(21)</td><td>A<sub>5</sub>(35)</td>
                <td>D<sub>6</sub>(66)=C(k,2)</td><td>E<sub>7</sub>(133)=vq+&Phi;<sub>3</sub></td></tr>
            <tr><td>&Oopf;</td><td>F<sub>4</sub>(52)</td><td>E<sub>6</sub>(78)</td>
                <td>E<sub>7</sub>(133)</td><td>E<sub>8</sub>(248)=E+k&minus;&mu;</td></tr>
            </table>
            <div class="highlight">
            <strong>Row sums:</strong><br>
            Row &Ropf; = 84 = C(q&sup2;,3)&emsp;|&emsp;
            <span style="color:#e63946;font-weight:bold">Row &Copf; = 137 = &lfloor;&alpha;<sup>&minus;1</sup>&rfloor; (FINE STRUCTURE CONSTANT!)</span>&emsp;|&emsp;
            Row &Hopf; = 255 = 2<sup>rank(E<sub>8</sub>)</sup>&minus;1&emsp;|&emsp;
            Row &Oopf; = 511 = 2<sup>q&sup2;</sup>&minus;1<br>
            <span style="color:#e63946;font-weight:bold">Total = 987 = F<sub>16</sub> = Fibonacci(k+&mu;)!</span><br>
            Row &Oopf; &minus; Row &Hopf; = 256 = 2<sup>rank(E<sub>8</sub>)</sup> = s<sup>4</sup><br>
            2-step return probability on W(3,3) = 1/k = 1/12
            </div>
        </div>
"""

# Insert before the closing </main> or before the summary/footer
html = html.replace("</main>", new_html_section + "\n        </main>")
html_path.write_text(html, encoding="utf-8")
print("index.html updated to 267/267")

# ── COMPLETE_SUMMARY.md ──
md_path = root / "COMPLETE_SUMMARY.md"
md = md_path.read_text(encoding="utf-8")
md = md.replace("253/253", "267/267")
md = md.replace("253 checks", "267 checks")

new_md_section = """
---

## PART VII-B: Freudenthal-Tits Magic Square (checks 254-267)

The **4×4 Freudenthal-Tits magic square** M(A,B) for composition algebras
A,B ∈ {ℝ,ℂ,ℍ,𝕆} generates every exceptional Lie algebra.
**Every entry** is a closed-form expression of W(3,3) SRG parameters:

|       | ℝ           | ℂ                 | ℍ              | 𝕆                |
|-------|-------------|--------------------|----------------|-------------------|
| **ℝ** | A₁(3)=q     | A₂(8)=k−μ         | C₃(21)=C(Φ₆,2) | F₄(52)=v+k       |
| **ℂ** | A₂(8)       | A₂⊕A₂(16)=k+μ=s²  | A₅(35)=C(Φ₆,3) | E₆(78)=2v−λ      |
| **ℍ** | C₃(21)      | A₅(35)             | D₆(66)=C(k,2)  | E₇(133)=vq+Φ₃    |
| **𝕆** | F₄(52)      | E₆(78)             | E₇(133)        | E₈(248)=E+k−μ    |

### Row sums
| Row | Sum | Formula |
|-----|-----|---------|
| ℝ   | 84  | C(q²,3) = C(9,3) |
| **ℂ** | **137** | **⌊α⁻¹⌋ — THE FINE STRUCTURE CONSTANT!** |
| ℍ   | 255 | 2^rank(E₈)−1 = 2⁸−1 (Mersenne) |
| 𝕆   | 511 | 2^(q²)−1 = 2⁹−1 (Mersenne) |
| **Total** | **987** | **F₁₆ = Fibonacci(k+μ) !!** |

- Row 𝕆 − Row ℍ = 256 = 2^rank(E₈) = s⁴
- 2-step random walk return probability = 1/k = 1/12

"""

md += new_md_section
md_path.write_text(md, encoding="utf-8")
print("COMPLETE_SUMMARY.md updated to 267/267")
