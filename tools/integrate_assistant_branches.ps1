param(
    [string]$RepoPath = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [string]$IntegrationWorktree = "",
    [string]$IntegrationBranch = "work/integration-toe",
    [string]$BaseRef = "origin/master",
    [string[]]$SourceBranches = @("work/codex-toe", "work/raptor-toe"),
    [switch]$Push
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-MainRepoPath {
    param([string]$WorkingDir)
    $commonRaw = (& git -C $WorkingDir rev-parse --git-common-dir).Trim()
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to resolve git common dir from '$WorkingDir'"
    }
    if ([System.IO.Path]::IsPathRooted($commonRaw)) {
        $commonPath = $commonRaw
    }
    else {
        $commonPath = (Resolve-Path (Join-Path $WorkingDir $commonRaw)).Path
    }
    return (Split-Path $commonPath -Parent)
}

function Invoke-Git {
    param(
        [string]$WorkingDir,
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$Args
    )
    & git -C $WorkingDir @Args
    if ($LASTEXITCODE -ne 0) {
        throw "git command failed in '$WorkingDir': git $($Args -join ' ')"
    }
}

function Get-WorktreePathForBranch {
    param(
        [string]$WorkingDir,
        [string]$BranchName
    )
    $lines = & git -C $WorkingDir worktree list --porcelain
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to list worktrees from '$WorkingDir'"
    }
    $currentPath = ""
    foreach ($line in $lines) {
        if ($line.StartsWith("worktree ")) {
            $currentPath = $line.Substring(9).Trim()
            continue
        }
        if ($line -eq "branch refs/heads/$BranchName") {
            return $currentPath
        }
    }
    return ""
}

function Assert-CleanWorktree {
    param([string]$WorkingDir)
    $status = (& git -C $WorkingDir status --porcelain)
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to read git status for $WorkingDir"
    }
    if ($status) {
        throw "Worktree is dirty: $WorkingDir. Commit/stash changes first."
    }
}

if ([string]::IsNullOrWhiteSpace($IntegrationWorktree)) {
    $mappedPath = Get-WorktreePathForBranch -WorkingDir $RepoPath -BranchName $IntegrationBranch
    if ($mappedPath) {
        $IntegrationWorktree = $mappedPath
    }
    else {
        $mainRepoPath = Get-MainRepoPath -WorkingDir $RepoPath
        $repoParent = Split-Path $mainRepoPath -Parent
        $repoName = Split-Path $mainRepoPath -Leaf
        $IntegrationWorktree = Join-Path $repoParent "$repoName.integration"
    }
}

if (-not (Test-Path $IntegrationWorktree)) {
    throw "Integration worktree not found: $IntegrationWorktree. Run setup_multi_assistant_worktrees.ps1 first."
}

Write-Host "[fetch] sync remotes"
Invoke-Git -WorkingDir $RepoPath fetch origin --prune

Write-Host "[verify] integration worktree is clean"
Assert-CleanWorktree -WorkingDir $IntegrationWorktree

Write-Host "[checkout] $IntegrationBranch"
Invoke-Git -WorkingDir $IntegrationWorktree checkout $IntegrationBranch

Write-Host "[update] fast-forward integration branch to $BaseRef"
Invoke-Git -WorkingDir $IntegrationWorktree merge --ff-only $BaseRef

foreach ($source in $SourceBranches) {
    Write-Host "[merge] $source -> $IntegrationBranch"
    Invoke-Git -WorkingDir $IntegrationWorktree merge --no-ff --no-edit $source
}

Write-Host "[status] final branch state"
& git -C $IntegrationWorktree status -sb

if ($Push) {
    Write-Host "[push] origin/$IntegrationBranch"
    Invoke-Git -WorkingDir $IntegrationWorktree push origin $IntegrationBranch
}
else {
    Write-Host "[skip] push disabled. Re-run with -Push to publish integration branch."
}
