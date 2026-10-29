# Starts a scheduled routine locally as a visible Remote Control session, with the prompt from
# tools/routines/<Name>.txt. Meant for a Windows scheduled task named "Routine <Name>".
# Usage: powershell -ExecutionPolicy Bypass -File tools\run_routine.ps1 -Name example [-Hours 8,9] [-Codex]
#   -Hours  only run in these local hours (24h), otherwise exit quietly
#   -Codex  run the prompt with the Codex CLI instead of Claude
# When Claude hits its usage limit, the task "Routine <Name>" gets a one-off trigger just after the reset,
# so the routine runs again by itself without using a reset credit.
param(
    [Parameter(Mandatory = $true)][string]$Name,
    [int[]]$Hours,
    [switch]$Codex,
    [switch]$Worker
)
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$promptFile = Join-Path $repo "tools\routines\$Name.txt"
$logDir = Join-Path $env:LOCALAPPDATA 'routines'
$work = Join-Path $logDir 'work'
New-Item -ItemType Directory -Force $work | Out-Null
$logFile = Join-Path $logDir "$Name.log"
$stamp = Get-Date -Format 'yyyy-MM-dd_HHmmss'
function Write-RoutineLog([string]$Message) { "$(Get-Date -Format o) $Message" | Out-File -Append -Encoding utf8 $logFile }
function Get-ClaudeLimit([string]$Transcript) {
    if (-not (Test-Path $Transcript)) { return $null }
    $line = Get-Content -LiteralPath $Transcript -Tail 60 | Select-String '"type":"assistant"' | Select-Object -Last 1
    if (-not $line) { return $null }
    try { $message = $line.Line | ConvertFrom-Json } catch { return $null }
    if ($message.apiError -eq 'usage_limit_reached' -and $message.quotaLimits.resetsAt) {
        return [DateTimeOffset]::FromUnixTimeSeconds([long]$message.quotaLimits.resetsAt).LocalDateTime.AddMinutes(1)
    }
    return $null
}
function Set-LimitRetry([datetime]$At) {
    $task = Get-ScheduledTask -TaskName "Routine $Name"
    # Keep the calendar and logon triggers, replace our own one-off recovery trigger.
    $triggers = @($task.Triggers | Where-Object { $_.CimClass.CimClassName -ne 'MSFT_TaskTimeTrigger' })
    $triggers += New-ScheduledTaskTrigger -Once -At $At
    Set-ScheduledTask -TaskName "Routine $Name" -Trigger $triggers | Out-Null
    Write-RoutineLog "rate_limited; retry_scheduled=$($At.ToString('o'))"
}

if ($Hours -and ((Get-Date).Hour -notin $Hours)) { exit 0 }
if (-not (Test-Path $promptFile)) { Write-RoutineLog "FAILED: no prompt file $promptFile"; throw "No prompt file $promptFile" }

# The scheduled task returns at once; a hidden worker owns the mutex for the whole run, including the agent.
# An overlap of a scheduled, logon and manual start can therefore never start a second run.
if (-not $Worker) {
    $arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" -Name $Name -Worker"
    if ($Codex) { $arguments += ' -Codex' }
    $child = Start-Process powershell -WindowStyle Hidden -ArgumentList $arguments -PassThru
    Write-RoutineLog "worker_launched pid=$($child.Id); this is not proof the routine succeeded"
    exit 0
}

$mutex = New-Object System.Threading.Mutex($false, "Local\Routine-$Name")
$locked = $false
try {
    try { $locked = $mutex.WaitOne(0) } catch [System.Threading.AbandonedMutexException] { $locked = $true }
    if (-not $locked) { Write-RoutineLog 'skipped: a worker already owns this routine'; exit 0 }

    # Latest runbooks, but never stash someone else's work in progress.
    if (-not (git -C $repo status --porcelain)) { git -C $repo pull --quiet --no-rebase 2>&1 | Out-File -Append $logFile }
    else { Write-RoutineLog 'sync skipped: checkout has local changes' }
    $prompt = Get-Content $promptFile -Raw

    if ($Codex) {
        $codexWork = Join-Path $logDir "codex-work\$stamp"
        New-Item -ItemType Directory -Force $codexWork | Out-Null
        $result = Join-Path $logDir "$Name-$stamp-result.txt"
        $agentLog = Join-Path $logDir "$Name-$stamp-agent.log"
        Write-RoutineLog "agent_started engine=codex result=$result"
        # Capture the real exit code and output of the agent, not the launcher's.
        $ErrorActionPreference = 'Continue'
        $prompt | & codex exec --skip-git-repo-check -C $codexWork -s danger-full-access -c 'approval_policy="never"' -o $result - *> $agentLog
        $agentExit = $LASTEXITCODE
        $ErrorActionPreference = 'Stop'
        Write-RoutineLog "agent_exited engine=codex exit=$agentExit; verify the result separately"
        if ($agentExit -ne 0) {
            # The CLI error can be wrapped over several lines in the captured output.
            if (Select-String -Path $agentLog -SimpleMatch "You've hit your usage limit") {
                $limitLine = Get-Content $agentLog | Select-String 'try again at (\d{1,2}:\d{2}\s*[AP]M)\.' | Select-Object -Last 1
                if ($limitLine) {
                    $clock = [datetime]::Parse($limitLine.Matches[0].Groups[1].Value, [Globalization.CultureInfo]::InvariantCulture)
                    $retryAt = (Get-Date).Date.Add($clock.TimeOfDay).AddMinutes(1)
                    if ($retryAt -le (Get-Date)) { $retryAt = $retryAt.AddDays(1) }
                    Set-LimitRetry $retryAt
                }
            }
            throw "Codex failed with exit code $agentExit"
        }
        return
    }

    $auth = & claude auth status | ConvertFrom-Json
    if (-not $auth.loggedIn) { throw 'Claude is logged out. Log in with /login first.' }
    # One fixed session per routine, so it shows up once in Remote Control instead of a new copy per run.
    $idFile = Join-Path $logDir "$Name.session"
    if (-not (Test-Path $idFile)) { [guid]::NewGuid().ToString() | Set-Content -NoNewline $idFile }
    $id = (Get-Content $idFile -Raw).Trim()
    $transcript = Join-Path $env:USERPROFILE ".claude\projects\$($work -replace '[^A-Za-z0-9]', '-')\$id.jsonl"
    $retryAt = Get-ClaudeLimit $transcript
    if ($retryAt -and $retryAt -gt (Get-Date)) { Set-LimitRetry $retryAt; exit 0 }
    # Stop only the exact old session before resuming.
    Get-CimInstance Win32_Process -Filter "Name='claude.exe'" |
        Where-Object { $_.CommandLine -match [regex]::Escape($id) } |
        ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
    $session = if (Test-Path $transcript) { "--resume $id" } else { "--session-id $id" }
    Write-RoutineLog "agent_started engine=claude session=$id; verify the result separately"
    # Executing a runbook needs no top model: Sonnet. The terminal stays interactive for Remote Control,
    # while this worker watches for the usage limit.
    $escapedPrompt = $prompt.Replace("'", "''")
    $command = "Set-Location '$work'; & claude --dangerously-skip-permissions --model sonnet $session --remote-control 'Routine-$Name' '$escapedPrompt'"
    $encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($command))
    $terminal = Start-Process powershell -WindowStyle Hidden -ArgumentList '-NoProfile', '-EncodedCommand', $encoded -PassThru
    do {
        if ($terminal.WaitForExit(30000)) { break }
        $retryAt = Get-ClaudeLimit $transcript
        if ($retryAt -and $retryAt -gt (Get-Date)) { Set-LimitRetry $retryAt; exit 0 }
    } while ($true)
    Write-RoutineLog "agent_exited engine=claude exit=$($terminal.ExitCode); verify the result separately"
} catch {
    Write-RoutineLog "FAILED: $($_.Exception.Message)"
    exit 1
} finally {
    if ($locked) { $mutex.ReleaseMutex() }
    $mutex.Dispose()
}
