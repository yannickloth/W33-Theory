# Multi-Assistant Workflow

This repo now supports a three-lane setup for concurrent agents:

- `codex` lane: `work/codex-toe`
- `raptor` lane: `work/raptor-toe`
- `integration` lane: `work/integration-toe`

Each lane is an isolated git worktree to prevent branch collisions and merge-marker corruption.

## 1) One-time bootstrap

From any copy of this repo:

```powershell
pwsh tools/setup_multi_assistant_worktrees.ps1
```

Default worktree locations (sibling folders):

- `<repo>.codex`
- `<repo>.raptor`
- `<repo>.integration`

## 2) Daily operating model

1. Codex edits only in `<repo>.codex` on branch `work/codex-toe`.
2. Raptor edits only in `<repo>.raptor` on branch `work/raptor-toe`.
3. Neither assistant pushes directly to `master`.
4. Each assistant commits/pushes only its own lane branch.
5. Integration happens only in `<repo>.integration`.

## 3) Integrate both lanes

From any copy of this repo:

```powershell
pwsh tools/integrate_assistant_branches.ps1 -Push
```

This script:

1. Fetches remotes.
2. Ensures integration worktree is clean.
3. Fast-forwards `work/integration-toe` to `origin/master`.
4. Merges `work/codex-toe` and `work/raptor-toe` with merge commits.
5. Optionally pushes `work/integration-toe`.

## 4) Promote to master

After integration tests pass:

```powershell
git -C "<repo>.integration" checkout master
git -C "<repo>.integration" merge --ff-only work/integration-toe
git -C "<repo>.integration" push origin master
```

Use PR merge instead of direct push if you want review gates.

## 5) Conflict safety rules

- If a worktree becomes dirty unexpectedly, stop and inspect with `git status`.
- Do not run destructive resets in shared lanes.
- Keep large generated artifacts in dedicated commits so integration diffs stay readable.
