@echo off

set "key="
set "count=0"

:: Change to the directory containing the AI.exe file
cd /d "C:\Users\ciste\Desktop\TowerAI"

:loop
set /a count+=1
echo Running towerAI.exe iteration %count%
start /B towerAI.exe

timeout /T 1800 /nobreak >nul

:: Check for user input
if defined key (
  echo User input detected. Exiting loop.
  goto :eof
)

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