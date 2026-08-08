@echo off
echo ===================================================
echo       FINOVO - Start Celery Worker + Beat
echo ===================================================
echo.
echo NOTE: Requires Redis to be running locally on port 6379.
echo.

cd /d "%~dp0"

IF NOT EXIST "venv\Scripts\activate.bat" (
    echo Error: Virtual environment not found.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo Starting Celery worker in background...
start "Celery Worker" cmd /k "celery -A config worker --loglevel=info"

timeout /t 3 >nul

echo Starting Celery beat scheduler...
celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler

pause
