param(
    [switch]$Execute
)

$ErrorActionPreference = "Stop"

Write-Host "Workspace cleanup preview (collaboration-safe)" -ForegroundColor Cyan
if ($Execute) {
    Write-Host "Mode: EXECUTE"
} else {
    Write-Host "Mode: DRY-RUN"
}
Write-Host ""

# Keep cleanup limited to common disposable caches/logs.
$targets = @(
    ".pytest_cache",
    ".mypy_cache",
    "__pycache__",
    "tmpclaude-*",
    "*.log",
    "*.aux",
    "*.out",
    "*.toc"
)

Write-Host "Target patterns:"
$targets | ForEach-Object { Write-Host "  - $_" }
Write-Host ""

# Show ignored files that would be removable without touching tracked content.
Write-Host "git clean preview (ignored files only, non-recursive overview):" -ForegroundColor Yellow
git clean -ndX
Write-Host ""

if (-not $Execute) {
    Write-Host "No files removed. Re-run with -Execute to apply cleanup." -ForegroundColor Green
    exit 0
}

Write-Host "Executing cleanup (ignored files only)..." -ForegroundColor Yellow
git clean -fdX
Write-Host "Cleanup complete." -ForegroundColor Green
