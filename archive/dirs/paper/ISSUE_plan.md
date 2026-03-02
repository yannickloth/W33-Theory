Project plan & next steps (short-term)

1. Literature review: expand `paper/reading_list.md` and populate `paper/bibliography.bib` with canonical references; write short annotations.
2. Figures: implement reproducible scripts in `paper/figures/` and `scripts/` that generate key visuals (embedding plots, candidate distributions, solver performance); add `paper/figures/README.md` describing how to regenerate.
3. Manuscript: expand `paper/PAPER_DRAFT.md` with Methods, Results, Figures, and Related Work; prepare `paper/Makefile` to build PDF via pandoc/LaTeX.
4. CI: add a GitHub Actions workflow to build the manuscript and generate/upload figure artifacts (issue created: #63).
5. Formalization: identify promising conjectures from computational results, attempt to formalize them, and open PRs for any formal proofs or supporting code.

I'll start by expanding the reading list and adding 6–10 canonical references over the next task cycle, then implement a figure-generation script for candidate statistics.
