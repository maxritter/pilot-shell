# QualityLayer bootstrap for native Windows. No administrator rights required.
# Download, verify SHA-256, then let the binary install its skills and settings.
[CmdletBinding()]
param(
    [string]$Version = $env:VERSION,
    [switch]$NonInteractive
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
if (-not $env:PATHEXT) { $env:PATHEXT = '.COM;.EXE;.BAT;.CMD' }
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$qlReleaseBase = if ($env:QUALITYLAYER_RELEASE_BASE) { $env:QUALITYLAYER_RELEASE_BASE } else { 'https://github.com/maxritter/pilot-shell/releases' }
$qlReleaseApi = if ($env:QUALITYLAYER_RELEASE_API) { $env:QUALITYLAYER_RELEASE_API } else { 'https://api.github.com/repos/maxritter/pilot-shell/releases?per_page=30' }
$qlHome = if ($env:HOME) { $env:HOME } else { $env:USERPROFILE }
if (-not $qlHome -or -not [IO.Path]::IsPathRooted($qlHome) -or -not (Test-Path -LiteralPath $qlHome -PathType Container)) {
    throw 'HOME or USERPROFILE must name an existing absolute user directory.'
}
$qlHome = (Get-Item -LiteralPath $qlHome).FullName
if ($qlHome.TrimEnd('\', '/') -eq [IO.Path]::GetPathRoot($qlHome).TrimEnd('\', '/')) {
    throw 'Refusing to install at the filesystem root.'
}
$env:HOME = $qlHome

# Use the OS architecture, even when PowerShell is running under x64 emulation on ARM.
$qlArch = if ($env:PROCESSOR_ARCHITEW6432) { $env:PROCESSOR_ARCHITEW6432 } else { $env:PROCESSOR_ARCHITECTURE }
$qlCpu = switch ($qlArch.ToUpperInvariant()) {
    'AMD64' { 'x64' }
    'ARM64' { 'arm64' }
    default { throw "Unsupported Windows CPU: $qlArch" }
}
$qlAsset = "qualitylayer-windows-$qlCpu.exe"
$qlWork = Join-Path ([IO.Path]::GetTempPath()) ("qualitylayer-install-" + [Guid]::NewGuid().ToString('N'))
[IO.Directory]::CreateDirectory($qlWork) | Out-Null
try {
    if (-not $Version) {
        $qlReleases = Invoke-RestMethod -Uri $qlReleaseApi
        $qlRelease = $qlReleases | Where-Object {
            -not $_.draft -and $_.tag_name -match '^v12\.' -and ($_.assets.name -contains $qlAsset)
        } | Select-Object -First 1
        if (-not $qlRelease) { throw "No QualityLayer 12 release carries $qlAsset." }
        $Version = $qlRelease.tag_name
    }
    $Version = $Version -replace '^v', ''
    if ($Version -notmatch '^12\.\d+\.\d+(?:-[A-Za-z0-9.-]+)?$') { throw "Invalid QualityLayer version: $Version" }
    $qlBase = "$qlReleaseBase/download/v$Version"
    $qlBinary = Join-Path $qlWork 'qualitylayer.exe'
    $qlChecksum = Join-Path $qlWork 'qualitylayer.sha256'
    Write-Host "Downloading QualityLayer $Version ($qlAsset)"
    Invoke-WebRequest -UseBasicParsing -Uri "$qlBase/$qlAsset" -OutFile $qlBinary
    Invoke-WebRequest -UseBasicParsing -Uri "$qlBase/$qlAsset.sha256" -OutFile $qlChecksum
    $qlExpected = ((Get-Content -LiteralPath $qlChecksum -Raw).Trim() -split '\s+')[0]
    if ($qlExpected -notmatch '^[0-9a-fA-F]{64}$') { throw 'The release checksum is invalid; nothing was installed.' }
    $qlActual = (Get-FileHash -LiteralPath $qlBinary -Algorithm SHA256).Hash
    if ($qlExpected -ne $qlActual) { throw 'Checksum mismatch; nothing was installed.' }
    Write-Host 'Checksum verified (SHA-256)'
    $qlArguments = @('install')
    if ($NonInteractive -or [Console]::IsInputRedirected) { $qlArguments += '--non-interactive' }
    & $qlBinary @qlArguments
    if ($LASTEXITCODE -ne 0) { throw "QualityLayer install failed (exit $LASTEXITCODE)." }
    $qlBinDir = Join-Path $qlHome '.qualitylayer\bin'
    # Current terminal only; the installer prints the command to add to a PowerShell profile.
    if (($env:Path -split ';') -notcontains $qlBinDir) { $env:Path = "$qlBinDir;$env:Path" }
} finally {
    Remove-Item -LiteralPath $qlWork -Recurse -Force -ErrorAction SilentlyContinue
}
