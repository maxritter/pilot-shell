# Authenticode-sign files with the command the windows-signing action exported
# (QUALITYLAYER_WINDOWS_SIGN_COMMAND, the same one Tauri's signCommand runs).
param([Parameter(Mandatory = $true)][string[]]$Path)
$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($env:QUALITYLAYER_WINDOWS_SIGN_COMMAND)) {
  throw 'QUALITYLAYER_WINDOWS_SIGN_COMMAND is not set: run the windows-signing action first'
}
$command = $env:QUALITYLAYER_WINDOWS_SIGN_COMMAND | ConvertFrom-Json
foreach ($file in $Path) {
  $full = (Resolve-Path -LiteralPath $file).Path
  $signArgs = @($command.args | ForEach-Object { if ($_ -eq '%1') { $full } else { $_ } })
  & $command.cmd @signArgs
  if ($LASTEXITCODE -ne 0) { throw "Signing $full failed ($LASTEXITCODE)" }
}
