# Watchdog for your Remote Control sessions in tools/sessions.json (same file as start_agents.ps1).
# Run it every 5 minutes and at logon, for example as a Windows scheduled task. For each session
# without a running claude.exe: resume it on its ORIGINAL id (never a new session). If the
# transcript shows it was mid-task when it dropped, a short continue prompt is typed into its
# console (tools/type_into_session.ps1). A session you closed on purpose should be removed from
# sessions.json. Log: %LOCALAPPDATA%\cloud-alter-ego\watchdog.log
#
# Usage: powershell -ExecutionPolicy Bypass -File tools\watch_sessions.ps1
$ErrorActionPreference = 'Continue'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$config = Join-Path $here 'sessions.json'
$typer = Join-Path $here 'type_into_session.ps1'
$log = Join-Path $env:LOCALAPPDATA 'cloud-alter-ego\watchdog.log'
New-Item -ItemType Directory -Force (Split-Path $log) | Out-Null
function Log($m) { "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $m" | Out-File -Append -Encoding utf8 $log }
function Type($procId, $text) {
    & powershell -NoProfile -ExecutionPolicy Bypass -File $typer -ProcessId $procId -Text $text | Out-Null
}

if (-not (Test-Path $config)) { Log "no $config, nothing to watch"; exit }
$claude = (Get-Command claude -ErrorAction Stop).Source

# Never fight a logged-out Claude: then it cannot resume anyway.
try { $auth = & $claude auth status | ConvertFrom-Json } catch { $auth = $null }
if (-not $auth -or -not $auth.loggedIn) { Log 'claude is logged out, nothing resumed'; exit }

function MidTask($id) {
    # True when the last conversation entry is a tool call or a tool result: the session dropped while working.
    $f = Get-ChildItem "$env:USERPROFILE\.claude\projects" -Recurse -Filter "$id.jsonl" -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $f) { return $false }
    $last = Get-Content $f.FullName -Tail 60 | Where-Object { $_ -match '"type":"(user|assistant)"' } | Select-Object -Last 1
    if (-not $last) { return $false }
    return ($last -match '"type":"tool_use"' -or $last -match '"tool_result"')
}

function Find-Claude($id) {
    Get-CimInstance Win32_Process -Filter "Name='claude.exe'" |
        Where-Object { $_.CommandLine -match [regex]::Escape($id) } | Select-Object -First 1
}

foreach ($s in (Get-Content $config -Raw | ConvertFrom-Json)) {
    if (Find-Claude $s.id) { continue }
    $wasBusy = MidTask $s.id
    $flags = @('--resume', $s.id, '--remote-control', "'$($s.name)'")
    if ($s.skipPermissions) { $flags = @('--dangerously-skip-permissions') + $flags }
    $cmd = "Set-Location '$($s.cwd)'; & '$claude' " + ($flags -join ' ')
    $enc = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($cmd))
    Start-Process powershell -WindowStyle Hidden -WorkingDirectory $s.cwd -ArgumentList '-NoExit', '-EncodedCommand', $enc
    Log "resumed $($s.name) ($($s.id)), mid-task: $wasBusy"
    if ($wasBusy) {
        Start-Sleep 45
        $p = Find-Claude $s.id
        if ($p) {
            $msg = 'You were restarted after a failure. Read your last steps in this conversation and continue where you were. If you were done, do nothing.'
            foreach ($word in ($msg -split ' ')) { Type $p.ProcessId $word; Type $p.ProcessId ' ' }
            Start-Sleep 1
            Type $p.ProcessId ([string][char]13)
            Log "sent continue prompt to $($s.name)"
        }
    }
}
