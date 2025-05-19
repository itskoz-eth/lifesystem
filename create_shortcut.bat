@echo off
echo Creating shortcut to Life System...
mklink "%USERPROFILE%\Desktop\Life System.lnk" "%~dp0run_life_system.bat"
if %errorlevel% equ 0 (
  echo Desktop shortcut created successfully!
) else (
  echo Failed to create shortcut. You might need to run this as administrator.
)
pause 