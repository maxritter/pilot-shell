# QualityLayer bootstrap for native Windows. No administrator rights required.
# Native Windows always has a screen, so it gets the QualityLayer App: the per-user setup is
# downloaded, verified against its SHA-256 and run silently, then the App's own command line
# installs its skills and settings and a small launcher takes the path agents call.
# -CliOnly installs the command line alone, as before. WSL2 uses install.sh inside the distribution.
[CmdletBinding()]
param(
    [string]$Version = $env:VERSION,
    [switch]$NonInteractive,
    [switch]$CliOnly
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
# What a release has to carry for this install: the App's setup, or with -CliOnly the command line.
$qlWanted = { param($qlTag) if ($CliOnly) { $qlAsset } else { "QualityLayer-$($qlTag -replace '^v', '')-$qlCpu-setup.exe" } }
$qlWork = Join-Path ([IO.Path]::GetTempPath()) ("qualitylayer-install-" + [Guid]::NewGuid().ToString('N'))
[IO.Directory]::CreateDirectory($qlWork) | Out-Null

# Save-Verified <file in the release> <where to put it>: the file and its .sha256, checked before
# anything is installed.
function Save-Verified([string]$Name, [string]$Destination) {
    Invoke-WebRequest -UseBasicParsing -Uri "$qlBase/$Name" -OutFile $Destination
    Invoke-WebRequest -UseBasicParsing -Uri "$qlBase/$Name.sha256" -OutFile "$Destination.sha256"
    $qlExpected = ((Get-Content -LiteralPath "$Destination.sha256" -Raw).Trim() -split '\s+')[0]
    if ($qlExpected -notmatch '^[0-9a-fA-F]{64}$') { throw 'The release checksum is invalid; nothing was installed.' }
    $qlActual = (Get-FileHash -LiteralPath $Destination -Algorithm SHA256).Hash
    if ($qlExpected -ne $qlActual) { throw 'Checksum mismatch; nothing was installed.' }
}

try {
    if (-not $Version) {
        $qlReleases = Invoke-RestMethod -Uri $qlReleaseApi
        $qlRelease = $qlReleases | Where-Object {
            -not $_.draft -and $_.tag_name -match '^v12\.' -and ($_.assets.name -contains (& $qlWanted $_.tag_name))
        } | Select-Object -First 1
        if (-not $qlRelease) { throw "No QualityLayer 12 release carries $(& $qlWanted 'v12')." }
        $Version = $qlRelease.tag_name
    }
    $Version = $Version -replace '^v', ''
    if ($Version -notmatch '^12\.\d+\.\d+(?:-[A-Za-z0-9.-]+)?$') { throw "Invalid QualityLayer version: $Version" }
    $qlBase = "$qlReleaseBase/download/v$Version"
    $qlQuiet = $NonInteractive -or [Console]::IsInputRedirected
    $qlArguments = @('install')
    if ($qlQuiet) { $qlArguments += '--non-interactive' }

    if ($CliOnly) {
        Write-Host "QualityLayer $Version - Windows $qlCpu, command line only"
        $qlBinary = Join-Path $qlWork 'qualitylayer.exe'
        Write-Host "Downloading QualityLayer $Version ($qlAsset)"
        Save-Verified $qlAsset $qlBinary
        Write-Host 'Checksum verified (SHA-256)'
        $qlRun = $qlArguments + '--cli-only'
        & $qlBinary @qlRun
        if ($LASTEXITCODE -ne 0) { throw "QualityLayer install failed (exit $LASTEXITCODE)." }
    } else {
        Write-Host "QualityLayer $Version - Windows $qlCpu, with a screen"
        $qlPackage = "QualityLayer-$Version-$qlCpu-setup.exe"
        $qlSetup = Join-Path $qlWork 'setup.exe'
        Write-Host "Downloading the QualityLayer App $Version ($qlPackage)"
        Save-Verified $qlPackage $qlSetup
        Write-Host 'Checksum verified (SHA-256)'
        $qlLocal = if ($env:LOCALAPPDATA) { $env:LOCALAPPDATA } else { Join-Path (Join-Path $qlHome 'AppData') 'Local' }
        $qlApp = Join-Path (Join-Path $qlLocal 'Programs') 'QualityLayer'
        # The setup installs for this user only. /D names the folder and must come last.
        $qlSetupRun = Start-Process -FilePath $qlSetup -ArgumentList @('/S', "/D=$qlApp") -Wait -PassThru
        if ($qlSetupRun.ExitCode -ne 0) { throw "The QualityLayer App's setup failed (exit $($qlSetupRun.ExitCode))." }
        $qlCli = Join-Path $qlApp 'qualitylayer-cli.exe'
        if (-not (Test-Path -LiteralPath $qlCli -PathType Leaf)) { throw "The App's command line is missing: $qlCli" }
        Write-Host 'Installed the QualityLayer App for this user'
        $qlRun = $qlArguments + @('--app', $qlApp)
        & $qlCli @qlRun
        if ($LASTEXITCODE -ne 0) { throw "QualityLayer install failed (exit $LASTEXITCODE)." }
        # On a terminal the App opens at once to finish setting up; an unattended run opens nothing.
        if (-not $qlQuiet) {
            Write-Host 'Opening the QualityLayer App...'
            Start-Process -FilePath (Join-Path $qlApp 'QualityLayer.exe')
        }
    }
    $qlBinDir = Join-Path $qlHome '.qualitylayer\bin'
    # Current terminal only; the installer prints the command to add to a PowerShell profile.
    if (($env:Path -split ';') -notcontains $qlBinDir) { $env:Path = "$qlBinDir;$env:Path" }
} finally {
    Remove-Item -LiteralPath $qlWork -Recurse -Force -ErrorAction SilentlyContinue
}
