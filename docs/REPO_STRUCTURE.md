# Repository Structure

This repo is large. The active theorem/program surfaces are concentrated in a
few directories; a large amount of historical computation and bundled output is
preserved alongside them.

## Start Here

- [README.md](/mnt/c/Repos/Theory of Everything/README.md): top-level project summary and reading route
- [docs/index.html](/mnt/c/Repos/Theory of Everything/docs/index.html): live public paper / promoted theorem surface
- [docs/march_2026_frontier_note.md](/mnt/c/Repos/Theory of Everything/docs/march_2026_frontier_note.md): current frontier and open wall

## Active Research Surfaces

- `exploration/`: exact theorem builders and bridge summaries
- `tests/`: targeted theorem regressions and search checks
- `tools/qiskit/`: local Qiskit workflow and discrete search/oracle tooling
- `tools/qiskit/bridge_oracle_ledger.json`: promoted local Qiskit bridge-oracle stack and operating points
- `tools/`: helper programs that are still part of the active research stack

## Heavy but Important Context

- `docs/`: public-facing notes, HTML surfaces, and supporting writeups
- `artifacts/`: small committed fixtures needed by live scripts/tests
- `data/atlas/`: vendored offline data kept in-repo for verification

## Historical / Archive Weight

- `archive/`: preserved historical notes, bundles, and migrated material
- `bundles/`: large generated or staged computation output
- `V*_output*/`: phase or pilot output drops
- `extracted_v*/`: preserved extracted snapshots

## Local Hygiene Policy

- Root-level deliverable zips and extracted bundle drops are treated as local
  drop artifacts, not primary repo structure.
- Generated helper output under `tools/artifacts/` is local scratch unless
  deliberately promoted elsewhere.
- If you need an inventory of current worktree clutter, run:

```bash
python3 tools/repo_cleanup_audit.py
```

The cleanup goal is not to hide active source work. It is to keep the live
entrypoints readable while preserving historical material and local research
drops without letting them overwhelm the repo root.
