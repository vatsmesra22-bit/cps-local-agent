# Removes the two scheduled tasks and the firewall rule created by install_tasks.ps1 (run as administrator).
foreach ($name in "CSP GPS Dashboard", "CSP GPS Report") {
    if (Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue) {
        Stop-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue
        Unregister-ScheduledTask -TaskName $name -Confirm:$false
    }
}
Get-NetFirewallRule -DisplayName "CSP GPS Dashboard 8501" -ErrorAction SilentlyContinue | Remove-NetFirewallRule
Write-Host "Removed."
