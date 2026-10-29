# Offline regression checks for run_routine.ps1. Starts no agents and changes no scheduled tasks.
# Usage: powershell -ExecutionPolicy Bypass -File tools\test_routine_recovery.ps1
$ErrorActionPreference = 'Stop'
$tokens = $null
$parseErrors = $null
$scriptPath = Join-Path $PSScriptRoot 'run_routine.ps1'
$ast = [Management.Automation.Language.Parser]::ParseFile($scriptPath, [ref]$tokens, [ref]$parseErrors)
if ($parseErrors.Count) { throw ($parseErrors | Out-String) }
$definition = $ast.FindAll({ param($node)
    $node -is [Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq 'Get-ClaudeLimit'
}, $true)[0]
. ([scriptblock]::Create($definition.Extent.Text))
$fixture = [IO.Path]::GetTempFileName()
try {
    $limited = '{"type":"assistant","apiError":"usage_limit_reached","quotaLimits":{"resetsAt":1791982800}}'
    [IO.File]::WriteAllText($fixture, $limited)
    $expected = [DateTimeOffset]::FromUnixTimeSeconds(1791982800).LocalDateTime.AddMinutes(1)
    if ((Get-ClaudeLimit $fixture) -ne $expected) { throw 'Structured reset parsing failed' }
    [IO.File]::AppendAllText($fixture, "`n" + '{"type":"assistant","message":{"content":[{"type":"text","text":"Continuing"}]}}')
    if ($null -ne (Get-ClaudeLimit $fixture)) { throw 'A stale rate limit must not stop a resumed agent' }
    [IO.File]::WriteAllText($fixture, '{"type":"assistant","apiError":"authentication_error"}')
    if ($null -ne (Get-ClaudeLimit $fixture)) { throw 'An authentication failure must not become a usage retry' }
    [IO.File]::WriteAllText($fixture, '{"type":"assistant",')
    if ($null -ne (Get-ClaudeLimit $fixture)) { throw 'A partially written transcript must be ignored' }
    $assignments = $ast.FindAll({ param($node)
        $node -is [Management.Automation.Language.AssignmentStatementAst] -and
        $node.Left -is [Management.Automation.Language.VariableExpressionAst] -and
        $node.Left.VariablePath.UserPath -ieq 'Codex'
    }, $true)
    if ($assignments.Count) { throw 'Do not overwrite the Codex switch parameter' }
    'PASS: parser, reset timestamp, stale limit, non-limit error, partial transcript, Codex switch'
} finally {
    Remove-Item -LiteralPath $fixture
}
