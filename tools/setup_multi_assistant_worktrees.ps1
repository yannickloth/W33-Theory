param(
    [string]$RepoPath = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [string]$BaseRef = "origin/master",
    [string]$CodexBranch = "work/codex-toe",
    [string]$RaptorBranch = "work/raptor-toe",
    [string]$IntegrationBranch = "work/integration-toe",
    [string]$CodexPath = "",
    [string]$RaptorPath = "",
    [string]$IntegrationPath = ""
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

function Test-BranchExists {
    param(
        [string]$WorkingDir,
        [string]$BranchName
    )
    & git -C $WorkingDir rev-parse --verify --quiet "refs/heads/$BranchName" *> $null
    return $LASTEXITCODE -eq 0
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

function Ensure-Worktree {
    param(
        [string]$WorkingDir,
        [string]$BranchName,
        [string]$PathName,
        [string]$BaseRefName
    )

    $existingPath = Get-WorktreePathForBranch -WorkingDir $WorkingDir -BranchName $BranchName
    if ($existingPath) {
        if ((Resolve-Path $existingPath).Path -eq $PathName -or $existingPath -eq $PathName) {
            Write-Host "[skip] branch already mapped: $BranchName -> $existingPath"
        }
        else {
            Write-Host "[skip] branch already mapped elsewhere: $BranchName -> $existingPath"
        }
        return
    }

    if (Test-Path $PathName) {
        Write-Host "[skip] worktree path exists: $PathName"
        return
    }

    if (Test-BranchExists -WorkingDir $WorkingDir -BranchName $BranchName) {
        Write-Host "[add] existing branch -> worktree: $BranchName -> $PathName"
        Invoke-Git -WorkingDir $WorkingDir worktree add $PathName $BranchName
    }
    else {
        Write-Host "[create] branch + worktree: $BranchName -> $PathName (base $BaseRefName)"
        Invoke-Git -WorkingDir $WorkingDir worktree add -b $BranchName $PathName $BaseRefName
    }
}

$mainRepoPath = Get-MainRepoPath -WorkingDir $RepoPath
$repoParent = Split-Path $mainRepoPath -Parent
$repoName = Split-Path $mainRepoPath -Leaf

if ([string]::IsNullOrWhiteSpace($CodexPath)) {
    $CodexPath = Join-Path $repoParent "$repoName.codex"
}
if ([string]::IsNullOrWhiteSpace($RaptorPath)) {
    $RaptorPath = Join-Path $repoParent "$repoName.raptor"
}
if ([string]::IsNullOrWhiteSpace($IntegrationPath)) {
    $IntegrationPath = Join-Path $repoParent "$repoName.integration"
}

Write-Host "[fetch] syncing remotes from $RepoPath"
Invoke-Git -WorkingDir $RepoPath fetch origin --prune

Ensure-Worktree -WorkingDir $RepoPath -BranchName $CodexBranch -PathName $CodexPath -BaseRefName $BaseRef
Ensure-Worktree -WorkingDir $RepoPath -BranchName $RaptorBranch -PathName $RaptorPath -BaseRefName $BaseRef
Ensure-Worktree -WorkingDir $RepoPath -BranchName $IntegrationBranch -PathName $IntegrationPath -BaseRefName $BaseRef

Write-Host ""
Write-Host "Worktree setup complete."
Write-Host "  codex:       $CodexPath  [$CodexBranch]"
Write-Host "  raptor:      $RaptorPath [$RaptorBranch]"
Write-Host "  integration: $IntegrationPath [$IntegrationBranch]"
Write-Host ""
Write-Host "Current worktree map:"
& git -C $RepoPath worktree list
