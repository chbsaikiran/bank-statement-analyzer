@echo off
setlocal ENABLEDELAYEDEXPANSION

REM =====================================================
REM Usage:
REM   run_for_details.bat "<input_csv>" [month-year]
REM Examples:
REM   run_for_details.bat "F:\Saikiran\Axis_Bank\Aug2025.csv"
REM   run_for_details.bat "F:\Saikiran\Axis_Bank\Aug2025.csv" 09-2025
REM =====================================================

if "%~1"=="" (
    echo Usage: %~nx0 input_csv [month-year]
    exit /b 1
)

set "CSV_FILE=%~1"
set "MONTH_ARG=%~2"
set "JSON_FILE=%~dp1%~n1.json"

echo.
echo ==========================================
echo Processing:
echo   CSV  = "%CSV_FILE%"
echo   JSON = "%JSON_FILE%"
if defined MONTH_ARG echo   Month = %MONTH_ARG%
echo ==========================================

REM --- Step 1: Create JSON ---
echo Creating JSON file...
python "%~dp0create_json_from_csv.py" "%CSV_FILE%" "%JSON_FILE%"
if errorlevel 1 (
    echo Error: create_json_from_csv.py failed.
    pause
    exit /b 1
)

echo JSON created successfully: "%JSON_FILE%"
echo ------------------------------------------

REM --- Step 2: Run analysis (with or without month argument) ---
if defined MONTH_ARG (
    echo Running analysis for month: %MONTH_ARG% ...
    python "%~dp0get_details_from_json.py" "%JSON_FILE%" "%MONTH_ARG%"
) else (
    echo Running analysis for all months...
    python "%~dp0get_details_from_json.py" "%JSON_FILE%"
)

if errorlevel 1 (
    echo Error: get_details_from_json.py failed.
    pause
    exit /b 1
)

echo ------------------------------------------
echo Processing complete!
pause
endlocal
