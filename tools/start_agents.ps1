# Resumes your named Remote Control sessions, each in its own PowerShell window, on their original
# session id. See skills/remote-control-sessions.md for the why and the checks.
#
# Put your sessions in tools/sessions.json (copy tools/sessions.example.json; it is gitignored
# because session ids are per machine).
#
# Usage: powershell -ExecutionPolicy Bypass -File tools\start_agents.ps1

$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$config = Join-Path $here 'sessions.json'
if (-not (Test-Path $config)) {
    throw "No $config yet. Copy sessions.example.json to sessions.json and fill in your sessions."
}

$claude = (Get-Command claude -ErrorAction Stop).Source
$auth = & $claude auth status | ConvertFrom-Json
if (-not $auth.loggedIn) {
    throw 'Claude is logged out. Log in once with /login in an interactive session, then run this again.'
}

$sessions = Get-Content $config -Raw | ConvertFrom-Json
foreach ($s in $sessions) {
    # One process per session id: close old copies first, two processes on one id break logging.
    Get-CimInstance Win32_Process -Filter "Name='claude.exe'" |
        Where-Object { $_.CommandLine -match [regex]::Escape($s.id) } |
        ForEach-Object { Stop-Process -Id $_.ProcessId -Force }

    $flags = @('--resume', $s.id, '--remote-control', "'$($s.name)'")
    if ($s.skipPermissions) { $flags = @('--dangerously-skip-permissions') + $flags }
    $cmd = "Set-Location '$($s.cwd)'; & '$claude' " + ($flags -join ' ')
    $enc = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($cmd))
    Start-Process powershell -WorkingDirectory $s.cwd -ArgumentList '-NoExit', '-EncodedCommand', $enc
    Write-Host "Started $($s.name) ($($s.id))"
}
