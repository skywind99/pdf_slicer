@echo off
chcp 65001 >nul 2>&1

echo.
echo ============================================
echo   PDF Slicer - EXE Build Script
echo ============================================
echo.

:: 1. pip upgrade
python -m pip install --upgrade pip -q

:: 2. ?? ?????
echo [1/3] Installing required packages...
python -m pip install customtkinter PyMuPDF Pillow pyinstaller -q
if errorlevel 1 (
    echo FAILED: pip install error
    pause
    exit /b 1
)

:: 3. customtkinter ?? ??
echo [2/3] Detecting customtkinter path...
for /f "delims=" %%i in ('python -c "import customtkinter,os;print(os.path.dirname(customtkinter.__file__))"') do set CTK_PATH=%%i

if "%CTK_PATH%"=="" (
    echo FAILED: customtkinter path not found
    pause
    exit /b 1
)
echo    Found: %CTK_PATH%

:: 4. PyInstaller ??
echo [3/3] Building EXE...
python -m PyInstaller ^
  --noconfirm ^
  --onefile ^
  --windowed ^
  --name "PDF_Slicer" ^
  --add-data "%CTK_PATH%;customtkinter/" ^
  pdf_slicer.py

echo.
if exist dist\PDF_Slicer.exe (
    echo ============================================
    echo   SUCCESS: dist\PDF_Slicer.exe
    echo ============================================
    explorer dist
) else (
    echo ============================================
    echo   FAILED: check errors above
    echo ============================================
)
echo.
pause
