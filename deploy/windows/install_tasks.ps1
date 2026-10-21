# Run ONCE on the Windows server, in PowerShell "Run as administrator", from this folder:
#   powershell -ExecutionPolicy Bypass -File .\install_tasks.ps1
# Creates two Windows Task Scheduler tasks:
#   "CSP GPS Dashboard" - starts the dashboard when the server boots (restarts it if it stops)
#   "CSP GPS Report"    - rebuilds the report every day at 10:00 and 15:00 from the shared export folder
$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$user = "SYSTEM"

$dash = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$root\deploy\windows\start_dashboard.bat`"" -WorkingDirectory $root
$boot = New-ScheduledTaskTrigger -AtStartup
$keep = New-ScheduledTaskSettingsSet -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit ([TimeSpan]::Zero) -StartWhenAvailable
Register-ScheduledTask -TaskName "CSP GPS Dashboard" -Action $dash -Trigger $boot -Settings $keep -User $user -RunLevel Highest -Force | Out-Null

$rep = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$root\scripts\daily_update.bat`"" -WorkingDirectory $root
$t10 = New-ScheduledTaskTrigger -Daily -At "10:00"
$t15 = New-ScheduledTaskTrigger -Daily -At "15:00"
$once = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 1)
Register-ScheduledTask -TaskName "CSP GPS Report" -Action $rep -Trigger @($t10, $t15) -Settings $once -User $user -RunLevel Highest -Force | Out-Null

# Let other computers reach the dashboard on port 8501 (office network only).
if (-not (Get-NetFirewallRule -DisplayName "CSP GPS Dashboard 8501" -ErrorAction SilentlyContinue)) {
    New-NetFirewallRule -DisplayName "CSP GPS Dashboard 8501" -Direction Inbound -Protocol TCP -LocalPort 8501 -Action Allow -Profile Domain,Private | Out-Null
}

Start-ScheduledTask -TaskName "CSP GPS Dashboard"
Write-Host "Done. Dashboard: http://$($env:COMPUTERNAME):8501  (or http://<server-ip>:8501)"
Write-Host "Report runs daily at 10:00 and 15:00. Logs: $root\logs"
