@echo off

set "key="
set "count=0"

:: Change to the directory containing the AI.exe file
cd /d "C:\Users\ciste\Desktop\TowerAI"

:loop
set /a count+=1
echo Running towerAI.exe iteration %count%
start /B towerAI.exe

:: Wait for the program to start
timeout /T 1 /nobreak >nul

timeout /T 3600 /nobreak >nul

:: Check for user input
if defined key (
  echo User input detected. Exiting loop.
  goto :eof
)

:: Send a space key to the program to stop it
powershell -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait(' ')" 

taskkill /f /im towerAI.exe >nul

:: Check for user input
if defined key (
  echo User input detected. Exiting loop.
  goto :eof
)

goto loop

:: Wait for user input
:wait
set /p key=Press space to terminate the loop...
goto loop