# Start / stop / restart the dev server (port 7171). Only touches that one: test and walk-trace
# servers run the same avesta74.exe with "-c <config>" and are left alone - killing every
# avesta74.exe used to take down a running test suite.
#   powershell -ExecutionPolicy Bypass -File tools\dev-server.ps1 start|stop|restart
param([ValidateSet("start", "stop", "restart")][string]$Action = "start")
$ErrorActionPreference = "Stop"
$serverDir = Join-Path $PSScriptRoot "..\server"

function Get-DevServer {
    Get-CimInstance Win32_Process -Filter "name='avesta74.exe'" |
        Where-Object { $_.CommandLine -notmatch '\s-c\s' }
}

function Stop-DevServer {
    $procs = @(Get-DevServer)
    if (-not $procs) { Write-Host "No dev server running."; return }
    foreach ($p in $procs) {
        Stop-Process -Id $p.ProcessId -Force
        Write-Host "Stopped dev server (PID $($p.ProcessId))."
    }
    Start-Sleep -Seconds 1
}

if ($Action -in "stop", "restart") { Stop-DevServer }
if ($Action -in "start", "restart") {
    if (Get-NetTCPConnection -LocalPort 7171 -State Listen -ErrorAction SilentlyContinue) {
        throw "Port 7171 is already in use - is the dev server running? Use: mise run restart-server"
    }
    Set-Location $serverDir
    & .\avesta74.exe
}
