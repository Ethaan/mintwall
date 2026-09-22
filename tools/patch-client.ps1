# Makes a copy of the original 7.4 Tibia.exe whose login servers point at $Ip and which loads
# mintwall.dll (client-mod\, smooth keyboard walking) at start-up. The original Tibia.exe is never modified.
#   client-mod\build.bat
#   powershell -ExecutionPolicy Bypass -File tools\patch-client.ps1 [-Ip 127.0.0.1]
param(
    [string]$Ip = "127.0.0.1",
    [string]$ClientDir = (Join-Path $PSScriptRoot "..\client\Tibia740"),
    [string]$OutName = "Tibia-mintwall.exe",
    [string]$ModDll = (Join-Path $PSScriptRoot "..\client-mod\build\mintwall.dll")
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

# --- Import mintwall.dll ------------------------------------------------------------------------
# A new read/write section ".mintw" holds a copy of the import descriptors plus one for
# mintwall.dll!MintwallInit; the import directory is pointed at it. Windows then loads the DLL
# before the client starts, exactly like the client's own DLLs.
function U16($o) { [BitConverter]::ToUInt16($bytes, $o) }
function U32($o) { [BitConverter]::ToUInt32($bytes, $o) }
function Put32([byte[]]$buf, $o, $v) { [BitConverter]::GetBytes([uint32]$v).CopyTo($buf, $o) }
function Align($v, $a) { [uint32]([math]::Ceiling($v / $a) * $a) }

$pe = U32 0x3C
$fileHeader = $pe + 4
$sections = U16 ($fileHeader + 2)
$opt = $fileHeader + 20
if ((U16 $opt) -ne 0x10B) { throw "Not a 32-bit PE" }
$sectionTable = $opt + (U16 ($fileHeader + 16))
$sectionAlign = U32 ($opt + 32); $fileAlign = U32 ($opt + 36); $headersSize = U32 ($opt + 60)
$importDir = $opt + 96 + 8
if ((U32 ($opt + 96 + 11 * 8)) -ne 0) { throw "Bound imports present - not handled" }
if ($sectionTable + ($sections + 1) * 40 -gt $headersSize) { throw "No room for another section header" }

function RvaToOffset($rva) {
    for ($s = 0; $s -lt $sections; $s++) {
        $h = $sectionTable + $s * 40
        $va = U32 ($h + 12); $size = [math]::Max((U32 ($h + 8)), (U32 ($h + 16)))
        if ($rva -ge $va -and $rva -lt $va + $size) { return $rva - $va + (U32 ($h + 20)) }
    }
    throw "RVA $rva is in no section"
}

$old = @()
$d = RvaToOffset (U32 $importDir)
while ((U32 ($d + 12)) -ne 0) { $old += , $bytes[$d..($d + 19)]; $d += 20 }

$last = $sectionTable + ($sections - 1) * 40
$newVa = Align ((U32 ($last + 12)) + (U32 ($last + 8))) $sectionAlign
$newRaw = Align ((U32 ($last + 20)) + (U32 ($last + 16))) $fileAlign
if ($newRaw -ne $bytes.Length) { throw "Data after the last section - not handled" }

$size = $fileAlign
$sec = New-Object byte[] $size
$ilt = 0x400; $iat = 0x410; $hintName = 0x420; $dllName = 0x440
if (($old.Count + 2) * 20 -gt $ilt) { throw "Too many imports for the section layout" }
for ($i = 0; $i -lt $old.Count; $i++) { [Array]::Copy([byte[]]$old[$i], 0, $sec, $i * 20, 20) }
$mine = $old.Count * 20
Put32 $sec ($mine + 0) ($newVa + $ilt)        # OriginalFirstThunk
Put32 $sec ($mine + 12) ($newVa + $dllName)   # Name
Put32 $sec ($mine + 16) ($newVa + $iat)       # FirstThunk
Put32 $sec $ilt ($newVa + $hintName)
Put32 $sec $iat ($newVa + $hintName)
$ascii.GetBytes("MintwallInit").CopyTo($sec, $hintName + 2)
$ascii.GetBytes("mintwall.dll").CopyTo($sec, $dllName)

$h = $sectionTable + $sections * 40
$ascii.GetBytes(".mintw").CopyTo($bytes, $h)
Put32 $bytes ($h + 8) $size; Put32 $bytes ($h + 12) $newVa
Put32 $bytes ($h + 16) $size; Put32 $bytes ($h + 20) $newRaw
Put32 $bytes ($h + 36) 3221225536              # 0xC0000040: initialized data, read, write
[BitConverter]::GetBytes([uint16]($sections + 1)).CopyTo($bytes, $fileHeader + 2)
Put32 $bytes ($opt + 56) ($newVa + $size)      # SizeOfImage
Put32 $bytes $importDir ($newVa)
Put32 $bytes ($importDir + 4) (($old.Count + 2) * 20)    # ours + the terminating null entry
Write-Host "added import mintwall.dll ($($old.Count) existing DLLs kept)"

$out = Join-Path $ClientDir $OutName
[IO.File]::WriteAllBytes($out, [byte[]]($bytes + $sec))
Write-Host "Wrote $out"

if (-not (Test-Path $ModDll)) { throw "$ModDll not found - run client-mod\build.bat first" }
Copy-Item $ModDll (Join-Path $ClientDir "mintwall.dll") -Force
Write-Host "Copied mintwall.dll"
