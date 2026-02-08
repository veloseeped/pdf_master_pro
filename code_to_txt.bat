@echo off
setlocal EnableDelayedExpansion

:: ============================================================
:: CONFIGURATION
:: ============================================================
set "OUTPUT_FILE=project_code.txt"
set "FILE_PATTERNS=*.py *.ini *.txt *.md "
set "IGNORE_DIRS=venv build dist .git __pycache__ .idea .vscode .pytest_cache egg-info"

:: ============================================================
:: MAIN EXECUTION
:: ============================================================

call :InitializeOutput
call :ScanAndCollect
echo [INFO] Build complete. Output saved to: %OUTPUT_FILE%
pause
goto :eof

:: ============================================================
:: FUNCTIONS
:: ============================================================

:: Cleans up previous artifacts
:InitializeOutput
    if exist "%OUTPUT_FILE%" del "%OUTPUT_FILE%"
    exit /b

:: Iterates recursively through files and applies filters
:ScanAndCollect
    echo [INFO] Scanning project files...
    
    for /r %%F in (%FILE_PATTERNS%) do (
        call :ShouldProcessFile "%%F" is_valid
        
        if "!is_valid!"=="true" (
            echo Processing: %%~nxF
            call :AppendToFile "%%F"
        )
    )
    exit /b

:: Determines if a file path contains ignored directory names
:: Args: %1 = File Path, %2 = Return Variable Name
:ShouldProcessFile
    set "file_path=%~1"
    set "result=true"
    
    :: Iterate through ignored directories to check for substring match
    for %%I in (%IGNORE_DIRS%) do (
        echo !file_path! | findstr /C:"\\%%I\\" >nul
        if !errorlevel! equ 0 set "result=false"
        
        :: Double check for directory root match (if needed) or simple string match
        echo !file_path! | findstr /C:"\%%I\" >nul
        if !errorlevel! equ 0 set "result=false"
    )
    
    set "%~2=!result!"
    exit /b

:: Formats and writes the file content
:: Args: %1 = File Path
:AppendToFile
    echo. >> "%OUTPUT_FILE%"
    echo ################################################################################ >> "%OUTPUT_FILE%"
    echo # FILE: %~1 >> "%OUTPUT_FILE%"
    echo ################################################################################ >> "%OUTPUT_FILE%"
    echo. >> "%OUTPUT_FILE%"
    type "%~1" >> "%OUTPUT_FILE%"
    echo. >> "%OUTPUT_FILE%"
    exit /b