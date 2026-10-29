# Windows logon fallback for the installed ChatGPT desktop app (run it from a logon scheduled task).
# The package startup task remains enabled; do not launch a second instance.
$ErrorActionPreference = 'Stop'
if (Get-Process -Name ChatGPT -ErrorAction SilentlyContinue) {
    Write-Output 'ChatGPT is already running.'
    exit 0
}
$app = @(Get-StartApps | Where-Object { $_.Name -eq 'ChatGPT' })
if ($app.Count -ne 1) {
    throw 'Expected exactly one installed ChatGPT application.'
}
Start-Process -FilePath (Join-Path $env:WINDIR 'explorer.exe') -WindowStyle Hidden -ArgumentList ('shell:AppsFolder\' + $app[0].AppID)
