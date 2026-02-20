Title: feat(monster + linfty): Pillars 58–60, M12-144 permrep, CE2 → l4 repairs

Summary
- Implements Pillars 58–60 and adds unit tests and docs updates.
- Adds Monster permrep suborbit metadata (M12 degree‑144) and accompanying tests.
- Repairs L_infty closure for failing mixed-sector triples: computes rational CE2 U/V, persists to artifact, and attaches an l4 prototype. Adds SNF/PSLQ verification artifacts.
- Small formatting / pre-commit fixes applied.

Files/areas changed (high level)
- tools/: CE2 repair helpers, L_infty attachers, SNF/PSLQ certificate tools
- artifacts/: persisted CE2 rational local solutions and PSLQ/SNF reports
- scripts/tests: Monster permrep signatures + centralizer tests; Pillars 58–60 tests

How to review / test
1. Run unit tests: `./.venv/Scripts/python.exe -m pytest -q` (should pass).
2. Quick verifier: `tools/exhaustive_homotopy_check_rationalized_l3.py` (will use persisted artifacts).
3. (Optional) Full canonical assembly: `tools/assemble_exact_l4_from_local_ce2.py` — CPU heavy.

Artifacts included
- patches/patches/fix-he-permrep-association/*.patch — patch files if you need to apply remotely.
- artifacts/ce2_rational_local_solutions.json (CE2 U/V persisted)
- artifacts/pslq_snf_ce2_uv_check.json (PSLQ/SNF checks)

Notes
- I configured a HTTPS remote fallback and an SSH-over-443 option in `~/.ssh/config`.
  - SSH-over-443 may be blocked on some networks (tested: timed out here).
  - HTTPS remote (origin-https) is available and `origin` push URL was set to HTTPS in this repo to ensure `git push` works when network allows.
- If network push still fails from this machine, apply the patches via `git am patches/fix-he-permrep-association/*.patch` on another machine and open a PR.

Checklist
- [x] Unit tests added/updated
- [x] CE2 artifacts persisted and SNF/PSLQ checks generated
- [x] Branch ready for PR: `fix/he-permrep-association`

Suggested reviewers: @wilcompute

---
Apply patches locally (if needed):
  git am patches/fix-he-permrep-association/*.patch

If you'd like, I can open the PR on GitHub for you (requires network access).
