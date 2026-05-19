@echo off
echo ============================================
echo       Stock Info System Startup Script
echo ============================================
echo.
echo Choose an option:
echo [1] Start Frontend (React)
echo [2] Start Backend (Spring Boot)
echo [3] Start Both (Frontend ^& Backend)
echo [4] Exit
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto frontend
if "%choice%"=="2" goto backend
if "%choice%"=="3" goto both
if "%choice%"=="4" goto exit

echo Invalid choice. Please run again.
pause
exit /b 1

:frontend
echo Starting React Frontend...
call start-frontend.bat
goto end

:backend
echo Starting Spring Boot Backend...
call start-backend.bat
goto end

:both
echo Starting both Frontend and Backend...
echo.
echo Opening Backend in new window...
start cmd /k "call start-backend.bat"
timeout /t 5 /nobreak > nul
echo Opening Frontend in new window...
start cmd /k "call start-frontend.bat"
echo.
echo Both services are starting...
echo Frontend will be available at: http://localhost:3000
echo Backend will be available at: http://localhost:8080
goto end

:exit
echo Exiting...
goto end

:end
pause
