@echo off
setlocal
cd /d "%~dp0"

if "%~1"=="" goto run
if /I "%~1"=="--help" goto help
if /I "%~1"=="-h" goto help
if /I "%~1"=="/?" goto help
goto run

:help
echo.
echo 使い方: rename.bat [オプション]
echo   --dry-run   実行せず表示のみ
echo   --move      コピーではなく移動
echo   --map PATH  マップ JSON を指定（既定: rename_map.json）
echo.
exit /b 0

:run
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    python "%~dp0scripts\rename.py" %*
    if %ERRORLEVEL% EQU 0 exit /b 0
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\rename.ps1" %*
exit /b %ERRORLEVEL%
