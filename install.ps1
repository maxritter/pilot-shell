# QualityLayer bootstrap for native Windows. Installs per user; an optional Defender repair
# asks for administrator approval only when a relevant ASR restriction is detected.
# Native Windows always has a screen, so it gets the QualityLayer App: the per-user setup is
# downloaded, verified against its signed SHA-256 and run silently, then the App's own command line
# installs its skills and settings and a small launcher takes the path agents call.
# -CliOnly installs the command line alone, as before. WSL2 uses install.sh inside the distribution.
# The release's SHA256SUMS is signed (SHA256SUMS.sig, `ssh-keygen -Y sign`): the signature is checked
# with `ssh-keygen -Y verify` against the key built into this script, then each download against its
# signed line, both mandatory, before anything is installed. QUALITYLAYER_RELEASE_SIGNER names
# another key for tests, and counts only when the release base is on this machine.
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
# The only key that may sign a release; the same line is built into `qualitylayer update`.
$qlSignerId = 'release@qualitylayer.dev'
$qlSignerNamespace = 'qualitylayer-release'
$qlSignerKey = 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOvc89TsfxkzK1lxTNLr/FHwImLq1oUWYmmXQ1iYL2oU'
if ($env:QUALITYLAYER_RELEASE_SIGNER -and $qlReleaseBase -match '^(file://|http://(127\.0\.0\.1|localhost)(:\d+)?(/|$))') {
    $qlSignerKey = (($env:QUALITYLAYER_RELEASE_SIGNER.Trim() -split '\s+')[0..1]) -join ' '
}
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

# Confirm-SignedSums: the release's SHA256SUMS and its signature, fetched once, and the signature
# checked against the key built into this script before any line of the sums is trusted.
$script:qlSums = $null
function Confirm-SignedSums {
    if ($script:qlSums) { return }
    $qlKeygen = Get-Command ssh-keygen -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $qlKeygen) { throw 'ssh-keygen is required to verify the release signature; nothing was installed.' }
    $qlSumsFile = Join-Path $qlWork 'SHA256SUMS'
    Invoke-WebRequest -UseBasicParsing -Uri "$qlBase/SHA256SUMS" -OutFile $qlSumsFile
    try {
        Invoke-WebRequest -UseBasicParsing -Uri "$qlBase/SHA256SUMS.sig" -OutFile "$qlSumsFile.sig"
    } catch {
        throw "The release's SHA256SUMS is not signed by QualityLayer: $qlBase/SHA256SUMS.sig is missing; nothing was installed."
    }
    $qlAllowed = Join-Path $qlWork 'allowed_signers'
    [IO.File]::WriteAllText($qlAllowed, "$qlSignerId namespaces=`"$qlSignerNamespace`" $qlSignerKey`n")
    $qlVerify = Start-Process -FilePath $qlKeygen.Source -NoNewWindow -Wait -PassThru `
        -ArgumentList @('-Y', 'verify', '-f', "`"$qlAllowed`"", '-I', $qlSignerId, '-n', $qlSignerNamespace, '-s', "`"$qlSumsFile.sig`"") `
        -RedirectStandardInput $qlSumsFile -RedirectStandardOutput (Join-Path $qlWork 'verify.out') -RedirectStandardError (Join-Path $qlWork 'verify.err')
    if ($qlVerify.ExitCode -ne 0) {
        $qlVerifyExit = if ($null -eq $qlVerify.ExitCode) { 'unavailable' } else { [string]$qlVerify.ExitCode }
        $qlVerifyError = [IO.File]::ReadAllText((Join-Path $qlWork 'verify.err')).Trim()
        $qlVerifyOutput = [IO.File]::ReadAllText((Join-Path $qlWork 'verify.out')).Trim()
        if ($qlVerifyError.Length -gt 4096) { $qlVerifyError = $qlVerifyError.Substring($qlVerifyError.Length - 4096) }
        if ($qlVerifyOutput.Length -gt 1024) { $qlVerifyOutput = $qlVerifyOutput.Substring($qlVerifyOutput.Length - 1024) }
        throw "The release's SHA256SUMS is not signed by QualityLayer; nothing was installed. Verifier: $($qlKeygen.Source); exit: $qlVerifyExit; stderr: $qlVerifyError; stdout: $qlVerifyOutput"
    }
    $script:qlSums = $qlSumsFile
}

# Save-Verified <file in the release> <where to put it>: the file, checked against its line in the
# signed SHA256SUMS before anything is installed.
function Save-Verified([string]$Name, [string]$Destination) {
    Invoke-WebRequest -UseBasicParsing -Uri "$qlBase/$Name" -OutFile $Destination
    Confirm-SignedSums
    $qlExpected = $null
    foreach ($qlLine in Get-Content -LiteralPath $script:qlSums) {
        $qlFields = $qlLine.Trim() -split '\s+'
        if ($qlFields.Count -ge 2 -and $qlFields[1] -eq $Name) { $qlExpected = $qlFields[0]; break }
    }
    if ($qlExpected -notmatch '^[0-9a-fA-F]{64}$') { throw "SHA256SUMS holds no checksum for $Name; nothing was installed." }
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
        # The NSIS package is run silently here, so an interactive bootstrap performs its optional
        # ASR check before invoking a CLI that Defender might otherwise prevent from starting.
        $qlRepair = Join-Path $qlApp 'QualityLayer-Windows-Repair.ps1'
        if (-not $qlQuiet -and (Test-Path -LiteralPath $qlRepair -PathType Leaf)) {
            $qlPowerShell = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
            $qlNativePowerShell = Join-Path $env:SystemRoot 'Sysnative\WindowsPowerShell\v1.0\powershell.exe'
            if (Test-Path -LiteralPath $qlNativePowerShell -PathType Leaf) { $qlPowerShell = $qlNativePowerShell }
            # A separate process keeps -WindowStyle Hidden from hiding the caller's console.
            $qlRepairArguments = '-NoLogo -NoProfile -ExecutionPolicy Bypass -File "' + $qlRepair + '" -Automatic'
            $qlRepairRun = Start-Process -FilePath $qlPowerShell -ArgumentList $qlRepairArguments -WindowStyle Hidden -Wait -PassThru
            if ($qlRepairRun.ExitCode -ne 0) {
                Write-Warning 'Windows security repair did not finish. Use QualityLayer - Repair Windows launch from the Start menu to retry.'
            }
        }
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
