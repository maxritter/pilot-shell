# Check Authenticode signatures of shipped Windows files.
#
# Profile mode (default, after the windows-signing action enabled signing): every file must have a
# Valid, timestamped signature whose signer certificate belongs to the Artifact Signing profile
# in QUALITYLAYER_WINDOWS_SIGNING_PROFILE. The profile is re-read now, so a certificate issued
# during this run's signing is listed; its subject is the validated identity, not a hand-set value.
#
# -Consistent (a job without Azure access): either every file is unsigned (a build whose
# preflight found no profile; a warning) or every file is validly signed and timestamped by one
# and the same subject. A mix fails.
param(
  [Parameter(Mandatory = $true)][string[]]$Path,
  [switch]$Consistent
)
$ErrorActionPreference = 'Stop'

# X.500 names list their parts in different orders depending on who prints them.
function Normalize([string]$subject) {
  if ([string]::IsNullOrWhiteSpace($subject)) { return '' }
  (($subject -split ',\s*(?=(?:[A-Za-z]+|OID\.[0-9.]+)=)') | ForEach-Object { $_.Trim() } | Sort-Object) -join ', '
}

$signatures = foreach ($file in $Path) {
  if (-not (Test-Path -LiteralPath $file -PathType Leaf)) { throw "Missing file to verify: $file" }
  $signature = Get-AuthenticodeSignature -LiteralPath $file
  Write-Output ("{0}: {1}; signer '{2}' ({3}); timestamp by '{4}'" -f $file, $signature.Status, $signature.SignerCertificate.Subject, $signature.SignerCertificate.Thumbprint, $signature.TimeStamperCertificate.Subject) | Out-Host
  [pscustomobject]@{ File = $file; Signature = $signature }
}

$failed = @()
if ($Consistent) {
  $unsigned = @($signatures | Where-Object { $_.Signature.Status -eq 'NotSigned' })
  if ($unsigned.Count -eq $signatures.Count) {
    Write-Output '::warning title=Windows build is NOT code-signed::No shipped Windows file carries an Authenticode signature; the signing preflight found no active certificate profile.'
    exit 0
  }
  $subjects = @($signatures | ForEach-Object { Normalize $_.Signature.SignerCertificate.Subject } | Sort-Object -Unique)
  if ($subjects.Count -ne 1) { $failed += "signers differ: $($subjects -join ' | ')" }
} else {
  if ([string]::IsNullOrWhiteSpace($env:QUALITYLAYER_WINDOWS_SIGNING_PROFILE)) {
    throw 'QUALITYLAYER_WINDOWS_SIGNING_PROFILE is not set: run the windows-signing action first'
  }
  $json = az rest --method get --url "https://management.azure.com$($env:QUALITYLAYER_WINDOWS_SIGNING_PROFILE)?api-version=2025-10-13"
  if ($LASTEXITCODE -ne 0) { throw 'The certificate profile cannot be read to verify its signatures' }
  $certificates = @((($json | Out-String) | ConvertFrom-Json).properties.certificates | Where-Object { $_ })
  if ($certificates.Count -eq 0) { throw 'The certificate profile lists no certificates' }
  $thumbprints = @($certificates | ForEach-Object { "$($_.thumbprint)".ToUpperInvariant() })
  $subjects = @($certificates | ForEach-Object { Normalize $_.subjectName })
  Write-Output "Profile certificates: $($certificates.Count); subjects: $(($subjects | Sort-Object -Unique) -join ' | ')"
}

foreach ($entry in $signatures) {
  $signature = $entry.Signature
  $signer = $signature.SignerCertificate
  if ($signature.Status -ne 'Valid') { $failed += "$($entry.File) ($($signature.Status): $($signature.StatusMessage))"; continue }
  if ($null -eq $signature.TimeStamperCertificate) { $failed += "$($entry.File) (no timestamp)"; continue }
  if (-not $Consistent) {
    $ours = ($thumbprints -contains $signer.Thumbprint.ToUpperInvariant()) -or ($subjects -contains (Normalize $signer.Subject))
    if (-not $ours) { $failed += "$($entry.File) (signer '$($signer.Subject)' is not a certificate of the profile)" }
  }
}
if ($failed.Count -gt 0) {
  throw "Authenticode verification failed:`n  $($failed -join "`n  ")"
}
Write-Output "Authenticode verified: $($signatures.Count) file(s)."
