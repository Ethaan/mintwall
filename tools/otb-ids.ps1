# Dumps "serverId clientId" pairs from an items.otb, plus its version header.
#   powershell -File tools\otb-ids.ps1 path\to\items.otb
param([Parameter(Mandatory)][string]$Path)
$raw = [IO.File]::ReadAllBytes((Resolve-Path $Path))
# unescape node stream (0xFD escapes the next byte); keep node markers as tokens
$nodes = New-Object System.Collections.Generic.List[object]
$cur = $null; $depth = 0
for ($i = 4; $i -lt $raw.Length; $i++) {
    $b = $raw[$i]
    if ($b -eq 0xFD) { $i++; $cur.Add($raw[$i]); continue }
    if ($b -eq 0xFE) { $depth++; $cur = New-Object System.Collections.Generic.List[byte]; $nodes.Add(@($depth, $cur)); continue }
    if ($b -eq 0xFF) { $depth--; continue }
    $cur.Add($b)
}
$root = $nodes[0][1].ToArray()
# root: type(1) flags(4) attr(1)=0x01 len(2) major(4) minor(4) build(4)
"# version major={0} minor={1} build={2}" -f [BitConverter]::ToUInt32($root,8), [BitConverter]::ToUInt32($root,12), [BitConverter]::ToUInt32($root,16)
foreach ($n in $nodes) {
    if ($n[0] -ne 2) { continue }
    $d = $n[1].ToArray(); $p = 5; $sid = $null; $cid = $null   # type(1) flags(4)
    while ($p + 3 -le $d.Length) {
        $attr = $d[$p]; $len = [BitConverter]::ToUInt16($d, $p + 1); $p += 3
        if ($attr -eq 0x10) { $sid = [BitConverter]::ToUInt16($d, $p) }
        elseif ($attr -eq 0x11) { $cid = [BitConverter]::ToUInt16($d, $p) }
        $p += $len
    }
    if ($sid) { "$sid $cid" }
}
