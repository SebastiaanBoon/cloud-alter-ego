# Starts a scheduled routine locally as a visible Remote Control session, with the prompt from
# tools/routines/<Name>.txt. Meant for a Windows scheduled task named "Routine <Name>".
# Usage: powershell -ExecutionPolicy Bypass -File tools\run_routine.ps1 -Name example [-Hours 8,9]
#   -Hours  only run in these local hours (24h), otherwise exit quietly
param(
    [Parameter(Mandatory = $true)][string]$Name,
    [int[]]$Hours
)
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$promptFile = Join-Path $repo "tools\routines\$Name.txt"
$logDir = Join-Path $env:LOCALAPPDATA 'routines'
New-Item -ItemType Directory -Force $logDir | Out-Null
$logFile = Join-Path $logDir "$Name.log"
function Write-RoutineLog([string]$Message) { "$(Get-Date -Format o) $Message" | Out-File -Append -Encoding utf8 $logFile }

if ($Hours -and ((Get-Date).Hour -notin $Hours)) { exit 0 }
if (-not (Test-Path $promptFile)) { Write-RoutineLog "FAILED: no prompt file $promptFile"; throw "No prompt file $promptFile" }

# Anti double-run: the mutex is held by the launcher until Claude exits.
$mutex = New-Object System.Threading.Mutex($false, "Local\Routine-$Name")
$locked = $false
try {
    try { $locked = $mutex.WaitOne(0) } catch [System.Threading.AbandonedMutexException] { $locked = $true }
    if (-not $locked) { Write-RoutineLog 'skipped: a worker already owns this routine'; exit 0 }

    # Latest runbooks, but never stash someone else's work in progress.
    if (-not (git -C $repo status --porcelain)) { git -C $repo pull --quiet --rebase 2>&1 | Out-File -Append $logFile }
    else { Write-RoutineLog 'sync skipped: checkout has local changes' }

    $prompt = (Get-Content $promptFile -Raw).Replace("'", "''")
    Write-RoutineLog 'agent started; verify the result separately'
    Set-Location $repo
    & claude --dangerously-skip-permissions --remote-control "Routine-$Name" $prompt
    Write-RoutineLog "agent exited code=$LASTEXITCODE"
} catch {
    Write-RoutineLog "FAILED: $($_.Exception.Message)"
    exit 1
} finally {
    if ($locked) { $mutex.ReleaseMutex() }
    $mutex.Dispose()
}
