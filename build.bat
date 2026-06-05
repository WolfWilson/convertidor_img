@echo off
REM Build script: create a one-dir Windows app with PyInstaller
SETLOCAL ENABLEDELAYEDEXPANSION

REM -- Activate virtualenv if present (common layout)
if exist venv\Scripts\activate.bat (
  call venv\Scripts\activate.bat
)

REM -- Ensure PyInstaller is available
python -m pip install --upgrade pyinstaller

REM -- Clean previous artifacts (optional)
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /q *.spec

REM -- Build: one-dir, GUI app (no console), use root icon Photo-Manipulation.ico
REM -- Use absolute paths (%~dp0) so --add-data works regardless of cwd
pyinstaller --onedir --noconsole --icon="%~dp0Photo-Manipulation.ico" --add-data "%~dp0styles;styles" --name "ConvertidorImg" "%~dp0main.py"

if %ERRORLEVEL% NEQ 0 (
  echo PyInstaller falló con código %ERRORLEVEL%.
  pause
  exit /b %ERRORLEVEL%
)

echo Build completado. Salida: dist\ConvertidorImg\
pause
