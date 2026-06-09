@echo off
echo ============================================================
echo  Smart Label Printer - Build Script
echo ============================================================
echo.

REM Install dependencies
echo Installing dependencies...
python -m pip install -r requirements.txt --break-system-packages
python -m pip install pyinstaller --break-system-packages

echo.
echo Building EXE...
if not exist backups mkdir backups
python -m PyInstaller SmartLabelPrinter.spec --clean

echo.
if exist "dist\SmartLabelPrinter.exe" (
    echo ============================================================
    echo  BUILD SUCCESSFUL!
    echo  Output: dist\SmartLabelPrinter.exe
    echo ============================================================
) else (
    echo BUILD FAILED - Check errors above.
)
pause
