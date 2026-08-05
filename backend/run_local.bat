@echo off
echo ===================================================
echo       FINOVO Backend Local Development Server
echo ===================================================
echo.

cd /d "%~dp0"

IF NOT EXIST "venv\Scripts\activate.bat" (
    echo Error: Virtual environment not found in 'venv' directory.
    echo Please make sure you have set up the project.
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Running Django development server on port 8000...
python manage.py runserver

pause
