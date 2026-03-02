Add CI job to build manuscript and generate figures.

- Add a GitHub Actions workflow that installs TeXlive/pandoc (or uses a pre-built container) and builds `paper/PAPER_DRAFT.md` into PDF/HTML.
- Add a job step that runs figure generation scripts (from `paper/figures/` or `scripts/`) so figures are always up-to-date and artifacts are uploaded.
- Document the build in `CONTRIBUTING.md` and add a badge to README.
