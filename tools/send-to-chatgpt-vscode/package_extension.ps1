<#
Package the VS Code extension folder into a .vsix archive (simple zip-based pack).
This is a lightweight local packer (no vsce required) intended for local install via
VS Code: "Extensions: Install from VSIX..."

Usage (from this folder):
  powershell -NoProfile -ExecutionPolicy Bypass -File ./package_extension.ps1

Result:
  Creates ../send-to-chatgpt-<ts>.vsix containing the extension files.
#>

Param()

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Resolve-Path $here
$ts = [int][double]::Parse((Get-Date -UFormat %s))
$out = Join-Path $root "..\send-to-chatgpt-$ts.vsix"

# Remove existing vsix if present
if (Test-Path $out) { Remove-Item $out -Force }

# Compress the extension folder contents into the vsix archive
Push-Location $root
try {
  # Create a temporary zip file
  $tmp = Join-Path $env:TEMP ("send-to-chatgpt-$ts.zip")
  if (Test-Path $tmp) { Remove-Item $tmp -Force }
  Compress-Archive -Path * -DestinationPath $tmp -Force
  # Move/rename to .vsix
  Move-Item -Path $tmp -Destination $out -Force
  Write-Host "Created: $out"
} finally {
  Pop-Location
}

Write-Host "To install: open VS Code -> Extensions: Install from VSIX... -> select $out"
