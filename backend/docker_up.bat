@echo off
echo ===================================================
echo       FINOVO Backend - Docker Compose Start
echo ===================================================
echo.

cd /d "%~dp0"

echo Building and starting Docker containers...
docker-compose up --build

pause
