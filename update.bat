@echo off
setlocal EnableExtensions EnableDelayedExpansion
title Zarfolder Updater
cd /d "%~dp0"
cls

:: ANSI Color Definitions
set "ESC="
set "G=%ESC%[92m"
set "C=%ESC%[96m"
set "W=%ESC%[0m"
set "Y=%ESC%[93m"

set "APP_PID=%~1"
set "MAX_WAIT=60"
set "WAIT_COUNT=0"
set "ZIP_FILE=Zarfolder_Windows.zip"
set "DEST_PATH=.."
set "APP_EXE="

echo %C%=======================================================%W%
echo           %G%Zarfolder%W% - %Y%Update Manager%W%
echo %C%=======================================================%W%
echo.

if defined APP_PID (
    echo %C%[%W%*%C%]%W% Status: %Y%Waiting for Zarfolder to close...%W%

    :wait_app
    tasklist /FI "PID eq %APP_PID%" 2>nul | find "%APP_PID%" >nul
    if not errorlevel 1 (
        set /a WAIT_COUNT+=1

        if !WAIT_COUNT! GEQ !MAX_WAIT! (
            echo.
            echo %Y%[ERROR] Zarfolder did not close in time.%W%
            echo Please close Zarfolder manually and run the updater again.
            pause
            exit /b 1
        )

        timeout /t 1 >nul
        goto wait_app
    )
) else (
    echo %C%[%W%*%C%]%W% Status: %Y%Waiting for the app to close...%W%
    timeout /t 3 /nobreak >nul
)

if not exist "%ZIP_FILE%" (
    echo.
    echo %Y%[ERROR] Update ZIP file was not found.%W%
    pause
    exit /b 1
)

echo %C%[%W%*%C%]%W% Status: %Y%Extracting new files...%W%

powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; $ProgressPreference='SilentlyContinue'; Expand-Archive -LiteralPath '%ZIP_FILE%' -DestinationPath '%DEST_PATH%' -Force"

if errorlevel 1 (
    echo.
    echo %Y%[ERROR] Failed to extract update files.%W%
    pause
    exit /b 1
)

del /f /q "%ZIP_FILE%" >nul 2>&1

if exist "%DEST_PATH%\Zarfolder.exe" (
    set "APP_EXE=Zarfolder.exe"
    del /f /q "Z-Organizer.exe" "%DEST_PATH%\Z-Organizer.exe" >nul 2>&1
) else if exist "%DEST_PATH%\Z-Organizer.exe" (
    set "APP_EXE=Z-Organizer.exe"
)

echo.
echo %G%-------------------------------------------------------%W%
echo   [SUCCESS] Update completed!
echo   Starting Zarfolder...
echo %G%-------------------------------------------------------%W%
echo.

if defined APP_EXE (
    pushd "%DEST_PATH%"
    start "" "!APP_EXE!"
    popd
) else (
    echo.
    echo %Y%[WARNING] Zarfolder executable was not found after update.%W%
    echo Please open Zarfolder manually.
    pause
)

timeout /t 2 >nul
start "" /b cmd /c "timeout /t 1 >nul & del /f /q ""%~f0"""
exit
