# Runs the server once and logs how it ended - the program the Windows service (tools/install-service.ps1, NSSM)
# starts. NSSM restarts it whenever it exits; this script tells the exits apart (docs/production-plan.md "3b"):
#   exit 10 (PlannedExitCode)  the daily server save (data/globalevents/scripts/serversave.lua): planned, back at once
#   exit 0                     a clean shutdown (GM command): restarted at once too
#   0xC000013A                 Ctrl+C / service stop
#   anything else              a CRASH: logged, then a back-off before exiting, so NSSM's restart comes later
#                              (BaseDelay * 2^(n-1) seconds, at most MaxDelay; n = crashes in the last WindowMinutes)
# The server's own output goes to this process's stdout/stderr, which NSSM writes to rotated log files; this
# script's log is <LogDir>\supervisor.log. It also prunes NSSM's rotated logs beyond the newest KeepRotated.
#   powershell -NoProfile -ExecutionPolicy Bypass -File tools\service-run.ps1 -ServerDir C:\mintwall\server -LogDir C:\mintwall\logs
param(
    [string]$ServerDir = "",
    [string]$LogDir = "",
    [string]$Exe = "avesta74.exe",           # tests run a stand-in (cmd.exe /c exit N)
    [string[]]$ExeArgs = @(),
    [int]$PlannedExitCode = 10,
    [int]$BaseDelay = 5,
    [int]$MaxDelay = 300,
    [int]$WindowMinutes = 15,
    [int]$KeepRotated = 20
)
$ErrorActionPreference = "Stop"
$CtrlCExit = -1073741510                     # 0xC000013A STATUS_CONTROL_C_EXIT
$root = Split-Path -Parent $PSScriptRoot
if (-not $ServerDir) { $ServerDir = Join-Path $root "server" }
if (-not $LogDir) { $LogDir = Join-Path $root "logs" }

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$supervisorLog = Join-Path $LogDir "supervisor.log"
$crashFile = Join-Path $LogDir "crashes.txt"

function Write-Log([string]$text) {
    $line = "{0} {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $text
    Add-Content -Path $supervisorLog -Value $line -Encoding utf8
    Write-Host "[supervisor] $line"
}

# NSSM names rotated logs <name>-<timestamp>.log next to the live one and never deletes them
foreach ($base in "server-stdout", "server-stderr") {
    Get-ChildItem -Path $LogDir -Filter "$base-*.log" -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending | Select-Object -Skip $KeepRotated |
        Remove-Item -Force -ErrorAction SilentlyContinue
}

Set-Location $ServerDir
$started = Get-Date
Write-Log "start $Exe $($ExeArgs -join ' ') in $ServerDir"
$exePath = if (Test-Path (Join-Path $ServerDir $Exe)) { Join-Path $ServerDir $Exe } else { $Exe }
# Start-Process + WaitForExit, not "& exe": a service stop sends Ctrl+C to this script and the server alike, and a
# .NET wait is not interrupted, so this script outlives the server's shutdown save instead of exiting first (NSSM
# then kills the process tree). -NoNewWindow: the server inherits this console and stdout/stderr.
$startArgs = @{ FilePath = $exePath; NoNewWindow = $true; PassThru = $true; WorkingDirectory = $ServerDir }
if ($ExeArgs.Count) {
    $startArgs.ArgumentList = $ExeArgs | ForEach-Object { if ($_ -match '\s') { '"' + $_ + '"' } else { $_ } }
}
$proc = Start-Process @startArgs
$null = $proc.Handle                         # keep the handle, or ExitCode stays empty
$proc.WaitForExit()
$code = $proc.ExitCode
$uptime = [int]((Get-Date) - $started).TotalSeconds

if ($code -eq $PlannedExitCode) {
    Write-Log "exit $code after ${uptime}s: planned restart (daily server save)"
    exit $code
}
if ($code -eq 0) {
    Write-Log "exit 0 after ${uptime}s: clean shutdown, restarting"
    exit 0
}
if ($code -eq $CtrlCExit) {
    Write-Log "exit 0xC000013A after ${uptime}s: stopped by Ctrl+C (service stop)"
    exit $code
}

# a crash: count the recent ones, back off
$now = Get-Date
$recent = @()
if (Test-Path $crashFile) {
    $recent = @(Get-Content $crashFile | Where-Object { $_ } |
        ForEach-Object { [datetime]::ParseExact($_, "o", $null, "RoundtripKind") } |
        Where-Object { ($now - $_).TotalMinutes -lt $WindowMinutes })
}
$recent += $now
Set-Content -Path $crashFile -Value ($recent | ForEach-Object { $_.ToString("o") }) -Encoding utf8
$n = $recent.Count
$delay = [int][Math]::Min($MaxDelay, $BaseDelay * [Math]::Pow(2, $n - 1))
$hex = "0x{0:X8}" -f $code
Write-Log "CRASH exit $code ($hex) after ${uptime}s; $n crash(es) in the last $WindowMinutes min; restart in ${delay}s"
Start-Sleep -Seconds $delay
exit $code
