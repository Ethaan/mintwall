# Logs a character into a local 7.4 test server, says each word, and prints the text the server sent back.
#   powershell -ExecutionPolicy Bypass -File tools\talk-test.ps1 -Words hi,job,bye
#
# Any NPC, wherever it stands (-Npc; the name as in data/npc or the spawn file, any case):
#   ... talk-test.ps1 -Npc Sam -Words "hi,trade,bye"                 GM /goto: logs in as 9 / 9 (GM Mintwall)
#   ... talk-test.ps1 -Npc Sam -Via db -Words "hi,job,bye"           a normal character (default Mintwall),
#        moved in the test database onto the NPC's spawn before it logs in (the server puts it on a free tile
#        next to it); the character must be logged out
#
# A test server, never your own: the port defaults to MINTWALL_TEST_PORT or 7181 (the test suite's server; start
# one with -StartServer), the database to MINTWALL_TEST_RUN\test.db3 or tests\.run\test.db3. Port 7171 and
# server\db.db3 (the dev server and its characters) are refused unless -Force.
#   ... talk-test.ps1 -StartServer -Port 7230 -RunDir C:\mintwall\tests\.run-talk -Npc Sam
#        starts an isolated test server there (fresh database from seed.sql), talks, and stops it again
param(
    [string]$Words = "hi,job,bye",
    [uint32]$Account = 111111,
    [string]$Password = "tibia",
    [string]$Character = "Mintwall",
    [string]$HostName = "127.0.0.1",
    [int]$Port = $(if ($env:MINTWALL_TEST_PORT) { [int]$env:MINTWALL_TEST_PORT } else { 7181 }),
    [string]$Npc = "",
    [ValidateSet("goto", "db")][string]$Via = "goto",
    [string]$Db = "",
    [string]$RunDir = "",
    [switch]$StartServer,
    [int]$Wait = 2500,
    [switch]$Force
)
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$serverDir = Join-Path $root "server"
$python = Join-Path $root "tests\.venv\Scripts\python.exe"
if (-not (Test-Path $python)) { $python = "python" }

if ($Port -eq 7171 -and -not $Force) {
    throw "port 7171 is the dev server (your own characters): talk-test runs against a test server - give -Port (MINTWALL_TEST_PORT, default 7181) or -Force"
}
if (-not $RunDir) { $RunDir = if ($env:MINTWALL_TEST_RUN) { $env:MINTWALL_TEST_RUN } else { Join-Path $root "tests\.run" } }
if (-not $Db) { $Db = Join-Path $RunDir "test.db3" }

function Find-NpcSpawn([string]$name) {
    # like tests/tibia74/npcs.py: a spawn names the NPC's file, position = spawn centre + offset
    $file = Get-ChildItem (Join-Path $serverDir "data\world") -Filter "*-spawns.xml" | Select-Object -First 1
    $xml = New-Object Xml.XmlDocument
    $xml.Load($file.FullName)
    foreach ($spawn in $xml.SelectNodes("//spawn")) {
        foreach ($n in $spawn.SelectNodes("npc")) {
            if ($n.GetAttribute("name") -ieq $name) {
                return [pscustomobject]@{ Name = $n.GetAttribute("name")
                    X = [int]$spawn.centerx + [int]$n.x; Y = [int]$spawn.centery + [int]$n.y; Z = [int]$n.z }
            }
        }
    }
    throw "no NPC '$name' in $($file.Name)"
}

$spawn = $null
if ($Npc) {
    $spawn = Find-NpcSpawn $Npc
    "$($spawn.Name) spawns at $($spawn.X), $($spawn.Y), $($spawn.Z) (it may wander a few tiles)"
    if ($Via -eq "goto" -and -not $PSBoundParameters.ContainsKey("Account")) {
        # /goto is a God command (data/commands.xml, access 3): seed.sql's God account
        $Account = 9; $Password = "9"
        if (-not $PSBoundParameters.ContainsKey("Character")) { $Character = "GM Mintwall" }
    }
}

$serverProc = $null
if ($StartServer) {
    $probe = New-Object Net.Sockets.TcpClient
    try { $taken = $probe.ConnectAsync("127.0.0.1", $Port).Wait(500) -and $probe.Connected } catch { $taken = $false }
    $probe.Close()
    if ($taken) { throw "port $Port is already in use - not starting a second server there" }
    # the test suite's own ServerProcess: own config, own fresh database, dies with the python process
    $code = "import sys; sys.path.insert(0, r'$root\tests'); from pathlib import Path; " +
            "from tibia74.server import ServerProcess; s = ServerProcess(port=$Port, run_dir=Path(r'$RunDir')); " +
            "s.start(); print('ready', flush=True); sys.stdin.read(); s.stop()"
    $psi = New-Object Diagnostics.ProcessStartInfo $python
    $psi.Arguments = "-c `"$code`""
    $psi.UseShellExecute = $false; $psi.RedirectStandardInput = $true; $psi.RedirectStandardOutput = $true
    $serverProc = [Diagnostics.Process]::Start($psi)
    "starting a test server on $Port in $RunDir (map load takes a while)..."
    $line = $serverProc.StandardOutput.ReadLine()
    if ($line -ne "ready") { throw "test server did not start - see $RunDir\server.log" }
}

try {
    if ($Npc -and $Via -eq "db") {
        if (-not (Test-Path $Db)) { throw "no database $Db - is the test server running from $RunDir?" }
        if ((Resolve-Path $Db).Path -ieq (Join-Path $serverDir "db.db3") -and -not $Force) {
            throw "$Db is the dev server's database (your own characters) - use a test database or -Force"
        }
        $sql = "import sqlite3, sys; c = sqlite3.connect(sys.argv[1], timeout=10); " +
               "n = c.execute('UPDATE players SET posx=?, posy=?, posz=? WHERE name=?', sys.argv[2:6]).rowcount; " +
               "c.commit(); sys.exit(0 if n else 3)"
        & $python -c $sql $Db $spawn.X $spawn.Y $spawn.Z $Character
        if ($LASTEXITCODE -eq 3) { throw "no character '$Character' in $Db" }
        if ($LASTEXITCODE -ne 0) { throw "could not update $Db" }
        "moved $Character onto $($spawn.Name)'s spawn in $Db"
    }

    function Str([string]$s) { $b = [Text.Encoding]::GetEncoding(28591).GetBytes($s); [BitConverter]::GetBytes([uint16]$b.Length) + $b }
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
    function Say([string]$text) { Send ([byte[]](@(0x96, 1) + (Str $text))) }   # 0x96 say, type 1 = normal speech

    $client = New-Object Net.Sockets.TcpClient($HostName, $Port)
    $script:stream = $client.GetStream()
    $script:recv = New-Object IO.MemoryStream
    $buf = New-Object byte[] 65536

    # 7.4 game login: 0x0A, os, version, gm flag, account, character, password (no encryption in 7.4)
    Send ([byte[]](@(0x0A) + [BitConverter]::GetBytes([uint16]2) + [BitConverter]::GetBytes([uint16]740) + @(0) +
        [BitConverter]::GetBytes($Account) + (Str $Character) + (Str $Password)))
    Drain $Wait
    "logged in as $Character"; Show

    if ($Npc -and $Via -eq "goto") {
        "> /goto $Npc"
        Say "/goto $Npc"   # the NPC's name as the server knows it (any case); the spawn file name matches it
        Drain 1500
        Show
    }

    foreach ($w in ($Words -split ",")) {
        "> $w"
        Say $w
        Drain $Wait
        Show
    }
    $client.Close()
}
finally {
    if ($serverProc) {
        $serverProc.StandardInput.Close()        # the python side stops its server and exits
        if (-not $serverProc.WaitForExit(20000)) { $serverProc.Kill() }
        "test server on $Port stopped"
    }
}
