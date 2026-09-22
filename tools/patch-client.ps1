# Makes a copy of the original 7.4 Tibia.exe whose login servers point at $Ip.
# The original Tibia.exe is never modified.
#   powershell -ExecutionPolicy Bypass -File tools\patch-client.ps1 [-Ip 127.0.0.1]
param(
    [string]$Ip = "127.0.0.1",
    [string]$ClientDir = (Join-Path $PSScriptRoot "..\client\Tibia740"),
    [string]$OutName = "Tibia-mintwall.exe"
)
$ErrorActionPreference = "Stop"
$src = Join-Path $ClientDir "Tibia.exe"
$bytes = [IO.File]::ReadAllBytes($src)
$ascii = [Text.Encoding]::ASCII
$text = $ascii.GetString($bytes)

# Hardcoded 7.4 login servers; each sits in its own fixed slot, NUL-terminated
$hosts = "tibia1.cipsoft.com", "tibia2.cipsoft.com", "server.tibia.com", "server2.tibia.com"
$maxLen = ($hosts | ForEach-Object { $_.Length } | Measure-Object -Minimum).Minimum
if ($Ip.Length -gt $maxLen) { throw "Address '$Ip' is longer than $maxLen characters" }

foreach ($h in $hosts) {
    $idx = $text.IndexOf($h + [char]0)
    if ($idx -lt 0) { throw "Login host '$h' not found - is this the original 7.4 Tibia.exe?" }
    $new = $ascii.GetBytes($Ip)
    for ($i = 0; $i -lt $h.Length; $i++) { $bytes[$idx + $i] = if ($i -lt $new.Length) { $new[$i] } else { 0 } }
    Write-Host "patched $h -> $Ip (offset $idx)"
}
$out = Join-Path $ClientDir $OutName
[IO.File]::WriteAllBytes($out, $bytes)
Write-Host "Wrote $out"
