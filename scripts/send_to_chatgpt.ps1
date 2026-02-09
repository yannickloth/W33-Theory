<#
PowerShell helper: copy input (or piped text) to clipboard and optionally open ChatGPT web.
Usage examples:
  Get-Content file.py | .\scripts\send_to_chatgpt.ps1 -Open
  .\scripts\send_to_chatgpt.ps1 "Explain this function" -Open
#>
param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$Text,
  [switch]$Open
)

$incoming = $null
if ($Text -and $Text.Length -gt 0) {
  $incoming = $Text -join ' '
} else {
  $stdin = [Console]::In.ReadToEnd()
  if ($stdin -and $stdin.Trim() -ne '') { $incoming = $stdin }
}

if (-not $incoming -or $incoming.Trim() -eq '') {
  Write-Host "No input supplied. Provide text as argument or pipe content. Example: Get-Content file.py | .\scripts\send_to_chatgpt.ps1 -Open"
  exit 1
}

Set-Clipboard -Value $incoming
if ($Open) {
  Start-Process "https://chat.openai.com/chat"
}
Write-Host "Copied to clipboard; open ChatGPT and paste (Ctrl+V) into the chat input. Select GPT‑5.2 and send to save to your ChatGPT history (if your plan supports it)."
