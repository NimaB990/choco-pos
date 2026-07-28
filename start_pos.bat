@echo off
REM Choco Paradise POS - Development Server Launcher

pushd "%~dp0"

echo ========================================
echo  Choco Paradise POS System
echo ========================================
echo.

if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    echo Virtual environment created.
)

echo Activating virtual environment...
call ".venv\Scripts\activate.bat"

echo Installing dependencies...
python -m pip install -q -r requirements.txt

echo.
echo ========================================
echo  POS System Starting...
echo ========================================
echo.
echo  Access the system at:
echo  - POS: http://localhost:8000
echo  - Admin: http://localhost:8000/admin
echo.
echo Press Ctrl+C to stop the server.
echo ========================================
echo.

:: මෙන්න මේ කමාන්ඩ් එකෙන් Chrome එක හරහා POS එක ඔටෝම ඕපන් වෙනවා!
start "" "http://localhost:8000"

python manage.py runserver

pause