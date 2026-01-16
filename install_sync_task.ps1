$Action = New-ScheduledTaskAction -Execute "c:\Users\Clement\.gemini\antigravity\playground\icy-interstellar\fitness-tracker\sync_drive_cron.bat" -WorkingDirectory "c:\Users\Clement\.gemini\antigravity\playground\icy-interstellar\fitness-tracker"
$Trigger = New-ScheduledTaskTrigger -Daily -At "07:00"
$TempTrigger = New-ScheduledTaskTrigger -Once -At "00:00" -RepetitionInterval (New-TimeSpan -Hours 2) -RepetitionDuration (New-TimeSpan -Hours 16)
$Trigger.Repetition = $TempTrigger.Repetition
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

$TaskName = "FitSync_Web_Import"

Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

Register-ScheduledTask -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -TaskName $TaskName -Description "Importe automatiquement les données FitSync depuis Google Drive tous les jours à 07h00 et toutes les 2h."

Write-Host "Tâche planifiée '$TaskName' créée avec succès !"
Write-Host "Elle s'exécutera tous les jours de 07h00 à 23h00, toutes les 2 heures."
