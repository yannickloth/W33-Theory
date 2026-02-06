Param(
    [int]$pr = 30,
    [string]$repo = "wilcompute/W33-Theory",
    [int]$interval = 30,
    [int]$timeoutMinutes = 120
)

$deadline = (Get-Date).AddMinutes($timeoutMinutes)
while ((Get-Date) -lt $deadline) {
    try {
        $jsonText = gh pr view $pr --repo $repo --json statusCheckRollup,mergeable,mergeStateStatus
        $json = $jsonText | ConvertFrom-Json
    } catch {
        Write-Output "gh command failed, retrying in $interval sec..."
        Start-Sleep -Seconds $interval
        continue
    }
    $checks = $json.statusCheckRollup
    $allCompleted = $true
    $allSuccess = $true
    if (-not $checks) {
        $allCompleted = $false
        $allSuccess = $false
    } else {
        foreach ($c in $checks) {
            if ($c.status -ne 'COMPLETED') { $allCompleted = $false; break }
            if ($c.conclusion -ne 'SUCCESS') { $allSuccess = $false; break }
        }
    }
    if ($allCompleted -and $allSuccess -and $json.mergeable -eq 'MERGEABLE') {
        Write-Output "All checks green and mergeable — merging now (squash)"
        gh pr merge $pr --repo $repo --squash --delete-branch --body "Auto-merged on green checks (squash)." --title "Auto-merge PR #$pr (squash)"
        exit 0
    } else {
        Write-Output "Not ready: mergeable=$($json.mergeable) allCompleted=$allCompleted allSuccess=$allSuccess time=$(Get-Date)"
        Start-Sleep -Seconds $interval
    }
}
Write-Output "Timeout waiting for checks to pass"
exit 1
