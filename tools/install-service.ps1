# Installs (or with -Uninstall removes) the Windows service that runs the server and restarts it on every exit
# (docs/production-plan.md "3b. Restart"). The service runs tools\service-run.ps1 under NSSM; that script starts
# server\avesta74.exe, logs exit 10 (the daily server save) as planned and anything else as a crash with a
# back-off. NSSM writes the server's stdout/stderr to <LogDir>\server-stdout.log / server-stderr.log, rotated
# at -RotateBytes.
#
# NSSM (https://nssm.cc, 2.24-101 or later) is not part of the repo: `winget install NSSM.NSSM`, or download it from
# https://nssm.cc/download and put win64\nssm.exe in PATH or at tools\nssm\nssm.exe (or pass -NssmPath).
#
#   powershell -ExecutionPolicy Bypass -File tools\install-service.ps1 -DryRun      print the commands, change nothing
#   powershell -ExecutionPolicy Bypass -File tools\install-service.ps1              install + start (as Administrator)
#   powershell -ExecutionPolicy Bypass -File tools\install-service.ps1 -Uninstall   stop + remove
# -WhatIf is the same as -DryRun. Without -Start the service is installed but not started (it starts at the next boot).
[CmdletBinding()]
param(
    [string]$ServiceName = "mintwall",
    [string]$ServerDir = "",
    [string]$LogDir = "",
    [string]$NssmPath = "",
    [string]$ServiceAccount = "",            # e.g. ".\mintwall"; empty = LocalSystem
    [string]$ServicePassword = "",
    [long]$RotateBytes = 10MB,
    [int]$StopTimeoutMs = 30000,             # Ctrl+C, then wait this long before closing harder
    [switch]$Start,
    [switch]$Uninstall,
    [Alias("WhatIf")][switch]$DryRun
)
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot      # ($PSScriptRoot is empty in param defaults on Windows PowerShell 5.1)
if (-not $ServerDir) { $ServerDir = Join-Path $root "server" }
if (-not $LogDir) { $LogDir = Join-Path $root "logs" }
$ServerDir = [IO.Path]::GetFullPath($ServerDir)
$LogDir = [IO.Path]::GetFullPath($LogDir)
$runner = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot "service-run.ps1"))
$powershell = Join-Path $env:SystemRoot "System32\WindowsPowerShell\v1.0\powershell.exe"

if (-not $NssmPath) {
    $local = Join-Path $PSScriptRoot "nssm\nssm.exe"
    $inPath = Get-Command nssm.exe -ErrorAction SilentlyContinue
    if ($inPath) { $NssmPath = $inPath.Source }
    elseif (Test-Path $local) { $NssmPath = [IO.Path]::GetFullPath($local) }
    else { $NssmPath = "nssm.exe" }
}

function Invoke-Nssm {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$NssmArgs)
    $display = @($NssmArgs)
    if ($display.Count -gt 4 -and $display[2] -eq "ObjectName") { $display[4] = "********" }
    $shown = ($display | ForEach-Object { if ($_ -match '[\s"]' -or $_ -eq '') { '"' + ($_ -replace '"', '\"') + '"' } else { $_ } }) -join ' '
    if ($DryRun) {
        Write-Output "nssm $shown"
        return
    }
    Write-Host "> nssm $shown"
    # Windows PowerShell 5.1 passes embedded quotes to native programs unescaped and drops empty arguments
    $legacy = $PSVersionTable.PSVersion -lt [version]"7.3" -or $PSNativeCommandArgumentPassing -eq "Legacy"
    $callArgs = if ($legacy) {
        $NssmArgs | ForEach-Object { if ($_ -eq '') { '""' } else { $_ -replace '(\\*)"', '$1$1\"' } }
    } else { $NssmArgs }
    & $NssmPath @callArgs
    if ($LASTEXITCODE -ne 0) { throw "nssm $($NssmArgs[0]) failed (exit code $LASTEXITCODE)" }
}

if ($DryRun) {
    Write-Output "DRY RUN - nothing is changed. NSSM: $NssmPath$(if (-not (Get-Command $NssmPath -ErrorAction SilentlyContinue)) { ' (not found: winget install NSSM.NSSM, or https://nssm.cc/download)' })"
} else {
    if (-not (Get-Command $NssmPath -ErrorAction SilentlyContinue)) {
        throw "nssm.exe not found. Install it (winget install NSSM.NSSM) or download it from https://nssm.cc/download, then pass -NssmPath or put it in PATH / tools\nssm\nssm.exe."
    }
    $admin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $admin) { throw "Run this from an elevated (Administrator) PowerShell." }
}

$exists = [bool](Get-Service -Name $ServiceName -ErrorAction SilentlyContinue)

if ($Uninstall) {
    if (-not $exists -and -not $DryRun) { Write-Host "No service '$ServiceName'."; exit 0 }
    # NSSM stops it the configured way: Ctrl+C, then WM_CLOSE, then terminate
    Invoke-Nssm stop $ServiceName
    Invoke-Nssm remove $ServiceName confirm
    if (-not $DryRun) { Write-Host "Removed service '$ServiceName'. Logs stay in $LogDir." }
    exit 0
}

if (-not (Test-Path (Join-Path $ServerDir "avesta74.exe"))) {
    $msg = "No avesta74.exe in $ServerDir (build it first: mise run build)."
    if ($DryRun) { Write-Output "warning: $msg" } else { throw $msg }
}

if ($DryRun) { Write-Output "mkdir $LogDir" } else { New-Item -ItemType Directory -Force -Path $LogDir | Out-Null }

$params = "-NoProfile -ExecutionPolicy Bypass -File `"$runner`" -ServerDir `"$ServerDir`" -LogDir `"$LogDir`""
if ($exists) {
    if (-not $DryRun) { Write-Host "Service '$ServiceName' exists - updating its settings." }
    Invoke-Nssm set $ServiceName Application $powershell
} else {
    Invoke-Nssm install $ServiceName $powershell
}
Invoke-Nssm set $ServiceName AppParameters $params
Invoke-Nssm set $ServiceName AppDirectory $ServerDir
Invoke-Nssm set $ServiceName DisplayName "Mintwall (Tibia 7.4 server)"
Invoke-Nssm set $ServiceName Description "Avesta 7.4 server from $ServerDir; restarted on every exit (exit 10 = daily server save). Logs: $LogDir"
Invoke-Nssm set $ServiceName Start SERVICE_AUTO_START
if ($ServiceAccount) {
    # the account needs write access to ServerDir (database, logs) and LogDir
    if ($ServicePassword) { Invoke-Nssm set $ServiceName ObjectName $ServiceAccount $ServicePassword }
    else { Invoke-Nssm set $ServiceName ObjectName $ServiceAccount }
}

# restart on any exit; the back-off after a crash is service-run.ps1's (NSSM adds its own if a run lasts < 10 s)
Invoke-Nssm set $ServiceName AppExit Default Restart
Invoke-Nssm set $ServiceName AppRestartDelay 0
Invoke-Nssm set $ServiceName AppThrottle 10000

# stop: Ctrl+C first (a console app), then WM_CLOSE, then thread exit, then terminate the process tree
Invoke-Nssm set $ServiceName AppStopMethodConsole $StopTimeoutMs
Invoke-Nssm set $ServiceName AppStopMethodWindow 5000
Invoke-Nssm set $ServiceName AppStopMethodThreads 5000
Invoke-Nssm set $ServiceName AppKillProcessTree 1

# output: stdin from nowhere (an engine error that waits for a key must not hang), stdout/stderr appended to
# files rotated at RotateBytes, also while running
Invoke-Nssm set $ServiceName AppStdin NUL
Invoke-Nssm set $ServiceName AppStdout (Join-Path $LogDir "server-stdout.log")
Invoke-Nssm set $ServiceName AppStderr (Join-Path $LogDir "server-stderr.log")
Invoke-Nssm set $ServiceName AppStdoutCreationDisposition 4
Invoke-Nssm set $ServiceName AppStderrCreationDisposition 4
Invoke-Nssm set $ServiceName AppRotateFiles 1
Invoke-Nssm set $ServiceName AppRotateOnline 1
Invoke-Nssm set $ServiceName AppRotateBytes $RotateBytes

if ($Start) { Invoke-Nssm start $ServiceName }
if (-not $DryRun) {
    Write-Host "Service '$ServiceName' installed$(if ($Start) { ' and started' } else { ' (not started: nssm start ' + $ServiceName + ')' })."
}
