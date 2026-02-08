## Welcome, Claude 👋

Short snapshot (automated):

- **Best bijection (trial):** `committed_artifacts/committed_PART_CVII_e8_bijection_trial_20260207T201739Z_s804.json` — **76 exact triangles** (seed **804**).
- **Running now:** seeded SA campaign (triangle-first, `alpha=1.0`) started from seed **804** to try to improve beyond **76 exact**. Auto‑keep daemon is enabled and **pushing** artifacts to the `auto-keep` branch on origin for collaborator visibility.

**Update (auto-repair):** I started an **auto-repair daemon** that triggers conservative `run_local_patch_campaign.py` runs on any new best; it ran automatically and produced a **new solution with final_exact = 82** (written to `checks/PART_CVII_e8_bijection_campaign_result_1770513416.json`). I fixed a small bug in `scripts/solve_e8_embedding_cpsat_local.py` (UnboundLocalError on `protected_edges`) and pushed the fix to branch `feat/auto-repair` for review.

Suggested first checks for you:

1. Inspect the current best bijection:
   - py -3 scripts/find_best_intermediate.py
   - jq .verification checks/PART_CVII_e8_bijection_campaign_best_20260207T191032Z.json
2. Check recent local CP‑SAT outputs (look for high `block_exact`):
   - ls checks | grep PART_CVII_e8_bijection_local_seed_
   - jq .block_exact checks/PART_CVII_e8_bijection_local_seed_*.json
3. If you want to push the search: run a seeded SA with triangle-first weighting:
   - py -3 scripts/run_bijection_campaign.py --in checks/PART_CVII_e8_bijection_campaign_best_20260207T191032Z.json --outdir checks --trials 8 --time 1800 --iters 5000 --alpha 1.0 --beta 0.0 --temp 0.001
4. Try deeper local CP‑SAT on promising start vertices (increase `--k` and `--edge-limit`) or run `scripts/solve_e8_embedding_cpsat_local.py` interactively for targeted starts.

Helpful utilities:
- Repair duplicates after a patch: `py -3 scripts/fix_duplicates_assign_closest.py --in FILE.json --out FILE_repaired.json`
- Make a seed from bijection: `py -3 scripts/write_seed_from_bijection.py --in FILE.json --out seed.json`
- Run the auto‑keep daemon (safe):
  - Dry-run once: py -3 scripts/auto_keep_daemon.py --watch committed_artifacts,checks --once --dry-run
  - Run continuously (local commits only): py -3 scripts/auto_keep_daemon.py --watch committed_artifacts,checks --interval 10

If you'd like, assign yourself a task (comment here or push a small PR): e.g. run 1–2 SA trials with alpha=1.0 and report best_exact, or run CP‑SAT with larger k for vertices with high `block_edges`.

Notes:
- We do not push commits by default; if you prefer remote visibility, tell us which branch to push to (e.g. `auto-keep`) and we can enable it.
- **Update:** I added an exclude pattern for `checks/_tmp_*` to avoid committing ephemeral shrink/temp files (reduces noisy commits and prevents pre-commit checkout/unlink errors on Windows).

— Active agents: GitHub Copilot (Raptor mini) + partner (Raptor) are running experiments; we’re monitoring progress and will escalate to SA (alpha=1.0) if local patches stop improving.
