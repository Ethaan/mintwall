# Logs a character into a local 7.4 server, says each word, and prints the text the server sent back.
#   powershell -ExecutionPolicy Bypass -File tools\talk-test.ps1 -Words hi,job,bye
param(
    [string]$Words = "hi,job,bye",
    [uint32]$Account = 111111,
    [string]$Password = "tibia",
    [string]$Character = "Mintwall",
    [string]$HostName = "127.0.0.1",
    [int]$Port = 7171
)
$ErrorActionPreference = "Stop"
function Str([string]$s) { $b = [Text.Encoding]::ASCII.GetBytes($s); [BitConverter]::GetBytes([uint16]$b.Length) + $b }
function Send([byte[]]$body) { $p = [byte[]]([BitConverter]::GetBytes([uint16]$body.Length) + $body); $script:stream.Write($p, 0, $p.Length) }
function Drain([int]$ms) {
    $end = (Get-Date).AddMilliseconds($ms)
    while ((Get-Date) -lt $end) {
        while ($script:stream.DataAvailable) { $n = $script:stream.Read($buf, 0, $buf.Length); $script:recv.Write($buf, 0, $n) }
        Start-Sleep -Milliseconds 100
    }
}
function Show {
    $txt = -join ($script:recv.ToArray() | ForEach-Object { if ($_ -ge 32 -and $_ -lt 127) { [char]$_ } else { "`n" } })
    $txt -split "`n" | Where-Object { $_.Length -ge 6 } | ForEach-Object { "   < $_" }
    $script:recv.SetLength(0)
}

$client = New-Object Net.Sockets.TcpClient($HostName, $Port)
$script:stream = $client.GetStream()
$script:recv = New-Object IO.MemoryStream
$buf = New-Object byte[] 65536

# 7.4 game login: 0x0A, os, version, gm flag, account, character, password (no encryption in 7.4)
Send ([byte[]](@(0x0A) + [BitConverter]::GetBytes([uint16]2) + [BitConverter]::GetBytes([uint16]740) + @(0) +
    [BitConverter]::GetBytes($Account) + (Str $Character) + (Str $Password)))
Drain 2500
"logged in as $Character"; Show

foreach ($w in ($Words -split ",")) {
    "> $w"
    Send ([byte[]](@(0x96, 1) + (Str $w)))   # 0x96 say, type 1 = normal speech
    Drain 2500
    Show
}
$client.Close()
