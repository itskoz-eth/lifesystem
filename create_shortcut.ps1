$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\Life System.lnk")
$Shortcut.TargetPath = "C:\Users\andre\.cursor\Cursor 4.7\LifeSystem\run_life_system.bat"
$Shortcut.WorkingDirectory = "C:\Users\andre\.cursor\Cursor 4.7\LifeSystem"
$Shortcut.Description = "Launch Life System Application"
$Shortcut.IconLocation = "shell32.dll,76"
$Shortcut.Save()
Write-Host "Desktop shortcut created successfully!" 